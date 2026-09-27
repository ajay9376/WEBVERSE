from datetime import datetime, timezone
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import json
from app.models.life_admin import Document, Reminder
from app.schemas.life_admin import DocumentResponse, ReminderResponse

class LifeAdminService:
    @staticmethod
    def format_document(doc: Document) -> DocumentResponse:
        metadata = {}
        if doc.metadata_json:
            try:
                metadata = json.loads(doc.metadata_json)
            except Exception:
                metadata = {}

        return DocumentResponse(
            id=doc.id,
            user_id=doc.user_id,
            filename=doc.filename,
            file_type=doc.file_type,
            file_size=doc.file_size,
            category=doc.category,
            tags=doc.tags,
            extracted_text_preview=doc.extracted_text[:200] + "..." if doc.extracted_text else None,
            metadata_fields=metadata,
            is_indexed=doc.is_indexed,
            created_at=doc.created_at
        )

    @staticmethod
    def format_reminder(rem: Reminder) -> ReminderResponse:
        now = datetime.now(timezone.utc)
        is_overdue = (rem.due_at.replace(tzinfo=timezone.utc) < now) if rem.due_at.tzinfo is None else (rem.due_at < now)
        return ReminderResponse(
            id=rem.id,
            user_id=rem.user_id,
            title=rem.title,
            description=rem.description,
            due_at=rem.due_at,
            priority=rem.priority,
            is_completed=rem.is_completed,
            linked_module=rem.linked_module,
            linked_id=rem.linked_id,
            created_at=rem.created_at,
            is_overdue=is_overdue and not rem.is_completed
        )
