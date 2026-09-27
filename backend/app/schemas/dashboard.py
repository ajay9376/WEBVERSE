from pydantic import BaseModel
from typing import Optional, List
from app.schemas.academic import SubjectResponse, AssignmentResponse, ExamResponse
from app.schemas.finance import FinanceAnalyticsResponse
from app.schemas.life_admin import ReminderResponse, DocumentResponse

class DashboardGlanceResponse(BaseModel):
    user_name: str
    greeting: str # "Good morning, Ajay"
    
    # Academics Glance
    overall_attendance_percent: float
    subjects_at_risk_count: int
    upcoming_assignments: List[AssignmentResponse]
    upcoming_exams: List[ExamResponse]
    
    # Finance Glance
    monthly_budget_target: float
    monthly_total_spent: float
    monthly_remaining_budget: float
    budget_health_status: str # HEALTHY, CAUTION, CRITICAL
    
    # Life Glance
    pending_reminders: List[ReminderResponse]
    urgent_alerts_count: int
    recent_documents: List[DocumentResponse]
    
    # Interconnected Node State
    active_dimensions: List[str] # ["ACADEMICS", "FINANCE", "LIFE_ADMIN"]
