from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import date, datetime
from app.models.finance import TransactionType, PaymentMethod

# Category Schemas
class ExpenseCategoryCreate(BaseModel):
    name: str
    icon: Optional[str] = "receipt"
    color: Optional[str] = "#10B981"
    budget_limit: Optional[float] = None

class ExpenseCategoryResponse(BaseModel):
    id: str
    user_id: str
    name: str
    icon: str
    color: str
    budget_limit: Optional[float] = None
    spent_amount: Optional[float] = 0.0

    class Config:
        from_attributes = True

# Transaction Schemas
class TransactionCreate(BaseModel):
    category_id: Optional[str] = None
    category_name: Optional[str] = None # Helper for fast AI / UI creation
    title: str
    amount: float
    type: Optional[TransactionType] = TransactionType.EXPENSE
    date: Optional[date] = None
    payment_method: Optional[PaymentMethod] = PaymentMethod.UPI
    notes: Optional[str] = None
    is_recurring: Optional[bool] = False

class TransactionResponse(BaseModel):
    id: str
    user_id: str
    category_id: Optional[str] = None
    category_name: Optional[str] = None
    category_color: Optional[str] = None
    title: str
    amount: float
    type: TransactionType
    date: date
    payment_method: PaymentMethod
    notes: Optional[str] = None
    is_recurring: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Subscription Schemas
class SubscriptionCreate(BaseModel):
    name: str
    amount: float
    billing_cycle: Optional[str] = "MONTHLY"
    next_billing_date: date
    is_active: Optional[bool] = True

class SubscriptionResponse(BaseModel):
    id: str
    user_id: str
    name: str
    amount: float
    billing_cycle: str
    next_billing_date: date
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Finance Analytics Schemas
class CategorySpend(BaseModel):
    category_id: Optional[str] = None
    category_name: str
    color: str
    amount: float
    percentage: float

class FinanceAnalyticsResponse(BaseModel):
    current_month: str # "2026-09"
    total_income: float
    total_expenses: float
    net_savings: float
    monthly_budget_target: float
    budget_used_percentage: float
    remaining_budget: float
    is_over_budget: bool
    burn_rate_per_day: float
    projected_month_end_expense: float
    top_categories: List[CategorySpend]
    recent_transactions: List[TransactionResponse]
