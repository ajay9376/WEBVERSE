from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timezone
import json
from app.models.life_admin import Document, Reminder

class LifeRetriever:
    @staticmethod
    async def retrieve_context(db: AsyncSession, user_id: str, query: str) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        
        # Pending Reminders
        rem_stmt = select(Reminder).where(
            Reminder.user_id == user_id,
            Reminder.is_completed == False
        ).order_by(Reminder.due_at.asc()).limit(8)
        rem_res = await db.execute(rem_stmt)
        reminders = rem_res.scalars().all()

        # Documents & Metadata
        doc_stmt = select(Document).where(Document.user_id == user_id).order_by(Document.created_at.desc())
        doc_res = await db.execute(doc_stmt)
        documents = doc_res.scalars().all()

        formatted_docs = []
        for d in documents:
            meta = {}
            if d.metadata_json:
                try:
                    meta = json.loads(d.metadata_json)
                except Exception:
                    pass
            formatted_docs.append({
                "filename": d.filename,
                "category": d.category.value,
                "extracted_fields": meta,
                "tags": d.tags,
                "text_summary": d.extracted_text[:150] if d.extracted_text else ""
            })

        return {
            "pending_reminders": [
                {
                    "title": r.title,
                    "due_at": r.due_at.strftime("%Y-%m-%d %H:%M"),
                    "priority": r.priority.value,
                    "module_link": r.linked_module
                }
                for r in reminders
            ],
            "stored_documents_and_metadata": formatted_docs
        }
