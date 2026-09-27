from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from app.models.academic import (
    AttendanceStatus,
    AssignmentStatus,
    AssignmentPriority,
    ExamType,
    AssessmentType,
    ProjectStatus,
)

# ----------------- Academic Profile Schemas -----------------
class AcademicProfileBase(BaseModel):
    college_name: Optional[str] = None
    university: Optional[str] = None
    degree: Optional[str] = None
    branch: Optional[str] = None
    current_year: Optional[int] = None
    current_semester: Optional[int] = None
    roll_number: Optional[str] = None
    academic_start_year: Optional[int] = None

class AcademicProfileCreate(AcademicProfileBase):
    pass

class AcademicProfileUpdate(AcademicProfileBase):
    pass

class AcademicProfileResponse(AcademicProfileBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ----------------- Subject Schemas -----------------
class SubjectBase(BaseModel):
    name: str
    code: Optional[str] = None
    credits: Optional[int] = 3
    semester: Optional[int] = None
    faculty_name: Optional[str] = None
    color: Optional[str] = "#8B5CF6"
    total_classes: Optional[int] = 0
    attended_classes: Optional[int] = 0
    target_attendance: Optional[float] = 80.0
    min_attendance: Optional[float] = 75.0

class SubjectCreate(SubjectBase):
    pass

class SubjectUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    credits: Optional[int] = None
    semester: Optional[int] = None
    faculty_name: Optional[str] = None
    color: Optional[str] = None
    total_classes: Optional[int] = None
    attended_classes: Optional[int] = None
    target_attendance: Optional[float] = None
    min_attendance: Optional[float] = None

class SubjectResponse(BaseModel):
    id: str
    user_id: str
    name: str
    code: Optional[str] = None
    credits: Optional[int] = 3
    semester: Optional[int] = None
    faculty_name: Optional[str] = None
    color: str = "#8B5CF6"
    total_classes: int = 0
    attended_classes: int = 0
    target_attendance: float = 80.0
    min_attendance: float = 75.0
    created_at: datetime
    updated_at: datetime

    # Calculated stats
    current_percentage: float = 0.0
    status_indicator: str = "SAFE"  # SAFE, ON_TRACK, WARNING, CRITICAL, NO_DATA
    bunkable_classes: int = 0
    needed_classes: int = 0

    model_config = ConfigDict(from_attributes=True)


# ----------------- Attendance Schemas -----------------
class AttendanceRecordCreate(BaseModel):
    subject_id: str
    date: date
    status: AttendanceStatus = AttendanceStatus.PRESENT
    remarks: Optional[str] = None

class AttendanceRecordResponse(BaseModel):
    id: str
    user_id: str
    subject_id: str
    subject_name: Optional[str] = None
    subject_code: Optional[str] = None
    date: date
    status: AttendanceStatus
    remarks: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class AttendanceSummaryResponse(BaseModel):
    overall_percentage: float
    total_classes: int
    attended_classes: int
    below_target_count: int
    subjects_count: int
    subjects: List[SubjectResponse]

class AttendanceProjectionResponse(BaseModel):
    subject_id: str
    subject_name: str
    subject_code: Optional[str] = None
    total_classes: int
    attended_classes: int
    current_percentage: float
    target_percentage: float
    min_percentage: float
    status_indicator: str
    classes_needed_for_target: int
    classes_safe_to_bunk: int
    if_attend_next_1: float
    if_miss_next_1: float
    if_attend_next_3: float
    if_miss_next_3: float
    if_attend_next_5: float
    if_miss_next_5: float


# ----------------- Timetable Schemas -----------------
class TimetableSlotBase(BaseModel):
    subject_id: str
    day_of_week: int  # 0=Monday, ..., 5=Saturday, 6=Sunday
    start_time: str   # "09:00"
    end_time: str     # "10:00"
    room: Optional[str] = None
    faculty_name: Optional[str] = None

class TimetableSlotCreate(TimetableSlotBase):
    pass

class TimetableSlotUpdate(BaseModel):
    subject_id: Optional[str] = None
    day_of_week: Optional[int] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    room: Optional[str] = None
    faculty_name: Optional[str] = None

class TimetableSlotResponse(TimetableSlotBase):
    id: str
    user_id: str
    subject_name: Optional[str] = None
    subject_code: Optional[str] = None
    subject_color: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ----------------- Assignment Schemas -----------------
class AssignmentBase(BaseModel):
    subject_id: str
    title: str
    description: Optional[str] = None
    due_date: datetime
    status: AssignmentStatus = AssignmentStatus.PENDING
    priority: AssignmentPriority = AssignmentPriority.MEDIUM
    total_marks: Optional[float] = None
    obtained_marks: Optional[float] = None

class AssignmentCreate(AssignmentBase):
    pass

class AssignmentUpdate(BaseModel):
    subject_id: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    status: Optional[AssignmentStatus] = None
    priority: Optional[AssignmentPriority] = None
    total_marks: Optional[float] = None
    obtained_marks: Optional[float] = None

class AssignmentResponse(AssignmentBase):
    id: str
    user_id: str
    subject_name: Optional[str] = None
    subject_code: Optional[str] = None
    subject_color: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ----------------- Exam Schemas -----------------
class ExamBase(BaseModel):
    subject_id: str
    title: str
    exam_type: ExamType = ExamType.MIDTERM
    exam_date: datetime
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    venue: Optional[str] = None
    syllabus_covered: Optional[str] = None
    max_marks: Optional[float] = 100.0
    obtained_marks: Optional[float] = None

class ExamCreate(ExamBase):
    pass

class ExamUpdate(BaseModel):
    subject_id: Optional[str] = None
    title: Optional[str] = None
    exam_type: Optional[ExamType] = None
    exam_date: Optional[datetime] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    venue: Optional[str] = None
    syllabus_covered: Optional[str] = None
    max_marks: Optional[float] = None
    obtained_marks: Optional[float] = None

class ExamResponse(ExamBase):
    id: str
    user_id: str
    subject_name: Optional[str] = None
    subject_code: Optional[str] = None
    subject_color: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ----------------- Internal Mark Schemas -----------------
class InternalMarkBase(BaseModel):
    subject_id: str
    assessment_name: str
    assessment_type: AssessmentType = AssessmentType.QUIZ
    marks_obtained: float
    max_marks: float
    assessment_date: Optional[date] = None
    remarks: Optional[str] = None

class InternalMarkCreate(InternalMarkBase):
    pass

class InternalMarkUpdate(BaseModel):
    subject_id: Optional[str] = None
    assessment_name: Optional[str] = None
    assessment_type: Optional[AssessmentType] = None
    marks_obtained: Optional[float] = None
    max_marks: Optional[float] = None
    assessment_date: Optional[date] = None
    remarks: Optional[str] = None

class InternalMarkResponse(InternalMarkBase):
    id: str
    user_id: str
    subject_name: Optional[str] = None
    subject_code: Optional[str] = None
    percentage: float = 0.0
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ----------------- Project Schemas -----------------
class AcademicProjectBase(BaseModel):
    subject_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    status: ProjectStatus = ProjectStatus.IN_PROGRESS
    deadline: Optional[datetime] = None
    repository_url: Optional[str] = None
    documentation_url: Optional[str] = None

class AcademicProjectCreate(AcademicProjectBase):
    pass

class AcademicProjectUpdate(BaseModel):
    subject_id: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None
    deadline: Optional[datetime] = None
    repository_url: Optional[str] = None
    documentation_url: Optional[str] = None

class AcademicProjectResponse(AcademicProjectBase):
    id: str
    user_id: str
    subject_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ----------------- Note Schemas -----------------
class AcademicNoteBase(BaseModel):
    subject_id: str
    title: str
    description: Optional[str] = None
    tags: Optional[str] = None
    file_url: Optional[str] = None
    file_name: Optional[str] = None

class AcademicNoteCreate(AcademicNoteBase):
    pass

class AcademicNoteUpdate(BaseModel):
    subject_id: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[str] = None
    file_url: Optional[str] = None
    file_name: Optional[str] = None

class AcademicNoteResponse(AcademicNoteBase):
    id: str
    user_id: str
    subject_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ----------------- Academic Dashboard / Glance Schemas -----------------
class AcademicAttendanceGlance(BaseModel):
    overall_percentage: float
    total_classes: int
    attended_classes: int
    below_target_count: int

class AcademicDashboardResponse(BaseModel):
    profile: Optional[AcademicProfileResponse] = None
    current_semester: Optional[int] = None
    subjects_count: int = 0
    attendance: AcademicAttendanceGlance
    low_attendance_subjects: List[SubjectResponse] = []
    upcoming_assignments: List[AssignmentResponse] = []
    upcoming_exams: List[ExamResponse] = []
    pending_assignments_count: int = 0
    recent_marks: List[InternalMarkResponse] = []
    projects_count: int = 0
    notes_count: int = 0
