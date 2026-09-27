import math
from datetime import datetime, timezone, date
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import func, desc, asc
from fastapi import HTTPException, status

from app.models.academic import (
    AcademicProfile,
    Subject,
    AttendanceRecord,
    TimetableSlot,
    Assignment,
    Exam,
    InternalMark,
    AcademicProject,
    AcademicNote,
    AttendanceStatus,
    AssignmentStatus,
    AssignmentPriority,
    ExamType,
    AssessmentType,
    ProjectStatus,
)
from app.schemas.academic import (
    AcademicProfileCreate,
    AcademicProfileUpdate,
    AcademicProfileResponse,
    SubjectCreate,
    SubjectUpdate,
    SubjectResponse,
    AttendanceRecordCreate,
    AttendanceRecordResponse,
    AttendanceSummaryResponse,
    AttendanceProjectionResponse,
    TimetableSlotCreate,
    TimetableSlotUpdate,
    TimetableSlotResponse,
    AssignmentCreate,
    AssignmentUpdate,
    AssignmentResponse,
    ExamCreate,
    ExamUpdate,
    ExamResponse,
    InternalMarkCreate,
    InternalMarkUpdate,
    InternalMarkResponse,
    AcademicProjectCreate,
    AcademicProjectUpdate,
    AcademicProjectResponse,
    AcademicNoteCreate,
    AcademicNoteUpdate,
    AcademicNoteResponse,
    AcademicDashboardResponse,
    AcademicAttendanceGlance,
)

class AcademicService:
    # ----------------- Pure Math / Attendance Calculations -----------------
    @staticmethod
    def calculate_attendance_metrics(attended: int, total: int, target: float = 80.0, min_pct: float = 75.0) -> Dict[str, Any]:
        if total <= 0:
            return {
                "percentage": 100.0 if attended > 0 else 0.0,
                "status_indicator": "NO_DATA" if total == 0 and attended == 0 else "SAFE",
                "bunkable_classes": 0,
                "needed_classes": 0,
            }
        
        # Guard against invalid negative numbers
        attended = max(0, attended)
        total = max(attended, total)

        pct = round((attended / total) * 100.0, 1)

        if pct >= target:
            status_indicator = "SAFE"
            # Number of classes that can be missed without dropping below target
            bunkable = max(0, int((attended * 100.0) / target) - total) if target > 0 else 0
            needed = 0
        else:
            status_indicator = "CRITICAL" if pct < min_pct else "ON_TRACK"
            bunkable = 0
            denom = 100.0 - target
            num = (target * total) - (100.0 * attended)
            needed = max(0, math.ceil(num / denom)) if denom > 0 else 0

        return {
            "percentage": pct,
            "status_indicator": status_indicator,
            "bunkable_classes": bunkable,
            "needed_classes": needed,
        }

    @staticmethod
    def calculate_projection_stats(subject: Subject) -> AttendanceProjectionResponse:
        metrics = AcademicService.calculate_attendance_metrics(
            subject.attended_classes,
            subject.total_classes,
            subject.target_attendance,
            subject.min_attendance
        )
        
        att = subject.attended_classes
        tot = subject.total_classes

        def sim_pct(add_att: int, add_tot: int) -> float:
            new_tot = tot + add_tot
            if new_tot <= 0:
                return 0.0
            return round(((att + add_att) / new_tot) * 100.0, 1)

        return AttendanceProjectionResponse(
            subject_id=subject.id,
            subject_name=subject.name,
            subject_code=subject.code,
            total_classes=tot,
            attended_classes=att,
            current_percentage=metrics["percentage"],
            target_percentage=subject.target_attendance,
            min_percentage=subject.min_attendance,
            status_indicator=metrics["status_indicator"],
            classes_needed_for_target=metrics["needed_classes"],
            classes_safe_to_bunk=metrics["bunkable_classes"],
            if_attend_next_1=sim_pct(1, 1),
            if_miss_next_1=sim_pct(0, 1),
            if_attend_next_3=sim_pct(3, 3),
            if_miss_next_3=sim_pct(0, 3),
            if_attend_next_5=sim_pct(5, 5),
            if_miss_next_5=sim_pct(0, 5),
        )

    # ----------------- Academic Profile -----------------
    @staticmethod
    async def get_academic_profile(db: AsyncSession, user_id: str) -> Optional[AcademicProfileResponse]:
        stmt = select(AcademicProfile).where(AcademicProfile.user_id == user_id)
        res = await db.execute(stmt)
        prof = res.scalars().first()
        if not prof:
            return None
        return AcademicProfileResponse.model_validate(prof)

    @staticmethod
    async def upsert_academic_profile(db: AsyncSession, user_id: str, profile_in: AcademicProfileCreate) -> AcademicProfileResponse:
        stmt = select(AcademicProfile).where(AcademicProfile.user_id == user_id)
        res = await db.execute(stmt)
        prof = res.scalars().first()

        if not prof:
            prof = AcademicProfile(
                user_id=user_id,
                college_name=profile_in.college_name,
                university=profile_in.university,
                degree=profile_in.degree,
                branch=profile_in.branch,
                current_year=profile_in.current_year,
                current_semester=profile_in.current_semester,
                roll_number=profile_in.roll_number,
                academic_start_year=profile_in.academic_start_year,
            )
            db.add(prof)
        else:
            for field, val in profile_in.model_dump(exclude_unset=True).items():
                setattr(prof, field, val)

        await db.commit()
        await db.refresh(prof)
        return AcademicProfileResponse.model_validate(prof)

    # ----------------- Subjects -----------------
    @staticmethod
    def _enrich_subject_response(sub: Subject) -> SubjectResponse:
        metrics = AcademicService.calculate_attendance_metrics(
            sub.attended_classes,
            sub.total_classes,
            sub.target_attendance,
            sub.min_attendance
        )
        resp = SubjectResponse.model_validate(sub)
        resp.current_percentage = metrics["percentage"]
        resp.status_indicator = metrics["status_indicator"]
        resp.bunkable_classes = metrics["bunkable_classes"]
        resp.needed_classes = metrics["needed_classes"]
        return resp

    @staticmethod
    async def get_subjects(db: AsyncSession, user_id: str) -> List[SubjectResponse]:
        stmt = select(Subject).where(Subject.user_id == user_id).order_by(Subject.name.asc())
        res = await db.execute(stmt)
        subjects = res.scalars().all()
        return [AcademicService._enrich_subject_response(s) for s in subjects]

    @staticmethod
    async def get_subject(db: AsyncSession, user_id: str, subject_id: str) -> SubjectResponse:
        stmt = select(Subject).where(Subject.id == subject_id, Subject.user_id == user_id)
        res = await db.execute(stmt)
        sub = res.scalars().first()
        if not sub:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found or unauthorized")
        return AcademicService._enrich_subject_response(sub)

    @staticmethod
    async def create_subject(db: AsyncSession, user_id: str, sub_in: SubjectCreate) -> SubjectResponse:
        # Validate counts
        att = sub_in.attended_classes if sub_in.attended_classes is not None else 0
        tot = sub_in.total_classes if sub_in.total_classes is not None else 0
        if att < 0 or tot < 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Class counts cannot be negative")
        if att > tot:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Attended classes cannot exceed total classes")

        sub = Subject(
            user_id=user_id,
            name=sub_in.name,
            code=sub_in.code,
            credits=sub_in.credits or 3,
            semester=sub_in.semester,
            faculty_name=sub_in.faculty_name,
            color=sub_in.color or "#8B5CF6",
            total_classes=tot,
            attended_classes=att,
            target_attendance=sub_in.target_attendance or 80.0,
            min_attendance=sub_in.min_attendance or 75.0,
        )
        db.add(sub)
        await db.commit()
        await db.refresh(sub)
        return AcademicService._enrich_subject_response(sub)

    @staticmethod
    async def update_subject(db: AsyncSession, user_id: str, subject_id: str, sub_in: SubjectUpdate) -> SubjectResponse:
        stmt = select(Subject).where(Subject.id == subject_id, Subject.user_id == user_id)
        res = await db.execute(stmt)
        sub = res.scalars().first()
        if not sub:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found or unauthorized")

        update_data = sub_in.model_dump(exclude_unset=True)
        
        target_att = update_data.get("attended_classes", sub.attended_classes)
        target_tot = update_data.get("total_classes", sub.total_classes)
        if target_att < 0 or target_tot < 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Class counts cannot be negative")
        if target_att > target_tot:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Attended classes cannot exceed total classes")

        for key, val in update_data.items():
            setattr(sub, key, val)

        await db.commit()
        await db.refresh(sub)
        return AcademicService._enrich_subject_response(sub)

    @staticmethod
    async def delete_subject(db: AsyncSession, user_id: str, subject_id: str) -> Dict[str, Any]:
        stmt = select(Subject).where(Subject.id == subject_id, Subject.user_id == user_id)
        res = await db.execute(stmt)
        sub = res.scalars().first()
        if not sub:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found or unauthorized")

        await db.delete(sub)
        await db.commit()
        return {"status": "SUCCESS", "message": f"Subject '{sub.name}' deleted"}

    # ----------------- Attendance Events & Projections -----------------
    @staticmethod
    async def mark_attendance(db: AsyncSession, user_id: str, att_in: AttendanceRecordCreate) -> AttendanceRecordResponse:
        # Verify subject ownership
        stmt = select(Subject).where(Subject.id == att_in.subject_id, Subject.user_id == user_id)
        res = await db.execute(stmt)
        sub = res.scalars().first()
        if not sub:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found or unauthorized")

        rec = AttendanceRecord(
            user_id=user_id,
            subject_id=att_in.subject_id,
            date=att_in.date,
            status=att_in.status,
            remarks=att_in.remarks,
        )
        db.add(rec)

        # Update authoritative counts on Subject
        sub.total_classes += 1
        if att_in.status in (AttendanceStatus.PRESENT, AttendanceStatus.DUTY):
            sub.attended_classes += 1

        await db.commit()
        await db.refresh(rec)

        return AttendanceRecordResponse(
            id=rec.id,
            user_id=rec.user_id,
            subject_id=rec.subject_id,
            subject_name=sub.name,
            subject_code=sub.code,
            date=rec.date,
            status=rec.status,
            remarks=rec.remarks,
            created_at=rec.created_at,
            updated_at=rec.updated_at,
        )

    @staticmethod
    async def get_attendance_history(db: AsyncSession, user_id: str, subject_id: str) -> List[AttendanceRecordResponse]:
        stmt_sub = select(Subject).where(Subject.id == subject_id, Subject.user_id == user_id)
        res_sub = await db.execute(stmt_sub)
        sub = res_sub.scalars().first()
        if not sub:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found or unauthorized")

        stmt = select(AttendanceRecord).where(
            AttendanceRecord.user_id == user_id,
            AttendanceRecord.subject_id == subject_id
        ).order_by(AttendanceRecord.date.desc())
        res = await db.execute(stmt)
        records = res.scalars().all()

        return [
            AttendanceRecordResponse(
                id=r.id,
                user_id=r.user_id,
                subject_id=r.subject_id,
                subject_name=sub.name,
                subject_code=sub.code,
                date=r.date,
                status=r.status,
                remarks=r.remarks,
                created_at=r.created_at,
                updated_at=r.updated_at,
            )
            for r in records
        ]

    @staticmethod
    async def get_attendance_summary(db: AsyncSession, user_id: str) -> AttendanceSummaryResponse:
        subjects_resp = await AcademicService.get_subjects(db, user_id)
        total_cls = sum(s.total_classes for s in subjects_resp)
        att_cls = sum(s.attended_classes for s in subjects_resp)
        overall_pct = round((att_cls / total_cls) * 100.0, 1) if total_cls > 0 else 100.0
        below_target = sum(1 for s in subjects_resp if s.current_percentage < s.target_attendance and s.total_classes > 0)

        return AttendanceSummaryResponse(
            overall_percentage=overall_pct,
            total_classes=total_cls,
            attended_classes=att_cls,
            below_target_count=below_target,
            subjects_count=len(subjects_resp),
            subjects=subjects_resp,
        )

    @staticmethod
    async def get_subject_projection(db: AsyncSession, user_id: str, subject_id: str) -> AttendanceProjectionResponse:
        stmt = select(Subject).where(Subject.id == subject_id, Subject.user_id == user_id)
        res = await db.execute(stmt)
        sub = res.scalars().first()
        if not sub:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found or unauthorized")
        return AcademicService.calculate_projection_stats(sub)

    # ----------------- Timetable -----------------
    @staticmethod
    async def get_timetable(db: AsyncSession, user_id: str) -> List[TimetableSlotResponse]:
        stmt = select(TimetableSlot).options(selectinload(TimetableSlot.subject)).where(
            TimetableSlot.user_id == user_id
        ).order_by(TimetableSlot.day_of_week.asc(), TimetableSlot.start_time.asc())
        res = await db.execute(stmt)
        slots = res.scalars().all()
        return [
            TimetableSlotResponse(
                id=s.id,
                user_id=s.user_id,
                subject_id=s.subject_id,
                subject_name=s.subject.name if s.subject else "Class",
                subject_code=s.subject.code if s.subject else None,
                subject_color=s.subject.color if s.subject else "#8B5CF6",
                day_of_week=s.day_of_week,
                start_time=s.start_time,
                end_time=s.end_time,
                room=s.room,
                faculty_name=s.faculty_name or (s.subject.faculty_name if s.subject else None),
                created_at=s.created_at,
                updated_at=s.updated_at,
            )
            for s in slots
        ]

    @staticmethod
    async def create_timetable_slot(db: AsyncSession, user_id: str, slot_in: TimetableSlotCreate) -> TimetableSlotResponse:
        stmt_sub = select(Subject).where(Subject.id == slot_in.subject_id, Subject.user_id == user_id)
        res_sub = await db.execute(stmt_sub)
        sub = res_sub.scalars().first()
        if not sub:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found or unauthorized")

        slot = TimetableSlot(
            user_id=user_id,
            subject_id=slot_in.subject_id,
            day_of_week=slot_in.day_of_week,
            start_time=slot_in.start_time,
            end_time=slot_in.end_time,
            room=slot_in.room,
            faculty_name=slot_in.faculty_name or sub.faculty_name,
        )
        db.add(slot)
        await db.commit()
        await db.refresh(slot)

        return TimetableSlotResponse(
            id=slot.id,
            user_id=slot.user_id,
            subject_id=slot.subject_id,
            subject_name=sub.name,
            subject_code=sub.code,
            subject_color=sub.color,
            day_of_week=slot.day_of_week,
            start_time=slot.start_time,
            end_time=slot.end_time,
            room=slot.room,
            faculty_name=slot.faculty_name,
            created_at=slot.created_at,
            updated_at=slot.updated_at,
        )

    @staticmethod
    async def update_timetable_slot(db: AsyncSession, user_id: str, slot_id: str, slot_in: TimetableSlotUpdate) -> TimetableSlotResponse:
        stmt = select(TimetableSlot).options(selectinload(TimetableSlot.subject)).where(
            TimetableSlot.id == slot_id, TimetableSlot.user_id == user_id
        )
        res = await db.execute(stmt)
        slot = res.scalars().first()
        if not slot:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Timetable slot not found or unauthorized")

        update_data = slot_in.model_dump(exclude_unset=True)
        if "subject_id" in update_data and update_data["subject_id"] != slot.subject_id:
            stmt_sub = select(Subject).where(Subject.id == update_data["subject_id"], Subject.user_id == user_id)
            res_sub = await db.execute(stmt_sub)
            if not res_sub.scalars().first():
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="New subject not found or unauthorized")

        for key, val in update_data.items():
            setattr(slot, key, val)

        await db.commit()
        await db.refresh(slot)
        sub = await db.get(Subject, slot.subject_id)

        return TimetableSlotResponse(
            id=slot.id,
            user_id=slot.user_id,
            subject_id=slot.subject_id,
            subject_name=sub.name if sub else "Class",
            subject_code=sub.code if sub else None,
            subject_color=sub.color if sub else "#8B5CF6",
            day_of_week=slot.day_of_week,
            start_time=slot.start_time,
            end_time=slot.end_time,
            room=slot.room,
            faculty_name=slot.faculty_name,
            created_at=slot.created_at,
            updated_at=slot.updated_at,
        )

    @staticmethod
    async def delete_timetable_slot(db: AsyncSession, user_id: str, slot_id: str) -> Dict[str, Any]:
        stmt = select(TimetableSlot).where(TimetableSlot.id == slot_id, TimetableSlot.user_id == user_id)
        res = await db.execute(stmt)
        slot = res.scalars().first()
        if not slot:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Timetable slot not found or unauthorized")

        await db.delete(slot)
        await db.commit()
        return {"status": "SUCCESS", "message": "Timetable slot deleted"}

    # ----------------- Assignments -----------------
    @staticmethod
    async def get_assignments(db: AsyncSession, user_id: str, status_filter: Optional[AssignmentStatus] = None) -> List[AssignmentResponse]:
        query = select(Assignment).options(selectinload(Assignment.subject)).where(Assignment.user_id == user_id)
        if status_filter:
            query = query.where(Assignment.status == status_filter)
        query = query.order_by(Assignment.due_date.asc())

        res = await db.execute(query)
        asgns = res.scalars().all()
        return [
            AssignmentResponse(
                id=a.id,
                user_id=a.user_id,
                subject_id=a.subject_id,
                subject_name=a.subject.name if a.subject else "Assignment",
                subject_code=a.subject.code if a.subject else None,
                subject_color=a.subject.color if a.subject else "#8B5CF6",
                title=a.title,
                description=a.description,
                due_date=a.due_date,
                status=a.status,
                priority=a.priority,
                total_marks=a.total_marks,
                obtained_marks=a.obtained_marks,
                created_at=a.created_at,
                updated_at=a.updated_at,
            )
            for a in asgns
        ]

    @staticmethod
    async def get_assignment(db: AsyncSession, user_id: str, asgn_id: str) -> AssignmentResponse:
        stmt = select(Assignment).options(selectinload(Assignment.subject)).where(
            Assignment.id == asgn_id, Assignment.user_id == user_id
        )
        res = await db.execute(stmt)
        a = res.scalars().first()
        if not a:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found or unauthorized")

        return AssignmentResponse(
            id=a.id,
            user_id=a.user_id,
            subject_id=a.subject_id,
            subject_name=a.subject.name if a.subject else "Assignment",
            subject_code=a.subject.code if a.subject else None,
            subject_color=a.subject.color if a.subject else "#8B5CF6",
            title=a.title,
            description=a.description,
            due_date=a.due_date,
            status=a.status,
            priority=a.priority,
            total_marks=a.total_marks,
            obtained_marks=a.obtained_marks,
            created_at=a.created_at,
            updated_at=a.updated_at,
        )

    @staticmethod
    async def create_assignment(db: AsyncSession, user_id: str, asgn_in: AssignmentCreate) -> AssignmentResponse:
        stmt_sub = select(Subject).where(Subject.id == asgn_in.subject_id, Subject.user_id == user_id)
        res_sub = await db.execute(stmt_sub)
        sub = res_sub.scalars().first()
        if not sub:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found or unauthorized")

        asgn = Assignment(
            user_id=user_id,
            subject_id=asgn_in.subject_id,
            title=asgn_in.title,
            description=asgn_in.description,
            due_date=asgn_in.due_date,
            status=asgn_in.status,
            priority=asgn_in.priority,
            total_marks=asgn_in.total_marks,
            obtained_marks=asgn_in.obtained_marks,
        )
        db.add(asgn)
        await db.commit()
        await db.refresh(asgn)

        return AssignmentResponse(
            id=asgn.id,
            user_id=asgn.user_id,
            subject_id=asgn.subject_id,
            subject_name=sub.name,
            subject_code=sub.code,
            subject_color=sub.color,
            title=asgn.title,
            description=asgn.description,
            due_date=asgn.due_date,
            status=asgn.status,
            priority=asgn.priority,
            total_marks=asgn.total_marks,
            obtained_marks=asgn.obtained_marks,
            created_at=asgn.created_at,
            updated_at=asgn.updated_at,
        )

    @staticmethod
    async def update_assignment(db: AsyncSession, user_id: str, asgn_id: str, asgn_in: AssignmentUpdate) -> AssignmentResponse:
        stmt = select(Assignment).options(selectinload(Assignment.subject)).where(
            Assignment.id == asgn_id, Assignment.user_id == user_id
        )
        res = await db.execute(stmt)
        a = res.scalars().first()
        if not a:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found or unauthorized")

        update_data = asgn_in.model_dump(exclude_unset=True)
        if "subject_id" in update_data and update_data["subject_id"] != a.subject_id:
            stmt_sub = select(Subject).where(Subject.id == update_data["subject_id"], Subject.user_id == user_id)
            res_sub = await db.execute(stmt_sub)
            if not res_sub.scalars().first():
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="New subject not found or unauthorized")

        for key, val in update_data.items():
            setattr(a, key, val)

        await db.commit()
        await db.refresh(a)
        sub = await db.get(Subject, a.subject_id)

        return AssignmentResponse(
            id=a.id,
            user_id=a.user_id,
            subject_id=a.subject_id,
            subject_name=sub.name if sub else "Assignment",
            subject_code=sub.code if sub else None,
            subject_color=sub.color if sub else "#8B5CF6",
            title=a.title,
            description=a.description,
            due_date=a.due_date,
            status=a.status,
            priority=a.priority,
            total_marks=a.total_marks,
            obtained_marks=a.obtained_marks,
            created_at=a.created_at,
            updated_at=a.updated_at,
        )

    @staticmethod
    async def delete_assignment(db: AsyncSession, user_id: str, asgn_id: str) -> Dict[str, Any]:
        stmt = select(Assignment).where(Assignment.id == asgn_id, Assignment.user_id == user_id)
        res = await db.execute(stmt)
        a = res.scalars().first()
        if not a:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found or unauthorized")

        await db.delete(a)
        await db.commit()
        return {"status": "SUCCESS", "message": "Assignment deleted"}

    # ----------------- Exams -----------------
    @staticmethod
    async def get_exams(db: AsyncSession, user_id: str) -> List[ExamResponse]:
        stmt = select(Exam).options(selectinload(Exam.subject)).where(
            Exam.user_id == user_id
        ).order_by(Exam.exam_date.asc())
        res = await db.execute(stmt)
        exams = res.scalars().all()
        return [
            ExamResponse(
                id=e.id,
                user_id=e.user_id,
                subject_id=e.subject_id,
                subject_name=e.subject.name if e.subject else "Exam",
                subject_code=e.subject.code if e.subject else None,
                subject_color=e.subject.color if e.subject else "#8B5CF6",
                title=e.title,
                exam_type=e.exam_type,
                exam_date=e.exam_date,
                start_time=e.start_time,
                end_time=e.end_time,
                venue=e.venue,
                syllabus_covered=e.syllabus_covered,
                max_marks=e.max_marks,
                obtained_marks=e.obtained_marks,
                created_at=e.created_at,
                updated_at=e.updated_at,
            )
            for e in exams
        ]

    @staticmethod
    async def get_exam(db: AsyncSession, user_id: str, exam_id: str) -> ExamResponse:
        stmt = select(Exam).options(selectinload(Exam.subject)).where(
            Exam.id == exam_id, Exam.user_id == user_id
        )
        res = await db.execute(stmt)
        e = res.scalars().first()
        if not e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found or unauthorized")

        return ExamResponse(
            id=e.id,
            user_id=e.user_id,
            subject_id=e.subject_id,
            subject_name=e.subject.name if e.subject else "Exam",
            subject_code=e.subject.code if e.subject else None,
            subject_color=e.subject.color if e.subject else "#8B5CF6",
            title=e.title,
            exam_type=e.exam_type,
            exam_date=e.exam_date,
            start_time=e.start_time,
            end_time=e.end_time,
            venue=e.venue,
            syllabus_covered=e.syllabus_covered,
            max_marks=e.max_marks,
            obtained_marks=e.obtained_marks,
            created_at=e.created_at,
            updated_at=e.updated_at,
        )

    @staticmethod
    async def create_exam(db: AsyncSession, user_id: str, exam_in: ExamCreate) -> ExamResponse:
        stmt_sub = select(Subject).where(Subject.id == exam_in.subject_id, Subject.user_id == user_id)
        res_sub = await db.execute(stmt_sub)
        sub = res_sub.scalars().first()
        if not sub:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found or unauthorized")

        exam = Exam(
            user_id=user_id,
            subject_id=exam_in.subject_id,
            title=exam_in.title,
            exam_type=exam_in.exam_type,
            exam_date=exam_in.exam_date,
            start_time=exam_in.start_time,
            end_time=exam_in.end_time,
            venue=exam_in.venue,
            syllabus_covered=exam_in.syllabus_covered,
            max_marks=exam_in.max_marks,
            obtained_marks=exam_in.obtained_marks,
        )
        db.add(exam)
        await db.commit()
        await db.refresh(exam)

        return ExamResponse(
            id=exam.id,
            user_id=exam.user_id,
            subject_id=exam.subject_id,
            subject_name=sub.name,
            subject_code=sub.code,
            subject_color=sub.color,
            title=exam.title,
            exam_type=exam.exam_type,
            exam_date=exam.exam_date,
            start_time=exam.start_time,
            end_time=exam.end_time,
            venue=exam.venue,
            syllabus_covered=exam.syllabus_covered,
            max_marks=exam.max_marks,
            obtained_marks=exam.obtained_marks,
            created_at=exam.created_at,
            updated_at=exam.updated_at,
        )

    @staticmethod
    async def update_exam(db: AsyncSession, user_id: str, exam_id: str, exam_in: ExamUpdate) -> ExamResponse:
        stmt = select(Exam).options(selectinload(Exam.subject)).where(
            Exam.id == exam_id, Exam.user_id == user_id
        )
        res = await db.execute(stmt)
        e = res.scalars().first()
        if not e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found or unauthorized")

        update_data = exam_in.model_dump(exclude_unset=True)
        if "subject_id" in update_data and update_data["subject_id"] != e.subject_id:
            stmt_sub = select(Subject).where(Subject.id == update_data["subject_id"], Subject.user_id == user_id)
            res_sub = await db.execute(stmt_sub)
            if not res_sub.scalars().first():
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="New subject not found or unauthorized")

        for key, val in update_data.items():
            setattr(e, key, val)

        await db.commit()
        await db.refresh(e)
        sub = await db.get(Subject, e.subject_id)

        return ExamResponse(
            id=e.id,
            user_id=e.user_id,
            subject_id=e.subject_id,
            subject_name=sub.name if sub else "Exam",
            subject_code=sub.code if sub else None,
            subject_color=sub.color if sub else "#8B5CF6",
            title=e.title,
            exam_type=e.exam_type,
            exam_date=e.exam_date,
            start_time=e.start_time,
            end_time=e.end_time,
            venue=e.venue,
            syllabus_covered=e.syllabus_covered,
            max_marks=e.max_marks,
            obtained_marks=e.obtained_marks,
            created_at=e.created_at,
            updated_at=e.updated_at,
        )

    @staticmethod
    async def delete_exam(db: AsyncSession, user_id: str, exam_id: str) -> Dict[str, Any]:
        stmt = select(Exam).where(Exam.id == exam_id, Exam.user_id == user_id)
        res = await db.execute(stmt)
        e = res.scalars().first()
        if not e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found or unauthorized")

        await db.delete(e)
        await db.commit()
        return {"status": "SUCCESS", "message": "Exam deleted"}

    # ----------------- Internal Marks -----------------
    @staticmethod
    async def get_internal_marks(db: AsyncSession, user_id: str, subject_id: Optional[str] = None) -> List[InternalMarkResponse]:
        query = select(InternalMark).options(selectinload(InternalMark.subject)).where(InternalMark.user_id == user_id)
        if subject_id:
            query = query.where(InternalMark.subject_id == subject_id)
        query = query.order_by(desc(InternalMark.assessment_date), desc(InternalMark.created_at))

        res = await db.execute(query)
        marks = res.scalars().all()
        return [
            InternalMarkResponse(
                id=m.id,
                user_id=m.user_id,
                subject_id=m.subject_id,
                subject_name=m.subject.name if m.subject else "Subject",
                subject_code=m.subject.code if m.subject else None,
                assessment_name=m.assessment_name,
                assessment_type=m.assessment_type,
                marks_obtained=m.marks_obtained,
                max_marks=m.max_marks,
                percentage=round((m.marks_obtained / m.max_marks) * 100.0, 1) if m.max_marks > 0 else 0.0,
                assessment_date=m.assessment_date,
                remarks=m.remarks,
                created_at=m.created_at,
                updated_at=m.updated_at,
            )
            for m in marks
        ]

    @staticmethod
    async def get_internal_mark(db: AsyncSession, user_id: str, mark_id: str) -> InternalMarkResponse:
        stmt = select(InternalMark).options(selectinload(InternalMark.subject)).where(
            InternalMark.id == mark_id, InternalMark.user_id == user_id
        )
        res = await db.execute(stmt)
        m = res.scalars().first()
        if not m:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Internal mark not found or unauthorized")

        return InternalMarkResponse(
            id=m.id,
            user_id=m.user_id,
            subject_id=m.subject_id,
            subject_name=m.subject.name if m.subject else "Subject",
            subject_code=m.subject.code if m.subject else None,
            assessment_name=m.assessment_name,
            assessment_type=m.assessment_type,
            marks_obtained=m.marks_obtained,
            max_marks=m.max_marks,
            percentage=round((m.marks_obtained / m.max_marks) * 100.0, 1) if m.max_marks > 0 else 0.0,
            assessment_date=m.assessment_date,
            remarks=m.remarks,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )

    @staticmethod
    async def create_internal_mark(db: AsyncSession, user_id: str, mark_in: InternalMarkCreate) -> InternalMarkResponse:
        if mark_in.max_marks <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Maximum marks must be greater than zero")
        if mark_in.marks_obtained < 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Marks obtained cannot be negative")

        stmt_sub = select(Subject).where(Subject.id == mark_in.subject_id, Subject.user_id == user_id)
        res_sub = await db.execute(stmt_sub)
        sub = res_sub.scalars().first()
        if not sub:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found or unauthorized")

        mark = InternalMark(
            user_id=user_id,
            subject_id=mark_in.subject_id,
            assessment_name=mark_in.assessment_name,
            assessment_type=mark_in.assessment_type,
            marks_obtained=mark_in.marks_obtained,
            max_marks=mark_in.max_marks,
            assessment_date=mark_in.assessment_date or date.today(),
            remarks=mark_in.remarks,
        )
        db.add(mark)
        await db.commit()
        await db.refresh(mark)

        return InternalMarkResponse(
            id=mark.id,
            user_id=mark.user_id,
            subject_id=mark.subject_id,
            subject_name=sub.name,
            subject_code=sub.code,
            assessment_name=mark.assessment_name,
            assessment_type=mark.assessment_type,
            marks_obtained=mark.marks_obtained,
            max_marks=mark.max_marks,
            percentage=round((mark.marks_obtained / mark.max_marks) * 100.0, 1) if mark.max_marks > 0 else 0.0,
            assessment_date=mark.assessment_date,
            remarks=mark.remarks,
            created_at=mark.created_at,
            updated_at=mark.updated_at,
        )

    @staticmethod
    async def update_internal_mark(db: AsyncSession, user_id: str, mark_id: str, mark_in: InternalMarkUpdate) -> InternalMarkResponse:
        stmt = select(InternalMark).options(selectinload(InternalMark.subject)).where(
            InternalMark.id == mark_id, InternalMark.user_id == user_id
        )
        res = await db.execute(stmt)
        m = res.scalars().first()
        if not m:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Internal mark not found or unauthorized")

        update_data = mark_in.model_dump(exclude_unset=True)
        new_max = update_data.get("max_marks", m.max_marks)
        new_obt = update_data.get("marks_obtained", m.marks_obtained)
        if new_max <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Maximum marks must be greater than zero")
        if new_obt < 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Marks obtained cannot be negative")

        for key, val in update_data.items():
            setattr(m, key, val)

        await db.commit()
        await db.refresh(m)
        sub = await db.get(Subject, m.subject_id)

        return InternalMarkResponse(
            id=m.id,
            user_id=m.user_id,
            subject_id=m.subject_id,
            subject_name=sub.name if sub else "Subject",
            subject_code=sub.code if sub else None,
            assessment_name=m.assessment_name,
            assessment_type=m.assessment_type,
            marks_obtained=m.marks_obtained,
            max_marks=m.max_marks,
            percentage=round((m.marks_obtained / m.max_marks) * 100.0, 1) if m.max_marks > 0 else 0.0,
            assessment_date=m.assessment_date,
            remarks=m.remarks,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )

    @staticmethod
    async def delete_internal_mark(db: AsyncSession, user_id: str, mark_id: str) -> Dict[str, Any]:
        stmt = select(InternalMark).where(InternalMark.id == mark_id, InternalMark.user_id == user_id)
        res = await db.execute(stmt)
        m = res.scalars().first()
        if not m:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Internal mark not found or unauthorized")

        await db.delete(m)
        await db.commit()
        return {"status": "SUCCESS", "message": "Internal mark deleted"}

    # ----------------- Projects -----------------
    @staticmethod
    async def get_projects(db: AsyncSession, user_id: str) -> List[AcademicProjectResponse]:
        stmt = select(AcademicProject).options(selectinload(AcademicProject.subject)).where(
            AcademicProject.user_id == user_id
        ).order_by(desc(AcademicProject.created_at))
        res = await db.execute(stmt)
        projects = res.scalars().all()
        return [
            AcademicProjectResponse(
                id=p.id,
                user_id=p.user_id,
                subject_id=p.subject_id,
                subject_name=p.subject.name if p.subject else None,
                title=p.title,
                description=p.description,
                status=p.status,
                deadline=p.deadline,
                repository_url=p.repository_url,
                documentation_url=p.documentation_url,
                created_at=p.created_at,
                updated_at=p.updated_at,
            )
            for p in projects
        ]

    @staticmethod
    async def get_project(db: AsyncSession, user_id: str, project_id: str) -> AcademicProjectResponse:
        stmt = select(AcademicProject).options(selectinload(AcademicProject.subject)).where(
            AcademicProject.id == project_id, AcademicProject.user_id == user_id
        )
        res = await db.execute(stmt)
        p = res.scalars().first()
        if not p:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Academic project not found or unauthorized")

        return AcademicProjectResponse(
            id=p.id,
            user_id=p.user_id,
            subject_id=p.subject_id,
            subject_name=p.subject.name if p.subject else None,
            title=p.title,
            description=p.description,
            status=p.status,
            deadline=p.deadline,
            repository_url=p.repository_url,
            documentation_url=p.documentation_url,
            created_at=p.created_at,
            updated_at=p.updated_at,
        )

    @staticmethod
    async def create_project(db: AsyncSession, user_id: str, proj_in: AcademicProjectCreate) -> AcademicProjectResponse:
        sub_name = None
        if proj_in.subject_id:
            stmt_sub = select(Subject).where(Subject.id == proj_in.subject_id, Subject.user_id == user_id)
            res_sub = await db.execute(stmt_sub)
            sub = res_sub.scalars().first()
            if not sub:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found or unauthorized")
            sub_name = sub.name

        proj = AcademicProject(
            user_id=user_id,
            subject_id=proj_in.subject_id,
            title=proj_in.title,
            description=proj_in.description,
            status=proj_in.status,
            deadline=proj_in.deadline,
            repository_url=proj_in.repository_url,
            documentation_url=proj_in.documentation_url,
        )
        db.add(proj)
        await db.commit()
        await db.refresh(proj)

        return AcademicProjectResponse(
            id=proj.id,
            user_id=proj.user_id,
            subject_id=proj.subject_id,
            subject_name=sub_name,
            title=proj.title,
            description=proj.description,
            status=proj.status,
            deadline=proj.deadline,
            repository_url=proj.repository_url,
            documentation_url=proj.documentation_url,
            created_at=proj.created_at,
            updated_at=proj.updated_at,
        )

    @staticmethod
    async def update_project(db: AsyncSession, user_id: str, project_id: str, proj_in: AcademicProjectUpdate) -> AcademicProjectResponse:
        stmt = select(AcademicProject).options(selectinload(AcademicProject.subject)).where(
            AcademicProject.id == project_id, AcademicProject.user_id == user_id
        )
        res = await db.execute(stmt)
        p = res.scalars().first()
        if not p:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Academic project not found or unauthorized")

        update_data = proj_in.model_dump(exclude_unset=True)
        if "subject_id" in update_data and update_data["subject_id"] is not None and update_data["subject_id"] != p.subject_id:
            stmt_sub = select(Subject).where(Subject.id == update_data["subject_id"], Subject.user_id == user_id)
            res_sub = await db.execute(stmt_sub)
            if not res_sub.scalars().first():
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="New subject not found or unauthorized")

        for key, val in update_data.items():
            setattr(p, key, val)

        await db.commit()
        await db.refresh(p)
        sub = await db.get(Subject, p.subject_id) if p.subject_id else None

        return AcademicProjectResponse(
            id=p.id,
            user_id=p.user_id,
            subject_id=p.subject_id,
            subject_name=sub.name if sub else None,
            title=p.title,
            description=p.description,
            status=p.status,
            deadline=p.deadline,
            repository_url=p.repository_url,
            documentation_url=p.documentation_url,
            created_at=p.created_at,
            updated_at=p.updated_at,
        )

    @staticmethod
    async def delete_project(db: AsyncSession, user_id: str, project_id: str) -> Dict[str, Any]:
        stmt = select(AcademicProject).where(AcademicProject.id == project_id, AcademicProject.user_id == user_id)
        res = await db.execute(stmt)
        p = res.scalars().first()
        if not p:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Academic project not found or unauthorized")

        await db.delete(p)
        await db.commit()
        return {"status": "SUCCESS", "message": "Academic project deleted"}

    # ----------------- Academic Notes -----------------
    @staticmethod
    async def get_notes(db: AsyncSession, user_id: str, subject_id: Optional[str] = None) -> List[AcademicNoteResponse]:
        query = select(AcademicNote).options(selectinload(AcademicNote.subject)).where(AcademicNote.user_id == user_id)
        if subject_id:
            query = query.where(AcademicNote.subject_id == subject_id)
        query = query.order_by(desc(AcademicNote.created_at))

        res = await db.execute(query)
        notes = res.scalars().all()
        return [
            AcademicNoteResponse(
                id=n.id,
                user_id=n.user_id,
                subject_id=n.subject_id,
                subject_name=n.subject.name if n.subject else "Subject",
                title=n.title,
                description=n.description,
                tags=n.tags,
                file_url=n.file_url,
                file_name=n.file_name,
                created_at=n.created_at,
                updated_at=n.updated_at,
            )
            for n in notes
        ]

    @staticmethod
    async def get_note(db: AsyncSession, user_id: str, note_id: str) -> AcademicNoteResponse:
        stmt = select(AcademicNote).options(selectinload(AcademicNote.subject)).where(
            AcademicNote.id == note_id, AcademicNote.user_id == user_id
        )
        res = await db.execute(stmt)
        n = res.scalars().first()
        if not n:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Academic note not found or unauthorized")

        return AcademicNoteResponse(
            id=n.id,
            user_id=n.user_id,
            subject_id=n.subject_id,
            subject_name=n.subject.name if n.subject else "Subject",
            title=n.title,
            description=n.description,
            tags=n.tags,
            file_url=n.file_url,
            file_name=n.file_name,
            created_at=n.created_at,
            updated_at=n.updated_at,
        )

    @staticmethod
    async def create_note(db: AsyncSession, user_id: str, note_in: AcademicNoteCreate) -> AcademicNoteResponse:
        stmt_sub = select(Subject).where(Subject.id == note_in.subject_id, Subject.user_id == user_id)
        res_sub = await db.execute(stmt_sub)
        sub = res_sub.scalars().first()
        if not sub:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found or unauthorized")

        note = AcademicNote(
            user_id=user_id,
            subject_id=note_in.subject_id,
            title=note_in.title,
            description=note_in.description,
            tags=note_in.tags,
            file_url=note_in.file_url,
            file_name=note_in.file_name,
        )
        db.add(note)
        await db.commit()
        await db.refresh(note)

        return AcademicNoteResponse(
            id=note.id,
            user_id=note.user_id,
            subject_id=note.subject_id,
            subject_name=sub.name,
            title=note.title,
            description=note.description,
            tags=note.tags,
            file_url=note.file_url,
            file_name=note.file_name,
            created_at=note.created_at,
            updated_at=note.updated_at,
        )

    @staticmethod
    async def update_note(db: AsyncSession, user_id: str, note_id: str, note_in: AcademicNoteUpdate) -> AcademicNoteResponse:
        stmt = select(AcademicNote).options(selectinload(AcademicNote.subject)).where(
            AcademicNote.id == note_id, AcademicNote.user_id == user_id
        )
        res = await db.execute(stmt)
        n = res.scalars().first()
        if not n:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Academic note not found or unauthorized")

        update_data = note_in.model_dump(exclude_unset=True)
        if "subject_id" in update_data and update_data["subject_id"] != n.subject_id:
            stmt_sub = select(Subject).where(Subject.id == update_data["subject_id"], Subject.user_id == user_id)
            res_sub = await db.execute(stmt_sub)
            if not res_sub.scalars().first():
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="New subject not found or unauthorized")

        for key, val in update_data.items():
            setattr(n, key, val)

        await db.commit()
        await db.refresh(n)
        sub = await db.get(Subject, n.subject_id)

        return AcademicNoteResponse(
            id=n.id,
            user_id=n.user_id,
            subject_id=n.subject_id,
            subject_name=sub.name if sub else "Subject",
            title=n.title,
            description=n.description,
            tags=n.tags,
            file_url=n.file_url,
            file_name=n.file_name,
            created_at=n.created_at,
            updated_at=n.updated_at,
        )

    @staticmethod
    async def delete_note(db: AsyncSession, user_id: str, note_id: str) -> Dict[str, Any]:
        stmt = select(AcademicNote).where(AcademicNote.id == note_id, AcademicNote.user_id == user_id)
        res = await db.execute(stmt)
        n = res.scalars().first()
        if not n:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Academic note not found or unauthorized")

        await db.delete(n)
        await db.commit()
        return {"status": "SUCCESS", "message": "Academic note deleted"}

    # ----------------- Dashboard & Summaries -----------------
    @staticmethod
    async def get_academic_dashboard(db: AsyncSession, user_id: str) -> AcademicDashboardResponse:
        profile = await AcademicService.get_academic_profile(db, user_id)
        subjects = await AcademicService.get_subjects(db, user_id)
        assignments = await AcademicService.get_assignments(db, user_id)
        exams = await AcademicService.get_exams(db, user_id)
        marks = await AcademicService.get_internal_marks(db, user_id)
        projects = await AcademicService.get_projects(db, user_id)
        notes = await AcademicService.get_notes(db, user_id)

        tot_cls = sum(s.total_classes for s in subjects)
        att_cls = sum(s.attended_classes for s in subjects)
        overall_pct = round((att_cls / tot_cls) * 100.0, 1) if tot_cls > 0 else 100.0

        low_att = [s for s in subjects if s.current_percentage < s.target_attendance and s.total_classes > 0]
        pending_asgns = [a for a in assignments if a.status in (AssignmentStatus.PENDING, AssignmentStatus.IN_PROGRESS)]
        
        now = datetime.now(timezone.utc)
        upcoming_asgns = [
            a for a in pending_asgns
            if a.due_date.replace(tzinfo=timezone.utc) >= now or a.due_date >= datetime.now()
        ][:5]
        
        upcoming_exms = [
            e for e in exams
            if e.exam_date.replace(tzinfo=timezone.utc) >= now or e.exam_date >= datetime.now()
        ][:5]

        return AcademicDashboardResponse(
            profile=profile,
            current_semester=profile.current_semester if profile else None,
            subjects_count=len(subjects),
            attendance=AcademicAttendanceGlance(
                overall_percentage=overall_pct,
                total_classes=tot_cls,
                attended_classes=att_cls,
                below_target_count=len(low_att),
            ),
            low_attendance_subjects=low_att,
            upcoming_assignments=upcoming_asgns if upcoming_asgns else pending_asgns[:5],
            upcoming_exams=upcoming_exms if upcoming_exms else exams[:5],
            pending_assignments_count=len(pending_asgns),
            recent_marks=marks[:5],
            projects_count=len(projects),
            notes_count=len(notes),
        )

    # ----------------- AI Context Retrieval (Structured & Grounded) -----------------
    @staticmethod
    async def get_academic_context(db: AsyncSession, user_id: str) -> Dict[str, Any]:
        """Provides verified academic telemetry for the AI router without hallucinations."""
        summary = await AcademicService.get_attendance_summary(db, user_id)
        assignments = await AcademicService.get_assignments(db, user_id, status_filter=AssignmentStatus.PENDING)
        exams = await AcademicService.get_exams(db, user_id)
        profile = await AcademicService.get_academic_profile(db, user_id)

        return {
            "source": "academics",
            "profile": profile.model_dump() if profile else None,
            "overall_attendance_percent": summary.overall_percentage,
            "total_classes": summary.total_classes,
            "attended_classes": summary.attended_classes,
            "below_target_subjects_count": summary.below_target_count,
            "subjects": [
                {
                    "name": s.name,
                    "code": s.code,
                    "attendance": {
                        "attended": s.attended_classes,
                        "total": s.total_classes,
                        "percentage": s.current_percentage,
                        "target": s.target_attendance,
                        "bunkable": s.bunkable_classes,
                        "needed": s.needed_classes,
                        "status": s.status_indicator,
                    }
                }
                for s in summary.subjects
            ],
            "pending_assignments": [
                {
                    "title": a.title,
                    "subject": a.subject_name,
                    "due_date": a.due_date.isoformat(),
                    "priority": a.priority.value if hasattr(a.priority, "value") else str(a.priority),
                }
                for a in assignments[:5]
            ],
            "upcoming_exams": [
                {
                    "title": e.title,
                    "subject": e.subject_name,
                    "exam_date": e.exam_date.isoformat(),
                    "venue": e.venue,
                }
                for e in exams[:5]
            ]
        }
