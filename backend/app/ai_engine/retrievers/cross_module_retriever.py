from typing import Dict, Any, List
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import func, and_

from app.models.academic import Subject, Assignment, Exam, AssignmentStatus
from app.models.finance import Transaction, Budget, TransactionType
from app.models.life_admin import Bill, Reminder, InsurancePolicy, BillStatus
from app.services.academic_service import AcademicService
from app.services.finance_service import FinanceService

class CrossModuleRetriever:
    """
    Retrieves composite context across all three Webverse modules to power 
    cross-domain reasoning queries such as:
    - "Can I afford to travel given my exams & bills?"
    - "What does my week look like across all dimensions?"
    - "Give me a holistic health check of my life right now."
    """

    @staticmethod
    async def retrieve_context(db: AsyncSession, user_id: str, query: str) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        week_end = now + timedelta(days=7)
        month_end = now + timedelta(days=30)

        # ── 1. ACADEMICS ─────────────────────────────────────────────────
        subjects = await AcademicService.get_subjects(db, user_id)
        overall_attendance = 0.0
        at_risk_subjects = []
        safe_subjects = []
        if subjects:
            total_held = sum(s.total_classes for s in subjects)
            total_attended = sum(s.attended_classes for s in subjects)
            if total_held > 0:
                overall_attendance = round((total_attended / total_held) * 100.0, 1)
            at_risk_subjects = [s.name for s in subjects if s.status_indicator in ("WARNING", "CRITICAL")]
            safe_subjects = [s.name for s in subjects if s.status_indicator == "SAFE"]

        # Upcoming exams (next 30 days)
        exam_stmt = select(Exam).options(selectinload(Exam.subject)).where(
            Exam.user_id == user_id,
            Exam.exam_date >= now.replace(tzinfo=None),
            Exam.exam_date <= month_end.replace(tzinfo=None)
        ).order_by(Exam.exam_date.asc()).limit(5)
        exam_res = await db.execute(exam_stmt)
        upcoming_exams = exam_res.scalars().all()

        # Pending assignments (next 7 days = high urgency)
        asgn_stmt = select(Assignment).options(selectinload(Assignment.subject)).where(
            Assignment.user_id == user_id,
            Assignment.status == AssignmentStatus.PENDING,
            Assignment.due_date >= now.replace(tzinfo=None),
            Assignment.due_date <= week_end.replace(tzinfo=None)
        ).order_by(Assignment.due_date.asc()).limit(4)
        asgn_res = await db.execute(asgn_stmt)
        urgent_assignments = asgn_res.scalars().all()

        # ── 2. FINANCE ────────────────────────────────────────────────────
        analytics = await FinanceService.get_finance_analytics(db, user_id)
        budget_health_score = "HEALTHY"
        if float(analytics.budget_used_percentage) > 90:
            budget_health_score = "CRITICAL"
        elif float(analytics.budget_used_percentage) > 70:
            budget_health_score = "CAUTION"

        # ── 3. LIFE ADMIN ─────────────────────────────────────────────────
        # Pending bills (next 30 days)
        bills_stmt = select(Bill).where(
            Bill.user_id == user_id,
            Bill.status == BillStatus.PENDING,
            Bill.due_date >= now.replace(tzinfo=None),
            Bill.due_date <= month_end.replace(tzinfo=None)
        ).order_by(Bill.due_date.asc()).limit(6)
        bills_res = await db.execute(bills_stmt)
        pending_bills = bills_res.scalars().all()
        total_bills_amount = sum(float(b.amount) for b in pending_bills)

        # Overdue bills
        overdue_stmt = select(Bill).where(
            Bill.user_id == user_id,
            Bill.status == BillStatus.PENDING,
            Bill.due_date < now.replace(tzinfo=None)
        )
        overdue_res = await db.execute(overdue_stmt)
        overdue_bills = overdue_res.scalars().all()

        # Expiring insurance (next 90 days)
        ins_stmt = select(InsurancePolicy).where(
            InsurancePolicy.user_id == user_id,
            InsurancePolicy.expiry_date >= now.replace(tzinfo=None),
            InsurancePolicy.expiry_date <= (now + timedelta(days=90)).replace(tzinfo=None)
        ).order_by(InsurancePolicy.expiry_date.asc()).limit(4)
        ins_res = await db.execute(ins_stmt)
        expiring_policies = ins_res.scalars().all()

        # Pending reminders (next 7 days)
        rem_stmt = select(Reminder).where(
            Reminder.user_id == user_id,
            Reminder.is_completed == False,
            Reminder.due_at >= now.replace(tzinfo=None),
            Reminder.due_at <= week_end.replace(tzinfo=None)
        ).order_by(Reminder.due_at.asc()).limit(5)
        rem_res = await db.execute(rem_stmt)
        upcoming_reminders = rem_res.scalars().all()

        # ── 4. COMPOSITE INTELLIGENCE METRICS ────────────────────────────
        # Net liquidity after bills
        remaining_after_bills = float(analytics.remaining_budget) - total_bills_amount
        is_liquid_after_bills = remaining_after_bills > 0
        is_exam_week = any(
            (e.exam_date - now.replace(tzinfo=None)).days <= 7
            for e in upcoming_exams
            if e.exam_date
        )

        return {
            # === Academics ===
            "academics_summary": {
                "overall_attendance_percentage": overall_attendance,
                "subjects_total": len(subjects),
                "subjects_at_risk": at_risk_subjects,
                "subjects_safe": safe_subjects,
                "is_exam_week": is_exam_week,
                "upcoming_exams_7d": [
                    {
                        "subject": e.subject.name if e.subject else "Unknown",
                        "title": e.title,
                        "exam_date": e.exam_date.strftime("%Y-%m-%d %H:%M") if e.exam_date else "N/A",
                        "days_away": (e.exam_date - now.replace(tzinfo=None)).days if e.exam_date else 999
                    }
                    for e in upcoming_exams
                    if e.exam_date and (e.exam_date - now.replace(tzinfo=None)).days <= 7
                ],
                "urgent_assignments": [
                    {
                        "subject": a.subject.name if a.subject else "General",
                        "title": a.title,
                        "due_date": a.due_date.strftime("%Y-%m-%d") if a.due_date else "N/A"
                    }
                    for a in urgent_assignments
                ]
            },

            # === Finance ===
            "finance_summary": {
                "remaining_budget": f"₹{float(analytics.remaining_budget):,.2f}",
                "remaining_budget_raw": float(analytics.remaining_budget),
                "total_spent_this_month": f"₹{float(analytics.total_expenses):,.2f}",
                "budget_used_percentage": f"{float(analytics.budget_used_percentage):.1f}%",
                "burn_rate_per_day": f"₹{float(analytics.burn_rate_per_day):,.2f}",
                "budget_health": budget_health_score,
                "is_over_budget": analytics.is_over_budget
            },

            # === Life Admin ===
            "life_admin_summary": {
                "pending_bills_count": len(pending_bills),
                "total_bills_due_this_month": f"₹{total_bills_amount:,.2f}",
                "total_bills_raw": total_bills_amount,
                "overdue_bills_count": len(overdue_bills),
                "upcoming_bills": [
                    {
                        "title": b.title,
                        "amount": f"₹{float(b.amount):,.2f}",
                        "raw_amount": float(b.amount),
                        "due_date": b.due_date.strftime("%Y-%m-%d") if b.due_date else "N/A",
                        "days_until_due": (b.due_date - now.replace(tzinfo=None)).days if b.due_date else 999
                    }
                    for b in pending_bills
                ],
                "expiring_policies": [
                    {
                        "policy_name": p.policy_name,
                        "provider": p.provider,
                        "expiry_date": p.expiry_date.strftime("%Y-%m-%d"),
                        "days_to_expiry": (p.expiry_date - now.replace(tzinfo=None)).days
                    }
                    for p in expiring_policies
                ],
                "upcoming_reminders": [
                    {
                        "title": r.title,
                        "due_at": r.due_at.strftime("%Y-%m-%d %H:%M") if r.due_at else "N/A",
                        "priority": r.priority.value if hasattr(r.priority, "value") else str(r.priority)
                    }
                    for r in upcoming_reminders
                ]
            },

            # === Composite Intelligence ===
            "intelligence_overlay": {
                "net_liquidity_after_bills": f"₹{remaining_after_bills:,.2f}",
                "net_liquidity_raw": remaining_after_bills,
                "is_liquid_after_bills": is_liquid_after_bills,
                "is_exam_week": is_exam_week,
                "has_overdue_bills": len(overdue_bills) > 0,
                "life_health_score": CrossModuleRetriever._compute_life_score(
                    overall_attendance, float(analytics.budget_used_percentage),
                    len(overdue_bills), is_exam_week, len(at_risk_subjects)
                ),
                "critical_alerts": CrossModuleRetriever._compute_alerts(
                    overdue_bills, expiring_policies, at_risk_subjects, analytics
                )
            }
        }

    @staticmethod
    def _compute_life_score(attendance: float, budget_used: float, overdue: int, exam_week: bool, at_risk: int) -> str:
        """Compute a qualitative life health score."""
        score = 100
        if attendance < 75:
            score -= 25
        elif attendance < 80:
            score -= 10
        if budget_used > 90:
            score -= 20
        elif budget_used > 70:
            score -= 10
        score -= overdue * 10
        score -= at_risk * 8
        if exam_week:
            score -= 5  # exam pressure
        if score >= 80:
            return "EXCELLENT"
        elif score >= 60:
            return "GOOD"
        elif score >= 40:
            return "NEEDS_ATTENTION"
        else:
            return "CRITICAL"

    @staticmethod
    def _compute_alerts(overdue_bills: list, expiring_policies: list, at_risk_subjects: list, analytics) -> List[str]:
        """Generate a list of critical textual alerts."""
        alerts = []
        if overdue_bills:
            alerts.append(f"⚠️ {len(overdue_bills)} bill(s) are OVERDUE and need immediate payment.")
        for p in expiring_policies:
            days = (p.expiry_date - datetime.now(timezone.utc).replace(tzinfo=None)).days
            if days <= 30:
                alerts.append(f"🛡️ Insurance '{p.policy_name}' expires in {days} days!")
        for s in at_risk_subjects:
            alerts.append(f"📚 Subject '{s}' is below minimum attendance threshold!")
        if float(analytics.budget_used_percentage) > 90:
            alerts.append(f"💸 Budget critically overspent ({float(analytics.budget_used_percentage):.1f}% used)!")
        return alerts
