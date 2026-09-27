from sqlalchemy import Column, String, Float, Date, DateTime, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum
from app.models.base import BaseModel

class TransactionType(str, enum.Enum):
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"

class PaymentMethod(str, enum.Enum):
    UPI = "UPI"
    CARD = "CARD"
    CASH = "CASH"
    NET_BANKING = "NET_BANKING"
    OTHER = "OTHER"

class ExpenseCategory(BaseModel):
    __tablename__ = "expense_categories"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    name = Column(String(50), nullable=False) # Food, Travel, Shopping, Bills, College, Subscriptions
    icon = Column(String(50), default="receipt", nullable=False)
    color = Column(String(30), default="#10B981", nullable=False)
    budget_limit = Column(Float, nullable=True)

    # Relationships
    user = relationship("User", back_populates="expense_categories")
    transactions = relationship("Transaction", back_populates="category", cascade="all, delete-orphan")

class Transaction(BaseModel):
    __tablename__ = "transactions"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    category_id = Column(String(36), ForeignKey("expense_categories.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(200), nullable=False)
    amount = Column(Float, nullable=False)
    type = Column(SQLEnum(TransactionType), default=TransactionType.EXPENSE, nullable=False)
    date = Column(Date, index=True, nullable=False)
    payment_method = Column(SQLEnum(PaymentMethod), default=PaymentMethod.UPI, nullable=False)
    notes = Column(String(255), nullable=True)
    is_recurring = Column(Boolean, default=False, nullable=False)

    # Relationships
    user = relationship("User", back_populates="transactions")
    category = relationship("ExpenseCategory", back_populates="transactions")

class Budget(BaseModel):
    __tablename__ = "budgets"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    month = Column(String(7), nullable=False) # e.g. "2026-09"
    total_budget_limit = Column(Float, nullable=False)
    spent_amount = Column(Float, default=0.0, nullable=False)

    # Relationships
    user = relationship("User", back_populates="budgets")

class Subscription(BaseModel):
    __tablename__ = "subscriptions"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    name = Column(String(100), nullable=False) # Spotify, Netflix, ChatGPT, GitHub Copilot
    amount = Column(Float, nullable=False)
    billing_cycle = Column(String(20), default="MONTHLY", nullable=False) # MONTHLY, YEARLY
    next_billing_date = Column(Date, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    user = relationship("User", back_populates="subscriptions")
