from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.services.finance_service import FinanceService
from app.models.finance import Subscription

class FinanceRetriever:
    @staticmethod
    async def retrieve_context(db: AsyncSession, user_id: str, query: str) -> Dict[str, Any]:
        analytics = await FinanceService.get_finance_analytics(db, user_id)
        
        # Subscriptions
        sub_stmt = select(Subscription).where(Subscription.user_id == user_id, Subscription.is_active == True)
        sub_res = await db.execute(sub_stmt)
        subscriptions = sub_res.scalars().all()

        return {
            "current_month": analytics.period,
            "monthly_budget_target": f"₹{float(analytics.monthly_budget_target):,.2f}",
            "total_expenses_this_month": f"₹{float(analytics.total_expenses):,.2f}",
            "remaining_budget": f"₹{float(analytics.remaining_budget):,.2f}",
            "budget_used_percentage": f"{analytics.budget_used_percentage}%",
            "is_over_budget": analytics.is_over_budget,
            "average_daily_burn_rate": f"₹{float(analytics.burn_rate_per_day):,.2f}/day",
            "projected_month_end_expense": f"₹{float(analytics.projected_month_end_expense):,.2f}",
            "top_spending_categories": [
                {
                    "category": c.category_name,
                    "spent": f"₹{float(c.amount):,.2f}",
                    "percentage": f"{c.percentage}%"
                }
                for c in analytics.top_categories
            ],
            "active_subscriptions": [
                {
                    "name": s.name,
                    "amount": f"₹{float(s.amount):,.2f}",
                    "cycle": s.billing_cycle.value if hasattr(s.billing_cycle, "value") else str(s.billing_cycle),
                    "next_date": s.next_billing_date.strftime("%Y-%m-%d")
                }
                for s in subscriptions
            ],
            "recent_transactions": [
                {
                    "title": t.title,
                    "amount": f"₹{float(t.amount):,.2f}",
                    "type": (t.transaction_type.value if hasattr(t.transaction_type, "value") else str(t.transaction_type)) if t.transaction_type else "EXPENSE",
                    "category": t.category_name,
                    "date": t.date.strftime("%Y-%m-%d") if t.date else ""
                }
                for t in analytics.recent_transactions[:6]
            ]
        }
