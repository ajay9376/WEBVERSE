from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime as PyDateTime, date as PyDate
from decimal import Decimal
from app.models.life_admin import (
    DocumentCategory,
    ReminderPriority,
    ReminderStatus,
    BillStatus,
    RecurrencePattern,
    PolicyType,
    PremiumFrequency,
    ImportantDateCategory,
)

# ----------------- Life Admin Category Schemas -----------------
class LifeAdminCategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    icon: Optional[str] = Field("folder", max_length=50)
    color: Optional[str] = Field("#00f3ff", max_length=30)

class LifeAdminCategoryCreate(LifeAdminCategoryBase):
    pass

class LifeAdminCategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None

class LifeAdminCategoryResponse(LifeAdminCategoryBase):
    id: str
    user_id: str
    is_system: bool = False
    created_at: PyDateTime
    updated_at: PyDateTime

    model_config = ConfigDict(from_attributes=True)

# ----------------- Document Schemas -----------------
class DocumentCreateMetadata(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    category: Optional[DocumentCategory] = DocumentCategory.OTHER
    category_id: Optional[str] = None
    description: Optional[str] = None
    issuer: Optional[str] = None
    reference_number: Optional[str] = None
    document_date: Optional[PyDateTime] = None
    expiry_date: Optional[PyDateTime] = None
    tags: Optional[str] = None

class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[DocumentCategory] = None
    category_id: Optional[str] = None
    description: Optional[str] = None
    issuer: Optional[str] = None
    reference_number: Optional[str] = None
    document_date: Optional[PyDateTime] = None
    expiry_date: Optional[PyDateTime] = None
    tags: Optional[str] = None

class DocumentResponse(BaseModel):
    id: str
    user_id: str
    category_id: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    filename: str
    file_name: Optional[str] = None
    file_type: str
    mime_type: Optional[str] = None
    file_size: float
    category: DocumentCategory
    tags: Optional[str] = None
    document_date: Optional[PyDateTime] = None
    expiry_date: Optional[PyDateTime] = None
    issuer: Optional[str] = None
    reference_number: Optional[str] = None
    extracted_text_preview: Optional[str] = None
    metadata_fields: Optional[Dict[str, Any]] = None
    is_indexed: bool = False
    days_until_expiry: Optional[int] = None
    is_expired: Optional[bool] = False
    created_at: PyDateTime
    updated_at: PyDateTime

    model_config = ConfigDict(from_attributes=True)

class DocumentQueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = 4

# ----------------- Bill Schemas -----------------
class BillBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    provider: str = Field(..., min_length=1, max_length=150)
    category: str = Field("UTILITIES", max_length=100)
    amount: Decimal = Field(..., gt=0)
    due_date: PyDateTime
    status: Optional[BillStatus] = BillStatus.PENDING
    recurring: Optional[bool] = False
    recurrence: Optional[RecurrencePattern] = RecurrencePattern.NONE
    payment_reference: Optional[str] = None
    notes: Optional[str] = None

class BillCreate(BillBase):
    pass

class BillUpdate(BaseModel):
    title: Optional[str] = None
    provider: Optional[str] = None
    category: Optional[str] = None
    amount: Optional[Decimal] = Field(None, gt=0)
    due_date: Optional[PyDateTime] = None
    status: Optional[BillStatus] = None
    recurring: Optional[bool] = None
    recurrence: Optional[RecurrencePattern] = None
    payment_reference: Optional[str] = None
    notes: Optional[str] = None

class BillResponse(BillBase):
    id: str
    user_id: str
    days_until_due: int = 0
    days_overdue: int = 0
    is_overdue: bool = False
    created_at: PyDateTime
    updated_at: PyDateTime

    model_config = ConfigDict(from_attributes=True)

# ----------------- Insurance Policy Schemas -----------------
class InsurancePolicyBase(BaseModel):
    provider: str = Field(..., min_length=1, max_length=150)
    policy_name: str = Field(..., min_length=1, max_length=200)
    policy_number: str = Field(..., min_length=1, max_length=100)
    policy_type: Optional[PolicyType] = PolicyType.OTHER
    start_date: Optional[PyDateTime] = None
    expiry_date: PyDateTime
    premium_amount: Decimal = Field(..., gt=0)
    premium_frequency: Optional[PremiumFrequency] = PremiumFrequency.YEARLY
    coverage_amount: Optional[Decimal] = None
    document_id: Optional[str] = None
    notes: Optional[str] = None

class InsurancePolicyCreate(InsurancePolicyBase):
    pass

class InsurancePolicyUpdate(BaseModel):
    provider: Optional[str] = None
    policy_name: Optional[str] = None
    policy_number: Optional[str] = None
    policy_type: Optional[PolicyType] = None
    start_date: Optional[PyDateTime] = None
    expiry_date: Optional[PyDateTime] = None
    premium_amount: Optional[Decimal] = Field(None, gt=0)
    premium_frequency: Optional[PremiumFrequency] = None
    coverage_amount: Optional[Decimal] = None
    document_id: Optional[str] = None
    notes: Optional[str] = None

class InsurancePolicyResponse(InsurancePolicyBase):
    id: str
    user_id: str
    days_until_expiry: int = 0
    is_expired: bool = False
    is_expiring_soon: bool = False
    created_at: PyDateTime
    updated_at: PyDateTime

    model_config = ConfigDict(from_attributes=True)

# ----------------- Important Date Schemas -----------------
class ImportantDateBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    date: PyDateTime
    category: Optional[ImportantDateCategory] = ImportantDateCategory.OTHER
    recurring: Optional[bool] = False
    recurrence: Optional[RecurrencePattern] = RecurrencePattern.NONE

class ImportantDateCreate(ImportantDateBase):
    pass

class ImportantDateUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    date: Optional[PyDateTime] = None
    category: Optional[ImportantDateCategory] = None
    recurring: Optional[bool] = None
    recurrence: Optional[RecurrencePattern] = None

class ImportantDateResponse(ImportantDateBase):
    id: str
    user_id: str
    days_remaining: int = 0
    is_past: bool = False
    created_at: PyDateTime
    updated_at: PyDateTime

    model_config = ConfigDict(from_attributes=True)

# ----------------- Reminder Schemas -----------------
class ReminderBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    due_at: PyDateTime
    priority: Optional[ReminderPriority] = ReminderPriority.MEDIUM
    status: Optional[ReminderStatus] = ReminderStatus.PENDING
    linked_module: Optional[str] = None # ACADEMIC, FINANCE, LIFE_ADMIN
    linked_id: Optional[str] = None

class ReminderCreate(ReminderBase):
    pass

class ReminderUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_at: Optional[PyDateTime] = None
    priority: Optional[ReminderPriority] = None
    status: Optional[ReminderStatus] = None
    is_completed: Optional[bool] = None
    linked_module: Optional[str] = None
    linked_id: Optional[str] = None

class ReminderResponse(ReminderBase):
    id: str
    user_id: str
    is_completed: bool = False
    is_overdue: bool = False
    days_until_due: int = 0
    created_at: PyDateTime
    updated_at: PyDateTime

    model_config = ConfigDict(from_attributes=True)

# ----------------- Life Admin Dashboard & Context -----------------
class BillsSummary(BaseModel):
    pending_count: int = 0
    overdue_count: int = 0
    paid_count: int = 0
    total_pending_amount: Decimal = Decimal("0.00")
    total_overdue_amount: Decimal = Decimal("0.00")
    upcoming_bills: List[BillResponse] = []

class PoliciesSummary(BaseModel):
    total_policies: int = 0
    expiring_soon_count: int = 0
    total_annual_premiums: Decimal = Decimal("0.00")
    expiring_policies: List[InsurancePolicyResponse] = []

class LifeAdminDashboardData(BaseModel):
    total_documents: int = 0
    category_counts: Dict[str, int] = {}
    bills_summary: BillsSummary
    policies_summary: PoliciesSummary
    upcoming_dates: List[ImportantDateResponse] = []
    pending_reminders: List[ReminderResponse] = []
    recent_documents: List[DocumentResponse] = []

class LifeAdminContext(BaseModel):
    source: str = "life_admin"
    total_documents: int = 0
    pending_bills: List[Dict[str, Any]] = []
    expiring_policies: List[Dict[str, Any]] = []
    upcoming_dates: List[Dict[str, Any]] = []
    pending_reminders: List[Dict[str, Any]] = []
