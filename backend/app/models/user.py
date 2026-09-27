from sqlalchemy import Column, String, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class User(BaseModel):
    __tablename__ = "users"

    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    avatar_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    college_name = Column(String(150), nullable=True)
    semester = Column(String(20), nullable=True)
    branch = Column(String(100), nullable=True)
    monthly_budget_target = Column(String(50), default="10000", nullable=True)

    # Relationships
    academic_profile = relationship("AcademicProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    subjects = relationship("Subject", back_populates="user", cascade="all, delete-orphan")
    attendance_records = relationship("AttendanceRecord", back_populates="user", cascade="all, delete-orphan")
    timetable_slots = relationship("TimetableSlot", back_populates="user", cascade="all, delete-orphan")
    assignments = relationship("Assignment", back_populates="user", cascade="all, delete-orphan")
    exams = relationship("Exam", back_populates="user", cascade="all, delete-orphan")
    internal_marks = relationship("InternalMark", back_populates="user", cascade="all, delete-orphan")
    academic_projects = relationship("AcademicProject", back_populates="user", cascade="all, delete-orphan")
    academic_notes = relationship("AcademicNote", back_populates="user", cascade="all, delete-orphan")
    
    expense_categories = relationship("ExpenseCategory", back_populates="user", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    budgets = relationship("Budget", back_populates="user", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")
    life_admin_categories = relationship("LifeAdminCategory", back_populates="user", cascade="all, delete-orphan")
    bills = relationship("Bill", back_populates="user", cascade="all, delete-orphan")
    insurance_policies = relationship("InsurancePolicy", back_populates="user", cascade="all, delete-orphan")
    important_dates = relationship("ImportantDate", back_populates="user", cascade="all, delete-orphan")
    reminders = relationship("Reminder", back_populates="user", cascade="all, delete-orphan")
    conversation_sessions = relationship("ConversationSession", back_populates="user", cascade="all, delete-orphan")
