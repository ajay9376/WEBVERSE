import pytest
import io
import uuid
from httpx import AsyncClient, ASGITransport
from datetime import datetime, timezone, timedelta
from main import app

def get_unique_email(prefix="life"):
    return f"{prefix}_{uuid.uuid4().hex[:6]}@webverse.ai"

@pytest.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

async def register_and_get_token(client: AsyncClient, email: str, name: str = "Life Admin User"):
    res = await client.post("/api/v1/auth/register", json={
        "email": email,
        "password": "SecurePassword123!",
        "full_name": name,
        "college_name": "Webverse Institute",
        "branch": "Cybernetics",
        "semester": "6"
    })
    assert res.status_code == 200, res.text
    data = res.json()
    return data["access_token"]

@pytest.mark.asyncio
async def test_life_admin_categories_crud_and_defaults(async_client: AsyncClient):
    email = get_unique_email("cat")
    token = await register_and_get_token(async_client, email)
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Get Categories - default 10 system categories should be auto-seeded
    res = await async_client.get("/api/v1/life-admin/categories", headers=headers)
    assert res.status_code == 200
    cats = res.json()
    assert len(cats) >= 10
    cat_names = [c["name"] for c in cats]
    assert "Identity" in cat_names
    assert "Insurance" in cat_names
    assert "Bills" in cat_names

    # 2. Create custom category
    res = await async_client.post("/api/v1/life-admin/categories", headers=headers, json={
        "name": "Tax Vault",
        "description": "Tax filings and ITR receipts",
        "icon": "file-text",
        "color": "#10b981"
    })
    assert res.status_code == 201
    custom_cat = res.json()
    assert custom_cat["name"] == "Tax Vault"
    assert custom_cat["is_system"] is False

    # 3. Update category
    res = await async_client.put(f"/api/v1/life-admin/categories/{custom_cat['id']}", headers=headers, json={
        "description": "Updated tax description",
        "color": "#00f3ff"
    })
    assert res.status_code == 200
    assert res.json()["description"] == "Updated tax description"

    # 4. Delete category
    res = await async_client.delete(f"/api/v1/life-admin/categories/{custom_cat['id']}", headers=headers)
    assert res.status_code == 200

@pytest.mark.asyncio
async def test_document_upload_download_metadata_and_deletion(async_client: AsyncClient):
    email = get_unique_email("doc")
    token = await register_and_get_token(async_client, email)
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Upload a valid text document
    file_content = b"Webverse Passport and Visa Confirmation 2026. Expiry Date: 2028-12-31."
    files = {"file": ("passport_sample.txt", io.BytesIO(file_content), "text/plain")}
    data = {
        "title": "International Passport",
        "category": "IDENTITY",
        "issuer": "Govt Passport Office",
        "reference_number": "P987654321",
        "expiry_date": (datetime.now(timezone.utc) + timedelta(days=700)).isoformat(),
        "tags": "passport, travel, identity"
    }

    res = await async_client.post("/api/v1/life-admin/documents/upload", headers=headers, data=data, files=files)
    assert res.status_code == 201, res.text
    doc = res.json()
    assert doc["title"] == "International Passport"
    assert doc["category"] == "IDENTITY"
    assert doc["issuer"] == "Govt Passport Office"
    assert doc["reference_number"] == "P987654321"
    assert doc["days_until_expiry"] > 600
    assert doc["is_expired"] is False
    doc_id = doc["id"]

    # 2. Retrieve document metadata
    res = await async_client.get(f"/api/v1/life-admin/documents/{doc_id}", headers=headers)
    assert res.status_code == 200
    assert res.json()["id"] == doc_id

    # 3. Download document bytes
    res = await async_client.get(f"/api/v1/life-admin/documents/{doc_id}/download", headers=headers)
    assert res.status_code == 200
    assert res.content == file_content
    assert "attachment" in res.headers["content-disposition"]

    # 4. Update document metadata
    res = await async_client.put(f"/api/v1/life-admin/documents/{doc_id}", headers=headers, json={
        "title": "International Passport (Renewed)",
        "tags": "passport, travel, renewed"
    })
    assert res.status_code == 200
    assert res.json()["title"] == "International Passport (Renewed)"

    # 5. Filter documents by category and search
    res = await async_client.get("/api/v1/life-admin/documents?category=IDENTITY&search=Renewed", headers=headers)
    assert res.status_code == 200
    assert len(res.json()) >= 1

    # 6. Delete document
    res = await async_client.delete(f"/api/v1/life-admin/documents/{doc_id}", headers=headers)
    assert res.status_code == 200
    
    # Verify 404 after deletion
    res = await async_client.get(f"/api/v1/life-admin/documents/{doc_id}", headers=headers)
    assert res.status_code == 404

@pytest.mark.asyncio
async def test_document_validation_and_path_traversal_protection(async_client: AsyncClient):
    email = get_unique_email("sec")
    token = await register_and_get_token(async_client, email)
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Reject invalid file extension (.exe)
    invalid_file = {"file": ("malware.exe", io.BytesIO(b"binary"), "application/x-msdownload")}
    res = await async_client.post("/api/v1/life-admin/documents/upload", headers=headers, files=invalid_file)
    assert res.status_code == 400
    assert "not allowed" in res.json()["detail"].lower()

    # 2. Path traversal in filename sanitized
    traversal_file = {"file": ("../../../../etc/passwd.txt", io.BytesIO(b"safe test content"), "text/plain")}
    res = await async_client.post("/api/v1/life-admin/documents/upload", headers=headers, files=traversal_file)
    assert res.status_code == 201
    doc = res.json()
    assert ".." not in doc["filename"]
    assert doc["filename"] == "passwd.txt"

@pytest.mark.asyncio
async def test_bills_crud_and_overdue_calculations(async_client: AsyncClient):
    email = get_unique_email("bill")
    token = await register_and_get_token(async_client, email)
    headers = {"Authorization": f"Bearer {token}"}

    now = datetime.now(timezone.utc)
    # Bill 1: Upcoming due in 5 days
    due_upcoming = (now + timedelta(days=5)).isoformat()
    # Bill 2: Overdue by 4 days
    due_overdue = (now - timedelta(days=4)).isoformat()

    # 1. Create upcoming bill
    res = await async_client.post("/api/v1/life-admin/bills", headers=headers, json={
        "title": "Airtel Fiber Broadband",
        "provider": "Airtel",
        "category": "INTERNET",
        "amount": "1178.50",
        "due_date": due_upcoming,
        "recurring": True,
        "recurrence": "MONTHLY"
    })
    assert res.status_code == 201, res.text
    bill_up = res.json()
    assert bill_up["title"] == "Airtel Fiber Broadband"
    assert bill_up["is_overdue"] is False
    assert bill_up["days_until_due"] == 5

    # 2. Create overdue bill
    res = await async_client.post("/api/v1/life-admin/bills", headers=headers, json={
        "title": "Electricity Bill",
        "provider": "BESCOM",
        "category": "ELECTRICITY",
        "amount": "2450.00",
        "due_date": due_overdue,
        "status": "PENDING"
    })
    assert res.status_code == 201
    bill_over = res.json()
    assert bill_over["is_overdue"] is True
    assert bill_over["days_overdue"] == 4

    # 3. Pay overdue bill
    res = await async_client.patch(f"/api/v1/life-admin/bills/{bill_over['id']}/pay?payment_reference=UPI-BESCOM-991", headers=headers)
    assert res.status_code == 200
    paid_bill = res.json()
    assert paid_bill["status"] == "PAID"
    assert paid_bill["payment_reference"] == "UPI-BESCOM-991"
    assert paid_bill["is_overdue"] is False

    # 4. Get all bills
    res = await async_client.get("/api/v1/life-admin/bills", headers=headers)
    assert res.status_code == 200
    assert len(res.json()) >= 2

@pytest.mark.asyncio
async def test_insurance_policy_crud_and_expiry_detection(async_client: AsyncClient):
    email = get_unique_email("ins")
    token = await register_and_get_token(async_client, email)
    headers = {"Authorization": f"Bearer {token}"}

    now = datetime.now(timezone.utc)
    expiry_soon = (now + timedelta(days=18)).isoformat()

    # 1. Create health insurance policy expiring in 18 days
    res = await async_client.post("/api/v1/life-admin/policies", headers=headers, json={
        "provider": "Star Health",
        "policy_name": "Comprehensive Health Guard",
        "policy_number": "SH-2026-90812",
        "policy_type": "HEALTH",
        "start_date": (now - timedelta(days=347)).isoformat(),
        "expiry_date": expiry_soon,
        "premium_amount": "14500.00",
        "premium_frequency": "YEARLY",
        "coverage_amount": "500000.00",
        "notes": "Cashless claim available at Apollo"
    })
    assert res.status_code == 201, res.text
    pol = res.json()
    assert pol["policy_name"] == "Comprehensive Health Guard"
    assert pol["policy_number"] == "SH-2026-90812"
    assert pol["days_until_expiry"] == 18
    assert pol["is_expiring_soon"] is True
    assert pol["is_expired"] is False

    # 2. Update policy
    res = await async_client.put(f"/api/v1/life-admin/policies/{pol['id']}", headers=headers, json={
        "coverage_amount": "1000000.00"
    })
    assert res.status_code == 200
    assert float(res.json()["coverage_amount"]) == 1000000.0

@pytest.mark.asyncio
async def test_important_dates_and_reminders(async_client: AsyncClient):
    email = get_unique_email("date")
    token = await register_and_get_token(async_client, email)
    headers = {"Authorization": f"Bearer {token}"}

    now = datetime.now(timezone.utc)
    target_date = (now + timedelta(days=45)).isoformat()

    # 1. Create important date
    res = await async_client.post("/api/v1/life-admin/dates", headers=headers, json={
        "title": "Driving License Renewal",
        "description": "RTO Zone 4 renewal window",
        "date": target_date,
        "category": "LICENSE",
        "recurring": True,
        "recurrence": "YEARLY"
    })
    assert res.status_code == 201
    dt_item = res.json()
    assert dt_item["title"] == "Driving License Renewal"
    assert dt_item["days_remaining"] == 45
    assert dt_item["is_past"] is False

    # 2. Create standalone Reminder
    rem_due = (now + timedelta(days=2)).isoformat()
    res = await async_client.post("/api/v1/life-admin/reminders", headers=headers, json={
        "title": "Submit Medical Reimbursement",
        "description": "Attach doctor prescription and pharmacy invoices",
        "due_at": rem_due,
        "priority": "HIGH"
    })
    assert res.status_code == 201
    rem = res.json()
    assert rem["title"] == "Submit Medical Reimbursement"
    assert rem["is_completed"] is False
    rem_id = rem["id"]

    # 3. Toggle reminder completion
    res = await async_client.patch(f"/api/v1/life-admin/reminders/{rem_id}/toggle", headers=headers)
    assert res.status_code == 200
    assert res.json()["is_completed"] is True

@pytest.mark.asyncio
async def test_life_admin_dashboard_and_ai_context(async_client: AsyncClient):
    email = get_unique_email("dash")
    token = await register_and_get_token(async_client, email)
    headers = {"Authorization": f"Bearer {token}"}

    # Upload doc
    files = {"file": ("degree.txt", io.BytesIO(b"B.Tech Computer Science Degree Certificate"), "text/plain")}
    await async_client.post("/api/v1/life-admin/documents/upload", headers=headers, data={"category": "EDUCATION", "title": "B.Tech Degree"}, files=files)

    # Add bill
    now = datetime.now(timezone.utc)
    await async_client.post("/api/v1/life-admin/bills", headers=headers, json={
        "title": "College Mess Fee",
        "provider": "Campus Caterers",
        "amount": "4500.00",
        "due_date": (now + timedelta(days=7)).isoformat()
    })

    # Add policy
    await async_client.post("/api/v1/life-admin/policies", headers=headers, json={
        "provider": "Acko",
        "policy_name": "Bike Insurance",
        "policy_number": "ACKO-BIKE-772",
        "policy_type": "VEHICLE",
        "expiry_date": (now + timedelta(days=25)).isoformat(),
        "premium_amount": "1890.00"
    })

    # Fetch Dashboard
    res = await async_client.get("/api/v1/life-admin/dashboard", headers=headers)
    assert res.status_code == 200
    dash = res.json()
    assert dash["total_documents"] >= 1
    assert dash["bills_summary"]["pending_count"] >= 1
    assert float(dash["bills_summary"]["total_pending_amount"]) >= 4500.0
    assert dash["policies_summary"]["expiring_soon_count"] >= 1
    assert len(dash["recent_documents"]) >= 1

    # Fetch AI Context
    res = await async_client.get("/api/v1/life-admin/context", headers=headers)
    assert res.status_code == 200
    ctx = res.json()
    assert ctx["source"] == "life_admin"
    assert ctx["total_documents"] >= 1
    assert len(ctx["pending_bills"]) >= 1
    assert len(ctx["expiring_policies"]) >= 1

@pytest.mark.asyncio
async def test_life_admin_user_isolation_and_security(async_client: AsyncClient):
    email_a = get_unique_email("user_a")
    token_a = await register_and_get_token(async_client, email_a, "User A")
    headers_a = {"Authorization": f"Bearer {token_a}"}

    email_b = get_unique_email("user_b")
    token_b = await register_and_get_token(async_client, email_b, "User B")
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # User A creates a document, bill, policy, date, and reminder
    file_a = {"file": ("secret_user_a.txt", io.BytesIO(b"User A confidential secret"), "text/plain")}
    doc_res = await async_client.post("/api/v1/life-admin/documents/upload", headers=headers_a, data={"title": "A Private Doc"}, files=file_a)
    doc_a_id = doc_res.json()["id"]

    now = datetime.now(timezone.utc)
    bill_res = await async_client.post("/api/v1/life-admin/bills", headers=headers_a, json={
        "title": "A Private Bill", "provider": "Provider A", "amount": "999.00", "due_date": (now + timedelta(days=3)).isoformat()
    })
    bill_a_id = bill_res.json()["id"]

    pol_res = await async_client.post("/api/v1/life-admin/policies", headers=headers_a, json={
        "provider": "Prov A", "policy_name": "A Life Policy", "policy_number": "POL-A-1", "expiry_date": (now + timedelta(days=20)).isoformat(), "premium_amount": "5000.00"
    })
    pol_a_id = pol_res.json()["id"]

    date_res = await async_client.post("/api/v1/life-admin/dates", headers=headers_a, json={
        "title": "A Secret Date", "date": (now + timedelta(days=10)).isoformat()
    })
    date_a_id = date_res.json()["id"]

    rem_res = await async_client.post("/api/v1/life-admin/reminders", headers=headers_a, json={
        "title": "A Secret Reminder", "due_at": (now + timedelta(days=1)).isoformat()
    })
    rem_a_id = rem_res.json()["id"]

    # User B attempts to access or manipulate User A's resources -> Must receive 404
    assert (await async_client.get(f"/api/v1/life-admin/documents/{doc_a_id}", headers=headers_b)).status_code == 404
    assert (await async_client.get(f"/api/v1/life-admin/documents/{doc_a_id}/download", headers=headers_b)).status_code == 404
    assert (await async_client.put(f"/api/v1/life-admin/documents/{doc_a_id}", headers=headers_b, json={"title": "Hacked"})).status_code == 404
    assert (await async_client.delete(f"/api/v1/life-admin/documents/{doc_a_id}", headers=headers_b)).status_code == 404

    assert (await async_client.get(f"/api/v1/life-admin/bills/{bill_a_id}", headers=headers_b)).status_code == 404
    assert (await async_client.patch(f"/api/v1/life-admin/bills/{bill_a_id}/pay", headers=headers_b)).status_code == 404
    assert (await async_client.delete(f"/api/v1/life-admin/bills/{bill_a_id}", headers=headers_b)).status_code == 404

    assert (await async_client.get(f"/api/v1/life-admin/policies/{pol_a_id}", headers=headers_b)).status_code == 404
    assert (await async_client.put(f"/api/v1/life-admin/policies/{pol_a_id}", headers=headers_b, json={"premium_amount": "1.00"})).status_code == 404
    assert (await async_client.delete(f"/api/v1/life-admin/policies/{pol_a_id}", headers=headers_b)).status_code == 404

    assert (await async_client.get(f"/api/v1/life-admin/dates/{date_a_id}", headers=headers_b)).status_code == 404
    assert (await async_client.delete(f"/api/v1/life-admin/dates/{date_a_id}", headers=headers_b)).status_code == 404

    assert (await async_client.get(f"/api/v1/life-admin/reminders/{rem_a_id}", headers=headers_b)).status_code == 404
    assert (await async_client.patch(f"/api/v1/life-admin/reminders/{rem_a_id}/toggle", headers=headers_b)).status_code == 404
    assert (await async_client.delete(f"/api/v1/life-admin/reminders/{rem_a_id}", headers=headers_b)).status_code == 404
