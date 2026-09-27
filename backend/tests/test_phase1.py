import pytest
import uuid
import os
from httpx import AsyncClient, ASGITransport
from main import app
from app.core.database import engine, Base
from app.services.storage import storage_service

@pytest.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

@pytest.mark.asyncio
async def test_health_and_root_endpoints():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        health_resp = await ac.get("/health")
        assert health_resp.status_code == 200
        assert health_resp.json()["status"] == "HEALTHY"

        root_resp = await ac.get("/")
        assert root_resp.status_code == 200
        assert root_resp.json()["system"] == "WEBVERSE Intelligence Engine"

@pytest.mark.asyncio
async def test_phase1_auth_and_protected_endpoints():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        unique_email = f"pioneer_{uuid.uuid4().hex[:6]}@webverse.ai"
        password = "SecurePassword123!"

        # 1. Register User
        reg_payload = {
            "email": unique_email,
            "password": password,
            "full_name": "Pioneer User",
            "college_name": "Apex Engineering Institute",
            "semester": "6th Semester",
            "branch": "Computer Science & AI",
            "monthly_budget_target": "15000"
        }
        reg_resp = await ac.post("/api/v1/auth/register", json=reg_payload)
        assert reg_resp.status_code == 200
        reg_data = reg_resp.json()
        assert "access_token" in reg_data
        assert reg_data["email"] == unique_email
        token = reg_data["access_token"]
        auth_headers = {"Authorization": f"Bearer {token}"}

        # 2. Re-registration with duplicate email must fail with 400
        dup_resp = await ac.post("/api/v1/auth/register", json=reg_payload)
        assert dup_resp.status_code == 400

        # 3. Login
        login_resp = await ac.post("/api/v1/auth/login", json={
            "email": unique_email,
            "password": password
        })
        assert login_resp.status_code == 200
        assert "access_token" in login_resp.json()

        # 4. Invalid Password Login must fail with 401
        invalid_login = await ac.post("/api/v1/auth/login", json={
            "email": unique_email,
            "password": "WrongPassword!"
        })
        assert invalid_login.status_code == 401

        # 5. Access Protected Profile Endpoint
        me_resp = await ac.get("/api/v1/auth/me", headers=auth_headers)
        assert me_resp.status_code == 200
        me_data = me_resp.json()
        assert me_data["email"] == unique_email
        assert me_data["full_name"] == "Pioneer User"
        assert me_data["college_name"] == "Apex Engineering Institute"

        # 6. Unauthenticated request to protected endpoint must return 401
        unauth_resp = await ac.get("/api/v1/auth/me")
        assert unauth_resp.status_code == 401

        # 7. Protected Dashboard Stats
        stats_resp = await ac.get("/api/v1/dashboard/stats", headers=auth_headers)
        assert stats_resp.status_code == 200
        stats = stats_resp.json()
        assert stats["system_status"] == "ONLINE"
        assert "PHASE 1" in stats["active_phase"]

@pytest.mark.asyncio
async def test_user_isolated_storage():
    user_id_1 = str(uuid.uuid4())
    user_id_2 = str(uuid.uuid4())
    file_content = b"Mock document content for user isolation testing"

    # User 1 saves file
    stored_name_1, rel_path_1 = await storage_service.save_file(user_id_1, "test_doc.pdf", file_content)
    assert user_id_1 in rel_path_1

    # User 1 can retrieve their file
    read_bytes = await storage_service.get_file_bytes(user_id_1, stored_name_1)
    assert read_bytes == file_content

    # User 2 cannot access User 1's file (throws FileNotFoundError)
    with pytest.raises(FileNotFoundError):
        await storage_service.get_file_bytes(user_id_2, stored_name_1)

    # Cleanup
    await storage_service.delete_file(user_id_1, stored_name_1)
