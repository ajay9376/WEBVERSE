from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.ai import SenderRole

class ChatMessageRequest(BaseModel):
    session_id: Optional[str] = None
    message: str
    stream: Optional[bool] = False

class CitationSource(BaseModel):
    module: str # ACADEMIC, FINANCE, LIFE_ADMIN, RAG_DOCUMENT
    title: str
    detail: str
    reference_id: Optional[str] = None

class ActionProposal(BaseModel):
    action_type: str # CREATE_EXPENSE, MARK_ATTENDANCE, CREATE_REMINDER, CREATE_ASSIGNMENT
    module: str
    params: Dict[str, Any]
    summary_text: str

class ChatMessageResponse(BaseModel):
    id: str
    session_id: str
    role: SenderRole
    content: str
    routed_modules: List[str] = []
    source_references: List[CitationSource] = []
    action_proposal: Optional[ActionProposal] = None
    action_status: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ConversationSessionResponse(BaseModel):
    id: str
    user_id: str
    title: str
    module_focus: str
    created_at: datetime
    messages: List[ChatMessageResponse] = []

    class Config:
        from_attributes = True

class ActionExecuteRequest(BaseModel):
    action_type: str
    params: Dict[str, Any]
    message_id: Optional[str] = None
