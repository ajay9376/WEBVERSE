from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.user import User
from app.models.academic import Subject, Assignment, Exam
from app.models.life_admin import Document, Reminder
from app.schemas.dashboard import DashboardGlanceResponse
from app.schemas.academic import AssignmentResponse, ExamResponse
from app.services.academic_service import AcademicService
from app.services.finance_service import FinanceService
from app.services.life_service import LifeAdminService

class DashboardService:
    @staticmethod
    async def get_dashboard_glance(db: AsyncSession, user: User) -> DashboardGlanceResponse:
        now = datetime.now(timezone.utc)
        hour = now.hour
        if 5 <= hour < 12:
            greeting = f"Good morning, {user.full_name}"
        elif 12 <= hour < 17:
            greeting = f"Good afternoon, {user.full_name}"
        elif 17 <= hour < 22:
            greeting = f"Good evening, {user.full_name}"
        else:
            greeting = f"Welcome to the Webverse, {user.full_name}"

        # 1. Academics
        subjects = await AcademicService.get_all_subjects_with_stats(db, user.id)
        overall_attendance = 100.0
        at_risk = 0
        if subjects:
            total_held = sum(s.total_classes for s in subjects)
            total_attended = sum(s.attended_classes for s in subjects)
            if total_held > 0:
                overall_attendance = round((total_attended / total_held) * 100.0, 1)
            at_risk = sum(1 for s in subjects if s.status_indicator in ("AT_RISK", "CRITICAL"))

        # Upcoming assignments
        asgn_stmt = select(Assignment).options(selectinload(Assignment.subject)).where(
            Assignment.user_id == user.id,
            Assignment.status != "SUBMITTED",
            Assignment.status != "GRADED"
        ).order_by(Assignment.due_date.asc()).limit(4)
        asgn_res = await db.execute(asgn_stmt)
        upcoming_assignments = [
            AssignmentResponse(
                id=a.id,
                user_id=a.user_id,
                subject_id=a.subject_id,
                subject_name=a.subject.name if a.subject else "General",
                subject_color=a.subject.color if a.subject else "#8B5CF6",
                title=a.title,
                description=a.description,
                due_date=a.due_date,
                status=a.status,
                total_marks=a.total_marks,
                obtained_marks=a.obtained_marks,
                created_at=a.created_at
            )
            for a in asgn_res.scalars().all()
        ]

        # Upcoming exams
        exam_stmt = select(Exam).options(selectinload(Exam.subject)).where(
            Exam.user_id == user.id,
            Exam.exam_date >= now.replace(tzinfo=None)
        ).order_by(Exam.exam_date.asc()).limit(3)
        exam_res = await db.execute(exam_stmt)
        upcoming_exams = [
            ExamResponse(
                id=e.id,
                user_id=e.user_id,
                subject_id=e.subject_id,
                subject_name=e.subject.name if e.subject else "Exam",
                subject_color=e.subject.color if e.subject else "#8B5CF6",
                title=e.title,
                exam_date=e.exam_date,
                location=e.location,
                syllabus_covered=e.syllabus_covered,
                total_marks=e.total_marks,
                obtained_marks=e.obtained_marks,
                created_at=e.created_at
            )
            for e in exam_res.scalars().all()
        ]

        # 2. Finance
        finance_analytics = await FinanceService.get_finance_analytics(db, user.id)
        budget_health = "HEALTHY"
        if finance_analytics.budget_used_percentage > 90.0:
            budget_health = "CRITICAL"
        elif finance_analytics.budget_used_percentage > 70.0:
            budget_health = "CAUTION"

        # 3. Life Admin
        rem_stmt = select(Reminder).where(
            Reminder.user_id == user.id,
            Reminder.is_completed == False
        ).order_by(Reminder.due_at.asc()).limit(5)
        rem_res = await db.execute(rem_stmt)
        pending_reminders = [LifeAdminService.format_reminder(r) for r in rem_res.scalars().all()]
        urgent_alerts = sum(1 for r in pending_reminders if r.priority == "CRITICAL" or r.is_overdue)

        # Recent docs
        doc_stmt = select(Document).where(Document.user_id == user.id).order_by(Document.created_at.desc()).limit(3)
        doc_res = await db.execute(doc_stmt)
        recent_docs = [LifeAdminService.format_document(d) for d in doc_res.scalars().all()]

        return DashboardGlanceResponse(
            user_name=user.full_name,
            greeting=greeting,
            overall_attendance_percent=overall_attendance,
            subjects_at_risk_count=at_risk,
            upcoming_assignments=upcoming_assignments,
            upcoming_exams=upcoming_exams,
            monthly_budget_target=finance_analytics.monthly_budget_target,
            monthly_total_spent=finance_analytics.total_expenses,
            monthly_remaining_budget=finance_analytics.remaining_budget,
            budget_health_status=budget_health,
            pending_reminders=pending_reminders,
            urgent_alerts_count=urgent_alerts,
            recent_documents=recent_docs,
            active_dimensions=["ACADEMICS", "FINANCE", "LIFE_ADMIN"]
        )
