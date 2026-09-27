from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Response, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
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
    InsurancePolicyCreate,
    InsurancePolicyUpdate,
    InsurancePolicyResponse,
    ImportantDateCreate,
    ImportantDateUpdate,
    ImportantDateResponse,
    ReminderCreate,
    ReminderUpdate,
    ReminderResponse,
    LifeAdminDashboardData,
    LifeAdminContext,
)
from app.services.life_service import LifeAdminService

router = APIRouter(prefix="/life-admin", tags=["Life Admin Vault"])


# -------------------------------------------------------------
# Dashboard & AI Context
# -------------------------------------------------------------
@router.get("/dashboard", response_model=LifeAdminDashboardData)
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await LifeAdminService.get_life_admin_dashboard(db, current_user.id)


@router.get("/context", response_model=LifeAdminContext)
async def get_context(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await LifeAdminService.get_life_admin_context(db, current_user.id)


# -------------------------------------------------------------
# Categories
# -------------------------------------------------------------
@router.get("/categories", response_model=List[LifeAdminCategoryResponse])
async def get_categories(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await LifeAdminService.get_categories(db, current_user.id)


@router.post("/categories", response_model=LifeAdminCategoryResponse, status_code=201)
async def create_category(
    cat_in: LifeAdminCategoryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await LifeAdminService.create_category(db, current_user.id, cat_in)


@router.put("/categories/{category_id}", response_model=LifeAdminCategoryResponse)
async def update_category(
    category_id: str,
    cat_in: LifeAdminCategoryUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await LifeAdminService.update_category(db, current_user.id, category_id, cat_in)


@router.delete("/categories/{category_id}")
async def delete_category(
    category_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    success = await LifeAdminService.delete_category(db, current_user.id, category_id)
    return {"success": success, "message": "Category deleted successfully"}


# -------------------------------------------------------------
# Documents
# -------------------------------------------------------------
@router.get("/documents", response_model=List[DocumentResponse])
async def get_documents(
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    expiry_filter: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await LifeAdminService.get_documents(
        db=db,
        user_id=current_user.id,
        category=category,
        search=search,
        expiry_filter=expiry_filter,
    )


@router.post("/documents/upload", response_model=DocumentResponse, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    category: Optional[str] = Form("OTHER"),
    category_id: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    issuer: Optional[str] = Form(None),
    reference_number: Optional[str] = Form(None),
    document_date: Optional[str] = Form(None),
    expiry_date: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    doc_dt = None
    exp_dt = None
    if document_date:
        try:
            doc_dt = datetime.fromisoformat(document_date.replace("Z", "+00:00"))
        except Exception:
            pass
    if expiry_date:
        try:
            exp_dt = datetime.fromisoformat(expiry_date.replace("Z", "+00:00"))
        except Exception:
            pass

    return await LifeAdminService.upload_document(
        db=db,
        user_id=current_user.id,
        file=file,
        title=title,
        category=category,
        category_id=category_id,
        description=description,
        issuer=issuer,
        reference_number=reference_number,
        document_date=doc_dt,
        expiry_date=exp_dt,
        tags=tags,
    )


@router.post("/documents", response_model=DocumentResponse, status_code=201)
async def create_document_metadata(
    doc_in: DocumentCreateMetadata,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await LifeAdminService.create_document_metadata(db, current_user.id, doc_in)


@router.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    doc = await LifeAdminService.get_document_by_id(db, current_user.id, document_id)
    return LifeAdminService.format_document(doc)


@router.get("/documents/{document_id}/download")
async def download_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    file_bytes, filename, content_type = await LifeAdminService.get_document_file(db, current_user.id, document_id)
    return Response(
        content=file_bytes,
        media_type=content_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.put("/documents/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: str,
    doc_in: DocumentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await LifeAdminService.update_document(db, current_user.id, document_id, doc_in)


@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    success = await LifeAdminService.delete_document(db, current_user.id, document_id)
    return {"success": success, "message": "Document removed from vault"}


# -------------------------------------------------------------
# Bills
# -------------------------------------------------------------
@router.get("/bills", response_model=List[BillResponse])
async def get_bills(
    status: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    provider: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await LifeAdminService.get_bills(
        db=db,
        user_id=current_user.id,
        status=status,
        category=category,
        provider=provider,
        search=search,
    )


@router.post("/bills", response_model=BillResponse, status_code=201)
async def create_bill(
    bill_in: BillCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await LifeAdminService.create_bill(db, current_user.id, bill_in)


@router.get("/bills/{bill_id}", response_model=BillResponse)
async def get_bill(
    bill_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    bill = await LifeAdminService.get_bill_by_id(db, current_user.id, bill_id)
    return LifeAdminService.format_bill(bill)


@router.put("/bills/{bill_id}", response_model=BillResponse)
async def update_bill(
    bill_id: str,
    bill_in: BillUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await LifeAdminService.update_bill(db, current_user.id, bill_id, bill_in)


@router.patch("/bills/{bill_id}/pay", response_model=BillResponse)
async def pay_bill(
    bill_id: str,
    payment_reference: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await LifeAdminService.mark_bill_paid(db, current_user.id, bill_id, payment_reference)


@router.delete("/bills/{bill_id}")
async def delete_bill(
    bill_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    success = await LifeAdminService.delete_bill(db, current_user.id, bill_id)
    return {"success": success, "message": "Bill deleted successfully"}


# -------------------------------------------------------------
# Insurance Policies
# -------------------------------------------------------------
@router.get("/policies", response_model=List[InsurancePolicyResponse])
async def get_policies(
    policy_type: Optional[str] = Query(None),
    provider: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await LifeAdminService.get_policies(
        db=db,
        user_id=current_user.id,
        policy_type=policy_type,
        provider=provider,
        search=search,
    )


@router.post("/policies", response_model=InsurancePolicyResponse, status_code=201)
async def create_policy(
    pol_in: InsurancePolicyCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await LifeAdminService.create_policy(db, current_user.id, pol_in)


@router.get("/policies/{policy_id}", response_model=InsurancePolicyResponse)
async def get_policy(
    policy_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    pol = await LifeAdminService.get_policy_by_id(db, current_user.id, policy_id)
    return LifeAdminService.format_policy(pol)


@router.put("/policies/{policy_id}", response_model=InsurancePolicyResponse)
async def update_policy(
    policy_id: str,
    pol_in: InsurancePolicyUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await LifeAdminService.update_policy(db, current_user.id, policy_id, pol_in)


@router.delete("/policies/{policy_id}")
async def delete_policy(
    policy_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    success = await LifeAdminService.delete_policy(db, current_user.id, policy_id)
    return {"success": success, "message": "Policy deleted successfully"}


# -------------------------------------------------------------
# Important Dates
# -------------------------------------------------------------
@router.get("/dates", response_model=List[ImportantDateResponse])
async def get_important_dates(
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await LifeAdminService.get_important_dates(
        db=db,
        user_id=current_user.id,
        category=category,
        search=search,
    )


@router.post("/dates", response_model=ImportantDateResponse, status_code=201)
async def create_important_date(
    date_in: ImportantDateCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await LifeAdminService.create_important_date(db, current_user.id, date_in)


@router.get("/dates/{date_id}", response_model=ImportantDateResponse)
async def get_important_date(
    date_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    d = await LifeAdminService.get_important_date_by_id(db, current_user.id, date_id)
    return LifeAdminService.format_important_date(d)


@router.put("/dates/{date_id}", response_model=ImportantDateResponse)
async def update_important_date(
    date_id: str,
    date_in: ImportantDateUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await LifeAdminService.update_important_date(db, current_user.id, date_id, date_in)


@router.delete("/dates/{date_id}")
async def delete_important_date(
    date_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    success = await LifeAdminService.delete_important_date(db, current_user.id, date_id)
    return {"success": success, "message": "Important date deleted successfully"}


# -------------------------------------------------------------
# Reminders
# -------------------------------------------------------------
@router.get("/reminders", response_model=List[ReminderResponse])
async def get_reminders(
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await LifeAdminService.get_reminders(
        db=db,
        user_id=current_user.id,
        status=status,
        priority=priority,
    )


@router.post("/reminders", response_model=ReminderResponse, status_code=201)
async def create_reminder(
    rem_in: ReminderCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await LifeAdminService.create_reminder(db, current_user.id, rem_in)


@router.get("/reminders/{reminder_id}", response_model=ReminderResponse)
async def get_reminder(
    reminder_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    r = await LifeAdminService.get_reminder_by_id(db, current_user.id, reminder_id)
    return LifeAdminService.format_reminder(r)


@router.put("/reminders/{reminder_id}", response_model=ReminderResponse)
async def update_reminder(
    reminder_id: str,
    rem_in: ReminderUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await LifeAdminService.update_reminder(db, current_user.id, reminder_id, rem_in)


@router.patch("/reminders/{reminder_id}/toggle", response_model=ReminderResponse)
async def toggle_reminder(
    reminder_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await LifeAdminService.toggle_reminder(db, current_user.id, reminder_id)


@router.delete("/reminders/{reminder_id}")
async def delete_reminder(
    reminder_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    success = await LifeAdminService.delete_reminder(db, current_user.id, reminder_id)
    return {"success": success, "message": "Reminder deleted successfully"}
