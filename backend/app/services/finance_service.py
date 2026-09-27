from datetime import datetime, date, timezone
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
import calendar
from app.models.finance import Transaction, ExpenseCategory, Budget, Subscription, TransactionType
from app.schemas.finance import FinanceAnalyticsResponse, CategorySpend, TransactionResponse

class FinanceService:
    @staticmethod
    async def get_finance_analytics(db: AsyncSession, user_id: str, target_month: str = None) -> FinanceAnalyticsResponse:
        today = date.today()
        if not target_month:
            target_month = today.strftime("%Y-%m") # e.g. "2026-09"

        year, month = map(int, target_month.split("-"))
        _, num_days_in_month = calendar.monthrange(year, month)
        start_date = date(year, month, 1)
        end_date = date(year, month, num_days_in_month)

        # Query transactions for this month
        stmt = select(Transaction).where(
            Transaction.user_id == user_id,
            Transaction.date >= start_date,
            Transaction.date <= end_date
        ).order_by(Transaction.date.desc())
        
        result = await db.execute(stmt)
        transactions = result.scalars().all()

        total_income = sum(t.amount for t in transactions if t.type == TransactionType.INCOME)
        total_expenses = sum(t.amount for t in transactions if t.type == TransactionType.EXPENSE)
        net_savings = total_income - total_expenses

        # Query user's monthly budget target
        budget_stmt = select(Budget).where(Budget.user_id == user_id, Budget.month == target_month)
        b_res = await db.execute(budget_stmt)
        budget = b_res.scalars().first()
        budget_target = budget.total_budget_limit if budget else 10000.0

        used_pct = round((total_expenses / budget_target * 100.0), 1) if budget_target > 0 else 0.0
        remaining_budget = max(0.0, budget_target - total_expenses)
        is_over = total_expenses > budget_target

        # Burn rate
        current_day = today.day if (today.year == year and today.month == month) else num_days_in_month
        burn_rate = round(total_expenses / max(1, current_day), 2)
        projected = round(burn_rate * num_days_in_month, 2)

        # Group by category
        cat_stmt = select(ExpenseCategory).where(ExpenseCategory.user_id == user_id)
        c_res = await db.execute(cat_stmt)
        categories = {c.id: c for c in c_res.scalars().all()}

        cat_spend_map: Dict[str, float] = {}
        for t in transactions:
            if t.type == TransactionType.EXPENSE:
                cat_key = t.category_id or "uncategorized"
                cat_spend_map[cat_key] = cat_spend_map.get(cat_key, 0.0) + t.amount

        top_categories: List[CategorySpend] = []
        for cat_id, amt in cat_spend_map.items():
            cat = categories.get(cat_id)
            c_name = cat.name if cat else "General Expenses"
            c_color = cat.color if cat else "#6B7280"
            pct = round((amt / total_expenses * 100.0), 1) if total_expenses > 0 else 0.0
            top_categories.append(CategorySpend(
                category_id=cat_id if cat else None,
                category_name=c_name,
                color=c_color,
                amount=amt,
                percentage=pct
            ))

        top_categories.sort(key=lambda x: x.amount, reverse=True)

        recent_txs = [
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
            for t in transactions[:10]
        ]

        return FinanceAnalyticsResponse(
            current_month=target_month,
            total_income=total_income,
            total_expenses=total_expenses,
            net_savings=net_savings,
            monthly_budget_target=budget_target,
            budget_used_percentage=used_pct,
            remaining_budget=remaining_budget,
            is_over_budget=is_over,
            burn_rate_per_day=burn_rate,
            projected_month_end_expense=projected,
            top_categories=top_categories,
            recent_transactions=recent_txs
        )
