import asyncio
import pytest
from httpx import AsyncClient, ASGITransport
from main import app
from app.core.database import engine, Base

@pytest.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

@pytest.mark.asyncio
async def test_health_and_root():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "HEALTHY"

        resp_root = await ac.get("/")
        assert resp_root.status_code == 200
        assert resp_root.json()["system"] == "WEBVERSE Intelligence Engine"

import uuid

@pytest.mark.asyncio
async def test_full_auth_and_multiverse_flow():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        unique_email = f"test_student_{uuid.uuid4().hex[:6]}@webverse.ai"
        # 1. Register User
        reg_payload = {
            "email": unique_email,
            "password": "QuantumPassword2026!",
            "full_name": "Ajay Multiverse",
            "college_name": "MIT Institute of Technology",
            "semester": "6th",
            "branch": "Computer Science & Engineering",
            "monthly_budget_target": "12000"
        }
        reg_resp = await ac.post("/api/v1/auth/register", json=reg_payload)
        assert reg_resp.status_code == 200, reg_resp.text
        token = reg_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Seed Demo Multiverse Records
        seed_resp = await ac.post("/api/v1/auth/seed-demo", headers=headers)
        assert seed_resp.status_code == 200
        assert seed_resp.json()["status"] == "SUCCESS"

        # 3. Check Dashboard Glance
        glance_resp = await ac.get("/api/v1/dashboard/glance", headers=headers)
        assert glance_resp.status_code == 200
        glance_data = glance_resp.json()
        assert glance_data["user_name"] == "Ajay Multiverse"
        assert glance_data["overall_attendance_percent"] > 0
        assert len(glance_data["upcoming_assignments"]) > 0
        assert len(glance_data["upcoming_exams"]) > 0

        # 4. Test Academics Subject & Attendance calculation
        subs_resp = await ac.get("/api/v1/academics/subjects", headers=headers)
        assert subs_resp.status_code == 200
        subs = subs_resp.json()
        daa_sub = next((s for s in subs if "Algorithms" in s["name"]), None)
        assert daa_sub is not None
        assert daa_sub["current_percentage"] == 75.0
        assert daa_sub["status_indicator"] == "ON_TRACK" or daa_sub["status_indicator"] == "SAFE"

        # 5. Test Finance Analytics
        fin_resp = await ac.get("/api/v1/finance/analytics", headers=headers)
        assert fin_resp.status_code == 200
        fin = fin_resp.json()
        assert fin["total_expenses"] > 0
        assert len(fin["top_categories"]) > 0

        # 6. Test Universal AI Query with Semantic Routing
        ai_resp = await ac.post("/api/v1/ai/chat", json={"message": "What is my current DAA attendance and how many classes can I miss?"}, headers=headers)
        assert ai_resp.status_code == 200
        ai_msg = ai_resp.json()
        assert "ACADEMICS" in ai_msg["routed_modules"]
        assert len(ai_msg["source_references"]) > 0

        # 7. Test AI Action Proposal & Execution
        action_query_resp = await ac.post("/api/v1/ai/chat", json={"message": "Add 350 for lunch"}, headers=headers)
        assert action_query_resp.status_code == 200
        action_msg = action_query_resp.json()
        assert action_msg["action_proposal"] is not None
        assert action_msg["action_proposal"]["action_type"] == "CREATE_EXPENSE"

        # Execute the action
        exec_resp = await ac.post("/api/v1/ai/action/execute", json={
            "action_type": action_msg["action_proposal"]["action_type"],
            "params": action_msg["action_proposal"]["params"],
            "message_id": action_msg["id"]
        }, headers=headers)
        assert exec_resp.status_code == 200
        assert exec_resp.json()["status"] == "SUCCESS"
