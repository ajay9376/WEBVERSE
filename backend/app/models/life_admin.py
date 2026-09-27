from sqlalchemy import Column, String, Float, DateTime, Boolean, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum
from app.models.base import BaseModel

class DocumentCategory(str, enum.Enum):
    INSURANCE = "INSURANCE"
    CERTIFICATE = "CERTIFICATE"
    BILL = "BILL"
    RECEIPT = "RECEIPT"
    IDENTITY = "IDENTITY"
    ACADEMIC = "ACADEMIC"
    MEDICAL = "MEDICAL"
    OTHER = "OTHER"

class ReminderPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class Document(BaseModel):
    __tablename__ = "documents"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=False) # application/pdf, image/jpeg, etc.
    file_size = Column(Float, nullable=False) # in KB
    category = Column(SQLEnum(DocumentCategory), default=DocumentCategory.OTHER, nullable=False)
    tags = Column(String(255), nullable=True) # comma-separated
    extracted_text = Column(Text, nullable=True)
    metadata_json = Column(Text, nullable=True) # JSON string: provider, policy_no, expiry_date, amount, etc.
    is_indexed = Column(Boolean, default=False, nullable=False)

    # Relationships
    user = relationship("User", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")

class Reminder(BaseModel):
    __tablename__ = "reminders"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    due_at = Column(DateTime, index=True, nullable=False)
    priority = Column(SQLEnum(ReminderPriority), default=ReminderPriority.MEDIUM, nullable=False)
    is_completed = Column(Boolean, default=False, nullable=False)
    linked_module = Column(String(50), nullable=True) # ACADEMIC, FINANCE, LIFE_ADMIN
    linked_id = Column(String(36), nullable=True)

    # Relationships
    user = relationship("User", back_populates="reminders")
