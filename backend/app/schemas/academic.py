from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime
from app.models.academic import AttendanceStatus, AssignmentStatus

# Subject Schemas
class SubjectCreate(BaseModel):
    name: str
    code: Optional[str] = None
    professor: Optional[str] = None
    color: Optional[str] = "#8B5CF6"
    min_attendance_percent: Optional[float] = 75.0
    target_attendance_percent: Optional[float] = 85.0

class SubjectUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    professor: Optional[str] = None
    color: Optional[str] = None
    min_attendance_percent: Optional[float] = None
    target_attendance_percent: Optional[float] = None

class SubjectResponse(BaseModel):
    id: str
    user_id: str
    name: str
    code: Optional[str] = None
    professor: Optional[str] = None
    color: str
    min_attendance_percent: float
    target_attendance_percent: float
    created_at: datetime

    # Calculated stats
    total_classes: Optional[int] = 0
    attended_classes: Optional[int] = 0
    current_percentage: Optional[float] = 0.0
    status_indicator: Optional[str] = "ON_TRACK" # SAFE, ON_TRACK, AT_RISK, CRITICAL
    bunkable_classes: Optional[int] = 0
    needed_classes: Optional[int] = 0

    class Config:
        from_attributes = True

# Attendance Schemas
class AttendanceMarkRequest(BaseModel):
    subject_id: str
    date: date
    status: AttendanceStatus
    notes: Optional[str] = None

class AttendanceRecordResponse(BaseModel):
    id: str
    user_id: str
    subject_id: str
    subject_name: Optional[str] = None
    date: date
    status: AttendanceStatus
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Timetable Schemas
class TimetableSlotCreate(BaseModel):
    subject_id: str
    day_of_week: int # 0=Mon, 6=Sun
    start_time: str # "09:00"
    end_time: str # "10:00"
    room: Optional[str] = None

class TimetableSlotResponse(BaseModel):
    id: str
    user_id: str
    subject_id: str
    subject_name: Optional[str] = None
    subject_code: Optional[str] = None
    subject_color: Optional[str] = None
    day_of_week: int
    start_time: str
    end_time: str
    room: Optional[str] = None

    class Config:
        from_attributes = True

# Assignment Schemas
class AssignmentCreate(BaseModel):
    subject_id: str
    title: str
    description: Optional[str] = None
    due_date: datetime
    total_marks: Optional[float] = None

class AssignmentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    status: Optional[AssignmentStatus] = None
    obtained_marks: Optional[float] = None
    total_marks: Optional[float] = None

class AssignmentResponse(BaseModel):
    id: str
    user_id: str
    subject_id: str
    subject_name: Optional[str] = None
    subject_color: Optional[str] = None
    title: str
    description: Optional[str] = None
    due_date: datetime
    status: AssignmentStatus
    total_marks: Optional[float] = None
    obtained_marks: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Exam Schemas
class ExamCreate(BaseModel):
    subject_id: str
    title: str
    exam_date: datetime
    location: Optional[str] = None
    syllabus_covered: Optional[str] = None
    total_marks: Optional[float] = 100.0

class ExamResponse(BaseModel):
    id: str
    user_id: str
    subject_id: str
    subject_name: Optional[str] = None
    subject_color: Optional[str] = None
    title: str
    exam_date: datetime
    location: Optional[str] = None
    syllabus_covered: Optional[str] = None
    total_marks: Optional[float] = None
    obtained_marks: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Academic Note Schemas
class AcademicNoteCreate(BaseModel):
    subject_id: str
    title: str
    content: str
    tags: Optional[str] = None

class AcademicNoteResponse(BaseModel):
    id: str
    user_id: str
    subject_id: str
    subject_name: Optional[str] = None
    title: str
    content: str
    tags: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
