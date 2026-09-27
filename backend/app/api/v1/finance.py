from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import date

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.finance import CategoryType, TransactionType, SubscriptionStatus
from app.schemas.finance import (
    ExpenseCategoryCreate,
    ExpenseCategoryUpdate,
    ExpenseCategoryResponse,
    TransactionCreate,
    TransactionUpdate,
    TransactionResponse,
    TransactionListResponse,
    BudgetCreate,
    BudgetResponse,
    BudgetUsageSummary,
    SubscriptionCreate,
    SubscriptionUpdate,
    SubscriptionResponse,
    CategoryAnalyticsResponse,
    SpendingTrendsResponse,
    FinancialSummaryResponse,
    FinanceDashboardResponse,
)
from app.services.finance_service import FinanceService

router = APIRouter(prefix="/finance", tags=["Finance / Money Manager"])

# ==========================================
# DASHBOARD & ANALYTICS
# ==========================================
@router.get("/dashboard", response_model=FinanceDashboardResponse)
async def get_finance_dashboard(
    period: Optional[str] = Query(None, description="Month period in YYYY-MM format, defaults to current month"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Returns authoritative financial dashboard data, burn rate, top categories, and trends."""
    return await FinanceService.get_finance_dashboard(db, current_user.id, period)

@router.get("/summary", response_model=FinancialSummaryResponse)
async def get_financial_summary(
    period: Optional[str] = Query(None, description="Month period in YYYY-MM format"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Returns monthly summary of income, expenses, savings rate, and budget usage."""
    return await FinanceService.get_financial_summary(db, current_user.id, period)

@router.get("/analytics/categories", response_model=CategoryAnalyticsResponse)
async def get_category_analytics(
    period: Optional[str] = Query(None, description="Month period in YYYY-MM format"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Returns category-wise spending breakdown and percentages."""
    return await FinanceService.get_category_analytics(db, current_user.id, period)

@router.get("/analytics/trends", response_model=SpendingTrendsResponse)
async def get_spending_trends(
    months: int = Query(6, ge=1, le=24, description="Number of past months to analyze"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Returns historical spending vs income trends across months."""
    return await FinanceService.get_spending_trends(db, current_user.id, months)

@router.get("/budgets/summary", response_model=BudgetUsageSummary)
async def get_budget_summary(
    period: Optional[str] = Query(None, description="Month period in YYYY-MM format"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Returns overall and category-level budget statuses with remaining balance and over-budget flags."""
    return await FinanceService.get_budget_summary(db, current_user.id, period)

# ==========================================
# CATEGORIES
# ==========================================
@router.get("/categories", response_model=List[ExpenseCategoryResponse])
async def list_categories(
    type: Optional[CategoryType] = Query(None, description="Filter by category type: INCOME or EXPENSE"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Lists all user categories including default system categories with current month spent totals."""
    return await FinanceService.get_categories(db, current_user.id, type)

@router.post("/categories", response_model=ExpenseCategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    data: ExpenseCategoryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Creates a custom user income or expense category."""
    return await FinanceService.create_category(db, current_user.id, data)

@router.put("/categories/{category_id}", response_model=ExpenseCategoryResponse)
async def update_category(
    category_id: str,
    data: ExpenseCategoryUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Updates category properties or monthly limit."""
    updated = await FinanceService.update_category(db, current_user.id, category_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Category not found")
    return updated

@router.delete("/categories/{category_id}")
async def delete_category(
    category_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Deletes a category safely without destroying transaction history."""
    success, message = await FinanceService.delete_category(db, current_user.id, category_id)
    if not success:
        raise HTTPException(status_code=404, detail=message)
    return {"message": message, "category_id": category_id}

# ==========================================
# TRANSACTIONS
# ==========================================
@router.get("/transactions", response_model=TransactionListResponse)
async def list_transactions(
    category_id: Optional[str] = Query(None),
    type: Optional[TransactionType] = Query(None, description="INCOME or EXPENSE"),
    time_range: Optional[str] = Query(None, description="today, this_week, this_month, last_month"),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Queries user transactions with deterministic filtering, total counts, and summary totals."""
    return await FinanceService.get_transactions(
        db, current_user.id, category_id, type, time_range, start_date, end_date, search, limit, offset
    )

@router.post("/transactions", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    data: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Records a new income or expense transaction with Decimal precision."""
    if data.amount <= 0:
        raise HTTPException(status_code=400, detail="Transaction amount must be greater than 0")
    return await FinanceService.create_transaction(db, current_user.id, data)

@router.get("/transactions/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieves a single transaction by ID."""
    tx = await FinanceService.get_transaction_by_id(db, current_user.id, transaction_id)
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return tx

@router.put("/transactions/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: str,
    data: TransactionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Updates an existing transaction."""
    if data.amount is not None and data.amount <= 0:
        raise HTTPException(status_code=400, detail="Transaction amount must be greater than 0")
    updated = await FinanceService.update_transaction(db, current_user.id, transaction_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return updated

@router.delete("/transactions/{transaction_id}")
async def delete_transaction(
    transaction_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Deletes a transaction record."""
    deleted = await FinanceService.delete_transaction(db, current_user.id, transaction_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {"message": "Transaction deleted successfully", "transaction_id": transaction_id}

# ==========================================
# BUDGETS
# ==========================================
@router.get("/budgets", response_model=List[BudgetResponse])
async def list_budgets(
    period: Optional[str] = Query(None, description="Month period in YYYY-MM format"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Lists all overall and category budgets configured for the given period."""
    return await FinanceService.get_budgets(db, current_user.id, period)

@router.post("/budgets", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
async def set_budget(
    data: BudgetCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Sets or updates an overall monthly budget or category-specific budget."""
    if data.amount <= 0:
        raise HTTPException(status_code=400, detail="Budget amount must be greater than 0")
    return await FinanceService.set_budget(db, current_user.id, data)

@router.delete("/budgets/{budget_id}")
async def delete_budget(
    budget_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Removes a budget allocation."""
    deleted = await FinanceService.delete_budget(db, current_user.id, budget_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Budget not found")
    return {"message": "Budget deleted successfully", "budget_id": budget_id}

# ==========================================
# SUBSCRIPTIONS
# ==========================================
@router.get("/subscriptions", response_model=List[SubscriptionResponse])
async def list_subscriptions(
    status_filter: Optional[SubscriptionStatus] = Query(None, alias="status"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Lists recurring subscriptions with monthly equivalent cost calculations."""
    return await FinanceService.get_subscriptions(db, current_user.id, status_filter)

@router.post("/subscriptions", response_model=SubscriptionResponse, status_code=status.HTTP_201_CREATED)
async def create_subscription(
    data: SubscriptionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Creates a new recurring subscription."""
    if data.amount <= 0:
        raise HTTPException(status_code=400, detail="Subscription amount must be greater than 0")
    return await FinanceService.create_subscription(db, current_user.id, data)

@router.get("/subscriptions/{subscription_id}", response_model=SubscriptionResponse)
async def get_subscription(
    subscription_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Gets details of a single subscription."""
    subs = await FinanceService.get_subscriptions(db, current_user.id)
    for s in subs:
        if s.id == subscription_id:
            return s
    raise HTTPException(status_code=404, detail="Subscription not found")

@router.put("/subscriptions/{subscription_id}", response_model=SubscriptionResponse)
async def update_subscription(
    subscription_id: str,
    data: SubscriptionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Updates a subscription or changes its status (ACTIVE, PAUSED, CANCELLED)."""
    if data.amount is not None and data.amount <= 0:
        raise HTTPException(status_code=400, detail="Subscription amount must be greater than 0")
    updated = await FinanceService.update_subscription(db, current_user.id, subscription_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return updated

@router.delete("/subscriptions/{subscription_id}")
async def delete_subscription(
    subscription_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Deletes a subscription record."""
    deleted = await FinanceService.delete_subscription(db, current_user.id, subscription_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return {"message": "Subscription deleted successfully", "subscription_id": subscription_id}
