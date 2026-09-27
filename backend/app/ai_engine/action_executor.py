from datetime import datetime, date, timezone
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.finance import Transaction, ExpenseCategory, TransactionType, PaymentMethod
from app.models.academic import AttendanceRecord, Subject, AttendanceStatus, Assignment, AssignmentStatus
from app.models.life_admin import Reminder, ReminderPriority

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
                notes="Marked via Webverse AI"
            )
            db.add(rec)
            await db.commit()
            return {"status": "SUCCESS", "message": f"Marked {subject.name} as {status_enum.value} for today"}

        elif action_type == "CREATE_REMINDER":
            title = params.get("title", "New Reminder")
            due_at_str = params.get("due_at")
            due_dt = datetime.now(timezone.utc)
            if due_at_str:
                try:
                    due_dt = datetime.fromisoformat(due_at_str)
                except Exception:
                    pass

            rem = Reminder(
                user_id=user_id,
                title=title,
                due_at=due_dt,
                priority=ReminderPriority.MEDIUM,
                linked_module=params.get("linked_module", "LIFE_ADMIN")
            )
            db.add(rem)
            await db.commit()
            return {"status": "SUCCESS", "message": f"Created reminder: '{title}'"}

        return {"status": "FAILED", "message": f"Unknown action type: {action_type}"}
