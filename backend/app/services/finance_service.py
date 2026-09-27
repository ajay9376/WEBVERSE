from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional, Tuple
from decimal import Decimal, ROUND_HALF_UP
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, and_, or_, delete
import calendar

from app.models.finance import (
    Transaction,
    ExpenseCategory,
    Budget,
    Subscription,
    CategoryType,
    TransactionType,
    PaymentMethod,
    BillingCycle,
    SubscriptionStatus,
)
from app.schemas.finance import (
    ExpenseCategoryCreate,
    ExpenseCategoryUpdate,
    ExpenseCategoryResponse,
    TransactionCreate,
    TransactionUpdate,
    TransactionResponse,
    TransactionListResponse,
    BudgetCreate,
    BudgetUpdate,
    BudgetResponse,
    BudgetUsageSummary,
    SubscriptionCreate,
    SubscriptionUpdate,
    SubscriptionResponse,
    SubscriptionsSummary,
    CategorySpend,
    CategoryAnalyticsResponse,
    MonthlyTrendPoint,
    SpendingTrendsResponse,
    FinancialSummaryResponse,
    FinanceDashboardResponse,
)

DEFAULT_EXPENSE_CATEGORIES = [
    {"name": "Food & Dining", "icon": "utensils", "color": "#F59E0B", "category_type": CategoryType.EXPENSE},
    {"name": "Travel & Transit", "icon": "car", "color": "#3B82F6", "category_type": CategoryType.EXPENSE},
    {"name": "Shopping & Lifestyle", "icon": "shopping-bag", "color": "#EC4899", "category_type": CategoryType.EXPENSE},
    {"name": "Education & Books", "icon": "book-open", "color": "#8B5CF6", "category_type": CategoryType.EXPENSE},
    {"name": "Bills & Utilities", "icon": "file-text", "color": "#EF4444", "category_type": CategoryType.EXPENSE},
    {"name": "Subscriptions", "icon": "refresh-cw", "color": "#06B6D4", "category_type": CategoryType.EXPENSE},
    {"name": "Entertainment", "icon": "film", "color": "#10B981", "category_type": CategoryType.EXPENSE},
    {"name": "Health & Fitness", "icon": "heart", "color": "#14B8A6", "category_type": CategoryType.EXPENSE},
    {"name": "Salary / Allowance", "icon": "dollar-sign", "color": "#10B981", "category_type": CategoryType.INCOME},
    {"name": "Other", "icon": "more-horizontal", "color": "#6B7280", "category_type": CategoryType.EXPENSE},
]

def to_decimal(val: Any) -> Decimal:
    """Safely converts float/int/str to Decimal with 2 decimal precision."""
    if val is None:
        return Decimal("0.00")
    if isinstance(val, Decimal):
        return val.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return Decimal(str(val)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class FinanceService:

    # ==========================================
    # CATEGORY OPERATIONS
    # ==========================================
    @staticmethod
    async def seed_default_categories_if_empty(db: AsyncSession, user_id: str) -> None:
        stmt = select(ExpenseCategory).where(ExpenseCategory.user_id == user_id)
        res = await db.execute(stmt)
        existing = res.scalars().first()
        if not existing:
            for cat_data in DEFAULT_EXPENSE_CATEGORIES:
                cat = ExpenseCategory(
                    user_id=user_id,
                    name=cat_data["name"],
                    icon=cat_data["icon"],
                    color=cat_data["color"],
                    category_type=cat_data["category_type"],
                    is_system=True,
                )
                db.add(cat)
            await db.commit()

    @staticmethod
    async def get_categories(db: AsyncSession, user_id: str, category_type: Optional[CategoryType] = None) -> List[ExpenseCategoryResponse]:
        await FinanceService.seed_default_categories_if_empty(db, user_id)
        stmt = select(ExpenseCategory).where(ExpenseCategory.user_id == user_id)
        if category_type:
            stmt = stmt.where(ExpenseCategory.category_type == category_type)
        stmt = stmt.order_by(ExpenseCategory.name.asc())
        res = await db.execute(stmt)
        categories = res.scalars().all()

        # Calculate current month spent for each category
        today = date.today()
        start_date = date(today.year, today.month, 1)
        _, last_day = calendar.monthrange(today.year, today.month)
        end_date = date(today.year, today.month, last_day)

        tx_stmt = select(
            Transaction.category_id,
            func.sum(Transaction.amount).label("total_spent")
        ).where(
            Transaction.user_id == user_id,
            Transaction.type == TransactionType.EXPENSE,
            Transaction.date >= start_date,
            Transaction.date <= end_date
        ).group_by(Transaction.category_id)
        tx_res = await db.execute(tx_stmt)
        spent_map = {row[0]: to_decimal(row[1]) for row in tx_res.all() if row[0]}

        return [
            ExpenseCategoryResponse(
                id=c.id,
                user_id=c.user_id,
                name=c.name,
                category_type=c.category_type,
                icon=c.icon,
                color=c.color,
                budget_limit=to_decimal(c.budget_limit) if c.budget_limit is not None else None,
                spent_amount=spent_map.get(c.id, Decimal("0.00")),
                is_system=c.is_system,
                created_at=c.created_at,
            )
            for c in categories
        ]

    @staticmethod
    async def create_category(db: AsyncSession, user_id: str, data: ExpenseCategoryCreate) -> ExpenseCategoryResponse:
        cat = ExpenseCategory(
            user_id=user_id,
            name=data.name.strip(),
            category_type=data.category_type or CategoryType.EXPENSE,
            icon=data.icon or "receipt",
            color=data.color or "#10B981",
            budget_limit=to_decimal(data.budget_limit) if data.budget_limit is not None else None,
            is_system=False,
        )
        db.add(cat)
        await db.commit()
        await db.refresh(cat)
        return ExpenseCategoryResponse(
            id=cat.id,
            user_id=cat.user_id,
            name=cat.name,
            category_type=cat.category_type,
            icon=cat.icon,
            color=cat.color,
            budget_limit=to_decimal(cat.budget_limit) if cat.budget_limit is not None else None,
            spent_amount=Decimal("0.00"),
            is_system=cat.is_system,
            created_at=cat.created_at,
        )

    @staticmethod
    async def update_category(db: AsyncSession, user_id: str, category_id: str, data: ExpenseCategoryUpdate) -> Optional[ExpenseCategoryResponse]:
        stmt = select(ExpenseCategory).where(ExpenseCategory.id == category_id, ExpenseCategory.user_id == user_id)
        res = await db.execute(stmt)
        cat = res.scalars().first()
        if not cat:
            return None

        if data.name is not None:
            cat.name = data.name.strip()
        if data.category_type is not None:
            cat.category_type = data.category_type
        if data.icon is not None:
            cat.icon = data.icon
        if data.color is not None:
            cat.color = data.color
        if data.budget_limit is not None:
            cat.budget_limit = to_decimal(data.budget_limit)

        await db.commit()
        await db.refresh(cat)
        return ExpenseCategoryResponse(
            id=cat.id,
            user_id=cat.user_id,
            name=cat.name,
            category_type=cat.category_type,
            icon=cat.icon,
            color=cat.color,
            budget_limit=to_decimal(cat.budget_limit) if cat.budget_limit is not None else None,
            spent_amount=Decimal("0.00"),
            is_system=cat.is_system,
            created_at=cat.created_at,
        )

    @staticmethod
    async def delete_category(db: AsyncSession, user_id: str, category_id: str) -> Tuple[bool, str]:
        stmt = select(ExpenseCategory).where(ExpenseCategory.id == category_id, ExpenseCategory.user_id == user_id)
        res = await db.execute(stmt)
        cat = res.scalars().first()
        if not cat:
            return False, "Category not found"

        # Check if transactions exist
        tx_count_stmt = select(func.count(Transaction.id)).where(Transaction.category_id == category_id, Transaction.user_id == user_id)
        tx_count_res = await db.execute(tx_count_stmt)
        count = tx_count_res.scalar() or 0

        if count > 0:
            # Reassign transactions to an 'Other' or uncategorized bucket instead of breaking financial history
            other_stmt = select(ExpenseCategory).where(
                ExpenseCategory.user_id == user_id,
                ExpenseCategory.name == "Other"
            )
            other_res = await db.execute(other_stmt)
            other_cat = other_res.scalars().first()
            new_cat_id = other_cat.id if other_cat else None

            from sqlalchemy import update
            await db.execute(
                update(Transaction).where(Transaction.category_id == category_id).values(category_id=new_cat_id)
            )

        await db.delete(cat)
        await db.commit()
        return True, "Category deleted successfully"

    # ==========================================
    # TRANSACTION OPERATIONS
    # ==========================================
    @staticmethod
    def _parse_date_filter(time_range: Optional[str], custom_start: Optional[date], custom_end: Optional[date]) -> Tuple[Optional[date], Optional[date]]:
        today = date.today()
        if custom_start or custom_end:
            return custom_start, custom_end

        if not time_range:
            return None, None

        tr = time_range.lower()
        if tr == "today":
            return today, today
        elif tr == "this_week":
            start = today - timedelta(days=today.weekday())
            end = start + timedelta(days=6)
            return start, end
        elif tr == "this_month":
            start = date(today.year, today.month, 1)
            _, last_day = calendar.monthrange(today.year, today.month)
            return start, date(today.year, today.month, last_day)
        elif tr == "last_month":
            if today.month == 1:
                year, month = today.year - 1, 12
            else:
                year, month = today.year, today.month - 1
            start = date(year, month, 1)
            _, last_day = calendar.monthrange(year, month)
            return start, date(year, month, last_day)
        return None, None

    @staticmethod
    async def get_transactions(
        db: AsyncSession,
        user_id: str,
        category_id: Optional[str] = None,
        transaction_type: Optional[TransactionType] = None,
        time_range: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> TransactionListResponse:
        start_filter, end_filter = FinanceService._parse_date_filter(time_range, start_date, end_date)

        conditions = [Transaction.user_id == user_id]
        if category_id:
            conditions.append(Transaction.category_id == category_id)
        if transaction_type:
            conditions.append(Transaction.type == transaction_type)
        if start_filter:
            conditions.append(Transaction.date >= start_filter)
        if end_filter:
            conditions.append(Transaction.date <= end_filter)
        if search:
            s = f"%{search.strip()}%"
            conditions.append(or_(Transaction.title.ilike(s), Transaction.merchant.ilike(s), Transaction.notes.ilike(s)))

        # Total counts & sums
        count_stmt = select(func.count(Transaction.id)).where(and_(*conditions))
        count_res = await db.execute(count_stmt)
        total_count = count_res.scalar() or 0

        # Sum query
        income_stmt = select(func.sum(Transaction.amount)).where(and_(*conditions, Transaction.type == TransactionType.INCOME))
        inc_res = await db.execute(income_stmt)
        total_income = to_decimal(inc_res.scalar())

        expense_stmt = select(func.sum(Transaction.amount)).where(and_(*conditions, Transaction.type == TransactionType.EXPENSE))
        exp_res = await db.execute(expense_stmt)
        total_expenses = to_decimal(exp_res.scalar())
        net_balance = total_income - total_expenses

        # Fetch records
        stmt = select(Transaction).where(and_(*conditions)).order_by(Transaction.date.desc(), Transaction.created_at.desc()).limit(limit).offset(offset)
        res = await db.execute(stmt)
        txs = res.scalars().all()

        # Category map for quick joins
        cat_stmt = select(ExpenseCategory).where(ExpenseCategory.user_id == user_id)
        c_res = await db.execute(cat_stmt)
        categories = {c.id: c for c in c_res.scalars().all()}

        results = []
        for t in txs:
            cat = categories.get(t.category_id)
            results.append(TransactionResponse(
                id=t.id,
                user_id=t.user_id,
                category_id=t.category_id,
                category_name=cat.name if cat else "General",
                category_color=cat.color if cat else "#6B7280",
                category_icon=cat.icon if cat else "receipt",
                title=t.title,
                merchant=t.merchant,
                amount=to_decimal(t.amount),
                type=t.transaction_type,
                transaction_type=t.transaction_type,
                date=t.date,
                payment_method=t.payment_method,
                notes=t.notes,
                is_recurring=t.is_recurring,
                receipt_document_id=t.receipt_document_id,
                created_at=t.created_at,
                updated_at=t.updated_at,
            ))

        return TransactionListResponse(
            transactions=results,
            total_count=total_count,
            total_income=total_income,
            total_expenses=total_expenses,
            net_balance=net_balance,
        )

    @staticmethod
    async def create_transaction(db: AsyncSession, user_id: str, data: TransactionCreate) -> TransactionResponse:
        # Resolve category if category_name was passed
        cat_id = data.category_id
        if not cat_id and data.category_name:
            c_res = await db.execute(
                select(ExpenseCategory).where(
                    ExpenseCategory.user_id == user_id,
                    ExpenseCategory.name.ilike(data.category_name.strip())
                )
            )
            cat = c_res.scalars().first()
            if not cat:
                cat = ExpenseCategory(
                    user_id=user_id,
                    name=data.category_name.strip(),
                    category_type=CategoryType.INCOME if data.resolved_type == TransactionType.INCOME else CategoryType.EXPENSE,
                    color="#10B981" if data.resolved_type == TransactionType.INCOME else "#EF4444"
                )
                db.add(cat)
                await db.flush()
            cat_id = cat.id

        tx = Transaction(
            user_id=user_id,
            category_id=cat_id,
            title=data.title.strip(),
            merchant=data.merchant.strip() if data.merchant else None,
            amount=to_decimal(data.amount),
            transaction_type=data.resolved_type,
            date=data.date or date.today(),
            payment_method=data.payment_method or PaymentMethod.UPI,
            notes=data.notes,
            is_recurring=data.is_recurring or False,
            receipt_document_id=data.receipt_document_id,
        )
        db.add(tx)
        await db.commit()
        await db.refresh(tx)

        cat_name = "General"
        cat_color = "#6B7280"
        cat_icon = "receipt"
        if tx.category_id:
            c = await db.get(ExpenseCategory, tx.category_id)
            if c:
                cat_name = c.name
                cat_color = c.color
                cat_icon = c.icon

        return TransactionResponse(
            id=tx.id,
            user_id=tx.user_id,
            category_id=tx.category_id,
            category_name=cat_name,
            category_color=cat_color,
            category_icon=cat_icon,
            title=tx.title,
            merchant=tx.merchant,
            amount=to_decimal(tx.amount),
            type=tx.transaction_type,
            transaction_type=tx.transaction_type,
            date=tx.date,
            payment_method=tx.payment_method,
            notes=tx.notes,
            is_recurring=tx.is_recurring,
            receipt_document_id=tx.receipt_document_id,
            created_at=tx.created_at,
            updated_at=tx.updated_at,
        )


    @staticmethod
    async def get_transaction_by_id(db: AsyncSession, user_id: str, tx_id: str) -> Optional[TransactionResponse]:
        stmt = select(Transaction).where(Transaction.id == tx_id, Transaction.user_id == user_id)
        res = await db.execute(stmt)
        tx = res.scalars().first()
        if not tx:
            return None

        cat_name = "General"
        cat_color = "#6B7280"
        cat_icon = "receipt"
        if tx.category_id:
            c = await db.get(ExpenseCategory, tx.category_id)
            if c:
                cat_name = c.name
                cat_color = c.color
                cat_icon = c.icon

        return TransactionResponse(
            id=tx.id,
            user_id=tx.user_id,
            category_id=tx.category_id,
            category_name=cat_name,
            category_color=cat_color,
            category_icon=cat_icon,
            title=tx.title,
            merchant=tx.merchant,
            amount=to_decimal(tx.amount),
            type=tx.transaction_type,
            transaction_type=tx.transaction_type,
            date=tx.date,
            payment_method=tx.payment_method,
            notes=tx.notes,
            is_recurring=tx.is_recurring,
            receipt_document_id=tx.receipt_document_id,
            created_at=tx.created_at,
            updated_at=tx.updated_at,
        )

    @staticmethod
    async def update_transaction(db: AsyncSession, user_id: str, tx_id: str, data: TransactionUpdate) -> Optional[TransactionResponse]:
        stmt = select(Transaction).where(Transaction.id == tx_id, Transaction.user_id == user_id)
        res = await db.execute(stmt)
        tx = res.scalars().first()
        if not tx:
            return None

        if data.title is not None:
            tx.title = data.title.strip()
        if data.amount is not None:
            tx.amount = to_decimal(data.amount)
        if data.type is not None:
            tx.transaction_type = data.type
        if data.date is not None:
            tx.date = data.date
        if data.payment_method is not None:
            tx.payment_method = data.payment_method
        if data.merchant is not None:
            tx.merchant = data.merchant.strip() if data.merchant else None
        if data.notes is not None:
            tx.notes = data.notes
        if data.is_recurring is not None:
            tx.is_recurring = data.is_recurring
        if data.category_id is not None:
            # Validate category ownership
            c_check = await db.execute(select(ExpenseCategory).where(ExpenseCategory.id == data.category_id, ExpenseCategory.user_id == user_id))
            if c_check.scalars().first():
                tx.category_id = data.category_id
        if data.receipt_document_id is not None:
            tx.receipt_document_id = data.receipt_document_id

        await db.commit()
        await db.refresh(tx)
        return await FinanceService.get_transaction_by_id(db, user_id, tx.id)

    @staticmethod
    async def delete_transaction(db: AsyncSession, user_id: str, tx_id: str) -> bool:
        stmt = select(Transaction).where(Transaction.id == tx_id, Transaction.user_id == user_id)
        res = await db.execute(stmt)
        tx = res.scalars().first()
        if not tx:
            return False
        await db.delete(tx)
        await db.commit()
        return True

    # ==========================================
    # BUDGET OPERATIONS
    # ==========================================
    @staticmethod
    async def get_budgets(db: AsyncSession, user_id: str, period: Optional[str] = None) -> List[BudgetResponse]:
        if not period:
            today = date.today()
            period = today.strftime("%Y-%m")

        stmt = select(Budget).where(Budget.user_id == user_id, Budget.period == period)
        res = await db.execute(stmt)
        budgets = res.scalars().all()

        # Fetch category spent for this period
        year, month = map(int, period.split("-"))
        _, last_day = calendar.monthrange(year, month)
        start_date = date(year, month, 1)
        end_date = date(year, month, last_day)

        tx_stmt = select(
            Transaction.category_id,
            func.sum(Transaction.amount).label("total_spent")
        ).where(
            Transaction.user_id == user_id,
            Transaction.type == TransactionType.EXPENSE,
            Transaction.date >= start_date,
            Transaction.date <= end_date
        ).group_by(Transaction.category_id)
        tx_res = await db.execute(tx_stmt)
        cat_spent_map = {row[0]: to_decimal(row[1]) for row in tx_res.all()}

        # Total overall spent
        total_spent = sum(cat_spent_map.values(), Decimal("0.00"))

        cat_stmt = select(ExpenseCategory).where(ExpenseCategory.user_id == user_id)
        c_res = await db.execute(cat_stmt)
        categories = {c.id: c for c in c_res.scalars().all()}

        results = []
        for b in budgets:
            limit = to_decimal(b.amount)
            if b.category_id:
                spent = cat_spent_map.get(b.category_id, Decimal("0.00"))
                cat = categories.get(b.category_id)
                c_name = cat.name if cat else "Specific Category"
                c_color = cat.color if cat else "#6B7280"
            else:
                spent = total_spent
                c_name = "Overall Monthly Budget"
                c_color = "#10B981"

            remaining = limit - spent
            pct = round(float(spent / limit * 100), 1) if limit > 0 else 0.0
            is_over = spent > limit

            results.append(BudgetResponse(
                id=b.id,
                user_id=b.user_id,
                category_id=b.category_id,
                category_name=c_name,
                category_color=c_color,
                amount=limit,
                month=b.month,
                year=b.year,
                period=b.period,
                spent_amount=spent,
                remaining_amount=remaining,
                percentage_used=pct,
                is_over_budget=is_over,
                created_at=b.created_at,
            ))
        return results

    @staticmethod
    async def set_budget(db: AsyncSession, user_id: str, data: BudgetCreate) -> BudgetResponse:
        period = f"{data.year:04d}-{data.month:02d}"
        
        # Check existing budget for same period & category
        stmt = select(Budget).where(
            Budget.user_id == user_id,
            Budget.period == period,
            Budget.category_id == data.category_id
        )
        res = await db.execute(stmt)
        b = res.scalars().first()

        if b:
            b.amount = to_decimal(data.amount)
            b.total_budget_limit = to_decimal(data.amount)
        else:
            b = Budget(
                user_id=user_id,
                category_id=data.category_id,
                amount=to_decimal(data.amount),
                total_budget_limit=to_decimal(data.amount),
                spent_amount=Decimal("0.00"),
                month=data.month,
                year=data.year,
                period=period,
            )
            db.add(b)

        await db.commit()
        await db.refresh(b)

        # Return updated response
        budgets = await FinanceService.get_budgets(db, user_id, period)
        for br in budgets:
            if br.id == b.id:
                return br

        return BudgetResponse(
            id=b.id,
            user_id=b.user_id,
            category_id=b.category_id,
            amount=to_decimal(b.amount),
            month=b.month,
            year=b.year,
            period=b.period,
            spent_amount=Decimal("0.00"),
            remaining_amount=to_decimal(b.amount),
            percentage_used=0.0,
            is_over_budget=False,
            created_at=b.created_at,
        )

    @staticmethod
    async def delete_budget(db: AsyncSession, user_id: str, budget_id: str) -> bool:
        stmt = select(Budget).where(Budget.id == budget_id, Budget.user_id == user_id)
        res = await db.execute(stmt)
        b = res.scalars().first()
        if not b:
            return False
        await db.delete(b)
        await db.commit()
        return True

    @staticmethod
    async def get_budget_summary(db: AsyncSession, user_id: str, period: Optional[str] = None) -> BudgetUsageSummary:
        if not period:
            today = date.today()
            period = today.strftime("%Y-%m")

        year, month = map(int, period.split("-"))
        _, last_day = calendar.monthrange(year, month)
        start_date = date(year, month, 1)
        end_date = date(year, month, last_day)

        # Query overall budget
        stmt = select(Budget).where(Budget.user_id == user_id, Budget.period == period, Budget.category_id.is_(None))
        res = await db.execute(stmt)
        overall_b = res.scalars().first()
        overall_limit = to_decimal(overall_b.amount) if overall_b else Decimal("10000.00")

        # Total expenses in period
        tx_stmt = select(func.sum(Transaction.amount)).where(
            Transaction.user_id == user_id,
            Transaction.type == TransactionType.EXPENSE,
            Transaction.date >= start_date,
            Transaction.date <= end_date
        )
        tx_res = await db.execute(tx_stmt)
        total_spent = to_decimal(tx_res.scalar())

        remaining = overall_limit - total_spent
        pct = round(float(total_spent / overall_limit * 100), 1) if overall_limit > 0 else 0.0
        is_over = total_spent > overall_limit

        cat_budgets = await FinanceService.get_budgets(db, user_id, period)

        return BudgetUsageSummary(
            period=period,
            overall_budget=overall_limit,
            total_spent=total_spent,
            remaining_budget=remaining,
            percentage_used=pct,
            is_over_budget=is_over,
            category_budgets=cat_budgets,
        )

    # ==========================================
    # SUBSCRIPTION OPERATIONS
    # ==========================================
    @staticmethod
    def calculate_monthly_equivalent(amount: Decimal, billing_cycle: BillingCycle) -> Decimal:
        amt = to_decimal(amount)
        if billing_cycle == BillingCycle.MONTHLY:
            return amt
        elif billing_cycle == BillingCycle.YEARLY:
            return (amt / Decimal("12")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        elif billing_cycle == BillingCycle.QUARTERLY:
            return (amt / Decimal("3")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        elif billing_cycle == BillingCycle.WEEKLY:
            return (amt * Decimal("52") / Decimal("12")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return amt

    @staticmethod
    async def get_subscriptions(db: AsyncSession, user_id: str, status: Optional[SubscriptionStatus] = None) -> List[SubscriptionResponse]:
        stmt = select(Subscription).where(Subscription.user_id == user_id)
        if status:
            stmt = stmt.where(Subscription.status == status)
        stmt = stmt.order_by(Subscription.next_billing_date.asc())
        res = await db.execute(stmt)
        subs = res.scalars().all()

        cat_stmt = select(ExpenseCategory).where(ExpenseCategory.user_id == user_id)
        c_res = await db.execute(cat_stmt)
        categories = {c.id: c for c in c_res.scalars().all()}

        results = []
        for s in subs:
            cat = categories.get(s.category_id)
            amt = to_decimal(s.amount)
            results.append(SubscriptionResponse(
                id=s.id,
                user_id=s.user_id,
                category_id=s.category_id,
                category_name=cat.name if cat else "Subscriptions",
                name=s.name,
                amount=amt,
                billing_cycle=s.billing_cycle,
                next_billing_date=s.next_billing_date,
                payment_method=s.payment_method,
                status=s.status,
                notes=s.notes,
                monthly_equivalent=FinanceService.calculate_monthly_equivalent(amt, s.billing_cycle),
                is_active=s.status == SubscriptionStatus.ACTIVE,
                created_at=s.created_at,
            ))
        return results

    @staticmethod
    async def create_subscription(db: AsyncSession, user_id: str, data: SubscriptionCreate) -> SubscriptionResponse:
        st = data.status or SubscriptionStatus.ACTIVE
        sub = Subscription(
            user_id=user_id,
            category_id=data.category_id,
            name=data.name.strip(),
            amount=to_decimal(data.amount),
            billing_cycle=data.billing_cycle or BillingCycle.MONTHLY,
            next_billing_date=data.next_billing_date,
            payment_method=data.payment_method or PaymentMethod.UPI,
            status=st,
            is_active=(st == SubscriptionStatus.ACTIVE),
            notes=data.notes,
        )
        db.add(sub)
        await db.commit()
        await db.refresh(sub)

        cat_name = "Subscriptions"
        if sub.category_id:
            c = await db.get(ExpenseCategory, sub.category_id)
            if c:
                cat_name = c.name

        amt = to_decimal(sub.amount)
        return SubscriptionResponse(
            id=sub.id,
            user_id=sub.user_id,
            category_id=sub.category_id,
            category_name=cat_name,
            name=sub.name,
            amount=amt,
            billing_cycle=sub.billing_cycle,
            next_billing_date=sub.next_billing_date,
            payment_method=sub.payment_method,
            status=sub.status,
            notes=sub.notes,
            monthly_equivalent=FinanceService.calculate_monthly_equivalent(amt, sub.billing_cycle),
            is_active=sub.status == SubscriptionStatus.ACTIVE,
            created_at=sub.created_at,
        )

    @staticmethod
    async def update_subscription(db: AsyncSession, user_id: str, sub_id: str, data: SubscriptionUpdate) -> Optional[SubscriptionResponse]:
        stmt = select(Subscription).where(Subscription.id == sub_id, Subscription.user_id == user_id)
        res = await db.execute(stmt)
        sub = res.scalars().first()
        if not sub:
            return None

        if data.name is not None:
            sub.name = data.name.strip()
        if data.amount is not None:
            sub.amount = to_decimal(data.amount)
        if data.billing_cycle is not None:
            sub.billing_cycle = data.billing_cycle
        if data.next_billing_date is not None:
            sub.next_billing_date = data.next_billing_date
        if data.category_id is not None:
            sub.category_id = data.category_id
        if data.payment_method is not None:
            sub.payment_method = data.payment_method
        if data.status is not None:
            sub.status = data.status
            sub.is_active = (data.status == SubscriptionStatus.ACTIVE)
        if data.notes is not None:
            sub.notes = data.notes

        await db.commit()
        await db.refresh(sub)


        subs = await FinanceService.get_subscriptions(db, user_id)
        for sr in subs:
            if sr.id == sub.id:
                return sr
        return None

    @staticmethod
    async def delete_subscription(db: AsyncSession, user_id: str, sub_id: str) -> bool:
        stmt = select(Subscription).where(Subscription.id == sub_id, Subscription.user_id == user_id)
        res = await db.execute(stmt)
        sub = res.scalars().first()
        if not sub:
            return False
        await db.delete(sub)
        await db.commit()
        return True

    # ==========================================
    # DETERMINISTIC FINANCIAL ANALYTICS & DASHBOARD
    # ==========================================
    @staticmethod
    async def get_financial_summary(db: AsyncSession, user_id: str, period: Optional[str] = None) -> FinancialSummaryResponse:
        today = date.today()
        if not period:
            period = today.strftime("%Y-%m")

        year, month = map(int, period.split("-"))
        _, last_day = calendar.monthrange(year, month)
        start_date = date(year, month, 1)
        end_date = date(year, month, last_day)

        # Monthly income
        inc_stmt = select(func.sum(Transaction.amount)).where(
            Transaction.user_id == user_id,
            Transaction.type == TransactionType.INCOME,
            Transaction.date >= start_date,
            Transaction.date <= end_date
        )
        inc_res = await db.execute(inc_stmt)
        income = to_decimal(inc_res.scalar())

        # Monthly expenses
        exp_stmt = select(func.sum(Transaction.amount)).where(
            Transaction.user_id == user_id,
            Transaction.type == TransactionType.EXPENSE,
            Transaction.date >= start_date,
            Transaction.date <= end_date
        )
        exp_res = await db.execute(exp_stmt)
        expenses = to_decimal(exp_res.scalar())
        net_balance = income - expenses

        savings_pct = round(float(net_balance / income * 100), 2) if income > 0 else 0.0

        # Monthly budget
        b_stmt = select(Budget).where(Budget.user_id == user_id, Budget.period == period, Budget.category_id.is_(None))
        b_res = await db.execute(b_stmt)
        budget = b_res.scalars().first()
        budget_target = to_decimal(budget.amount) if budget else Decimal("10000.00")

        remaining_budget = budget_target - expenses
        budget_used_pct = round(float(expenses / budget_target * 100), 1) if budget_target > 0 else 0.0
        is_over = expenses > budget_target

        return FinancialSummaryResponse(
            period=period,
            income=income,
            expenses=expenses,
            net_balance=net_balance,
            savings_percentage=savings_pct,
            budget_target=budget_target,
            budget_remaining=remaining_budget,
            budget_used_percentage=budget_used_pct,
            is_over_budget=is_over,
        )

    @staticmethod
    async def get_category_analytics(db: AsyncSession, user_id: str, period: Optional[str] = None) -> CategoryAnalyticsResponse:
        today = date.today()
        if not period:
            period = today.strftime("%Y-%m")

        year, month = map(int, period.split("-"))
        _, last_day = calendar.monthrange(year, month)
        start_date = date(year, month, 1)
        end_date = date(year, month, last_day)

        cat_stmt = select(ExpenseCategory).where(ExpenseCategory.user_id == user_id)
        c_res = await db.execute(cat_stmt)
        categories = {c.id: c for c in c_res.scalars().all()}

        tx_stmt = select(
            Transaction.category_id,
            func.sum(Transaction.amount).label("total_spent")
        ).where(
            Transaction.user_id == user_id,
            Transaction.type == TransactionType.EXPENSE,
            Transaction.date >= start_date,
            Transaction.date <= end_date
        ).group_by(Transaction.category_id)
        tx_res = await db.execute(tx_stmt)

        cat_spends = []
        total_expenses = Decimal("0.00")
        for cat_id, spent_val in tx_res.all():
            spent = to_decimal(spent_val)
            total_expenses += spent
            cat = categories.get(cat_id)
            c_name = cat.name if cat else "General Expenses"
            c_color = cat.color if cat else "#6B7280"
            c_icon = cat.icon if cat else "receipt"
            c_limit = to_decimal(cat.budget_limit) if (cat and cat.budget_limit is not None) else None
            is_over = (c_limit is not None and spent > c_limit)

            cat_spends.append(CategorySpend(
                category_id=cat_id,
                category_name=c_name,
                color=c_color,
                icon=c_icon,
                amount=spent,
                percentage=0.0, # Computed below
                budget_limit=c_limit,
                is_over_budget=is_over,
            ))

        # Compute percentages
        for cs in cat_spends:
            cs.percentage = round(float(cs.amount / total_expenses * 100), 1) if total_expenses > 0 else 0.0

        cat_spends.sort(key=lambda x: x.amount, reverse=True)

        return CategoryAnalyticsResponse(
            period=period,
            total_expenses=total_expenses,
            categories=cat_spends,
        )

    @staticmethod
    async def get_spending_trends(db: AsyncSession, user_id: str, num_months: int = 6) -> SpendingTrendsResponse:
        today = date.today()
        trends: List[MonthlyTrendPoint] = []

        # Iterate past N months in chronological order
        for i in range(num_months - 1, -1, -1):
            # Compute year & month
            total_month = today.year * 12 + today.month - 1 - i
            y = total_month // 12
            m = total_month % 12 + 1
            period_str = f"{y:04d}-{m:02d}"
            label = f"{calendar.month_abbr[m]} {y}"

            _, last_day = calendar.monthrange(y, m)
            start_date = date(y, m, 1)
            end_date = date(y, m, last_day)

            inc_stmt = select(func.sum(Transaction.amount)).where(
                Transaction.user_id == user_id,
                Transaction.type == TransactionType.INCOME,
                Transaction.date >= start_date,
                Transaction.date <= end_date
            )
            inc_res = await db.execute(inc_stmt)
            inc = to_decimal(inc_res.scalar())

            exp_stmt = select(func.sum(Transaction.amount)).where(
                Transaction.user_id == user_id,
                Transaction.type == TransactionType.EXPENSE,
                Transaction.date >= start_date,
                Transaction.date <= end_date
            )
            exp_res = await db.execute(exp_stmt)
            exp = to_decimal(exp_res.scalar())

            trends.append(MonthlyTrendPoint(
                month_label=label,
                period=period_str,
                income=inc,
                expenses=exp,
                net_savings=inc - exp,
            ))

        return SpendingTrendsResponse(
            period_count=len(trends),
            trends=trends,
        )

    @staticmethod
    async def get_finance_dashboard(db: AsyncSession, user_id: str, period: Optional[str] = None) -> FinanceDashboardResponse:
        await FinanceService.seed_default_categories_if_empty(db, user_id)
        today = date.today()
        if not period:
            period = today.strftime("%Y-%m")

        summary = await FinanceService.get_financial_summary(db, user_id, period)
        cat_analytics = await FinanceService.get_category_analytics(db, user_id, period)
        trends_resp = await FinanceService.get_spending_trends(db, user_id, num_months=6)

        # Active subscriptions
        subs = await FinanceService.get_subscriptions(db, user_id, status=SubscriptionStatus.ACTIVE)
        active_sub_count = len(subs)
        monthly_sub_total = sum((s.monthly_equivalent for s in subs), Decimal("0.00"))

        # Upcoming renewals within 30 days
        next_30 = today + timedelta(days=30)
        upcoming_subs = [s for s in subs if today <= s.next_billing_date <= next_30]

        # Recent transactions (top 10)
        recent_tx_resp = await FinanceService.get_transactions(db, user_id, limit=10)

        # Burn rate
        year, month = map(int, period.split("-"))
        _, num_days = calendar.monthrange(year, month)
        passed_days = today.day if (today.year == year and today.month == month) else num_days
        burn_rate = (summary.expenses / Decimal(str(max(1, passed_days)))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        projected_end = (burn_rate * Decimal(str(num_days))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        return FinanceDashboardResponse(
            period=period,
            total_income=summary.income,
            total_expenses=summary.expenses,
            net_balance=summary.net_balance,
            savings_percentage=summary.savings_percentage,
            monthly_budget_target=summary.budget_target,
            remaining_budget=summary.budget_remaining,
            budget_used_percentage=summary.budget_used_percentage,
            is_over_budget=summary.is_over_budget,
            burn_rate_per_day=burn_rate,
            projected_month_end_expense=projected_end,
            active_subscriptions_count=active_sub_count,
            monthly_subscription_total=monthly_sub_total,
            top_categories=cat_analytics.categories[:6],
            recent_transactions=recent_tx_resp.transactions,
            upcoming_subscriptions=upcoming_subs[:5],
            spending_trends=trends_resp.trends,
        )

    # ==========================================
    # FUTURE AI RETRIEVAL CONTEXT HOOK
    # ==========================================
    @staticmethod
    async def get_financial_context(db: AsyncSession, user_id: str) -> Dict[str, Any]:
        """Provides verified deterministic financial context for Universal AI retrieval."""
        dash = await FinanceService.get_finance_dashboard(db, user_id)
        top_cat = dash.top_categories[0].model_dump() if dash.top_categories else None
        return {
            "source": "finance",
            "period": dash.period,
            "income": float(dash.total_income),
            "expenses": float(dash.total_expenses),
            "balance": float(dash.net_balance),
            "monthly_budget": float(dash.monthly_budget_target),
            "remaining_budget": float(dash.remaining_budget),
            "budget_used_percentage": dash.budget_used_percentage,
            "is_over_budget": dash.is_over_budget,
            "top_category": top_cat,
            "active_subscriptions": dash.active_subscriptions_count,
            "monthly_subscription_cost": float(dash.monthly_subscription_total),
            "recent_transactions_count": len(dash.recent_transactions),
        }

    @staticmethod
    async def get_finance_analytics(db: AsyncSession, user_id: str, target_month: Optional[str] = None) -> FinanceDashboardResponse:
        """Backward compatibility alias for dashboard glance and legacy analytics."""
        return await FinanceService.get_finance_dashboard(db, user_id, target_month)



