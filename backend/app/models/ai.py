from sqlalchemy import Column, String, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum
from app.models.base import BaseModel

class SenderRole(str, enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class ConversationSession(BaseModel):
    __tablename__ = "conversation_sessions"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    title = Column(String(200), default="New Life Synthesis", nullable=False)
    module_focus = Column(String(50), default="UNIVERSAL", nullable=False) # UNIVERSAL, ACADEMIC, FINANCE, LIFE_ADMIN

    # Relationships
    user = relationship("User", back_populates="conversation_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan", order_by="ChatMessage.created_at")

class ChatMessage(BaseModel):
    __tablename__ = "chat_messages"

    session_id = Column(String(36), ForeignKey("conversation_sessions.id", ondelete="CASCADE"), index=True, nullable=False)
    role = Column(SQLEnum(SenderRole), nullable=False)
    content = Column(Text, nullable=False)
    routed_modules = Column(String(255), nullable=True) # e.g. "ACADEMIC,FINANCE"
    source_references = Column(Text, nullable=True) # JSON string of citations
    action_proposal = Column(Text, nullable=True) # JSON string of proposed tool actions
    action_status = Column(String(50), nullable=True) # PROPOSED, EXECUTED, CANCELLED

    # Relationships
    session = relationship("ConversationSession", back_populates="messages")
