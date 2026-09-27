from sqlalchemy import Column, String, Float, Integer, Date, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum
from app.models.base import BaseModel

class AttendanceStatus(str, enum.Enum):
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    DUTY = "DUTY"
    EXCUSED = "EXCUSED"

class AssignmentStatus(str, enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"

class AssignmentPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class ExamType(str, enum.Enum):
    QUIZ = "QUIZ"
    INTERNAL = "INTERNAL"
    MIDTERM = "MIDTERM"
    END_SEM = "END_SEM"
    LAB = "LAB"
    OTHER = "OTHER"

class AssessmentType(str, enum.Enum):
    QUIZ = "QUIZ"
    ASSIGNMENT = "ASSIGNMENT"
    MIDTERM = "MIDTERM"
    LAB = "LAB"
    PROJECT = "PROJECT"
    OTHER = "OTHER"

class ProjectStatus(str, enum.Enum):
    PLANNING = "PLANNING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    SUBMITTED = "SUBMITTED"

class AcademicProfile(BaseModel):
    __tablename__ = "academic_profiles"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    college_name = Column(String(150), nullable=True)
    university = Column(String(150), nullable=True)
    degree = Column(String(100), nullable=True)
    branch = Column(String(100), nullable=True)
    current_year = Column(Integer, nullable=True)
    current_semester = Column(Integer, nullable=True)
    roll_number = Column(String(50), nullable=True)
    academic_start_year = Column(Integer, nullable=True)

    # Relationships
    user = relationship("User", back_populates="academic_profile")

class Subject(BaseModel):
    __tablename__ = "subjects"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    name = Column(String(100), nullable=False)
    code = Column(String(30), nullable=True)
    credits = Column(Integer, default=3, nullable=True)
    semester = Column(Integer, nullable=True)
    faculty_name = Column(String(100), nullable=True)
    color = Column(String(30), default="#8B5CF6", nullable=False)
    total_classes = Column(Integer, default=0, nullable=False)
    attended_classes = Column(Integer, default=0, nullable=False)
    target_attendance = Column(Float, default=80.0, nullable=False)
    min_attendance = Column(Float, default=75.0, nullable=False)

    # Relationships
    user = relationship("User", back_populates="subjects")
    attendance_records = relationship("AttendanceRecord", back_populates="subject", cascade="all, delete-orphan")
    timetable_slots = relationship("TimetableSlot", back_populates="subject", cascade="all, delete-orphan")
    assignments = relationship("Assignment", back_populates="subject", cascade="all, delete-orphan")
    exams = relationship("Exam", back_populates="subject", cascade="all, delete-orphan")
    internal_marks = relationship("InternalMark", back_populates="subject", cascade="all, delete-orphan")
    projects = relationship("AcademicProject", back_populates="subject", cascade="all, delete-orphan")
    notes = relationship("AcademicNote", back_populates="subject", cascade="all, delete-orphan")

class AttendanceRecord(BaseModel):
    __tablename__ = "attendance_records"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    subject_id = Column(String(36), ForeignKey("subjects.id", ondelete="CASCADE"), index=True, nullable=False)
    date = Column(Date, index=True, nullable=False)
    status = Column(SQLEnum(AttendanceStatus), default=AttendanceStatus.PRESENT, nullable=False)
    remarks = Column(String(255), nullable=True)

    # Relationships
    user = relationship("User", back_populates="attendance_records")
    subject = relationship("Subject", back_populates="attendance_records")

class TimetableSlot(BaseModel):
    __tablename__ = "timetable_slots"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    subject_id = Column(String(36), ForeignKey("subjects.id", ondelete="CASCADE"), index=True, nullable=False)
    day_of_week = Column(Integer, nullable=False)  # 0=Monday, 1=Tuesday, 2=Wednesday, 3=Thursday, 4=Friday, 5=Saturday, 6=Sunday
    start_time = Column(String(10), nullable=False)  # "09:00"
    end_time = Column(String(10), nullable=False)    # "10:00"
    room = Column(String(50), nullable=True)
    faculty_name = Column(String(100), nullable=True)

    # Relationships
    user = relationship("User", back_populates="timetable_slots")
    subject = relationship("Subject", back_populates="timetable_slots")

class Assignment(BaseModel):
    __tablename__ = "assignments"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    subject_id = Column(String(36), ForeignKey("subjects.id", ondelete="CASCADE"), index=True, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    due_date = Column(DateTime, index=True, nullable=False)
    status = Column(SQLEnum(AssignmentStatus), default=AssignmentStatus.PENDING, nullable=False)
    priority = Column(SQLEnum(AssignmentPriority), default=AssignmentPriority.MEDIUM, nullable=False)
    total_marks = Column(Float, nullable=True)
    obtained_marks = Column(Float, nullable=True)

    # Relationships
    user = relationship("User", back_populates="assignments")
    subject = relationship("Subject", back_populates="assignments")

class Exam(BaseModel):
    __tablename__ = "exams"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    subject_id = Column(String(36), ForeignKey("subjects.id", ondelete="CASCADE"), index=True, nullable=False)
    title = Column(String(200), nullable=False)
    exam_type = Column(SQLEnum(ExamType), default=ExamType.MIDTERM, nullable=False)
    exam_date = Column(DateTime, index=True, nullable=False)
    start_time = Column(String(10), nullable=True)
    end_time = Column(String(10), nullable=True)
    venue = Column(String(100), nullable=True)
    syllabus_covered = Column(Text, nullable=True)
    max_marks = Column(Float, default=100.0, nullable=True)
    obtained_marks = Column(Float, nullable=True)

    # Relationships
    user = relationship("User", back_populates="exams")
    subject = relationship("Subject", back_populates="exams")

class InternalMark(BaseModel):
    __tablename__ = "internal_marks"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    subject_id = Column(String(36), ForeignKey("subjects.id", ondelete="CASCADE"), index=True, nullable=False)
    assessment_name = Column(String(150), nullable=False)
    assessment_type = Column(SQLEnum(AssessmentType), default=AssessmentType.QUIZ, nullable=False)
    marks_obtained = Column(Float, nullable=False)
    max_marks = Column(Float, nullable=False)
    assessment_date = Column(Date, nullable=True)
    remarks = Column(String(255), nullable=True)

    # Relationships
    user = relationship("User", back_populates="internal_marks")
    subject = relationship("Subject", back_populates="internal_marks")

class AcademicProject(BaseModel):
    __tablename__ = "academic_projects"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    subject_id = Column(String(36), ForeignKey("subjects.id", ondelete="SET NULL"), index=True, nullable=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(SQLEnum(ProjectStatus), default=ProjectStatus.IN_PROGRESS, nullable=False)
    deadline = Column(DateTime, nullable=True)
    repository_url = Column(String(255), nullable=True)
    documentation_url = Column(String(255), nullable=True)

    # Relationships
    user = relationship("User", back_populates="academic_projects")
    subject = relationship("Subject", back_populates="projects")

class AcademicNote(BaseModel):
    __tablename__ = "academic_notes"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    subject_id = Column(String(36), ForeignKey("subjects.id", ondelete="CASCADE"), index=True, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    tags = Column(String(200), nullable=True)
    file_url = Column(String(500), nullable=True)
    file_name = Column(String(255), nullable=True)

    # Relationships
    user = relationship("User", back_populates="academic_notes")
    subject = relationship("Subject", back_populates="notes")
