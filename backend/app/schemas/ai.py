from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.ai import SenderRole

class ChatMessageRequest(BaseModel):
    session_id: Optional[str] = None
    message: str
    stream: Optional[bool] = False

class ConversationCreateRequest(BaseModel):
    title: Optional[str] = "New Life Synthesis"
    module_focus: Optional[str] = "UNIVERSAL"

class CitationSource(BaseModel):
    module: str  # ACADEMICS, FINANCE, LIFE_ADMIN, RAG_DOCUMENT, CROSS_MODULE
    title: str
    detail: str
    reference_id: Optional[str] = None

class ActionProposal(BaseModel):
    action_type: str  # CREATE_EXPENSE, MARK_ATTENDANCE, CREATE_REMINDER, CREATE_ASSIGNMENT, CREATE_BILL
    module: str
    params: Dict[str, Any]
    summary_text: str

class ChatMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    session_id: str
    role: SenderRole
    content: str
    routed_modules: List[str] = []
    source_references: List[CitationSource] = []
    action_proposal: Optional[ActionProposal] = None
    action_status: Optional[str] = None
    created_at: datetime

class ConversationSessionBriefResponse(BaseModel):
    """Lightweight session summary without messages — for the list view."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    title: str
    module_focus: str
    message_count: int = 0
    created_at: datetime

class ConversationSessionResponse(BaseModel):
    """Full session with all messages and citations."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    title: str
    module_focus: str
    created_at: datetime
    messages: List[ChatMessageResponse] = []

class ActionExecuteRequest(BaseModel):
    action_type: str
    params: Dict[str, Any]
    message_id: Optional[str] = None
