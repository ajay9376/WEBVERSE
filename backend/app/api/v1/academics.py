from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from datetime import date
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.academic import Subject, AttendanceRecord, TimetableSlot, Assignment, Exam, AcademicNote, AttendanceStatus
from app.schemas.academic import (
    SubjectCreate, SubjectResponse, AttendanceMarkRequest, AttendanceRecordResponse,
    TimetableSlotCreate, TimetableSlotResponse, AssignmentCreate, AssignmentResponse,
    ExamCreate, ExamResponse, AcademicNoteCreate, AcademicNoteResponse
)
from app.services.academic_service import AcademicService

router = APIRouter(prefix="/academics", tags=["Academics"])

# --- Subjects ---
@router.get("/subjects", response_model=List[SubjectResponse])
async def get_subjects(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await AcademicService.get_all_subjects_with_stats(db, current_user.id)

@router.post("/subjects", response_model=SubjectResponse)
async def create_subject(sub_in: SubjectCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    sub = Subject(
        user_id=current_user.id,
        name=sub_in.name,
        code=sub_in.code,
        professor=sub_in.professor,
        color=sub_in.color or "#8B5CF6",
        min_attendance_percent=sub_in.min_attendance_percent or 75.0,
        target_attendance_percent=sub_in.target_attendance_percent or 85.0
    )
    db.add(sub)
    await db.commit()
    await db.refresh(sub)
    return await AcademicService.get_subject_with_stats(db, sub)

# --- Attendance ---
@router.post("/attendance/mark", response_model=AttendanceRecordResponse)
async def mark_attendance(att_in: AttendanceMarkRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    rec = AttendanceRecord(
        user_id=current_user.id,
        subject_id=att_in.subject_id,
        date=att_in.date,
        status=att_in.status,
        notes=att_in.notes
    )
    db.add(rec)
    await db.commit()
    await db.refresh(rec)
    return rec

@router.get("/attendance/history/{subject_id}", response_model=List[AttendanceRecordResponse])
async def get_attendance_history(subject_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    stmt = select(AttendanceRecord).where(
        AttendanceRecord.user_id == current_user.id,
        AttendanceRecord.subject_id == subject_id
    ).order_by(AttendanceRecord.date.desc())
    res = await db.execute(stmt)
    return res.scalars().all()

from sqlalchemy.orm import selectinload

# --- Timetable ---
@router.get("/timetable", response_model=List[TimetableSlotResponse])
async def get_timetable(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    stmt = select(TimetableSlot).options(selectinload(TimetableSlot.subject)).where(TimetableSlot.user_id == current_user.id).order_by(TimetableSlot.day_of_week, TimetableSlot.start_time)
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
            room=s.room
        )
        for s in slots
    ]

@router.post("/timetable", response_model=TimetableSlotResponse)
async def create_timetable_slot(slot_in: TimetableSlotCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    slot = TimetableSlot(
        user_id=current_user.id,
        subject_id=slot_in.subject_id,
        day_of_week=slot_in.day_of_week,
        start_time=slot_in.start_time,
        end_time=slot_in.end_time,
        room=slot_in.room
    )
    db.add(slot)
    await db.commit()
    await db.refresh(slot)
    
    sub = await db.get(Subject, slot_in.subject_id)
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
        room=slot.room
    )

# --- Assignments & Exams ---
@router.get("/assignments", response_model=List[AssignmentResponse])
async def get_assignments(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    stmt = select(Assignment).options(selectinload(Assignment.subject)).where(Assignment.user_id == current_user.id).order_by(Assignment.due_date.asc())
    res = await db.execute(stmt)
    asgns = res.scalars().all()
    return [
        AssignmentResponse(
            id=a.id,
            user_id=a.user_id,
            subject_id=a.subject_id,
            subject_name=a.subject.name if a.subject else "Assignment",
            subject_color=a.subject.color if a.subject else "#8B5CF6",
            title=a.title,
            description=a.description,
            due_date=a.due_date,
            status=a.status,
            total_marks=a.total_marks,
            obtained_marks=a.obtained_marks,
            created_at=a.created_at
        )
        for a in asgns
    ]

@router.post("/assignments", response_model=AssignmentResponse)
async def create_assignment(asgn_in: AssignmentCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    asgn = Assignment(
        user_id=current_user.id,
        subject_id=asgn_in.subject_id,
        title=asgn_in.title,
        description=asgn_in.description,
        due_date=asgn_in.due_date,
        total_marks=asgn_in.total_marks
    )
    db.add(asgn)
    await db.commit()
    await db.refresh(asgn)
    sub = await db.get(Subject, asgn_in.subject_id)
    return AssignmentResponse(
        id=asgn.id,
        user_id=asgn.user_id,
        subject_id=asgn.subject_id,
        subject_name=sub.name if sub else "Assignment",
        subject_color=sub.color if sub else "#8B5CF6",
        title=asgn.title,
        description=asgn.description,
        due_date=asgn.due_date,
        status=asgn.status,
        total_marks=asgn.total_marks,
        obtained_marks=asgn.obtained_marks,
        created_at=asgn.created_at
    )

@router.get("/exams", response_model=List[ExamResponse])
async def get_exams(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    stmt = select(Exam).options(selectinload(Exam.subject)).where(Exam.user_id == current_user.id).order_by(Exam.exam_date.asc())
    res = await db.execute(stmt)
    exams = res.scalars().all()
    return [
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
        for e in exams
    ]

@router.post("/exams", response_model=ExamResponse)
async def create_exam(exam_in: ExamCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    exam = Exam(
        user_id=current_user.id,
        subject_id=exam_in.subject_id,
        title=exam_in.title,
        exam_date=exam_in.exam_date,
        location=exam_in.location,
        syllabus_covered=exam_in.syllabus_covered,
        total_marks=exam_in.total_marks
    )
    db.add(exam)
    await db.commit()
    await db.refresh(exam)
    sub = await db.get(Subject, exam_in.subject_id)
    return ExamResponse(
        id=exam.id,
        user_id=exam.user_id,
        subject_id=exam.subject_id,
        subject_name=sub.name if sub else "Exam",
        subject_color=sub.color if sub else "#8B5CF6",
        title=exam.title,
        exam_date=exam.exam_date,
        location=exam.location,
        syllabus_covered=exam.syllabus_covered,
        total_marks=exam.total_marks,
        obtained_marks=exam.obtained_marks,
        created_at=exam.created_at
    )
