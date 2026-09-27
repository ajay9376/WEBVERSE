from datetime import datetime, date, timezone, timedelta
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.finance import Transaction, ExpenseCategory, TransactionType, PaymentMethod
from app.models.academic import AttendanceRecord, Subject, AttendanceStatus, Assignment, AssignmentStatus, AssignmentPriority
from app.models.life_admin import Reminder, ReminderPriority, Bill, BillStatus, RecurrencePattern

class ActionExecutor:
    @staticmethod
    async def execute_action(db: AsyncSession, user_id: str, action_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
        if action_type == "CREATE_EXPENSE":
            amount = float(params.get("amount", 0.0))
            title = params.get("title", "AI Logged Expense")
            category_name = params.get("category_name", "General")
            
            # Find or create category
            cat_stmt = select(ExpenseCategory).where(
                ExpenseCategory.user_id == user_id, 
                ExpenseCategory.name.ilike(category_name)
            )
            c_res = await db.execute(cat_stmt)
            cat = c_res.scalars().first()
            if not cat:
                cat = ExpenseCategory(
                    user_id=user_id,
                    name=category_name.capitalize(),
                    color="#10B981"
                )
                db.add(cat)
                await db.flush()

            tx = Transaction(
                user_id=user_id,
                category_id=cat.id,
                title=title,
                amount=amount,
                type=TransactionType.EXPENSE,
                date=date.today(),
                payment_method=PaymentMethod.UPI
            )
            db.add(tx)
            await db.commit()
            return {"status": "SUCCESS", "message": f"Successfully created expense of ₹{amount:,.2f} for '{title}'"}

        elif action_type == "MARK_ATTENDANCE":
            subject_name = params.get("subject_name", "")
            status_str = params.get("status", "PRESENT").upper()
            status_enum = AttendanceStatus[status_str] if status_str in AttendanceStatus.__members__ else AttendanceStatus.PRESENT

            sub_stmt = select(Subject).where(
                Subject.user_id == user_id,
                Subject.name.ilike(f"%{subject_name}%")
            )
            s_res = await db.execute(sub_stmt)
            subject = s_res.scalars().first()
            if not subject:
                return {"status": "FAILED", "message": f"Subject '{subject_name}' not found"}

            rec = AttendanceRecord(
                user_id=user_id,
                subject_id=subject.id,
                date=date.today(),
                status=status_enum,
                remarks="Marked via Webverse AI"
            )
            db.add(rec)
            subject.total_classes = (subject.total_classes or 0) + 1
            if status_enum in (AttendanceStatus.PRESENT, AttendanceStatus.DUTY):
                subject.attended_classes = (subject.attended_classes or 0) + 1
            await db.commit()
            return {"status": "SUCCESS", "message": f"Marked {subject.name} as {status_enum.value} for today"}

        elif action_type == "CREATE_REMINDER":
            title = params.get("title", "New Reminder")
            due_at_str = params.get("due_at")
            due_dt = datetime.now(timezone.utc) + timedelta(days=1)
            if due_at_str:
                try:
                    due_dt = datetime.fromisoformat(due_at_str)
                except Exception:
                    pass

            p_str = params.get("priority", "MEDIUM").upper()
            priority_enum = ReminderPriority[p_str] if p_str in ReminderPriority.__members__ else ReminderPriority.MEDIUM

            rem = Reminder(
                user_id=user_id,
                title=title,
                due_at=due_dt,
                priority=priority_enum,
                linked_module=params.get("linked_module", "LIFE_ADMIN")
            )
            db.add(rem)
            await db.commit()
            return {"status": "SUCCESS", "message": f"Created reminder: '{title}'"}

        elif action_type == "CREATE_BILL":
            title = params.get("title", "New Bill")
            provider = params.get("provider", "Utility Provider")
            amount = float(params.get("amount", 0.0))
            category = params.get("category", "UTILITIES")
            due_date_str = params.get("due_date")
            due_dt = datetime.now(timezone.utc) + timedelta(days=7)
            if due_date_str:
                try:
                    due_dt = datetime.fromisoformat(due_date_str)
                except Exception:
                    pass

            bill = Bill(
                user_id=user_id,
                title=title,
                provider=provider,
                amount=amount,
                category=category,
                due_date=due_dt,
                status=BillStatus.PENDING,
                recurring=bool(params.get("recurring", False)),
                recurrence=RecurrencePattern.MONTHLY if params.get("recurring") else RecurrencePattern.NONE
            )
            db.add(bill)
            await db.commit()
            return {"status": "SUCCESS", "message": f"Successfully created bill '{title}' for ₹{amount:,.2f}"}

        elif action_type == "CREATE_ASSIGNMENT":
            title = params.get("title", "New Assignment")
            subject_name = params.get("subject_name", "")
            description = params.get("description", "Created via Webverse AI")
            total_marks = float(params.get("total_marks", 100.0))
            due_date_str = params.get("due_date")
            due_dt = datetime.now(timezone.utc) + timedelta(days=5)
            if due_date_str:
                try:
                    due_dt = datetime.fromisoformat(due_date_str)
                except Exception:
                    pass

            sub_stmt = select(Subject).where(
                Subject.user_id == user_id,
                Subject.name.ilike(f"%{subject_name}%")
            )
            s_res = await db.execute(sub_stmt)
            subject = s_res.scalars().first()
            if not subject:
                return {"status": "FAILED", "message": f"Subject '{subject_name}' not found for assignment"}

            asgn = Assignment(
                user_id=user_id,
                subject_id=subject.id,
                title=title,
                description=description,
                due_date=due_dt,
                status=AssignmentStatus.PENDING,
                priority=AssignmentPriority.MEDIUM,
                total_marks=total_marks
            )
            db.add(asgn)
            await db.commit()
            return {"status": "SUCCESS", "message": f"Successfully created assignment '{title}' for {subject.name}"}

        return {"status": "FAILED", "message": f"Unknown action type: {action_type}"}
