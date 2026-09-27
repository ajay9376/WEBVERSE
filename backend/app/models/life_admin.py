from sqlalchemy import Column, String, Float, DateTime, Boolean, Text, ForeignKey, Numeric, Date, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum
from datetime import datetime, timezone
from app.models.base import BaseModel

class DocumentCategory(str, enum.Enum):
    IDENTITY = "IDENTITY"
    EDUCATION = "EDUCATION"
    INSURANCE = "INSURANCE"
    FINANCE = "FINANCE"
    BILLS = "BILLS"
    MEDICAL = "MEDICAL"
    TRAVEL = "TRAVEL"
    CERTIFICATES = "CERTIFICATES"
    LEGAL = "LEGAL"
    OTHER = "OTHER"

class ReminderPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class ReminderStatus(str, enum.Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class BillStatus(str, enum.Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    OVERDUE = "OVERDUE"
    CANCELLED = "CANCELLED"

class RecurrencePattern(str, enum.Enum):
    NONE = "NONE"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    YEARLY = "YEARLY"
    CUSTOM = "CUSTOM"

class PolicyType(str, enum.Enum):
    HEALTH = "HEALTH"
    VEHICLE = "VEHICLE"
    LIFE = "LIFE"
    TRAVEL = "TRAVEL"
    HOME = "HOME"
    OTHER = "OTHER"

class PremiumFrequency(str, enum.Enum):
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    YEARLY = "YEARLY"
    ONE_TIME = "ONE_TIME"

class ImportantDateCategory(str, enum.Enum):
    PASSPORT = "PASSPORT"
    LICENSE = "LICENSE"
    WARRANTY = "WARRANTY"
    COLLEGE = "COLLEGE"
    RENEWAL = "RENEWAL"
    ANNIVERSARY = "ANNIVERSARY"
    OTHER = "OTHER"

class LifeAdminCategory(BaseModel):
    __tablename__ = "life_admin_categories"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    icon = Column(String(50), default="folder", nullable=False)
    color = Column(String(30), default="#00f3ff", nullable=False)
    is_system = Column(Boolean, default=False, nullable=False)

    # Relationships
    user = relationship("User", back_populates="life_admin_categories")
    documents = relationship("Document", back_populates="category_rel")

class Document(BaseModel):
    __tablename__ = "documents"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    category_id = Column(String(36), ForeignKey("life_admin_categories.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(100), nullable=False) # application/pdf, image/png, etc.
    file_size = Column(Float, nullable=False) # in KB
    category = Column(SQLEnum(DocumentCategory), default=DocumentCategory.OTHER, nullable=False)
    tags = Column(String(255), nullable=True) # comma-separated
    document_date = Column(DateTime, nullable=True)
    expiry_date = Column(DateTime, nullable=True)
    issuer = Column(String(150), nullable=True)
    reference_number = Column(String(100), nullable=True)
    extracted_text = Column(Text, nullable=True)
    metadata_json = Column(Text, nullable=True)
    is_indexed = Column(Boolean, default=False, nullable=False)

    # Relationships
    user = relationship("User", back_populates="documents")
    category_rel = relationship("LifeAdminCategory", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")

    @property
    def file_name(self) -> str:
        return self.filename

    @property
    def mime_type(self) -> str:
        return self.file_type

    @property
    def storage_key(self) -> str:
        return self.stored_filename

class Bill(BaseModel):
    __tablename__ = "bills"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    title = Column(String(255), nullable=False)
    provider = Column(String(150), nullable=False)
    category = Column(String(100), default="UTILITIES", nullable=False) # Electricity, Internet, Rent, Tuition, Mess
    amount = Column(Numeric(12, 2), nullable=False)
    due_date = Column(DateTime, index=True, nullable=False)
    status = Column(SQLEnum(BillStatus), default=BillStatus.PENDING, nullable=False)
    recurring = Column(Boolean, default=False, nullable=False)
    recurrence = Column(SQLEnum(RecurrencePattern), default=RecurrencePattern.NONE, nullable=False)
    payment_reference = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", back_populates="bills")

class InsurancePolicy(BaseModel):
    __tablename__ = "insurance_policies"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    provider = Column(String(150), nullable=False)
    policy_name = Column(String(200), nullable=False)
    policy_number = Column(String(100), nullable=False)
    policy_type = Column(SQLEnum(PolicyType), default=PolicyType.OTHER, nullable=False)
    start_date = Column(DateTime, nullable=True)
    expiry_date = Column(DateTime, index=True, nullable=False)
    premium_amount = Column(Numeric(12, 2), nullable=False)
    premium_frequency = Column(SQLEnum(PremiumFrequency), default=PremiumFrequency.YEARLY, nullable=False)
    coverage_amount = Column(Numeric(12, 2), nullable=True)
    document_id = Column(String(36), nullable=True)
    notes = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", back_populates="insurance_policies")

class ImportantDate(BaseModel):
    __tablename__ = "important_dates"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    date = Column(DateTime, index=True, nullable=False)
    category = Column(SQLEnum(ImportantDateCategory), default=ImportantDateCategory.OTHER, nullable=False)
    recurring = Column(Boolean, default=False, nullable=False)
    recurrence = Column(SQLEnum(RecurrencePattern), default=RecurrencePattern.NONE, nullable=False)

    # Relationships
    user = relationship("User", back_populates="important_dates")

class Reminder(BaseModel):
    __tablename__ = "reminders"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    due_at = Column(DateTime, index=True, nullable=False)
    priority = Column(SQLEnum(ReminderPriority), default=ReminderPriority.MEDIUM, nullable=False)
    status = Column(SQLEnum(ReminderStatus), default=ReminderStatus.PENDING, nullable=False)
    is_completed = Column(Boolean, default=False, nullable=False)
    linked_module = Column(String(50), nullable=True) # ACADEMIC, FINANCE, LIFE_ADMIN
    linked_id = Column(String(36), nullable=True)

    # Relationships
    user = relationship("User", back_populates="reminders")
