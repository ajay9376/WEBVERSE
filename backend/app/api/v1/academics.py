from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import date

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.academic import AttendanceStatus, AssignmentStatus
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
)
from app.services.academic_service import AcademicService

router = APIRouter(prefix="/academics", tags=["Academics / StudentOS"])

# ==================== ACADEMIC PROFILE ====================
@router.get("/profile", response_model=Optional[AcademicProfileResponse])
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await AcademicService.get_academic_profile(db, current_user.id)

@router.put("/profile", response_model=AcademicProfileResponse)
async def update_profile(
    profile_in: AcademicProfileCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await AcademicService.upsert_academic_profile(db, current_user.id, profile_in)


# ==================== SUBJECTS ====================
@router.get("/subjects", response_model=List[SubjectResponse])
async def get_subjects(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await AcademicService.get_subjects(db, current_user.id)

@router.post("/subjects", response_model=SubjectResponse, status_code=status.HTTP_201_CREATED)
async def create_subject(
    sub_in: SubjectCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await AcademicService.create_subject(db, current_user.id, sub_in)

@router.get("/subjects/{subject_id}", response_model=SubjectResponse)
async def get_subject(
    subject_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await AcademicService.get_subject(db, current_user.id, subject_id)

@router.put("/subjects/{subject_id}", response_model=SubjectResponse)
async def update_subject(
    subject_id: str,
    sub_in: SubjectUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await AcademicService.update_subject(db, current_user.id, subject_id, sub_in)

@router.delete("/subjects/{subject_id}")
async def delete_subject(
    subject_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await AcademicService.delete_subject(db, current_user.id, subject_id)


# ==================== ATTENDANCE ====================
@router.post("/attendance/mark", response_model=AttendanceRecordResponse, status_code=status.HTTP_201_CREATED)
async def mark_attendance(
    att_in: AttendanceRecordCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await AcademicService.mark_attendance(db, current_user.id, att_in)

@router.get("/subjects/{subject_id}/attendance", response_model=List[AttendanceRecordResponse])
async def get_subject_attendance_history(
    subject_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await AcademicService.get_attendance_history(db, current_user.id, subject_id)

@router.post("/subjects/{subject_id}/attendance", response_model=AttendanceRecordResponse, status_code=status.HTTP_201_CREATED)
async def log_subject_attendance(
    subject_id: str,
    att_in: AttendanceRecordCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    att_in.subject_id = subject_id
    return await AcademicService.mark_attendance(db, current_user.id, att_in)

@router.get("/attendance/summary", response_model=AttendanceSummaryResponse)
async def get_attendance_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await AcademicService.get_attendance_summary(db, current_user.id)

@router.get("/attendance/{subject_id}/projection", response_model=AttendanceProjectionResponse)
async def get_attendance_projection(
    subject_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await AcademicService.get_subject_projection(db, current_user.id, subject_id)


# ==================== TIMETABLE ====================
@router.get("/timetable", response_model=List[TimetableSlotResponse])
async def get_timetable(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await AcademicService.get_timetable(db, current_user.id)

@router.post("/timetable", response_model=TimetableSlotResponse, status_code=status.HTTP_201_CREATED)
async def create_timetable_slot(
    slot_in: TimetableSlotCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await AcademicService.create_timetable_slot(db, current_user.id, slot_in)

@router.put("/timetable/{slot_id}", response_model=TimetableSlotResponse)
async def update_timetable_slot(
    slot_id: str,
    slot_in: TimetableSlotUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await AcademicService.update_timetable_slot(db, current_user.id, slot_id, slot_in)

@router.delete("/timetable/{slot_id}")
async def delete_timetable_slot(
    slot_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await AcademicService.delete_timetable_slot(db, current_user.id, slot_id)


# ==================== ASSIGNMENTS ====================
@router.get("/assignments", response_model=List[AssignmentResponse])
async def get_assignments(
    status_filter: Optional[AssignmentStatus] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await AcademicService.get_assignments(db, current_user.id, status_filter)

@router.post("/assignments", response_model=AssignmentResponse, status_code=status.HTTP_201_CREATED)
async def create_assignment(
    asgn_in: AssignmentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await AcademicService.create_assignment(db, current_user.id, asgn_in)

@router.get("/assignments/{asgn_id}", response_model=AssignmentResponse)
async def get_assignment(
    asgn_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await AcademicService.get_assignment(db, current_user.id, asgn_id)

@router.put("/assignments/{asgn_id}", response_model=AssignmentResponse)
async def update_assignment(
    asgn_id: str,
    asgn_in: AssignmentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await AcademicService.update_assignment(db, current_user.id, asgn_id, asgn_in)

@router.delete("/assignments/{asgn_id}")
async def delete_assignment(
    asgn_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await AcademicService.delete_assignment(db, current_user.id, asgn_id)


# ==================== EXAMS ====================
@router.get("/exams", response_model=List[ExamResponse])
async def get_exams(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await AcademicService.get_exams(db, current_user.id)

@router.post("/exams", response_model=ExamResponse, status_code=status.HTTP_201_CREATED)
async def create_exam(
    exam_in: ExamCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await AcademicService.create_exam(db, current_user.id, exam_in)

@router.get("/exams/{exam_id}", response_model=ExamResponse)
async def get_exam(
    exam_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await AcademicService.get_exam(db, current_user.id, exam_id)

@router.put("/exams/{exam_id}", response_model=ExamResponse)
async def update_exam(
    exam_id: str,
    exam_in: ExamUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await AcademicService.update_exam(db, current_user.id, exam_id, exam_in)

@router.delete("/exams/{exam_id}")
async def delete_exam(
    exam_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await AcademicService.delete_exam(db, current_user.id, exam_id)


# ==================== INTERNAL MARKS ====================
@router.get("/marks", response_model=List[InternalMarkResponse])
async def get_internal_marks(
    subject_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await AcademicService.get_internal_marks(db, current_user.id, subject_id)

@router.post("/marks", response_model=InternalMarkResponse, status_code=status.HTTP_201_CREATED)
async def create_internal_mark(
    mark_in: InternalMarkCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await AcademicService.create_internal_mark(db, current_user.id, mark_in)

@router.get("/marks/{mark_id}", response_model=InternalMarkResponse)
async def get_internal_mark(
    mark_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await AcademicService.get_internal_mark(db, current_user.id, mark_id)

@router.put("/marks/{mark_id}", response_model=InternalMarkResponse)
async def update_internal_mark(
    mark_id: str,
    mark_in: InternalMarkUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await AcademicService.update_internal_mark(db, current_user.id, mark_id, mark_in)

@router.delete("/marks/{mark_id}")
async def delete_internal_mark(
    mark_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await AcademicService.delete_internal_mark(db, current_user.id, mark_id)


# ==================== PROJECTS ====================
@router.get("/projects", response_model=List[AcademicProjectResponse])
async def get_projects(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await AcademicService.get_projects(db, current_user.id)

@router.post("/projects", response_model=AcademicProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    proj_in: AcademicProjectCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await AcademicService.create_project(db, current_user.id, proj_in)

@router.get("/projects/{project_id}", response_model=AcademicProjectResponse)
async def get_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await AcademicService.get_project(db, current_user.id, project_id)

@router.put("/projects/{project_id}", response_model=AcademicProjectResponse)
async def update_project(
    project_id: str,
    proj_in: AcademicProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await AcademicService.update_project(db, current_user.id, project_id, proj_in)

@router.delete("/projects/{project_id}")
async def delete_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await AcademicService.delete_project(db, current_user.id, project_id)


# ==================== NOTES ====================
@router.get("/notes", response_model=List[AcademicNoteResponse])
async def get_notes(
    subject_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await AcademicService.get_notes(db, current_user.id, subject_id)

@router.post("/notes", response_model=AcademicNoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(
    note_in: AcademicNoteCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await AcademicService.create_note(db, current_user.id, note_in)

@router.get("/notes/{note_id}", response_model=AcademicNoteResponse)
async def get_note(
    note_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await AcademicService.get_note(db, current_user.id, note_id)

@router.put("/notes/{note_id}", response_model=AcademicNoteResponse)
async def update_note(
    note_id: str,
    note_in: AcademicNoteUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await AcademicService.update_note(db, current_user.id, note_id, note_in)

@router.delete("/notes/{note_id}")
async def delete_note(
    note_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await AcademicService.delete_note(db, current_user.id, note_id)


# ==================== ACADEMIC DASHBOARD ====================
@router.get("/dashboard", response_model=AcademicDashboardResponse)
async def get_academic_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await AcademicService.get_academic_dashboard(db, current_user.id)
