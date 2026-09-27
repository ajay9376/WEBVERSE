from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Dict, Any
import json
from datetime import datetime, timezone
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.ai import ConversationSession, ChatMessage, SenderRole
from app.schemas.ai import (
    ChatMessageRequest, ChatMessageResponse, ConversationSessionResponse, 
    ActionExecuteRequest, ActionProposal, CitationSource
)
from app.ai_engine.router import AIRouter
from app.ai_engine.retrievers.academic_retriever import AcademicRetriever
from app.ai_engine.retrievers.finance_retriever import FinanceRetriever
from app.ai_engine.retrievers.life_retriever import LifeRetriever
from app.ai_engine.rag_engine import RAGEngine
from app.ai_engine.llm_client import llm_client
from app.ai_engine.action_executor import ActionExecutor

router = APIRouter(prefix="/ai", tags=["Universal AI"])

@router.get("/sessions", response_model=List[ConversationSessionResponse])
async def get_sessions(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    stmt = select(ConversationSession).where(ConversationSession.user_id == current_user.id).order_by(ConversationSession.created_at.desc())
    res = await db.execute(stmt)
    sessions = res.scalars().all()
    
    resp = []
    for s in sessions:
        msg_stmt = select(ChatMessage).where(ChatMessage.session_id == s.id).order_by(ChatMessage.created_at.asc())
        m_res = await db.execute(msg_stmt)
        msgs = m_res.scalars().all()
        
        formatted_msgs = []
        for m in msgs:
            citations = []
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

            formatted_msgs.append(ChatMessageResponse(
                id=m.id,
                session_id=m.session_id,
                role=m.role,
                content=m.content,
                routed_modules=m.routed_modules.split(",") if m.routed_modules else [],
                source_references=citations,
                action_proposal=action_prop,
                action_status=m.action_status,
                created_at=m.created_at
            ))

        resp.append(ConversationSessionResponse(
            id=s.id,
            user_id=s.user_id,
            title=s.title,
            module_focus=s.module_focus,
            created_at=s.created_at,
            messages=formatted_msgs
        ))
    return resp

@router.post("/chat", response_model=ChatMessageResponse)
async def chat_query(
    chat_in: ChatMessageRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # 1. Resolve or Create Session
    session = None
    if chat_in.session_id:
        s_res = await db.execute(select(ConversationSession).where(ConversationSession.id == chat_in.session_id, ConversationSession.user_id == current_user.id))
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

    # 2. Save User Message
    user_msg = ChatMessage(
        session_id=session.id,
        role=SenderRole.USER,
        content=chat_in.message
    )
    db.add(user_msg)
    await db.flush()

    # 3. AI Semantic Router: Intent and Target Modules
    routed_modules, intent = AIRouter.route_query(chat_in.message)

    # 4. Deterministic Multi-Module Retrieval
    retrieved_context: Dict[str, Any] = {}

    if "ACADEMICS" in routed_modules:
        retrieved_context["academics"] = await AcademicRetriever.retrieve_context(db, current_user.id, chat_in.message)

    if "FINANCE" in routed_modules:
        retrieved_context["finance"] = await FinanceRetriever.retrieve_context(db, current_user.id, chat_in.message)

    if "LIFE_ADMIN" in routed_modules:
        retrieved_context["life_admin"] = await LifeRetriever.retrieve_context(db, current_user.id, chat_in.message)

    # Always check RAG document chunks for any specific keyword matches
    rag_chunks = await RAGEngine.search_relevant_chunks(db, current_user.id, chat_in.message, top_k=3)
    if rag_chunks:
        retrieved_context["personal_rag_documents"] = rag_chunks

    # 5. Get recent conversation history for multi-turn context
    hist_stmt = select(ChatMessage).where(ChatMessage.session_id == session.id).order_by(ChatMessage.created_at.desc()).limit(6)
    h_res = await db.execute(hist_stmt)
    history_msgs = list(reversed(h_res.scalars().all()))
    conv_history = [{"role": m.role.value, "content": m.content} for m in history_msgs]

    # 6. LLM Synthesis & Reasoning
    ai_result = await llm_client.generate_response(chat_in.message, retrieved_context, conv_history)

    # 7. Persist AI Message
    citations_json = json.dumps([c.model_dump() for c in ai_result["citations"]]) if ai_result["citations"] else None
    action_proposal_json = json.dumps(ai_result["action_proposal"].model_dump()) if ai_result["action_proposal"] else None

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

@router.post("/action/execute")
async def execute_action(
    action_in: ActionExecuteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await ActionExecutor.execute_action(
        db=db,
        user_id=current_user.id,
        action_type=action_in.action_type,
        params=action_in.params
    )
    
    # Update message status if message_id provided
    if action_in.message_id:
        m_stmt = select(ChatMessage).where(ChatMessage.id == action_in.message_id)
        m_res = await db.execute(m_stmt)
        msg = m_res.scalars().first()
        if msg:
            msg.action_status = "EXECUTED" if result.get("status") == "SUCCESS" else "FAILED"
            await db.commit()

    return result
