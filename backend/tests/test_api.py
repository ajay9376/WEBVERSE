import asyncio
import pytest
import uuid
from datetime import datetime, timezone, timedelta
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

        # 2. Create Real Academic Subject
        sub_resp = await ac.post("/api/v1/academics/subjects", json={
            "name": "Design & Analysis of Algorithms",
            "code": "CS301",
            "credits": 4,
            "faculty_name": "Dr. Turing",
            "total_classes": 40,
            "attended_classes": 30,
            "target_attendance": 80.0,
            "min_attendance": 75.0
        }, headers=headers)
        assert sub_resp.status_code == 201
        sub_data = sub_resp.json()
        sub_id = sub_data["id"]

        # Create Assignment & Exam
        due_date = (datetime.now() + timedelta(days=3)).isoformat()
        exam_date = (datetime.now() + timedelta(days=7)).isoformat()
        await ac.post("/api/v1/academics/assignments", json={
            "subject_id": sub_id,
            "title": "Dynamic Programming Problem Set",
            "due_date": due_date,
            "priority": "HIGH"
        }, headers=headers)

        await ac.post("/api/v1/academics/exams", json={
            "subject_id": sub_id,
            "title": "DAA Mid-Sem Examination",
            "exam_type": "MIDTERM",
            "exam_date": exam_date,
            "venue": "Hall B-302"
        }, headers=headers)

        # 3. Check Dashboard Glance
        glance_resp = await ac.get("/api/v1/dashboard/glance", headers=headers)
        assert glance_resp.status_code == 200
        glance_data = glance_resp.json()
        assert glance_data["user_name"] == "Ajay Multiverse"
        assert glance_data["overall_attendance_percent"] == 75.0
        assert len(glance_data["upcoming_assignments"]) > 0
        assert len(glance_data["upcoming_exams"]) > 0

        # 4. Test Academics Subject & Attendance calculation
        subs_resp = await ac.get("/api/v1/academics/subjects", headers=headers)
        assert subs_resp.status_code == 200
        subs = subs_resp.json()
        daa_sub = next((s for s in subs if "Algorithms" in s["name"]), None)
        assert daa_sub is not None
        assert daa_sub["current_percentage"] == 75.0
        assert daa_sub["status_indicator"] == "ON_TRACK"
        assert daa_sub["needed_classes"] > 0
