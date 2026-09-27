import os
import json
import uuid
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any, Tuple
from decimal import Decimal
from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, or_, and_, delete

from app.models.life_admin import (
    Document,
    LifeAdminCategory,
    Bill,
    InsurancePolicy,
    ImportantDate,
    Reminder,
    DocumentCategory,
    ReminderPriority,
    ReminderStatus,
    BillStatus,
    RecurrencePattern,
    PolicyType,
    PremiumFrequency,
    ImportantDateCategory,
)
from app.schemas.life_admin import (
    LifeAdminCategoryCreate,
    LifeAdminCategoryUpdate,
    LifeAdminCategoryResponse,
    DocumentCreateMetadata,
    DocumentUpdate,
    DocumentResponse,
    BillCreate,
    BillUpdate,
    BillResponse,
    BillsSummary,
    InsurancePolicyCreate,
    InsurancePolicyUpdate,
    InsurancePolicyResponse,
    PoliciesSummary,
    ImportantDateCreate,
    ImportantDateUpdate,
    ImportantDateResponse,
    ReminderCreate,
    ReminderUpdate,
    ReminderResponse,
    LifeAdminDashboardData,
    LifeAdminContext,
)
from app.services.storage import storage_service
from app.services.document_parser import DocumentParserService
from app.ai_engine.rag_engine import RAGEngine

ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".docx", ".txt", ".csv", ".webp"}
MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024  # 25 MB

DEFAULT_LIFE_ADMIN_CATEGORIES = [
    {"name": "Identity", "description": "Passports, ID cards, driving licenses", "icon": "id-card", "color": "#00f3ff"},
    {"name": "Education", "description": "Degrees, marksheets, certificates", "icon": "graduation-cap", "color": "#a855f7"},
    {"name": "Insurance", "description": "Health, vehicle, life policies", "icon": "shield", "color": "#10b981"},
    {"name": "Finance", "description": "Tax returns, bank records, investments", "icon": "landmark", "color": "#f59e0b"},
    {"name": "Bills", "description": "Utility invoices, rent receipts, payment slips", "icon": "receipt", "color": "#ec4899"},
    {"name": "Medical", "description": "Prescriptions, health records, lab reports", "icon": "heart-pulse", "color": "#ef4444"},
    {"name": "Travel", "description": "Tickets, visas, travel itineraries", "icon": "plane", "color": "#3b82f6"},
    {"name": "Certificates", "description": "Awards, professional credentials", "icon": "award", "color": "#8b5cf6"},
    {"name": "Legal", "description": "Agreements, contracts, legal notices", "icon": "scale", "color": "#6366f1"},
    {"name": "Other", "description": "Miscellaneous administrative items", "icon": "folder", "color": "#64748b"},
]


class LifeAdminService:
    # -------------------------------------------------------------
    # Formatting Helpers & Date Difference Calculations
    # -------------------------------------------------------------
    @staticmethod
    def _now() -> datetime:
        return datetime.now(timezone.utc)

    @staticmethod
    def _normalize_dt(dt: Optional[datetime]) -> Optional[datetime]:
        if dt is None:
            return None
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt

    @classmethod
    def format_document(cls, doc: Document) -> DocumentResponse:
        metadata = {}
        if doc.metadata_json:
            try:
                metadata = json.loads(doc.metadata_json)
            except Exception:
                metadata = {}

        now = cls._now()
        days_until_expiry = None
        is_expired = False
        if doc.expiry_date:
            exp = cls._normalize_dt(doc.expiry_date)
            delta = (exp.date() - now.date()).days
            days_until_expiry = delta
            is_expired = delta < 0

        title_display = doc.title or doc.filename

        return DocumentResponse(
            id=doc.id,
            user_id=doc.user_id,
            category_id=doc.category_id,
            title=title_display,
            description=doc.description,
            filename=doc.filename,
            file_name=doc.filename,
            file_type=doc.file_type,
            mime_type=doc.file_type,
            file_size=doc.file_size,
            category=doc.category,
            tags=doc.tags,
            document_date=doc.document_date,
            expiry_date=doc.expiry_date,
            issuer=doc.issuer,
            reference_number=doc.reference_number,
            extracted_text_preview=(doc.extracted_text[:200] + "...") if doc.extracted_text else None,
            metadata_fields=metadata,
            is_indexed=doc.is_indexed,
            days_until_expiry=days_until_expiry,
            is_expired=is_expired,
            created_at=doc.created_at,
            updated_at=doc.updated_at,
        )

    @classmethod
    def format_bill(cls, bill: Bill) -> BillResponse:
        now = cls._now()
        due = cls._normalize_dt(bill.due_date)
        delta = (due.date() - now.date()).days
        
        is_overdue = (delta < 0 and bill.status != BillStatus.PAID and bill.status != BillStatus.CANCELLED)
        days_until_due = max(0, delta)
        days_overdue = abs(delta) if delta < 0 else 0

        return BillResponse(
            id=bill.id,
            user_id=bill.user_id,
            title=bill.title,
            provider=bill.provider,
            category=bill.category,
            amount=Decimal(str(bill.amount)),
            due_date=bill.due_date,
            status=bill.status,
            recurring=bill.recurring,
            recurrence=bill.recurrence,
            payment_reference=bill.payment_reference,
            notes=bill.notes,
            days_until_due=days_until_due,
            days_overdue=days_overdue,
            is_overdue=is_overdue,
            created_at=bill.created_at,
            updated_at=bill.updated_at,
        )

    @classmethod
    def format_policy(cls, pol: InsurancePolicy) -> InsurancePolicyResponse:
        now = cls._now()
        exp = cls._normalize_dt(pol.expiry_date)
        delta = (exp.date() - now.date()).days
        
        is_expired = delta < 0
        is_expiring_soon = 0 <= delta <= 30

        return InsurancePolicyResponse(
            id=pol.id,
            user_id=pol.user_id,
            provider=pol.provider,
            policy_name=pol.policy_name,
            policy_number=pol.policy_number,
            policy_type=pol.policy_type,
            start_date=pol.start_date,
            expiry_date=pol.expiry_date,
            premium_amount=Decimal(str(pol.premium_amount)),
            premium_frequency=pol.premium_frequency,
            coverage_amount=Decimal(str(pol.coverage_amount)) if pol.coverage_amount is not None else None,
            document_id=pol.document_id,
            notes=pol.notes,
            days_until_expiry=delta,
            is_expired=is_expired,
            is_expiring_soon=is_expiring_soon,
            created_at=pol.created_at,
            updated_at=pol.updated_at,
        )

    @classmethod
    def format_important_date(cls, dt_item: ImportantDate) -> ImportantDateResponse:
        now = cls._now()
        target = cls._normalize_dt(dt_item.date)
        delta = (target.date() - now.date()).days

        return ImportantDateResponse(
            id=dt_item.id,
            user_id=dt_item.user_id,
            title=dt_item.title,
            description=dt_item.description,
            date=dt_item.date,
            category=dt_item.category,
            recurring=dt_item.recurring,
            recurrence=dt_item.recurrence,
            days_remaining=delta,
            is_past=delta < 0,
            created_at=dt_item.created_at,
            updated_at=dt_item.updated_at,
        )

    @classmethod
    def format_reminder(cls, rem: Reminder) -> ReminderResponse:
        now = cls._now()
        due = cls._normalize_dt(rem.due_at)
        delta = (due.date() - now.date()).days
        is_overdue = (due < now) and not rem.is_completed and rem.status != ReminderStatus.COMPLETED

        return ReminderResponse(
            id=rem.id,
            user_id=rem.user_id,
            title=rem.title,
            description=rem.description,
            due_at=rem.due_at,
            priority=rem.priority,
            status=rem.status,
            is_completed=rem.is_completed or rem.status == ReminderStatus.COMPLETED,
            linked_module=rem.linked_module,
            linked_id=rem.linked_id,
            is_overdue=is_overdue,
            days_until_due=delta,
            created_at=rem.created_at,
            updated_at=rem.updated_at,
        )

    # -------------------------------------------------------------
    # Category Management
    # -------------------------------------------------------------
    @classmethod
    async def seed_default_categories(cls, db: AsyncSession, user_id: str) -> None:
        stmt = select(LifeAdminCategory).where(LifeAdminCategory.user_id == user_id)
        res = await db.execute(stmt)
        existing = res.scalars().all()
        if not existing:
            for cat in DEFAULT_LIFE_ADMIN_CATEGORIES:
                c = LifeAdminCategory(
                    user_id=user_id,
                    name=cat["name"],
                    description=cat["description"],
                    icon=cat["icon"],
                    color=cat["color"],
                    is_system=True,
                )
                db.add(c)
            await db.commit()

    @classmethod
    async def get_categories(cls, db: AsyncSession, user_id: str) -> List[LifeAdminCategoryResponse]:
        await cls.seed_default_categories(db, user_id)
        stmt = select(LifeAdminCategory).where(LifeAdminCategory.user_id == user_id).order_by(LifeAdminCategory.name.asc())
        res = await db.execute(stmt)
        return [LifeAdminCategoryResponse.model_validate(c) for c in res.scalars().all()]

    @classmethod
    async def create_category(cls, db: AsyncSession, user_id: str, cat_in: LifeAdminCategoryCreate) -> LifeAdminCategoryResponse:
        c = LifeAdminCategory(
            user_id=user_id,
            name=cat_in.name,
            description=cat_in.description,
            icon=cat_in.icon or "folder",
            color=cat_in.color or "#00f3ff",
            is_system=False,
        )
        db.add(c)
        await db.commit()
        await db.refresh(c)
        return LifeAdminCategoryResponse.model_validate(c)

    @classmethod
    async def update_category(cls, db: AsyncSession, user_id: str, cat_id: str, cat_in: LifeAdminCategoryUpdate) -> LifeAdminCategoryResponse:
        stmt = select(LifeAdminCategory).where(LifeAdminCategory.id == cat_id, LifeAdminCategory.user_id == user_id)
        res = await db.execute(stmt)
        c = res.scalars().first()
        if not c:
            raise HTTPException(status_code=404, detail="Category not found")
        
        if cat_in.name is not None:
            c.name = cat_in.name
        if cat_in.description is not None:
            c.description = cat_in.description
        if cat_in.icon is not None:
            c.icon = cat_in.icon
        if cat_in.color is not None:
            c.color = cat_in.color

        await db.commit()
        await db.refresh(c)
        return LifeAdminCategoryResponse.model_validate(c)

    @classmethod
    async def delete_category(cls, db: AsyncSession, user_id: str, cat_id: str) -> bool:
        stmt = select(LifeAdminCategory).where(LifeAdminCategory.id == cat_id, LifeAdminCategory.user_id == user_id)
        res = await db.execute(stmt)
        c = res.scalars().first()
        if not c:
            raise HTTPException(status_code=404, detail="Category not found")

        # Set category_id to NULL on any documents linked to this category to prevent broken records
        doc_stmt = select(Document).where(Document.category_id == cat_id, Document.user_id == user_id)
        doc_res = await db.execute(doc_stmt)
        for doc in doc_res.scalars().all():
            doc.category_id = None

        await db.delete(c)
        await db.commit()
        return True

    # -------------------------------------------------------------
    # Document Vault Management (Upload, Retrieval, Storage)
    # -------------------------------------------------------------
    @classmethod
    async def get_documents(
        cls,
        db: AsyncSession,
        user_id: str,
        category: Optional[str] = None,
        search: Optional[str] = None,
        expiry_filter: Optional[str] = None, # expiring_soon, expired
    ) -> List[DocumentResponse]:
        stmt = select(Document).where(Document.user_id == user_id)
        
        if category:
            cat_upper = category.upper()
            if cat_upper in DocumentCategory.__members__:
                stmt = stmt.where(Document.category == DocumentCategory[cat_upper])
            else:
                stmt = stmt.join(LifeAdminCategory, Document.category_id == LifeAdminCategory.id, isouter=True).where(
                    or_(Document.category == cat_upper, LifeAdminCategory.name.ilike(f"%{category}%"))
                )

        if search:
            s = f"%{search}%"
            stmt = stmt.where(or_(
                Document.title.ilike(s),
                Document.filename.ilike(s),
                Document.issuer.ilike(s),
                Document.reference_number.ilike(s),
                Document.tags.ilike(s),
                Document.description.ilike(s),
            ))

        now = cls._now()
        if expiry_filter == "expiring_soon":
            thirty_days = now + timedelta(days=30)
            stmt = stmt.where(and_(Document.expiry_date.isnot(None), Document.expiry_date >= now, Document.expiry_date <= thirty_days))
        elif expiry_filter == "expired":
            stmt = stmt.where(and_(Document.expiry_date.isnot(None), Document.expiry_date < now))

        stmt = stmt.order_by(Document.created_at.desc())
        res = await db.execute(stmt)
        return [cls.format_document(d) for d in res.scalars().all()]

    @classmethod
    async def get_document_by_id(cls, db: AsyncSession, user_id: str, doc_id: str) -> Document:
        stmt = select(Document).where(Document.id == doc_id, Document.user_id == user_id)
        res = await db.execute(stmt)
        doc = res.scalars().first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        return doc

    @classmethod
    async def upload_document(
        cls,
        db: AsyncSession,
        user_id: str,
        file: UploadFile,
        title: Optional[str] = None,
        category: Optional[str] = "OTHER",
        category_id: Optional[str] = None,
        description: Optional[str] = None,
        issuer: Optional[str] = None,
        reference_number: Optional[str] = None,
        document_date: Optional[datetime] = None,
        expiry_date: Optional[datetime] = None,
        tags: Optional[str] = None,
    ) -> DocumentResponse:
        # Validate filename and path traversal
        raw_filename = os.path.basename(file.filename or "uploaded_file.bin")
        ext = os.path.splitext(raw_filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS and not raw_filename.endswith(".bin"):
            raise HTTPException(status_code=400, detail=f"File extension {ext} not allowed. Supported: {', '.join(ALLOWED_EXTENSIONS)}")

        content = await file.read()
        if len(content) > MAX_FILE_SIZE_BYTES:
            raise HTTPException(status_code=400, detail="File size exceeds maximum allowed 25MB.")

        # Save securely using storage abstraction
        stored_filename, relative_path = await storage_service.save_file(user_id, raw_filename, content)
        file_size_kb = round(len(content) / 1024.0, 2)

        # Extract text for future search and RAG indexing
        extracted_text = ""
        full_physical_path = os.path.join(storage_service.base_dir, user_id, stored_filename) if hasattr(storage_service, "base_dir") else relative_path
        if ext == ".pdf":
            extracted_text = DocumentParserService.extract_text_from_pdf(full_physical_path)
        elif ext in {".txt", ".csv"}:
            try:
                extracted_text = content.decode("utf-8", errors="ignore")
            except Exception:
                extracted_text = ""

        # Extract structured metadata fields
        extracted_metadata = DocumentParserService.extract_metadata_fields(extracted_text, raw_filename)

        # Infer category if left default
        cat_enum = DocumentCategory.OTHER
        if category and category.upper() in DocumentCategory.__members__:
            cat_enum = DocumentCategory[category.upper()]
        elif "insurance" in extracted_text.lower() or "policy" in extracted_text.lower():
            cat_enum = DocumentCategory.INSURANCE
        elif "certificate" in extracted_text.lower() or "degree" in extracted_text.lower():
            cat_enum = DocumentCategory.EDUCATION
        elif "bill" in extracted_text.lower() or "invoice" in extracted_text.lower():
            cat_enum = DocumentCategory.BILLS
        elif "passport" in extracted_text.lower() or "identity" in extracted_text.lower() or "license" in extracted_text.lower():
            cat_enum = DocumentCategory.IDENTITY

        # Build Document entity
        doc = Document(
            user_id=user_id,
            category_id=category_id,
            title=title or raw_filename,
            description=description,
            filename=raw_filename,
            stored_filename=stored_filename,
            file_path=relative_path,
            file_type=file.content_type or "application/octet-stream",
            file_size=file_size_kb,
            category=cat_enum,
            tags=tags,
            document_date=document_date,
            expiry_date=expiry_date,
            issuer=issuer,
            reference_number=reference_number,
            extracted_text=extracted_text,
            metadata_json=json.dumps(extracted_metadata),
            is_indexed=bool(extracted_text),
        )
        db.add(doc)
        await db.commit()
        await db.refresh(doc)

        # Index chunks for RAG
        if extracted_text:
            try:
                chunks = DocumentParserService.chunk_text(extracted_text, chunk_size=300, overlap=30)
                if chunks:
                    await RAGEngine.index_document_chunks(db, user_id, doc.id, chunks)
            except Exception:
                pass

        # Auto-create reminder if expiry date exists
        if expiry_date:
            try:
                rem = Reminder(
                    user_id=user_id,
                    title=f"{doc.title or doc.filename} Expiry Notice",
                    description=f"Expiring document: {doc.title}. Reference: {doc.reference_number or 'N/A'}",
                    due_at=expiry_date,
                    priority=ReminderPriority.HIGH,
                    status=ReminderStatus.PENDING,
                    is_completed=False,
                    linked_module="LIFE_ADMIN",
                    linked_id=doc.id,
                )
                db.add(rem)
                await db.commit()
            except Exception:
                pass

        return cls.format_document(doc)

    @classmethod
    async def create_document_metadata(
        cls,
        db: AsyncSession,
        user_id: str,
        doc_in: DocumentCreateMetadata,
    ) -> DocumentResponse:
        # Create virtual document entry (e.g. physical document tracked without digital upload)
        doc = Document(
            user_id=user_id,
            category_id=doc_in.category_id,
            title=doc_in.title,
            description=doc_in.description,
            filename=f"{doc_in.title}.record",
            stored_filename=f"{uuid.uuid4()}.record",
            file_path=f"{user_id}/virtual_record",
            file_type="application/vnd.webverse.record",
            file_size=0.0,
            category=doc_in.category or DocumentCategory.OTHER,
            tags=doc_in.tags,
            document_date=doc_in.document_date,
            expiry_date=doc_in.expiry_date,
            issuer=doc_in.issuer,
            reference_number=doc_in.reference_number,
            is_indexed=False,
        )
        db.add(doc)
        await db.commit()
        await db.refresh(doc)
        return cls.format_document(doc)

    @classmethod
    async def update_document(
        cls,
        db: AsyncSession,
        user_id: str,
        doc_id: str,
        doc_in: DocumentUpdate,
    ) -> DocumentResponse:
        doc = await cls.get_document_by_id(db, user_id, doc_id)
        if doc_in.title is not None:
            doc.title = doc_in.title
        if doc_in.category is not None:
            doc.category = doc_in.category
        if doc_in.category_id is not None:
            doc.category_id = doc_in.category_id
        if doc_in.description is not None:
            doc.description = doc_in.description
        if doc_in.issuer is not None:
            doc.issuer = doc_in.issuer
        if doc_in.reference_number is not None:
            doc.reference_number = doc_in.reference_number
        if doc_in.document_date is not None:
            doc.document_date = doc_in.document_date
        if doc_in.expiry_date is not None:
            doc.expiry_date = doc_in.expiry_date
        if doc_in.tags is not None:
            doc.tags = doc_in.tags

        await db.commit()
        await db.refresh(doc)
        return cls.format_document(doc)

    @classmethod
    async def delete_document(cls, db: AsyncSession, user_id: str, doc_id: str) -> bool:
        doc = await cls.get_document_by_id(db, user_id, doc_id)
        # Delete file from storage
        try:
            await storage_service.delete_file(user_id, doc.stored_filename)
        except Exception:
            pass

        # Delete any linked reminders
        rem_stmt = delete(Reminder).where(Reminder.linked_id == doc.id, Reminder.user_id == user_id)
        await db.execute(rem_stmt)

        await db.delete(doc)
        await db.commit()
        return True

    @classmethod
    async def get_document_file(cls, db: AsyncSession, user_id: str, doc_id: str) -> Tuple[bytes, str, str]:
        doc = await cls.get_document_by_id(db, user_id, doc_id)
        file_bytes = await storage_service.get_file_bytes(user_id, doc.stored_filename)
        return file_bytes, doc.filename, doc.file_type

    # -------------------------------------------------------------
    # Bills Management
    # -------------------------------------------------------------
    @classmethod
    async def get_bills(
        cls,
        db: AsyncSession,
        user_id: str,
        status: Optional[str] = None,
        category: Optional[str] = None,
        provider: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[BillResponse]:
        stmt = select(Bill).where(Bill.user_id == user_id)
        if status and status.upper() in BillStatus.__members__:
            stmt = stmt.where(Bill.status == BillStatus[status.upper()])
        if category:
            stmt = stmt.where(Bill.category.ilike(f"%{category}%"))
        if provider:
            stmt = stmt.where(Bill.provider.ilike(f"%{provider}%"))
        if search:
            s = f"%{search}%"
            stmt = stmt.where(or_(Bill.title.ilike(s), Bill.provider.ilike(s), Bill.notes.ilike(s)))

        stmt = stmt.order_by(Bill.due_date.asc())
        res = await db.execute(stmt)
        return [cls.format_bill(b) for b in res.scalars().all()]

    @classmethod
    async def get_bill_by_id(cls, db: AsyncSession, user_id: str, bill_id: str) -> Bill:
        stmt = select(Bill).where(Bill.id == bill_id, Bill.user_id == user_id)
        res = await db.execute(stmt)
        bill = res.scalars().first()
        if not bill:
            raise HTTPException(status_code=404, detail="Bill not found")
        return bill

    @classmethod
    async def create_bill(cls, db: AsyncSession, user_id: str, bill_in: BillCreate) -> BillResponse:
        bill = Bill(
            user_id=user_id,
            title=bill_in.title,
            provider=bill_in.provider,
            category=bill_in.category or "UTILITIES",
            amount=bill_in.amount,
            due_date=bill_in.due_date,
            status=bill_in.status or BillStatus.PENDING,
            recurring=bill_in.recurring or False,
            recurrence=bill_in.recurrence or RecurrencePattern.NONE,
            payment_reference=bill_in.payment_reference,
            notes=bill_in.notes,
        )
        db.add(bill)
        await db.commit()
        await db.refresh(bill)

        # Automatically create reminder for bill due date
        try:
            rem = Reminder(
                user_id=user_id,
                title=f"Bill Due: {bill.title} ({bill.provider})",
                description=f"Amount: ₹{bill.amount:.2f}. Category: {bill.category}",
                due_at=bill.due_date,
                priority=ReminderPriority.HIGH,
                status=ReminderStatus.PENDING,
                is_completed=False,
                linked_module="LIFE_ADMIN",
                linked_id=bill.id,
            )
            db.add(rem)
            await db.commit()
        except Exception:
            pass

        return cls.format_bill(bill)

    @classmethod
    async def update_bill(cls, db: AsyncSession, user_id: str, bill_id: str, bill_in: BillUpdate) -> BillResponse:
        bill = await cls.get_bill_by_id(db, user_id, bill_id)
        if bill_in.title is not None:
            bill.title = bill_in.title
        if bill_in.provider is not None:
            bill.provider = bill_in.provider
        if bill_in.category is not None:
            bill.category = bill_in.category
        if bill_in.amount is not None:
            bill.amount = bill_in.amount
        if bill_in.due_date is not None:
            bill.due_date = bill_in.due_date
        if bill_in.status is not None:
            bill.status = bill_in.status
        if bill_in.recurring is not None:
            bill.recurring = bill_in.recurring
        if bill_in.recurrence is not None:
            bill.recurrence = bill_in.recurrence
        if bill_in.payment_reference is not None:
            bill.payment_reference = bill_in.payment_reference
        if bill_in.notes is not None:
            bill.notes = bill_in.notes

        await db.commit()
        await db.refresh(bill)
        return cls.format_bill(bill)

    @classmethod
    async def mark_bill_paid(cls, db: AsyncSession, user_id: str, bill_id: str, payment_ref: Optional[str] = None) -> BillResponse:
        bill = await cls.get_bill_by_id(db, user_id, bill_id)
        bill.status = BillStatus.PAID
        if payment_ref:
            bill.payment_reference = payment_ref
        
        # Complete any linked reminders
        rem_stmt = select(Reminder).where(Reminder.linked_id == bill.id, Reminder.user_id == user_id)
        rem_res = await db.execute(rem_stmt)
        for r in rem_res.scalars().all():
            r.is_completed = True
            r.status = ReminderStatus.COMPLETED

        await db.commit()
        await db.refresh(bill)
        return cls.format_bill(bill)

    @classmethod
    async def delete_bill(cls, db: AsyncSession, user_id: str, bill_id: str) -> bool:
        bill = await cls.get_bill_by_id(db, user_id, bill_id)
        # Delete linked reminders
        rem_stmt = delete(Reminder).where(Reminder.linked_id == bill.id, Reminder.user_id == user_id)
        await db.execute(rem_stmt)
        await db.delete(bill)
        await db.commit()
        return True

    # -------------------------------------------------------------
    # Insurance Policy Management
    # -------------------------------------------------------------
    @classmethod
    async def get_policies(
        cls,
        db: AsyncSession,
        user_id: str,
        policy_type: Optional[str] = None,
        provider: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[InsurancePolicyResponse]:
        stmt = select(InsurancePolicy).where(InsurancePolicy.user_id == user_id)
        if policy_type and policy_type.upper() in PolicyType.__members__:
            stmt = stmt.where(InsurancePolicy.policy_type == PolicyType[policy_type.upper()])
        if provider:
            stmt = stmt.where(InsurancePolicy.provider.ilike(f"%{provider}%"))
        if search:
            s = f"%{search}%"
            stmt = stmt.where(or_(
                InsurancePolicy.policy_name.ilike(s),
                InsurancePolicy.policy_number.ilike(s),
                InsurancePolicy.provider.ilike(s),
                InsurancePolicy.notes.ilike(s),
            ))

        stmt = stmt.order_by(InsurancePolicy.expiry_date.asc())
        res = await db.execute(stmt)
        return [cls.format_policy(p) for p in res.scalars().all()]

    @classmethod
    async def get_policy_by_id(cls, db: AsyncSession, user_id: str, policy_id: str) -> InsurancePolicy:
        stmt = select(InsurancePolicy).where(InsurancePolicy.id == policy_id, InsurancePolicy.user_id == user_id)
        res = await db.execute(stmt)
        pol = res.scalars().first()
        if not pol:
            raise HTTPException(status_code=404, detail="Insurance policy not found")
        return pol

    @classmethod
    async def create_policy(cls, db: AsyncSession, user_id: str, pol_in: InsurancePolicyCreate) -> InsurancePolicyResponse:
        pol = InsurancePolicy(
            user_id=user_id,
            provider=pol_in.provider,
            policy_name=pol_in.policy_name,
            policy_number=pol_in.policy_number,
            policy_type=pol_in.policy_type or PolicyType.OTHER,
            start_date=pol_in.start_date,
            expiry_date=pol_in.expiry_date,
            premium_amount=pol_in.premium_amount,
            premium_frequency=pol_in.premium_frequency or PremiumFrequency.YEARLY,
            coverage_amount=pol_in.coverage_amount,
            document_id=pol_in.document_id,
            notes=pol_in.notes,
        )
        db.add(pol)
        await db.commit()
        await db.refresh(pol)

        # Create renewal reminder
        try:
            rem = Reminder(
                user_id=user_id,
                title=f"Policy Renewal: {pol.policy_name} ({pol.provider})",
                description=f"Policy #{pol.policy_number}. Premium: ₹{pol.premium_amount:.2f}",
                due_at=pol.expiry_date,
                priority=ReminderPriority.HIGH,
                status=ReminderStatus.PENDING,
                is_completed=False,
                linked_module="LIFE_ADMIN",
                linked_id=pol.id,
            )
            db.add(rem)
            await db.commit()
        except Exception:
            pass

        return cls.format_policy(pol)

    @classmethod
    async def update_policy(cls, db: AsyncSession, user_id: str, policy_id: str, pol_in: InsurancePolicyUpdate) -> InsurancePolicyResponse:
        pol = await cls.get_policy_by_id(db, user_id, policy_id)
        if pol_in.provider is not None:
            pol.provider = pol_in.provider
        if pol_in.policy_name is not None:
            pol.policy_name = pol_in.policy_name
        if pol_in.policy_number is not None:
            pol.policy_number = pol_in.policy_number
        if pol_in.policy_type is not None:
            pol.policy_type = pol_in.policy_type
        if pol_in.start_date is not None:
            pol.start_date = pol_in.start_date
        if pol_in.expiry_date is not None:
            pol.expiry_date = pol_in.expiry_date
        if pol_in.premium_amount is not None:
            pol.premium_amount = pol_in.premium_amount
        if pol_in.premium_frequency is not None:
            pol.premium_frequency = pol_in.premium_frequency
        if pol_in.coverage_amount is not None:
            pol.coverage_amount = pol_in.coverage_amount
        if pol_in.document_id is not None:
            pol.document_id = pol_in.document_id
        if pol_in.notes is not None:
            pol.notes = pol_in.notes

        await db.commit()
        await db.refresh(pol)
        return cls.format_policy(pol)

    @classmethod
    async def delete_policy(cls, db: AsyncSession, user_id: str, policy_id: str) -> bool:
        pol = await cls.get_policy_by_id(db, user_id, policy_id)
        rem_stmt = delete(Reminder).where(Reminder.linked_id == pol.id, Reminder.user_id == user_id)
        await db.execute(rem_stmt)
        await db.delete(pol)
        await db.commit()
        return True

    # -------------------------------------------------------------
    # Important Dates Management
    # -------------------------------------------------------------
    @classmethod
    async def get_important_dates(
        cls,
        db: AsyncSession,
        user_id: str,
        category: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[ImportantDateResponse]:
        stmt = select(ImportantDate).where(ImportantDate.user_id == user_id)
        if category and category.upper() in ImportantDateCategory.__members__:
            stmt = stmt.where(ImportantDate.category == ImportantDateCategory[category.upper()])
        if search:
            s = f"%{search}%"
            stmt = stmt.where(or_(ImportantDate.title.ilike(s), ImportantDate.description.ilike(s)))

        stmt = stmt.order_by(ImportantDate.date.asc())
        res = await db.execute(stmt)
        return [cls.format_important_date(d) for d in res.scalars().all()]

    @classmethod
    async def get_important_date_by_id(cls, db: AsyncSession, user_id: str, date_id: str) -> ImportantDate:
        stmt = select(ImportantDate).where(ImportantDate.id == date_id, ImportantDate.user_id == user_id)
        res = await db.execute(stmt)
        d = res.scalars().first()
        if not d:
            raise HTTPException(status_code=404, detail="Important date record not found")
        return d

    @classmethod
    async def create_important_date(cls, db: AsyncSession, user_id: str, date_in: ImportantDateCreate) -> ImportantDateResponse:
        d = ImportantDate(
            user_id=user_id,
            title=date_in.title,
            description=date_in.description,
            date=date_in.date,
            category=date_in.category or ImportantDateCategory.OTHER,
            recurring=date_in.recurring or False,
            recurrence=date_in.recurrence or RecurrencePattern.NONE,
        )
        db.add(d)
        await db.commit()
        await db.refresh(d)

        # Create reminder
        try:
            rem = Reminder(
                user_id=user_id,
                title=f"Important Date: {d.title}",
                description=d.description or "Life Admin Milestone",
                due_at=d.date,
                priority=ReminderPriority.HIGH,
                status=ReminderStatus.PENDING,
                is_completed=False,
                linked_module="LIFE_ADMIN",
                linked_id=d.id,
            )
            db.add(rem)
            await db.commit()
        except Exception:
            pass

        return cls.format_important_date(d)

    @classmethod
    async def update_important_date(cls, db: AsyncSession, user_id: str, date_id: str, date_in: ImportantDateUpdate) -> ImportantDateResponse:
        d = await cls.get_important_date_by_id(db, user_id, date_id)
        if date_in.title is not None:
            d.title = date_in.title
        if date_in.description is not None:
            d.description = date_in.description
        if date_in.date is not None:
            d.date = date_in.date
        if date_in.category is not None:
            d.category = date_in.category
        if date_in.recurring is not None:
            d.recurring = date_in.recurring
        if date_in.recurrence is not None:
            d.recurrence = date_in.recurrence

        await db.commit()
        await db.refresh(d)
        return cls.format_important_date(d)

    @classmethod
    async def delete_important_date(cls, db: AsyncSession, user_id: str, date_id: str) -> bool:
        d = await cls.get_important_date_by_id(db, user_id, date_id)
        rem_stmt = delete(Reminder).where(Reminder.linked_id == d.id, Reminder.user_id == user_id)
        await db.execute(rem_stmt)
        await db.delete(d)
        await db.commit()
        return True

    # -------------------------------------------------------------
    # Reminders Management
    # -------------------------------------------------------------
    @classmethod
    async def get_reminders(
        cls,
        db: AsyncSession,
        user_id: str,
        status: Optional[str] = None,
        priority: Optional[str] = None,
    ) -> List[ReminderResponse]:
        stmt = select(Reminder).where(Reminder.user_id == user_id)
        if status:
            if status.upper() == "COMPLETED":
                stmt = stmt.where(or_(Reminder.is_completed == True, Reminder.status == ReminderStatus.COMPLETED))
            elif status.upper() == "PENDING":
                stmt = stmt.where(and_(Reminder.is_completed == False, Reminder.status == ReminderStatus.PENDING))
        if priority and priority.upper() in ReminderPriority.__members__:
            stmt = stmt.where(Reminder.priority == ReminderPriority[priority.upper()])

        stmt = stmt.order_by(Reminder.due_at.asc())
        res = await db.execute(stmt)
        return [cls.format_reminder(r) for r in res.scalars().all()]

    @classmethod
    async def get_reminder_by_id(cls, db: AsyncSession, user_id: str, rem_id: str) -> Reminder:
        stmt = select(Reminder).where(Reminder.id == rem_id, Reminder.user_id == user_id)
        res = await db.execute(stmt)
        rem = res.scalars().first()
        if not rem:
            raise HTTPException(status_code=404, detail="Reminder not found")
        return rem

    @classmethod
    async def create_reminder(cls, db: AsyncSession, user_id: str, rem_in: ReminderCreate) -> ReminderResponse:
        rem = Reminder(
            user_id=user_id,
            title=rem_in.title,
            description=rem_in.description,
            due_at=rem_in.due_at,
            priority=rem_in.priority or ReminderPriority.MEDIUM,
            status=rem_in.status or ReminderStatus.PENDING,
            is_completed=(rem_in.status == ReminderStatus.COMPLETED),
            linked_module=rem_in.linked_module or "LIFE_ADMIN",
            linked_id=rem_in.linked_id,
        )
        db.add(rem)
        await db.commit()
        await db.refresh(rem)
        return cls.format_reminder(rem)

    @classmethod
    async def update_reminder(cls, db: AsyncSession, user_id: str, rem_id: str, rem_in: ReminderUpdate) -> ReminderResponse:
        rem = await cls.get_reminder_by_id(db, user_id, rem_id)
        if rem_in.title is not None:
            rem.title = rem_in.title
        if rem_in.description is not None:
            rem.description = rem_in.description
        if rem_in.due_at is not None:
            rem.due_at = rem_in.due_at
        if rem_in.priority is not None:
            rem.priority = rem_in.priority
        if rem_in.status is not None:
            rem.status = rem_in.status
            rem.is_completed = (rem_in.status == ReminderStatus.COMPLETED)
        if rem_in.is_completed is not None:
            rem.is_completed = rem_in.is_completed
            rem.status = ReminderStatus.COMPLETED if rem_in.is_completed else ReminderStatus.PENDING

        await db.commit()
        await db.refresh(rem)
        return cls.format_reminder(rem)

    @classmethod
    async def toggle_reminder(cls, db: AsyncSession, user_id: str, rem_id: str) -> ReminderResponse:
        rem = await cls.get_reminder_by_id(db, user_id, rem_id)
        rem.is_completed = not rem.is_completed
        rem.status = ReminderStatus.COMPLETED if rem.is_completed else ReminderStatus.PENDING
        await db.commit()
        await db.refresh(rem)
        return cls.format_reminder(rem)

    @classmethod
    async def delete_reminder(cls, db: AsyncSession, user_id: str, rem_id: str) -> bool:
        rem = await cls.get_reminder_by_id(db, user_id, rem_id)
        await db.delete(rem)
        await db.commit()
        return True

    # -------------------------------------------------------------
    # Dashboard Aggregation & Future AI Context
    # -------------------------------------------------------------
    @classmethod
    async def get_life_admin_dashboard(cls, db: AsyncSession, user_id: str) -> LifeAdminDashboardData:
        now = cls._now()
        thirty_days = now + timedelta(days=30)

        # 1. Documents
        doc_stmt = select(Document).where(Document.user_id == user_id).order_by(Document.created_at.desc())
        doc_res = await db.execute(doc_stmt)
        all_docs = doc_res.scalars().all()
        total_documents = len(all_docs)
        
        category_counts: Dict[str, int] = {}
        for d in all_docs:
            cat_name = d.category.value if hasattr(d.category, "value") else str(d.category)
            category_counts[cat_name] = category_counts.get(cat_name, 0) + 1

        recent_documents = [cls.format_document(d) for d in all_docs[:5]]

        # 2. Bills Summary
        bill_stmt = select(Bill).where(Bill.user_id == user_id).order_by(Bill.due_date.asc())
        bill_res = await db.execute(bill_stmt)
        all_bills = bill_res.scalars().all()

        pending_count = 0
        overdue_count = 0
        paid_count = 0
        total_pending_amount = Decimal("0.00")
        total_overdue_amount = Decimal("0.00")
        upcoming_bills_list: List[BillResponse] = []

        for b in all_bills:
            due = cls._normalize_dt(b.due_date)
            delta = (due.date() - now.date()).days
            amt = Decimal(str(b.amount))

            if b.status == BillStatus.PAID:
                paid_count += 1
            elif b.status == BillStatus.CANCELLED:
                pass
            elif delta < 0:
                overdue_count += 1
                total_overdue_amount += amt
                upcoming_bills_list.append(cls.format_bill(b))
            else:
                pending_count += 1
                total_pending_amount += amt
                if delta <= 30:
                    upcoming_bills_list.append(cls.format_bill(b))

        bills_summary = BillsSummary(
            pending_count=pending_count,
            overdue_count=overdue_count,
            paid_count=paid_count,
            total_pending_amount=total_pending_amount,
            total_overdue_amount=total_overdue_amount,
            upcoming_bills=upcoming_bills_list[:6],
        )

        # 3. Policies Summary
        pol_stmt = select(InsurancePolicy).where(InsurancePolicy.user_id == user_id).order_by(InsurancePolicy.expiry_date.asc())
        pol_res = await db.execute(pol_stmt)
        all_pols = pol_res.scalars().all()

        expiring_soon_count = 0
        total_annual_premiums = Decimal("0.00")
        expiring_policies_list: List[InsurancePolicyResponse] = []

        for p in all_pols:
            exp = cls._normalize_dt(p.expiry_date)
            delta = (exp.date() - now.date()).days
            
            # Annual premium normalizer
            prem = Decimal(str(p.premium_amount))
            if p.premium_frequency == PremiumFrequency.MONTHLY:
                total_annual_premiums += prem * 12
            elif p.premium_frequency == PremiumFrequency.QUARTERLY:
                total_annual_premiums += prem * 4
            elif p.premium_frequency == PremiumFrequency.YEARLY:
                total_annual_premiums += prem
            elif p.premium_frequency == PremiumFrequency.ONE_TIME:
                total_annual_premiums += prem

            if delta <= 60:
                if 0 <= delta <= 30:
                    expiring_soon_count += 1
                expiring_policies_list.append(cls.format_policy(p))

        policies_summary = PoliciesSummary(
            total_policies=len(all_pols),
            expiring_soon_count=expiring_soon_count,
            total_annual_premiums=total_annual_premiums,
            expiring_policies=expiring_policies_list[:6],
        )

        # 4. Upcoming Important Dates (next 60 days)
        date_stmt = select(ImportantDate).where(ImportantDate.user_id == user_id, ImportantDate.date >= now).order_by(ImportantDate.date.asc())
        date_res = await db.execute(date_stmt)
        upcoming_dates = [cls.format_important_date(d) for d in date_res.scalars().all()[:6]]

        # 5. Pending Reminders
        rem_stmt = select(Reminder).where(
            Reminder.user_id == user_id,
            Reminder.is_completed == False,
            Reminder.status != ReminderStatus.COMPLETED
        ).order_by(Reminder.due_at.asc())
        rem_res = await db.execute(rem_stmt)
        pending_reminders = [cls.format_reminder(r) for r in rem_res.scalars().all()[:6]]

        return LifeAdminDashboardData(
            total_documents=total_documents,
            category_counts=category_counts,
            bills_summary=bills_summary,
            policies_summary=policies_summary,
            upcoming_dates=upcoming_dates,
            pending_reminders=pending_reminders,
            recent_documents=recent_documents,
        )

    @classmethod
    async def get_life_admin_context(cls, db: AsyncSession, user_id: str) -> LifeAdminContext:
        dash = await cls.get_life_admin_dashboard(db, user_id)
        return LifeAdminContext(
            source="life_admin",
            total_documents=dash.total_documents,
            pending_bills=[
                {
                    "title": b.title,
                    "provider": b.provider,
                    "amount": float(b.amount),
                    "due_date": b.due_date.isoformat(),
                    "days_until_due": b.days_until_due,
                    "is_overdue": b.is_overdue,
                }
                for b in dash.bills_summary.upcoming_bills
            ],
            expiring_policies=[
                {
                    "policy_name": p.policy_name,
                    "provider": p.provider,
                    "policy_number": p.policy_number,
                    "expiry_date": p.expiry_date.isoformat(),
                    "days_until_expiry": p.days_until_expiry,
                }
                for p in dash.policies_summary.expiring_policies
            ],
            upcoming_dates=[
                {
                    "title": d.title,
                    "date": d.date.isoformat(),
                    "category": d.category.value if hasattr(d.category, "value") else str(d.category),
                    "days_remaining": d.days_remaining,
                }
                for d in dash.upcoming_dates
            ],
            pending_reminders=[
                {
                    "title": r.title,
                    "due_at": r.due_at.isoformat(),
                    "priority": r.priority.value if hasattr(r.priority, "value") else str(r.priority),
                    "is_overdue": r.is_overdue,
                }
                for r in dash.pending_reminders
            ],
        )
