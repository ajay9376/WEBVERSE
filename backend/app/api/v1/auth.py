from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, date, timedelta, timezone
from app.core.database import get_db
from app.core.security import get_password_hash, verify_password, create_access_token, get_current_user
from app.models.user import User
from app.models.academic import Subject, AttendanceRecord, TimetableSlot, Assignment, Exam, AttendanceStatus, AssignmentStatus
from app.models.finance import ExpenseCategory, Transaction, Budget, Subscription, TransactionType, PaymentMethod
from app.models.life_admin import Document, Reminder, DocumentCategory, ReminderPriority
from app.schemas.auth import UserRegisterRequest, UserLoginRequest, TokenResponse, UserProfileResponse, UserUpdateRequest

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=TokenResponse)
async def register(user_in: UserRegisterRequest, db: AsyncSession = Depends(get_db)):
    # Check if user already exists
    res = await db.execute(select(User).where(User.email == user_in.email))
    if res.scalars().first():
        raise HTTPException(status_code=400, detail="A user with this email already exists")

    new_user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        college_name=user_in.college_name,
        semester=user_in.semester,
        branch=user_in.branch,
        monthly_budget_target=user_in.monthly_budget_target or "10000"
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # Automatically create default expense categories
    default_cats = [
        ("Food & Dining", "utensils", "#EF4444", 4000.0),
        ("College & Books", "book-open", "#8B5CF6", 2000.0),
        ("Travel & Transit", "car", "#3B82F6", 1500.0),
        ("Bills & Utilities", "zap", "#F59E0B", 1000.0),
        ("Subscriptions", "tv", "#10B981", 1000.0),
        ("Shopping & Leisure", "shopping-bag", "#EC4899", 1500.0)
    ]
    for name, icon, color, budget in default_cats:
        cat = ExpenseCategory(user_id=new_user.id, name=name, icon=icon, color=color, budget_limit=budget)
        db.add(cat)
    await db.commit()

    token = create_access_token(new_user.id)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user_id=new_user.id,
        email=new_user.email,
        full_name=new_user.full_name
    )

@router.post("/login", response_model=TokenResponse)
async def login(login_in: UserLoginRequest, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(User).where(User.email == login_in.email))
    user = res.scalars().first()
    if not user or not verify_password(login_in.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    
    token = create_access_token(user.id)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user_id=user.id,
        email=user.email,
        full_name=user.full_name
    )

@router.get("/me", response_model=UserProfileResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/seed-demo")
async def seed_demo_data(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """
    Seeds rich connected multiverse records for the user.
    """
    today = date.today()
    now = datetime.now(timezone.utc)

    # 1. Subjects
    daa = Subject(user_id=current_user.id, name="Design & Analysis of Algorithms", code="CS501", professor="Dr. Sharma", color="#8B5CF6", min_attendance_percent=75.0, target_attendance_percent=85.0)
    os_sub = Subject(user_id=current_user.id, name="Operating Systems", code="CS502", professor="Prof. Verma", color="#06B6D4", min_attendance_percent=75.0, target_attendance_percent=80.0)
    dbms = Subject(user_id=current_user.id, name="Database Management Systems", code="CS503", professor="Dr. Iyer", color="#10B981", min_attendance_percent=75.0, target_attendance_percent=85.0)
    cn = Subject(user_id=current_user.id, name="Computer Networks", code="CS504", professor="Prof. Roy", color="#F59E0B", min_attendance_percent=75.0, target_attendance_percent=80.0)
    db.add_all([daa, os_sub, dbms, cn])
    await db.flush()

    # Attendance logs (DAA: 18/24 = 75%)
    for i in range(24):
        d = today - timedelta(days=28 - i)
        status = AttendanceStatus.PRESENT if i < 18 else AttendanceStatus.ABSENT
        db.add(AttendanceRecord(user_id=current_user.id, subject_id=daa.id, date=d, status=status))

    # OS: 20/22 = 90.9%
    for i in range(22):
        d = today - timedelta(days=26 - i)
        status = AttendanceStatus.PRESENT if i < 20 else AttendanceStatus.ABSENT
        db.add(AttendanceRecord(user_id=current_user.id, subject_id=os_sub.id, date=d, status=status))

    # DBMS: 14/20 = 70% (Critical)
    for i in range(20):
        d = today - timedelta(days=24 - i)
        status = AttendanceStatus.PRESENT if i < 14 else AttendanceStatus.ABSENT
        db.add(AttendanceRecord(user_id=current_user.id, subject_id=dbms.id, date=d, status=status))

    # 2. Upcoming Assignments & Exams
    db.add(Assignment(
        user_id=current_user.id,
        subject_id=daa.id,
        title="Dynamic Programming Greedy Graph Problems",
        due_date=now + timedelta(days=3),
        status=AssignmentStatus.PENDING,
        total_marks=25.0
    ))
    db.add(Assignment(
        user_id=current_user.id,
        subject_id=dbms.id,
        title="B+ Tree Indexing & SQL Optimization Assignment",
        due_date=now + timedelta(days=6),
        status=AssignmentStatus.IN_PROGRESS,
        total_marks=20.0
    ))

    db.add(Exam(
        user_id=current_user.id,
        subject_id=daa.id,
        title="DAA Mid-Semester Theory Exam",
        exam_date=now + timedelta(days=5),
        location="Hall 302, Academic Block B",
        syllabus_covered="Divide & Conquer, Greedy Methods, Dynamic Programming, NP-Completeness",
        total_marks=50.0
    ))
    db.add(Exam(
        user_id=current_user.id,
        subject_id=os_sub.id,
        title="OS Lab Practical & Viva",
        exam_date=now + timedelta(days=8),
        location="Computer Lab 4",
        syllabus_covered="Process Synchronization, Semaphores, Deadlock Avoidance Algorithms",
        total_marks=40.0
    ))

    # 3. Timetable
    db.add(TimetableSlot(user_id=current_user.id, subject_id=daa.id, day_of_week=0, start_time="09:00", end_time="10:00", room="B-301"))
    db.add(TimetableSlot(user_id=current_user.id, subject_id=os_sub.id, day_of_week=0, start_time="10:00", end_time="11:00", room="B-302"))
    db.add(TimetableSlot(user_id=current_user.id, subject_id=dbms.id, day_of_week=1, start_time="11:15", end_time="12:15", room="Lab 2"))

    # 4. Transactions & Categories
    cat_res = await db.execute(select(ExpenseCategory).where(ExpenseCategory.user_id == current_user.id))
    cats = {c.name: c for c in cat_res.scalars().all()}
    
    food_cat = cats.get("Food & Dining")
    travel_cat = cats.get("Travel & Transit")
    bills_cat = cats.get("Bills & Utilities")

    if food_cat:
        db.add(Transaction(user_id=current_user.id, category_id=food_cat.id, title="Campus Cafeteria Lunch & Coffee", amount=280.0, date=today - timedelta(days=1)))
        db.add(Transaction(user_id=current_user.id, category_id=food_cat.id, title="Weekend Pizza Dinner with Friends", amount=850.0, date=today - timedelta(days=3)))
        db.add(Transaction(user_id=current_user.id, category_id=food_cat.id, title="Grocery & Healthy Snacks", amount=1240.0, date=today - timedelta(days=7)))
    if travel_cat:
        db.add(Transaction(user_id=current_user.id, category_id=travel_cat.id, title="Metro Smart Card Recharge", amount=500.0, date=today - timedelta(days=5)))
    if bills_cat:
        db.add(Transaction(user_id=current_user.id, category_id=bills_cat.id, title="Hostel High-Speed WiFi Subscription", amount=799.0, date=today - timedelta(days=10)))

    # Subscriptions
    db.add(Subscription(user_id=current_user.id, name="Spotify Student Premium", amount=59.0, billing_cycle="MONTHLY", next_billing_date=today + timedelta(days=12)))
    db.add(Subscription(user_id=current_user.id, name="GitHub Copilot Student", amount=0.0, billing_cycle="YEARLY", next_billing_date=today + timedelta(days=180)))

    # 5. Life Admin Documents & Reminders
    db.add(Reminder(
        user_id=current_user.id,
        title="Pay Hostel Electricity Bill",
        description="Pay before the 5th to avoid late penalty fee",
        due_at=now + timedelta(days=2),
        priority=ReminderPriority.HIGH,
        linked_module="FINANCE"
    ))
    db.add(Reminder(
        user_id=current_user.id,
        title="Submit Health Insurance Claim Receipt",
        due_at=now + timedelta(days=7),
        priority=ReminderPriority.MEDIUM,
        linked_module="LIFE_ADMIN"
    ))

    # Sample Document metadata
    import json
    doc_meta = {
        "policy_number": "POL-STAR-883921",
        "provider": "Star Health Insurance",
        "expiry_date": (today + timedelta(days=32)).strftime("%d/%m/%Y"),
        "premium": "₹4,200",
        "coverage": "₹5,00,000"
    }
    db.add(Document(
        user_id=current_user.id,
        filename="Health_Insurance_Policy_2026.pdf",
        stored_filename="demo_insurance.pdf",
        file_path="./uploads/demo_insurance.pdf",
        file_type="application/pdf",
        file_size=345.5,
        category=DocumentCategory.INSURANCE,
        tags="insurance,health,star_health,important",
        extracted_text="Star Health Comprehensive Student Insurance Policy. Policy Number: POL-STAR-883921. Valid till 30/10/2026. Total Sum Insured: Rs. 5,00,000. Annual Premium: Rs. 4,200.",
        metadata_json=json.dumps(doc_meta),
        is_indexed=True
    ))

    await db.commit()
    return {"status": "SUCCESS", "message": "Demo Multiverse records seeded successfully!"}
