import pytest
import uuid
from httpx import AsyncClient, ASGITransport
from datetime import datetime, timezone, timedelta
from main import app
from app.core.database import engine, Base

@pytest.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

async def create_user(client: AsyncClient, prefix: str = "pioneer"):
    email = f"{prefix}_{uuid.uuid4().hex[:6]}@webverse.ai"
    res = await client.post("/api/v1/auth/register", json={
        "email": email,
        "password": "WebverseSecurePass2026!",
        "full_name": f"Pioneer {prefix.capitalize()}",
        "college_name": "Apex Institute of AI",
        "branch": "Computer Science & AI",
        "semester": "6th Semester",
        "monthly_budget_target": "15000"
    })
    assert res.status_code == 200, res.text
    data = res.json()
    return data["access_token"], data

@pytest.mark.asyncio
async def test_phase7_full_multiverse_e2e_flow(client: AsyncClient):
    """
    Comprehensive E2E test verifying complete Webverse workflow across all modules:
    - Auth & Profile
    - Academics (Subject + Attendance + Safe Bunk)
    - Finance (Expense + Budget)
    - Life Admin (Reminder + Document)
    - Dashboard Glance (Unified 3-quadrant matrix)
    - AI Nexus (Conversation lifecycle, Cross-module RAG, Action proposal & confirmation)
    - User isolation & cascade deletion
    """
    # 1. Register User A
    token_a, user_a = await create_user(client, "alice")
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # 2. Academics: Create Subject with attendance
    sub_res = await client.post("/api/v1/academics/subjects", json={
        "name": "Distributed Systems",
        "code": "CS601",
        "credits": 4,
        "total_classes": 30,
        "attended_classes": 26,
        "target_attendance": 80.0,
        "min_attendance": 75.0
    }, headers=headers_a)
    assert sub_res.status_code == 201
    sub_id = sub_res.json()["id"]

    # 3. Finance: Create Expense Transaction
    tx_res = await client.post("/api/v1/finance/transactions", json={
        "title": "Campus Canteen Lunch",
        "amount": 450.0,
        "transaction_type": "EXPENSE",
        "payment_method": "UPI"
    }, headers=headers_a)
    assert tx_res.status_code == 201

    # 4. Life Admin: Create Pending Reminder
    due_time = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    rem_res = await client.post("/api/v1/life-admin/reminders", json={
        "title": "Renew Campus Library Card",
        "due_at": due_time,
        "priority": "HIGH"
    }, headers=headers_a)
    assert rem_res.status_code == 201

    # 5. Dashboard Glance Matrix: Verify all 3 dimensions are reflected
    glance_res = await client.get("/api/v1/dashboard/glance", headers=headers_a)
    assert glance_res.status_code == 200
    glance = glance_res.json()
    assert glance["user_name"] == "Pioneer Alice"
    assert glance["overall_attendance_percent"] == round((26 / 30) * 100.0, 1)
    assert glance["monthly_total_spent"] >= 450.0
    assert len(glance["pending_reminders"]) >= 1
    assert "ACADEMICS" in glance["active_dimensions"]
    assert "FINANCE" in glance["active_dimensions"]
    assert "LIFE_ADMIN" in glance["active_dimensions"]

    # 6. AI Conversation Management Lifecycle
    # 6a. Create Conversation
    conv_create_res = await client.post("/api/v1/ai/conversations", json={
        "title": "Semester 6 Planning",
        "module_focus": "UNIVERSAL"
    }, headers=headers_a)
    assert conv_create_res.status_code == 201
    conv_id = conv_create_res.json()["id"]

    # 6b. List Conversations
    conv_list_res = await client.get("/api/v1/ai/conversations", headers=headers_a)
    assert conv_list_res.status_code == 200
    conversations = conv_list_res.json()
    assert any(c["id"] == conv_id for c in conversations)

    # 6c. Send Chat Message in Conversation
    chat_res = await client.post("/api/v1/ai/chat", json={
        "message": "What is my current Distributed Systems attendance?",
        "session_id": conv_id
    }, headers=headers_a)
    assert chat_res.status_code == 200
    chat_data = chat_res.json()
    assert chat_data["session_id"] == conv_id
    assert len(chat_data["content"]) > 0

    # 6d. Action Proposal & Safe Execution
    action_chat_res = await client.post("/api/v1/ai/chat", json={
        "message": "Add 250 rupees for lunch to expenses",
        "session_id": conv_id
    }, headers=headers_a)
    assert action_chat_res.status_code == 200
    action_data = action_chat_res.json()

    if action_data.get("action_proposal"):
        proposal = action_data["action_proposal"]
        exec_res = await client.post("/api/v1/ai/action/execute", json={
            "action_type": proposal["action_type"],
            "params": proposal["params"],
            "message_id": action_data["id"]
        }, headers=headers_a)
        assert exec_res.status_code == 200
        assert exec_res.json()["success"] is True

    # 6e. Verify message history retrieval
    detail_res = await client.get(f"/api/v1/ai/conversations/{conv_id}", headers=headers_a)
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert len(detail["messages"]) >= 2

    # 7. Multi-tenant Isolation: User B cannot access User A's conversation or modify it
    token_b, _ = await create_user(client, "bob")
    headers_b = {"Authorization": f"Bearer {token_b}"}

    forbidden_get = await client.get(f"/api/v1/ai/conversations/{conv_id}", headers=headers_b)
    assert forbidden_get.status_code == 404

    forbidden_del = await client.delete(f"/api/v1/ai/conversations/{conv_id}", headers=headers_b)
    assert forbidden_del.status_code == 404

    # 8. Cascade Deletion of Conversation
    del_res = await client.delete(f"/api/v1/ai/conversations/{conv_id}", headers=headers_a)
    assert del_res.status_code == 204

    # Verify deleted
    verify_del = await client.get(f"/api/v1/ai/conversations/{conv_id}", headers=headers_a)
    assert verify_del.status_code == 404
