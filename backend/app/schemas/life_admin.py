from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.life_admin import DocumentCategory, ReminderPriority

# Document Schemas
class DocumentResponse(BaseModel):
    id: str
    user_id: str
    filename: str
    file_type: str
    file_size: float
    category: DocumentCategory
    tags: Optional[str] = None
    extracted_text_preview: Optional[str] = None
    metadata_fields: Optional[Dict[str, Any]] = None
    is_indexed: bool
    created_at: datetime

    class Config:
        from_attributes = True

class DocumentQueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = 4

# Reminder Schemas
class ReminderCreate(BaseModel):
    title: str
    description: Optional[str] = None
    due_at: datetime
    priority: Optional[ReminderPriority] = ReminderPriority.MEDIUM
    linked_module: Optional[str] = None # ACADEMIC, FINANCE, LIFE_ADMIN
    linked_id: Optional[str] = None

class ReminderUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_at: Optional[datetime] = None
    priority: Optional[ReminderPriority] = None
    is_completed: Optional[bool] = None

class ReminderResponse(BaseModel):
    id: str
    user_id: str
    title: str
    description: Optional[str] = None
    due_at: datetime
    priority: ReminderPriority
    is_completed: bool
    linked_module: Optional[str] = None
    linked_id: Optional[str] = None
    created_at: datetime
    is_overdue: Optional[bool] = False

    class Config:
        from_attributes = True
