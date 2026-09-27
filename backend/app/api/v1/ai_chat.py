from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, delete
from typing import List, Dict, Any
import json
from datetime import datetime, timezone
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.ai import ConversationSession, ChatMessage, SenderRole
from app.schemas.ai import (
    ChatMessageRequest, ChatMessageResponse,
    ConversationSessionResponse, ConversationSessionBriefResponse,
    ConversationCreateRequest, ActionExecuteRequest, ActionProposal, CitationSource
)
from app.ai_engine.router import AIRouter
from app.ai_engine.retrievers.academic_retriever import AcademicRetriever
from app.ai_engine.retrievers.finance_retriever import FinanceRetriever
from app.ai_engine.retrievers.life_retriever import LifeRetriever
from app.ai_engine.retrievers.cross_module_retriever import CrossModuleRetriever
from app.ai_engine.rag_engine import RAGEngine
from app.ai_engine.llm_client import llm_client
from app.ai_engine.action_executor import ActionExecutor
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["Universal AI"])

# ─────────────────────────────────────────────────────────────────────────────
# HELPER: serialize a DB message to ChatMessageResponse
# ─────────────────────────────────────────────────────────────────────────────
def _serialize_message(m: ChatMessage) -> ChatMessageResponse:
    citations: List[CitationSource] = []
    if m.source_references:
        try:
            citations = [CitationSource(**c) for c in json.loads(m.source_references)]
        except Exception:
            pass

    action_prop = None
    if m.action_proposal:
        try:
            action_prop = ActionProposal(**json.loads(m.action_proposal))
        except Exception:
            pass

    return ChatMessageResponse(
        id=m.id,
        session_id=m.session_id,
        role=m.role,
        content=m.content,
        routed_modules=m.routed_modules.split(",") if m.routed_modules else [],
        source_references=citations,
        action_proposal=action_prop,
        action_status=m.action_status,
        created_at=m.created_at
    )


# ─────────────────────────────────────────────────────────────────────────────
# CONVERSATION MANAGEMENT
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/conversations", response_model=List[ConversationSessionBriefResponse])
async def list_conversations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all conversation sessions for the current user (brief view, no messages)."""
    stmt = select(ConversationSession).where(
        ConversationSession.user_id == current_user.id
    ).order_by(ConversationSession.created_at.desc())
    res = await db.execute(stmt)
    sessions = res.scalars().all()

    result = []
    for s in sessions:
        # Count messages without loading them all
        count_stmt = select(func.count()).where(ChatMessage.session_id == s.id)
        count_res = await db.execute(count_stmt)
        msg_count = count_res.scalar() or 0

        result.append(ConversationSessionBriefResponse(
            id=s.id,
            user_id=s.user_id,
            title=s.title,
            module_focus=s.module_focus,
            message_count=msg_count,
            created_at=s.created_at
        ))
    return result


@router.post("/conversations", response_model=ConversationSessionBriefResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    data: ConversationCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Explicitly create a new conversation session."""
    session = ConversationSession(
        user_id=current_user.id,
        title=data.title,
        module_focus=data.module_focus or "UNIVERSAL"
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)

    return ConversationSessionBriefResponse(
        id=session.id,
        user_id=session.user_id,
        title=session.title,
        module_focus=session.module_focus,
        message_count=0,
        created_at=session.created_at
    )


@router.get("/conversations/{conversation_id}", response_model=ConversationSessionResponse)
async def get_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a single conversation session with all its messages."""
    s_res = await db.execute(
        select(ConversationSession).where(
            ConversationSession.id == conversation_id,
            ConversationSession.user_id == current_user.id  # ownership enforced
        )
    )
    session = s_res.scalars().first()
    if not session:
        raise HTTPException(status_code=404, detail="Conversation not found")

    msg_res = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session.id)
        .order_by(ChatMessage.created_at.asc())
    )
    messages = msg_res.scalars().all()

    return ConversationSessionResponse(
        id=session.id,
        user_id=session.user_id,
        title=session.title,
        module_focus=session.module_focus,
        created_at=session.created_at,
        messages=[_serialize_message(m) for m in messages]
    )


@router.get("/conversations/{conversation_id}/messages", response_model=List[ChatMessageResponse])
async def get_conversation_messages(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get only the messages for a conversation (lightweight for infinite scroll)."""
    # Verify ownership first
    s_res = await db.execute(
        select(ConversationSession).where(
            ConversationSession.id == conversation_id,
            ConversationSession.user_id == current_user.id
        )
    )
    session = s_res.scalars().first()
    if not session:
        raise HTTPException(status_code=404, detail="Conversation not found")

    msg_res = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session.id)
        .order_by(ChatMessage.created_at.asc())
    )
    messages = msg_res.scalars().all()
    return [_serialize_message(m) for m in messages]


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a conversation session and all its messages (cascade delete)."""
    s_res = await db.execute(
        select(ConversationSession).where(
            ConversationSession.id == conversation_id,
            ConversationSession.user_id == current_user.id  # ownership enforced
        )
    )
    session = s_res.scalars().first()
    if not session:
        raise HTTPException(status_code=404, detail="Conversation not found")

    await db.delete(session)  # cascade deletes messages via relationship
    await db.commit()


# ─────────────────────────────────────────────────────────────────────────────
# LEGACY: GET /ai/sessions (kept for backward compat with frontend)
# ─────────────────────────────────────────────────────────────────────────────
@router.get("/sessions", response_model=List[ConversationSessionResponse])
async def get_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Legacy endpoint: returns sessions with full messages. Use /conversations instead."""
    stmt = select(ConversationSession).where(
        ConversationSession.user_id == current_user.id
    ).order_by(ConversationSession.created_at.desc())
    res = await db.execute(stmt)
    sessions = res.scalars().all()

    result = []
    for s in sessions:
        msg_res = await db.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == s.id)
            .order_by(ChatMessage.created_at.asc())
        )
        messages = msg_res.scalars().all()
        result.append(ConversationSessionResponse(
            id=s.id, user_id=s.user_id, title=s.title,
            module_focus=s.module_focus, created_at=s.created_at,
            messages=[_serialize_message(m) for m in messages]
        ))
    return result


# ─────────────────────────────────────────────────────────────────────────────
# UNIVERSAL AI CHAT  — POST /ai/chat
# ─────────────────────────────────────────────────────────────────────────────
@router.post("/chat", response_model=ChatMessageResponse)
async def chat_query(
    chat_in: ChatMessageRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    The Universal AI chat endpoint.

    Pipeline:
      USER MESSAGE
        → Query Router (intent + module detection)
        → Multi-Module Retrievers (deterministic, structured context)
        → Optional Cross-Module aggregation
        → LLM Synthesis (context-grounded, no DB access)
        → Persist + Return (with citations)

    The LLM NEVER accesses the database directly.
    All personal data comes from controlled retrieval services.
    """
    # ── 1. Resolve or auto-create session ─────────────────────────────────
    session = None
    if chat_in.session_id:
        s_res = await db.execute(
            select(ConversationSession).where(
                ConversationSession.id == chat_in.session_id,
                ConversationSession.user_id == current_user.id  # ownership enforced
            )
        )
        session = s_res.scalars().first()

    if not session:
        session_title = (chat_in.message[:35] + "...") if len(chat_in.message) > 35 else chat_in.message
        session = ConversationSession(
            user_id=current_user.id,
            title=session_title,
            module_focus="UNIVERSAL"
        )
        db.add(session)
        await db.flush()

    # ── 2. Persist user message ────────────────────────────────────────────
    user_msg = ChatMessage(
        session_id=session.id,
        role=SenderRole.USER,
        content=chat_in.message
    )
    db.add(user_msg)
    await db.flush()

    # ── 3. Semantic Router — intent + target module detection ──────────────
    routed_modules, intent = AIRouter.route_query(chat_in.message)
    logger.info(f"[AI Router] user={current_user.id} modules={routed_modules} intent={intent}")

    # ── 4. Deterministic multi-module retrieval ────────────────────────────
    # The LLM receives ONLY structured context produced by these retrievers.
    # It NEVER receives raw SQL, raw DB sessions, or unfiltered table dumps.
    retrieved_context: Dict[str, Any] = {}

    if "ACADEMICS" in routed_modules:
        retrieved_context["academics"] = await AcademicRetriever.retrieve_context(
            db, current_user.id, chat_in.message
        )

    if "FINANCE" in routed_modules:
        retrieved_context["finance"] = await FinanceRetriever.retrieve_context(
            db, current_user.id, chat_in.message
        )

    if "LIFE_ADMIN" in routed_modules:
        retrieved_context["life_admin"] = await LifeRetriever.retrieve_context(
            db, current_user.id, chat_in.message
        )

    # Cross-module composite context: triggered for CROSS_MODULE intent or ≥2 modules
    if intent == "CROSS_MODULE" or len(routed_modules) >= 2:
        retrieved_context["cross_module"] = await CrossModuleRetriever.retrieve_context(
            db, current_user.id, chat_in.message
        )
        logger.info(f"[AI Router] Cross-module context added for user={current_user.id}")

    # RAG document search for specific keyword matches
    rag_chunks = await RAGEngine.search_relevant_chunks(
        db, current_user.id, chat_in.message, top_k=3
    )
    if rag_chunks:
        retrieved_context["personal_rag_documents"] = rag_chunks

    # ── 5. Recent conversation context (multi-turn resolution) ─────────────
    hist_stmt = (
        select(ChatMessage)
        .where(ChatMessage.session_id == session.id)
        .order_by(ChatMessage.created_at.desc())
        .limit(6)  # last 3 turns (user + assistant pairs)
    )
    h_res = await db.execute(hist_stmt)
    history_msgs = list(reversed(h_res.scalars().all()))
    conv_history = [{"role": m.role.value, "content": m.content} for m in history_msgs]

    # ── 6. LLM synthesis — context-grounded, no hallucination ─────────────
    # The LLM receives verified context only. It explains/combines values.
    # Deterministic calculations (attendance %, remaining budget, etc.)
    # are always sourced from retrievers, never computed by the LLM.
    ai_result = await llm_client.generate_response(
        chat_in.message, retrieved_context, conv_history
    )

    # ── 7. Persist AI response with citations ─────────────────────────────
    citations_json = (
        json.dumps([c.model_dump() for c in ai_result["citations"]])
        if ai_result["citations"] else None
    )
    action_proposal_json = (
        json.dumps(ai_result["action_proposal"].model_dump())
        if ai_result["action_proposal"] else None
    )

    ai_msg = ChatMessage(
        session_id=session.id,
        role=SenderRole.ASSISTANT,
        content=ai_result["content"],
        routed_modules=",".join(routed_modules),
        source_references=citations_json,
        action_proposal=action_proposal_json,
        action_status="PROPOSED" if ai_result["action_proposal"] else None
    )
    db.add(ai_msg)
    await db.commit()
    await db.refresh(ai_msg)

    return ChatMessageResponse(
        id=ai_msg.id,
        session_id=ai_msg.session_id,
        role=ai_msg.role,
        content=ai_msg.content,
        routed_modules=routed_modules,
        source_references=ai_result["citations"],
        action_proposal=ai_result["action_proposal"],
        action_status=ai_msg.action_status,
        created_at=ai_msg.created_at
    )


# ─────────────────────────────────────────────────────────────────────────────
# ACTION EXECUTION  — POST /ai/action/execute
# ─────────────────────────────────────────────────────────────────────────────
@router.post("/action/execute")
async def execute_action(
    action_in: ActionExecuteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Execute a proposed AI action.

    The user must explicitly confirm action proposals from the chat.
    This endpoint is the only path through which AI suggestions can
    modify user data. All mutations are audit-logged via message status.
    """
    result = await ActionExecutor.execute_action(
        db=db,
        user_id=current_user.id,
        action_type=action_in.action_type,
        params=action_in.params
    )

    # Update message action status for audit trail
    if action_in.message_id:
        m_stmt = select(ChatMessage).where(ChatMessage.id == action_in.message_id)
        m_res = await db.execute(m_stmt)
        msg = m_res.scalars().first()
        if msg:
            msg.action_status = "EXECUTED" if result.get("status") == "SUCCESS" else "FAILED"
            await db.commit()

    return result
