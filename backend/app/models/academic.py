from sqlalchemy import Column, String, Float, Integer, Date, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum
from app.models.base import BaseModel

class AttendanceStatus(str, enum.Enum):
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    CANCELLED = "CANCELLED"
    DUTY_LEAVE = "DUTY_LEAVE"

class AssignmentStatus(str, enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    SUBMITTED = "SUBMITTED"
    GRADED = "GRADED"

class Subject(BaseModel):
    __tablename__ = "subjects"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    name = Column(String(100), nullable=False)
    code = Column(String(20), nullable=True)
    professor = Column(String(100), nullable=True)
    color = Column(String(30), default="#8B5CF6", nullable=False)
    min_attendance_percent = Column(Float, default=75.0, nullable=False)
    target_attendance_percent = Column(Float, default=85.0, nullable=False)

    # Relationships
    user = relationship("User", back_populates="subjects")
    attendance_records = relationship("AttendanceRecord", back_populates="subject", cascade="all, delete-orphan")
    timetable_slots = relationship("TimetableSlot", back_populates="subject", cascade="all, delete-orphan")
    assignments = relationship("Assignment", back_populates="subject", cascade="all, delete-orphan")
    exams = relationship("Exam", back_populates="subject", cascade="all, delete-orphan")
    notes = relationship("AcademicNote", back_populates="subject", cascade="all, delete-orphan")

class AttendanceRecord(BaseModel):
    __tablename__ = "attendance_records"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    subject_id = Column(String(36), ForeignKey("subjects.id", ondelete="CASCADE"), index=True, nullable=False)
    date = Column(Date, index=True, nullable=False)
    status = Column(SQLEnum(AttendanceStatus), default=AttendanceStatus.PRESENT, nullable=False)
    notes = Column(String(255), nullable=True)

    # Relationships
    user = relationship("User", back_populates="attendance_records")
    subject = relationship("Subject", back_populates="attendance_records")

class TimetableSlot(BaseModel):
    __tablename__ = "timetable_slots"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    subject_id = Column(String(36), ForeignKey("subjects.id", ondelete="CASCADE"), index=True, nullable=False)
    day_of_week = Column(Integer, nullable=False)  # 0=Monday, 6=Sunday
    start_time = Column(String(10), nullable=False)  # "09:00"
    end_time = Column(String(10), nullable=False)    # "10:00"
    room = Column(String(50), nullable=True)

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
    total_marks = Column(Float, nullable=True)
    obtained_marks = Column(Float, nullable=True)

    # Relationships
    user = relationship("User", back_populates="assignments")
    subject = relationship("Subject", back_populates="assignments")

class Exam(BaseModel):
    __tablename__ = "exams"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    subject_id = Column(String(36), ForeignKey("subjects.id", ondelete="CASCADE"), index=True, nullable=False)
    title = Column(String(200), nullable=False) # e.g. "Mid-Term Exam", "Finals"
    exam_date = Column(DateTime, index=True, nullable=False)
    location = Column(String(100), nullable=True)
    syllabus_covered = Column(Text, nullable=True)
    total_marks = Column(Float, default=100.0, nullable=True)
    obtained_marks = Column(Float, nullable=True)

    # Relationships
    user = relationship("User", back_populates="exams")
    subject = relationship("Subject", back_populates="exams")

class AcademicNote(BaseModel):
    __tablename__ = "academic_notes"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    subject_id = Column(String(36), ForeignKey("subjects.id", ondelete="CASCADE"), index=True, nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    tags = Column(String(200), nullable=True) # comma-separated

    # Relationships
    user = relationship("User", back_populates="academic_notes")
    subject = relationship("Subject", back_populates="notes")
