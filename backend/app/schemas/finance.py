from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List, Dict, Any, Union
from datetime import date as PyDate, datetime as PyDateTime
from decimal import Decimal
from app.models.finance import (
    CategoryType,
    TransactionType,
    PaymentMethod,
    BillingCycle,
    SubscriptionStatus,
)

# ==========================================
# CATEGORY SCHEMAS
# ==========================================
class ExpenseCategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    category_type: Optional[CategoryType] = CategoryType.EXPENSE
    icon: Optional[str] = "receipt"
    color: Optional[str] = "#10B981"
    budget_limit: Optional[Decimal] = Field(default=None, ge=0)

class ExpenseCategoryCreate(ExpenseCategoryBase):
    pass

class ExpenseCategoryUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=50)
    category_type: Optional[CategoryType] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    budget_limit: Optional[Decimal] = Field(default=None, ge=0)

class ExpenseCategoryResponse(BaseModel):
    id: str
    user_id: str
    name: str
    category_type: CategoryType
    icon: str
    color: str
    budget_limit: Optional[Decimal] = None
    spent_amount: Optional[Decimal] = Decimal("0.00")
    is_system: bool = False
    created_at: Optional[PyDateTime] = None

    model_config = ConfigDict(from_attributes=True)

# ==========================================
# TRANSACTION SCHEMAS
# ==========================================
class TransactionBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    amount: Decimal = Field(..., gt=0, description="Authoritative monetary amount must be greater than 0")
    type: Optional[TransactionType] = None
    transaction_type: Optional[TransactionType] = None
    date: Optional[PyDate] = None
    payment_method: Optional[PaymentMethod] = PaymentMethod.UPI
    merchant: Optional[str] = Field(default=None, max_length=150)
    notes: Optional[str] = None
    is_recurring: Optional[bool] = False
    category_id: Optional[str] = None
    category_name: Optional[str] = None # Fast creation helper
    receipt_document_id: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)

    @property
    def resolved_type(self) -> TransactionType:
        return self.type or self.transaction_type or TransactionType.EXPENSE

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    amount: Optional[Decimal] = Field(default=None, gt=0)
    type: Optional[TransactionType] = None
    transaction_type: Optional[TransactionType] = None
    date: Optional[PyDate] = None
    payment_method: Optional[PaymentMethod] = None
    merchant: Optional[str] = Field(default=None, max_length=150)
    notes: Optional[str] = None
    is_recurring: Optional[bool] = None
    category_id: Optional[str] = None
    receipt_document_id: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)

    @property
    def resolved_type(self) -> Optional[TransactionType]:
        return self.type or self.transaction_type

class TransactionResponse(BaseModel):
    id: str
    user_id: str
    category_id: Optional[str] = None
    category_name: Optional[str] = "General"
    category_color: Optional[str] = "#6B7280"
    category_icon: Optional[str] = "receipt"
    title: str
    merchant: Optional[str] = None
    amount: Decimal
    type: TransactionType = TransactionType.EXPENSE
    transaction_type: Optional[TransactionType] = None
    date: PyDate
    payment_method: PaymentMethod
    notes: Optional[str] = None
    is_recurring: bool = False
    receipt_document_id: Optional[str] = None
    created_at: PyDateTime
    updated_at: Optional[PyDateTime] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class TransactionListResponse(BaseModel):
    transactions: List[TransactionResponse]
    total_count: int
    total_income: Decimal
    total_expenses: Decimal
    net_balance: Decimal

# ==========================================
# BUDGET SCHEMAS
# ==========================================
class BudgetBase(BaseModel):
    category_id: Optional[str] = None # None means overall monthly budget
    amount: Decimal = Field(..., gt=0)
    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., ge=2020, le=2100)

class BudgetCreate(BudgetBase):
    pass

class BudgetUpdate(BaseModel):
    amount: Optional[Decimal] = Field(default=None, gt=0)

class BudgetResponse(BaseModel):
    id: str
    user_id: str
    category_id: Optional[str] = None
    category_name: Optional[str] = None
    category_color: Optional[str] = None
    amount: Decimal
    month: int
    year: int
    period: str
    spent_amount: Decimal = Decimal("0.00")
    remaining_amount: Decimal = Decimal("0.00")
    percentage_used: float = 0.0
    is_over_budget: bool = False
    created_at: PyDateTime

    model_config = ConfigDict(from_attributes=True)

class BudgetUsageSummary(BaseModel):
    period: str # "YYYY-MM"
    overall_budget: Decimal
    total_spent: Decimal
    remaining_budget: Decimal # Can be negative if over budget
    percentage_used: float
    is_over_budget: bool
    category_budgets: List[BudgetResponse]

# ==========================================
# SUBSCRIPTION SCHEMAS
# ==========================================
class SubscriptionBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    amount: Decimal = Field(..., gt=0)
    billing_cycle: Optional[BillingCycle] = BillingCycle.MONTHLY
    next_billing_date: PyDate
    category_id: Optional[str] = None
    payment_method: Optional[PaymentMethod] = PaymentMethod.UPI
    status: Optional[SubscriptionStatus] = SubscriptionStatus.ACTIVE
    notes: Optional[str] = None

class SubscriptionCreate(SubscriptionBase):
    pass

class SubscriptionUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    amount: Optional[Decimal] = Field(default=None, gt=0)
    billing_cycle: Optional[BillingCycle] = None
    next_billing_date: Optional[PyDate] = None
    category_id: Optional[str] = None
    payment_method: Optional[PaymentMethod] = None
    status: Optional[SubscriptionStatus] = None
    notes: Optional[str] = None

class SubscriptionResponse(BaseModel):
    id: str
    user_id: str
    category_id: Optional[str] = None
    category_name: Optional[str] = "Subscriptions"
    name: str
    amount: Decimal
    billing_cycle: BillingCycle
    next_billing_date: PyDate
    payment_method: PaymentMethod
    status: SubscriptionStatus
    notes: Optional[str] = None
    monthly_equivalent: Decimal = Decimal("0.00")
    is_active: bool = True
    created_at: PyDateTime

    model_config = ConfigDict(from_attributes=True)

class SubscriptionsSummary(BaseModel):
    total_active_count: int
    total_monthly_equivalent: Decimal
    upcoming_this_month_count: int
    subscriptions: List[SubscriptionResponse]

# ==========================================
# ANALYTICS & DASHBOARD SCHEMAS
# ==========================================
class CategorySpend(BaseModel):
    category_id: Optional[str] = None
    category_name: str
    color: str
    icon: str
    amount: Decimal
    percentage: float
    budget_limit: Optional[Decimal] = None
    is_over_budget: bool = False

class CategoryAnalyticsResponse(BaseModel):
    period: str
    total_expenses: Decimal
    categories: List[CategorySpend]

class MonthlyTrendPoint(BaseModel):
    month_label: str # e.g. "Jun 2026", "2026-06"
    period: str      # e.g. "2026-06"
    income: Decimal
    expenses: Decimal
    net_savings: Decimal

class SpendingTrendsResponse(BaseModel):
    period_count: int
    trends: List[MonthlyTrendPoint]

class FinancialSummaryResponse(BaseModel):
    period: str # "2026-09"
    income: Decimal
    expenses: Decimal
    net_balance: Decimal
    savings_percentage: float
    budget_target: Decimal
    budget_remaining: Decimal
    budget_used_percentage: float
    is_over_budget: bool

class FinanceDashboardResponse(BaseModel):
    period: str # "2026-09"
    total_income: Decimal
    total_expenses: Decimal
    net_balance: Decimal
    savings_percentage: float
    monthly_budget_target: Decimal
    remaining_budget: Decimal
    budget_used_percentage: float
    is_over_budget: bool
    burn_rate_per_day: Decimal
    projected_month_end_expense: Decimal
    active_subscriptions_count: int
    monthly_subscription_total: Decimal
    top_categories: List[CategorySpend]
    recent_transactions: List[TransactionResponse]
    upcoming_subscriptions: List[SubscriptionResponse]
    spending_trends: List[MonthlyTrendPoint]

# Backward compatibility alias
FinanceAnalyticsResponse = FinanceDashboardResponse
