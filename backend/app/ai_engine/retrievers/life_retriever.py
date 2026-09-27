from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timezone
import json
from app.models.life_admin import Document, Reminder, Bill, InsurancePolicy, ImportantDate, BillStatus

class LifeRetriever:
    @staticmethod
    async def retrieve_context(db: AsyncSession, user_id: str, query: str) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        
        # 1. Pending Bills
        bill_stmt = select(Bill).where(
            Bill.user_id == user_id,
            Bill.status == BillStatus.PENDING
        ).order_by(Bill.due_date.asc()).limit(8)
        bill_res = await db.execute(bill_stmt)
        bills = bill_res.scalars().all()

        # 2. Insurance Policies
        ins_stmt = select(InsurancePolicy).where(
            InsurancePolicy.user_id == user_id
        ).order_by(InsurancePolicy.expiry_date.asc()).limit(6)
        ins_res = await db.execute(ins_stmt)
        policies = ins_res.scalars().all()

        # 3. Important Dates & Renewals
        date_stmt = select(ImportantDate).where(
            ImportantDate.user_id == user_id
        ).order_by(ImportantDate.date.asc()).limit(8)
        date_res = await db.execute(date_stmt)
        important_dates = date_res.scalars().all()

        # 4. Pending Reminders
        rem_stmt = select(Reminder).where(
            Reminder.user_id == user_id,
            Reminder.is_completed == False
        ).order_by(Reminder.due_at.asc()).limit(8)
        rem_res = await db.execute(rem_stmt)
        reminders = rem_res.scalars().all()

        # 5. Documents & Metadata
        doc_stmt = select(Document).where(Document.user_id == user_id).order_by(Document.created_at.desc()).limit(10)
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
                "category": d.category.value if hasattr(d.category, "value") else str(d.category),
                "extracted_fields": meta,
                "tags": d.tags,
                "text_summary": d.extracted_text[:150] if d.extracted_text else ""
            })

        return {
            "pending_bills": [
                {
                    "title": b.title,
                    "provider": b.provider,
                    "amount": f"₹{float(b.amount):,.2f}",
                    "raw_amount": float(b.amount),
                    "due_date": b.due_date.strftime("%Y-%m-%d"),
                    "category": b.category,
                    "recurring": b.recurring
                }
                for b in bills
            ],
            "active_insurance_policies": [
                {
                    "policy_name": p.policy_name,
                    "provider": p.provider,
                    "policy_number": p.policy_number,
                    "type": p.policy_type.value if hasattr(p.policy_type, "value") else str(p.policy_type),
                    "expiry_date": p.expiry_date.strftime("%Y-%m-%d"),
                    "premium": f"₹{float(p.premium_amount):,.2f}",
                    "coverage": f"₹{float(p.coverage_amount):,.2f}" if p.coverage_amount else "N/A"
                }
                for p in policies
            ],
            "important_dates": [
                {
                    "title": idt.title,
                    "date": idt.date.strftime("%Y-%m-%d"),
                    "category": idt.category.value if hasattr(idt.category, "value") else str(idt.category),
                    "description": idt.description or ""
                }
                for idt in important_dates
            ],
            "pending_reminders": [
                {
                    "title": r.title,
                    "due_at": r.due_at.strftime("%Y-%m-%d %H:%M"),
                    "priority": r.priority.value if hasattr(r.priority, "value") else str(r.priority),
                    "module_link": r.linked_module
                }
                for r in reminders
            ],
            "stored_documents_and_metadata": formatted_docs
        }
