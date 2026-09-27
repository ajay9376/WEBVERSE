from datetime import datetime, timezone, date
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from app.models.academic import Subject, AttendanceRecord, TimetableSlot, Assignment, Exam, AcademicNote, AttendanceStatus
from app.schemas.academic import SubjectResponse

class AcademicService:
    @staticmethod
    async def get_subject_with_stats(db: AsyncSession, subject: Subject) -> SubjectResponse:
        # Fetch attendance records for this subject
        stmt = select(AttendanceRecord).where(AttendanceRecord.subject_id == subject.id)
        result = await db.execute(stmt)
        records = result.scalars().all()

        total_classes = len(records)
        attended_classes = sum(1 for r in records if r.status in (AttendanceStatus.PRESENT, AttendanceStatus.DUTY_LEAVE))
        
        current_percentage = 100.0
        if total_classes > 0:
            current_percentage = round((attended_classes / total_classes) * 100.0, 1)

        target = subject.target_attendance_percent or 85.0
        min_pct = subject.min_attendance_percent or 75.0

        # Calculate safe bunks or required classes
        bunkable = 0
        needed = 0

        if current_percentage >= target:
            status_indicator = "SAFE"
            # How many can be missed without dropping below target
            # (attended) / (total + x) >= target/100
            # x <= (attended * 100 / target) - total
            if target > 0:
                max_total = int(attended_classes * 100 / target)
                bunkable = max(0, max_total - total_classes)
        elif current_percentage >= min_pct:
            status_indicator = "ON_TRACK"
            if min_pct > 0:
                max_total = int(attended_classes * 100 / min_pct)
                bunkable = max(0, max_total - total_classes)
        else:
            status_indicator = "CRITICAL"
            # How many consecutive classes needed to reach min_pct
            # (attended + y) / (total + y) >= min_pct/100
            # 100*attended + 100y >= min_pct*total + min_pct*y
            # y*(100 - min_pct) >= min_pct*total - 100*attended
            denom = 100 - min_pct
            if denom > 0:
                num = (min_pct * total_classes) - (100 * attended_classes)
                needed = max(0, int(num / denom) + (1 if num % denom != 0 else 0))

        resp = SubjectResponse.model_validate(subject)
        resp.total_classes = total_classes
        resp.attended_classes = attended_classes
        resp.current_percentage = current_percentage
        resp.status_indicator = status_indicator
        resp.bunkable_classes = bunkable
        resp.needed_classes = needed
        return resp

    @staticmethod
    async def get_all_subjects_with_stats(db: AsyncSession, user_id: str) -> List[SubjectResponse]:
        stmt = select(Subject).where(Subject.user_id == user_id)
        res = await db.execute(stmt)
        subjects = res.scalars().all()
        return [await AcademicService.get_subject_with_stats(db, s) for s in subjects]
