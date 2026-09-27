import os
import uuid
import json
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from datetime import datetime, timezone
from app.core.database import get_db
from app.core.config import settings
from app.core.security import get_current_user
from app.models.user import User
from app.models.life_admin import Document, Reminder, DocumentCategory, ReminderPriority
from app.schemas.life_admin import DocumentResponse, ReminderCreate, ReminderUpdate, ReminderResponse
from app.services.life_service import LifeAdminService
from app.services.document_parser import DocumentParserService
from app.ai_engine.rag_engine import RAGEngine

router = APIRouter(prefix="/life-admin", tags=["Life Admin"])

@router.get("/documents", response_model=List[DocumentResponse])
async def get_documents(
    category: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Document).where(Document.user_id == current_user.id)
    if category and category in DocumentCategory.__members__:
        stmt = stmt.where(Document.category == DocumentCategory[category])
    stmt = stmt.order_by(Document.created_at.desc())
    res = await db.execute(stmt)
    docs = res.scalars().all()
    return [LifeAdminService.format_document(d) for d in docs]

@router.post("/documents/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    category: Optional[str] = Form("OTHER"),
    tags: Optional[str] = Form(""),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Secure unique filename
    file_ext = os.path.splitext(file.filename)[1]
    stored_name = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, stored_name)

    # Save to disk
    contents = await file.read()
    file_size_kb = round(len(contents) / 1024.0, 2)
    with open(file_path, "wb") as f:
        f.write(contents)

    # Extract text
    extracted_text = ""
    if file_ext.lower() == ".pdf":
        extracted_text = DocumentParserService.extract_text_from_pdf(file_path)
    else:
        try:
            extracted_text = contents.decode("utf-8", errors="ignore")
        except Exception:
            extracted_text = "Uploaded binary file."

    # Extract structured metadata fields
    extracted_metadata = DocumentParserService.extract_metadata_fields(extracted_text, file.filename)
    
    # Auto-infer category if user left it as OTHER
    cat_enum = DocumentCategory.OTHER
    if category in DocumentCategory.__members__:
        cat_enum = DocumentCategory[category]
    elif "policy" in extracted_text.lower() or "insurance" in extracted_text.lower():
        cat_enum = DocumentCategory.INSURANCE
    elif "certificate" in extracted_text.lower() or "completed" in extracted_text.lower():
        cat_enum = DocumentCategory.CERTIFICATE
    elif "bill" in extracted_text.lower() or "invoice" in extracted_text.lower():
        cat_enum = DocumentCategory.BILL

    doc = Document(
        user_id=current_user.id,
        filename=file.filename,
        stored_filename=stored_name,
        file_path=file_path,
        file_type=file.content_type or "application/octet-stream",
        file_size=file_size_kb,
        category=cat_enum,
        tags=tags,
        extracted_text=extracted_text,
        metadata_json=json.dumps(extracted_metadata),
        is_indexed=True
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)

    # Chunk and index in vector store for RAG
    if extracted_text:
        chunks = DocumentParserService.chunk_text(extracted_text, chunk_size=300, overlap=30)
        if chunks:
            await RAGEngine.index_document_chunks(db, current_user.id, doc.id, chunks)

    # Automatically create a Reminder if an expiry date is found
    if "expiry_date" in extracted_metadata:
        try:
            exp_str = extracted_metadata["expiry_date"]
            # Create reminder for the expiry
            rem = Reminder(
                user_id=current_user.id,
                title=f"{doc.filename} Expiry Notice",
                description=f"Auto-extracted expiry on {exp_str}. Policy/Doc: {doc.filename}",
                due_at=datetime.now(timezone.utc), # Set notice
                priority=ReminderPriority.HIGH,
                linked_module="LIFE_ADMIN",
                linked_id=doc.id
            )
            db.add(rem)
            await db.commit()
        except Exception:
            pass

    return LifeAdminService.format_document(doc)

# --- Reminders ---
@router.get("/reminders", response_model=List[ReminderResponse])
async def get_reminders(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    stmt = select(Reminder).where(Reminder.user_id == current_user.id).order_by(Reminder.due_at.asc())
    res = await db.execute(stmt)
    return [LifeAdminService.format_reminder(r) for r in res.scalars().all()]

@router.post("/reminders", response_model=ReminderResponse)
async def create_reminder(rem_in: ReminderCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    rem = Reminder(
        user_id=current_user.id,
        title=rem_in.title,
        description=rem_in.description,
        due_at=rem_in.due_at,
        priority=rem_in.priority or ReminderPriority.MEDIUM,
        linked_module=rem_in.linked_module or "LIFE_ADMIN",
        linked_id=rem_in.linked_id
    )
    db.add(rem)
    await db.commit()
    await db.refresh(rem)
    return LifeAdminService.format_reminder(rem)

@router.patch("/reminders/{reminder_id}/toggle", response_model=ReminderResponse)
async def toggle_reminder(reminder_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    stmt = select(Reminder).where(Reminder.id == reminder_id, Reminder.user_id == current_user.id)
    res = await db.execute(stmt)
    rem = res.scalars().first()
    if not rem:
        raise HTTPException(status_code=404, detail="Reminder not found")
    rem.is_completed = not rem.is_completed
    await db.commit()
    await db.refresh(rem)
    return LifeAdminService.format_reminder(rem)
