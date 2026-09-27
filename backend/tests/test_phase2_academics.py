import pytest
import uuid
from datetime import datetime, timezone, timedelta, date
from httpx import AsyncClient, ASGITransport
from main import app
from app.core.database import engine, Base

@pytest.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

async def get_authenticated_client(user_suffix: str = "1"):
    transport = ASGITransport(app=app)
    ac = AsyncClient(transport=transport, base_url="http://test")
    email = f"student_{user_suffix}_{uuid.uuid4().hex[:6]}@webverse.ai"
    reg_resp = await ac.post("/api/v1/auth/register", json={
        "email": email,
        "password": "QuantumSecurePassword2026!",
        "full_name": f"Student {user_suffix}",
        "college_name": "Webverse Institute of Tech",
        "semester": "6",
        "branch": "Computer Science & AI"
    })
    assert reg_resp.status_code == 200
    token = reg_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    return ac, headers, reg_resp.json()["user_id"]


@pytest.mark.asyncio
async def test_academic_profile_crud():
    ac, headers, user_id = await get_authenticated_client("profile")
    
    # 1. Initially profile might be None
    get_res = await ac.get("/api/v1/academics/profile", headers=headers)
    assert get_res.status_code == 200

    # 2. Upsert profile
    put_res = await ac.put("/api/v1/academics/profile", json={
        "college_name": "MIT World Peace University",
        "university": "MIT-WPU",
        "degree": "B.Tech",
        "branch": "Artificial Intelligence & Data Science",
        "current_year": 3,
        "current_semester": 6,
        "roll_number": "MIT-2023-AI-042",
        "academic_start_year": 2023
    }, headers=headers)
    assert put_res.status_code == 200
    prof = put_res.json()
    assert prof["college_name"] == "MIT World Peace University"
    assert prof["degree"] == "B.Tech"
    assert prof["current_semester"] == 6
    assert prof["roll_number"] == "MIT-2023-AI-042"

    # 3. Retrieve profile again
    get_res2 = await ac.get("/api/v1/academics/profile", headers=headers)
    assert get_res2.status_code == 200
    assert get_res2.json()["roll_number"] == "MIT-2023-AI-042"
    await ac.aclose()


@pytest.mark.asyncio
async def test_subject_crud_and_attendance_calculations():
    ac, headers, user_id = await get_authenticated_client("subjects")

    # 1. Create Subject with 39 attended out of 50 total (78%), target 80%
    sub_res = await ac.post("/api/v1/academics/subjects", json={
        "name": "Data Structures & Algorithms",
        "code": "CS201",
        "credits": 4,
        "semester": 6,
        "faculty_name": "Prof. Donald Knuth",
        "color": "#6366F1",
        "total_classes": 50,
        "attended_classes": 39,
        "target_attendance": 80.0,
        "min_attendance": 75.0
    }, headers=headers)
    assert sub_res.status_code == 201
    sub = sub_res.json()
    sub_id = sub["id"]
    assert sub["name"] == "Data Structures & Algorithms"
    assert sub["current_percentage"] == 78.0
    # target is 80%: (80*50 - 3900) / 20 = 100 / 20 = 5 classes needed
    assert sub["needed_classes"] == 5
    assert sub["bunkable_classes"] == 0

    # 2. Get subject by ID
    get_sub = await ac.get(f"/api/v1/academics/subjects/{sub_id}", headers=headers)
    assert get_sub.status_code == 200
    assert get_sub.json()["id"] == sub_id

    # 3. Update subject attendance (attended 45 / 50 = 90%)
    up_sub = await ac.put(f"/api/v1/academics/subjects/{sub_id}", json={
        "attended_classes": 45,
        "total_classes": 50
    }, headers=headers)
    assert up_sub.status_code == 200
    updated = up_sub.json()
    assert updated["current_percentage"] == 90.0
    assert updated["status_indicator"] == "SAFE"
    # bunkable: 45 * 100 / 80 - 50 = 56 - 50 = 6 safe bunks
    assert updated["bunkable_classes"] == 6
    assert updated["needed_classes"] == 0

    # 4. Attendance Projection
    proj_res = await ac.get(f"/api/v1/academics/attendance/{sub_id}/projection", headers=headers)
    assert proj_res.status_code == 200
    proj = proj_res.json()
    assert proj["current_percentage"] == 90.0
    # If miss next 1: 45 / 51 = 88.2%
    assert proj["if_miss_next_1"] == 88.2
    # If attend next 1: 46 / 51 = 90.2%
    assert proj["if_attend_next_1"] == 90.2

    # 5. Delete subject
    del_res = await ac.delete(f"/api/v1/academics/subjects/{sub_id}", headers=headers)
    assert del_res.status_code == 200
    # Confirm deletion
    get_after_del = await ac.get(f"/api/v1/academics/subjects/{sub_id}", headers=headers)
    assert get_after_del.status_code == 404
    await ac.aclose()


@pytest.mark.asyncio
async def test_attendance_logging_and_summary():
    ac, headers, user_id = await get_authenticated_client("att_log")

    # Create subject starting with 0 classes
    sub_res = await ac.post("/api/v1/academics/subjects", json={
        "name": "Operating Systems",
        "code": "CS302",
        "credits": 3,
        "total_classes": 0,
        "attended_classes": 0,
        "target_attendance": 80.0
    }, headers=headers)
    sub_id = sub_res.json()["id"]

    # Mark PRESENT
    mark1 = await ac.post(f"/api/v1/academics/subjects/{sub_id}/attendance", json={
        "subject_id": sub_id,
        "date": "2026-09-27",
        "status": "PRESENT",
        "remarks": "Process Scheduling lecture"
    }, headers=headers)
    assert mark1.status_code == 201

    # Mark ABSENT
    mark2 = await ac.post(f"/api/v1/academics/subjects/{sub_id}/attendance", json={
        "subject_id": sub_id,
        "date": "2026-09-28",
        "status": "ABSENT",
        "remarks": "Medical reason"
    }, headers=headers)
    assert mark2.status_code == 201

    # Check subject: total should be 2, attended should be 1, current_pct = 50.0%
    sub_check = await ac.get(f"/api/v1/academics/subjects/{sub_id}", headers=headers)
    assert sub_check.status_code == 200
    assert sub_check.json()["total_classes"] == 2
    assert sub_check.json()["attended_classes"] == 1
    assert sub_check.json()["current_percentage"] == 50.0

    # Check attendance history
    hist_res = await ac.get(f"/api/v1/academics/subjects/{sub_id}/attendance", headers=headers)
    assert hist_res.status_code == 200
    assert len(hist_res.json()) == 2

    # Check summary
    summ_res = await ac.get("/api/v1/academics/attendance/summary", headers=headers)
    assert summ_res.status_code == 200
    summ = summ_res.json()
    assert summ["total_classes"] == 2
    assert summ["attended_classes"] == 1
    assert summ["overall_percentage"] == 50.0
    await ac.aclose()


@pytest.mark.asyncio
async def test_timetable_assignments_exams_marks_projects_notes():
    ac, headers, user_id = await get_authenticated_client("full_suite")

    # Create Subject
    sub_res = await ac.post("/api/v1/academics/subjects", json={
        "name": "Database Management Systems",
        "code": "CS401",
        "credits": 4,
        "total_classes": 20,
        "attended_classes": 18,
        "target_attendance": 80.0
    }, headers=headers)
    sub_id = sub_res.json()["id"]

    # 1. Timetable Slot
    tt_res = await ac.post("/api/v1/academics/timetable", json={
        "subject_id": sub_id,
        "day_of_week": 0, # Monday
        "start_time": "10:00",
        "end_time": "11:00",
        "room": "Room 404",
        "faculty_name": "Prof. Codd"
    }, headers=headers)
    assert tt_res.status_code == 201
    slot_id = tt_res.json()["id"]

    tt_list = await ac.get("/api/v1/academics/timetable", headers=headers)
    assert tt_list.status_code == 200
    assert len(tt_list.json()) == 1

    # 2. Assignment
    due = (datetime.now() + timedelta(days=5)).isoformat()
    asgn_res = await ac.post("/api/v1/academics/assignments", json={
        "subject_id": sub_id,
        "title": "SQL Query Optimization Assignment",
        "description": "Index design and execution plans",
        "due_date": due,
        "priority": "HIGH",
        "total_marks": 25.0
    }, headers=headers)
    assert asgn_res.status_code == 201
    asgn_id = asgn_res.json()["id"]

    # Update Assignment to COMPLETED
    asgn_up = await ac.put(f"/api/v1/academics/assignments/{asgn_id}", json={
        "status": "COMPLETED",
        "obtained_marks": 24.0
    }, headers=headers)
    assert asgn_up.status_code == 200
    assert asgn_up.json()["status"] == "COMPLETED"

    # 3. Exam
    exm_date = (datetime.now() + timedelta(days=10)).isoformat()
    exm_res = await ac.post("/api/v1/academics/exams", json={
        "subject_id": sub_id,
        "title": "DBMS Midterm Examination",
        "exam_type": "MIDTERM",
        "exam_date": exm_date,
        "venue": "Hall A",
        "syllabus_covered": "Relational Algebra, SQL, Normalization",
        "max_marks": 50.0
    }, headers=headers)
    assert exm_res.status_code == 201
    exm_id = exm_res.json()["id"]

    # 4. Internal Marks
    mark_res = await ac.post("/api/v1/academics/marks", json={
        "subject_id": sub_id,
        "assessment_name": "Quiz 1: SQL Joins",
        "assessment_type": "QUIZ",
        "marks_obtained": 19.0,
        "max_marks": 20.0,
        "assessment_date": "2026-09-25",
        "remarks": "Top score in batch"
    }, headers=headers)
    assert mark_res.status_code == 201
    assert mark_res.json()["percentage"] == 95.0

    # 5. Academic Project
    proj_res = await ac.post("/api/v1/academics/projects", json={
        "subject_id": sub_id,
        "title": "Distributed Key-Value Store",
        "description": "Raft consensus implementation in Go",
        "status": "IN_PROGRESS",
        "repository_url": "https://github.com/student/raft-kv",
        "documentation_url": "https://docs.webverse.ai/projects/raft"
    }, headers=headers)
    assert proj_res.status_code == 201
    assert proj_res.json()["title"] == "Distributed Key-Value Store"

    # 6. Academic Note
    note_res = await ac.post("/api/v1/academics/notes", json={
        "subject_id": sub_id,
        "title": "B-Tree Indexing Deep Dive",
        "description": "Notes from today's disk block splitting lecture",
        "tags": "dbms,btree,indexes"
    }, headers=headers)
    assert note_res.status_code == 201
    assert note_res.json()["tags"] == "dbms,btree,indexes"

    # 7. Academic Dashboard Glance
    dash_res = await ac.get("/api/v1/academics/dashboard", headers=headers)
    assert dash_res.status_code == 200
    dash = dash_res.json()
    assert dash["subjects_count"] == 1
    assert dash["attendance"]["overall_percentage"] == 90.0
    assert dash["projects_count"] == 1
    assert dash["notes_count"] == 1
    await ac.aclose()


@pytest.mark.asyncio
async def test_user_isolation_and_security():
    ac1, headers1, user1_id = await get_authenticated_client("user_a")
    ac2, headers2, user2_id = await get_authenticated_client("user_b")

    # User 1 creates Subject
    sub_res = await ac1.post("/api/v1/academics/subjects", json={
        "name": "Secret User 1 Subject",
        "code": "U1-001",
        "total_classes": 10,
        "attended_classes": 9
    }, headers=headers1)
    sub1_id = sub_res.json()["id"]

    # User 2 tries to access User 1's subject -> must return 404
    get_res = await ac2.get(f"/api/v1/academics/subjects/{sub1_id}", headers=headers2)
    assert get_res.status_code == 404

    # User 2 tries to update User 1's subject -> must return 404
    up_res = await ac2.put(f"/api/v1/academics/subjects/{sub1_id}", json={"name": "Hacked"}, headers=headers2)
    assert up_res.status_code == 404

    # User 2 tries to delete User 1's subject -> must return 404
    del_res = await ac2.delete(f"/api/v1/academics/subjects/{sub1_id}", headers=headers2)
    assert del_res.status_code == 404

    # User 2 tries to log attendance for User 1's subject -> must return 404
    att_res = await ac2.post(f"/api/v1/academics/subjects/{sub1_id}/attendance", json={
        "subject_id": sub1_id,
        "date": "2026-09-27",
        "status": "PRESENT"
    }, headers=headers2)
    assert att_res.status_code == 404

    # Unauthenticated request -> must return 401
    unauth = await ac1.get("/api/v1/academics/subjects")
    assert unauth.status_code == 401

    await ac1.aclose()
    await ac2.aclose()


@pytest.mark.asyncio
async def test_validation_errors():
    ac, headers, user_id = await get_authenticated_client("val_err")

    # 1. Attended > Total on create -> 400
    invalid_sub = await ac.post("/api/v1/academics/subjects", json={
        "name": "Invalid Subject",
        "total_classes": 10,
        "attended_classes": 15
    }, headers=headers)
    assert invalid_sub.status_code == 400

    # 2. Negative marks on internal mark -> 400
    sub_res = await ac.post("/api/v1/academics/subjects", json={"name": "Valid Sub", "total_classes": 0, "attended_classes": 0}, headers=headers)
    s_id = sub_res.json()["id"]

    neg_mark = await ac.post("/api/v1/academics/marks", json={
        "subject_id": s_id,
        "assessment_name": "Test",
        "marks_obtained": -5.0,
        "max_marks": 20.0
    }, headers=headers)
    assert neg_mark.status_code == 400

    zero_max = await ac.post("/api/v1/academics/marks", json={
        "subject_id": s_id,
        "assessment_name": "Test",
        "marks_obtained": 5.0,
        "max_marks": 0.0
    }, headers=headers)
    assert zero_max.status_code == 400

    await ac.aclose()
