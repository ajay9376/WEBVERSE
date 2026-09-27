from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from datetime import date
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.finance import ExpenseCategory, Transaction, Budget, Subscription, TransactionType, PaymentMethod
from app.schemas.finance import (
    ExpenseCategoryCreate, ExpenseCategoryResponse, TransactionCreate, TransactionResponse,
    SubscriptionCreate, SubscriptionResponse, FinanceAnalyticsResponse
)
from app.services.finance_service import FinanceService

router = APIRouter(prefix="/finance", tags=["Finance"])

@router.get("/analytics", response_model=FinanceAnalyticsResponse)
async def get_analytics(
    month: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await FinanceService.get_finance_analytics(db, current_user.id, month)

@router.get("/categories", response_model=List[ExpenseCategoryResponse])
async def get_categories(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    stmt = select(ExpenseCategory).where(ExpenseCategory.user_id == current_user.id)
    res = await db.execute(stmt)
    return res.scalars().all()

@router.post("/categories", response_model=ExpenseCategoryResponse)
async def create_category(cat_in: ExpenseCategoryCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    cat = ExpenseCategory(
        user_id=current_user.id,
        name=cat_in.name,
        icon=cat_in.icon or "receipt",
        color=cat_in.color or "#10B981",
        budget_limit=cat_in.budget_limit
    )
    db.add(cat)
    await db.commit()
    await db.refresh(cat)
    return cat

@router.get("/transactions", response_model=List[TransactionResponse])
async def get_transactions(
    category_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Transaction).join(ExpenseCategory, isouter=True).where(Transaction.user_id == current_user.id)
    if category_id:
        stmt = stmt.where(Transaction.category_id == category_id)
    stmt = stmt.order_by(Transaction.date.desc())
    res = await db.execute(stmt)
    txs = res.scalars().all()
    
    # Map category details
    cat_stmt = select(ExpenseCategory).where(ExpenseCategory.user_id == current_user.id)
    c_res = await db.execute(cat_stmt)
    categories = {c.id: c for c in c_res.scalars().all()}

    return [
        TransactionResponse(
            id=t.id,
            user_id=t.user_id,
            category_id=t.category_id,
            category_name=categories[t.category_id].name if t.category_id in categories else "General",
            category_color=categories[t.category_id].color if t.category_id in categories else "#6B7280",
            title=t.title,
            amount=t.amount,
            type=t.type,
            date=t.date,
            payment_method=t.payment_method,
            notes=t.notes,
            is_recurring=t.is_recurring,
            created_at=t.created_at
        )
        for t in txs
    ]

@router.post("/transactions", response_model=TransactionResponse)
async def create_transaction(tx_in: TransactionCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    cat_id = tx_in.category_id
    if not cat_id and tx_in.category_name:
        c_res = await db.execute(select(ExpenseCategory).where(ExpenseCategory.user_id == current_user.id, ExpenseCategory.name.ilike(tx_in.category_name)))
        cat = c_res.scalars().first()
        if not cat:
            cat = ExpenseCategory(user_id=current_user.id, name=tx_in.category_name, color="#10B981")
            db.add(cat)
            await db.flush()
        cat_id = cat.id

    tx = Transaction(
        user_id=current_user.id,
        category_id=cat_id,
        title=tx_in.title,
        amount=tx_in.amount,
        type=tx_in.type or TransactionType.EXPENSE,
        date=tx_in.date or date.today(),
        payment_method=tx_in.payment_method or PaymentMethod.UPI,
        notes=tx_in.notes,
        is_recurring=tx_in.is_recurring or False
    )
    db.add(tx)
    await db.commit()
    await db.refresh(tx)

    cat_name = "General"
    cat_color = "#6B7280"
    if tx.category_id:
        c = await db.get(ExpenseCategory, tx.category_id)
        if c:
            cat_name = c.name
            cat_color = c.color

    return TransactionResponse(
        id=tx.id,
        user_id=tx.user_id,
        category_id=tx.category_id,
        category_name=cat_name,
        category_color=cat_color,
        title=tx.title,
        amount=tx.amount,
        type=tx.type,
        date=tx.date,
        payment_method=tx.payment_method,
        notes=tx.notes,
        is_recurring=tx.is_recurring,
        created_at=tx.created_at
    )

@router.get("/subscriptions", response_model=List[SubscriptionResponse])
async def get_subscriptions(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    stmt = select(Subscription).where(Subscription.user_id == current_user.id).order_by(Subscription.next_billing_date.asc())
    res = await db.execute(stmt)
    return res.scalars().all()

@router.post("/subscriptions", response_model=SubscriptionResponse)
async def create_subscription(sub_in: SubscriptionCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    sub = Subscription(
        user_id=current_user.id,
        name=sub_in.name,
        amount=sub_in.amount,
        billing_cycle=sub_in.billing_cycle or "MONTHLY",
        next_billing_date=sub_in.next_billing_date,
        is_active=sub_in.is_active if sub_in.is_active is not None else True
    )
    db.add(sub)
    await db.commit()
    await db.refresh(sub)
    return sub
