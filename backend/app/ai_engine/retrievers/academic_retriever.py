from typing import Dict, Any, List
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.academic import Subject, AttendanceRecord, TimetableSlot, Assignment, Exam, AcademicNote
from app.services.academic_service import AcademicService

class AcademicRetriever:
    @staticmethod
    async def retrieve_context(db: AsyncSession, user_id: str, query: str) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        subjects = await AcademicService.get_all_subjects_with_stats(db, user_id)
        
        # Upcoming assignments (next 14 days)
        asgn_stmt = select(Assignment).options(selectinload(Assignment.subject)).where(
            Assignment.user_id == user_id,
            Assignment.due_date >= (now - timedelta(days=1)).replace(tzinfo=None)
        ).order_by(Assignment.due_date.asc())
        asgn_res = await db.execute(asgn_stmt)
        assignments = asgn_res.scalars().all()

        # Upcoming exams
        exam_stmt = select(Exam).options(selectinload(Exam.subject)).where(
            Exam.user_id == user_id,
            Exam.exam_date >= (now - timedelta(days=1)).replace(tzinfo=None)
        ).order_by(Exam.exam_date.asc())
        exam_res = await db.execute(exam_stmt)
        exams = exam_res.scalars().all()

        # Timetable
        tt_stmt = select(TimetableSlot).options(selectinload(TimetableSlot.subject)).where(TimetableSlot.user_id == user_id)
        tt_res = await db.execute(tt_stmt)
        slots = tt_res.scalars().all()

        days_map = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        return {
            "subjects": [
                {
                    "name": s.name,
                    "code": s.code,
                    "attendance_percentage": f"{s.current_percentage}%",
                    "attended": s.attended_classes,
                    "total_classes": s.total_classes,
                    "status": s.status_indicator,
                    "bunkable_classes_safe": s.bunkable_classes,
                    "needed_classes_to_reach_target": s.needed_classes
                }
                for s in subjects
            ],
            "upcoming_assignments": [
                {
                    "subject": a.subject.name if a.subject else "General",
                    "title": a.title,
                    "due_date": a.due_date.strftime("%Y-%m-%d %H:%M"),
                    "status": a.status
                }
                for a in assignments
            ],
            "upcoming_exams": [
                {
                    "subject": e.subject.name if e.subject else "General",
                    "title": e.title,
                    "exam_date": e.exam_date.strftime("%Y-%m-%d %H:%M"),
                    "syllabus": e.syllabus_covered
                }
                for e in exams
            ],
            "timetable_schedule": [
                {
                    "day": days_map[slot.day_of_week] if slot.day_of_week < len(days_map) else str(slot.day_of_week),
                    "subject": slot.subject.name if slot.subject else "Class",
                    "time": f"{slot.start_time} - {slot.end_time}",
                    "room": slot.room
                }
                for slot in slots
            ]
        }
