from sqlalchemy import Column, String, Numeric, Date, DateTime, Boolean, ForeignKey, Enum as SQLEnum, Integer, Text
from sqlalchemy.orm import relationship, synonym
import enum
from decimal import Decimal
from app.models.base import BaseModel

class CategoryType(str, enum.Enum):
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"

class TransactionType(str, enum.Enum):
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"

class PaymentMethod(str, enum.Enum):
    CASH = "CASH"
    UPI = "UPI"
    CARD = "CARD"
    BANK_TRANSFER = "BANK_TRANSFER"
    OTHER = "OTHER"

class BillingCycle(str, enum.Enum):
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    YEARLY = "YEARLY"
    CUSTOM = "CUSTOM"

class SubscriptionStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    CANCELLED = "CANCELLED"

class ExpenseCategory(BaseModel):
    __tablename__ = "expense_categories"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    name = Column(String(50), nullable=False) # e.g. Food, Travel, Shopping, Bills, College, Subscriptions
    category_type = Column(SQLEnum(CategoryType), default=CategoryType.EXPENSE, nullable=False)
    icon = Column(String(50), default="receipt", nullable=False)
    color = Column(String(30), default="#10B981", nullable=False)
    budget_limit = Column(Numeric(12, 2), nullable=True) # Optional category-level monthly cap
    is_system = Column(Boolean, default=False, nullable=False)

    # Relationships
    user = relationship("User", back_populates="expense_categories")
    transactions = relationship("Transaction", back_populates="category", cascade="all, delete-orphan")
    budgets = relationship("Budget", back_populates="category", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="category", cascade="all, delete-orphan")

class Transaction(BaseModel):
    __tablename__ = "transactions"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    category_id = Column(String(36), ForeignKey("expense_categories.id", ondelete="SET NULL"), index=True, nullable=True)
    title = Column(String(200), nullable=False)
    merchant = Column(String(150), nullable=True)
    amount = Column(Numeric(12, 2), nullable=False)
    type = Column("type", SQLEnum(TransactionType), default=TransactionType.EXPENSE, nullable=False)
    date = Column(Date, index=True, nullable=False)
    payment_method = Column(SQLEnum(PaymentMethod), default=PaymentMethod.UPI, nullable=False)
    notes = Column(Text, nullable=True)
    is_recurring = Column(Boolean, default=False, nullable=False)
    receipt_document_id = Column(String(36), nullable=True) # Prepared for future Phase 6 receipt storage/RAG link

    # Relationships
    user = relationship("User", back_populates="transactions")
    category = relationship("ExpenseCategory", back_populates="transactions")

    @property
    def transaction_type(self) -> TransactionType:
        return self.type

    @transaction_type.setter
    def transaction_type(self, val: TransactionType):
        self.type = val

class Budget(BaseModel):
    __tablename__ = "budgets"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    category_id = Column(String(36), ForeignKey("expense_categories.id", ondelete="CASCADE"), nullable=True) # Null = Overall monthly budget
    amount = Column("amount", Numeric(12, 2), default=Decimal("10000.00"), nullable=True)
    total_budget_limit = Column("total_budget_limit", Numeric(12, 2), default=Decimal("10000.00"), nullable=True)
    spent_amount = Column("spent_amount", Numeric(12, 2), default=Decimal("0.00"), nullable=False)
    month = Column("month", String(7), nullable=False) # e.g. "2026-09" or int string
    year = Column("year", Integer, default=2026, nullable=False)
    period = Column("period", String(7), default="2026-09", index=True, nullable=False)

    # Relationships
    user = relationship("User", back_populates="budgets")
    category = relationship("ExpenseCategory", back_populates="budgets")

class Subscription(BaseModel):
    __tablename__ = "subscriptions"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    category_id = Column(String(36), ForeignKey("expense_categories.id", ondelete="SET NULL"), nullable=True)
    name = Column(String(100), nullable=False) # Spotify, Netflix, GitHub Copilot, Gym
    amount = Column(Numeric(12, 2), nullable=False)
    billing_cycle = Column(SQLEnum(BillingCycle), default=BillingCycle.MONTHLY, nullable=False)
    next_billing_date = Column(Date, index=True, nullable=False)
    payment_method = Column(SQLEnum(PaymentMethod), default=PaymentMethod.UPI, nullable=False)
    status = Column(SQLEnum(SubscriptionStatus), default=SubscriptionStatus.ACTIVE, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    notes = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", back_populates="subscriptions")
    category = relationship("ExpenseCategory", back_populates="subscriptions")
