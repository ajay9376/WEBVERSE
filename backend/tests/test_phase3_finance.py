import pytest
import uuid
from httpx import AsyncClient, ASGITransport
from datetime import date, timedelta
from decimal import Decimal
from main import app

@pytest.mark.asyncio
async def test_finance_categories_crud_and_defaults():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        uid = uuid.uuid4().hex[:6]
        # 1. Register and login User A
        reg_resp = await ac.post("/api/v1/auth/register", json={
            "email": f"finance_user_a_{uid}@webverse.ai",
            "password": "SecurePassword123!",
            "full_name": "Finance Alpha"
        })
        assert reg_resp.status_code in (200, 201)
        token = reg_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. List categories (seeds defaults automatically)
        cats_resp = await ac.get("/api/v1/finance/categories", headers=headers)
        assert cats_resp.status_code == 200
        cats = cats_resp.json()
        assert len(cats) >= 5
        cat_names = [c["name"] for c in cats]
        assert "Food & Dining" in cat_names
        assert "Travel & Transit" in cat_names

        # 3. Create custom category
        new_cat_resp = await ac.post("/api/v1/finance/categories", json={
            "name": "Hostel Rent",
            "category_type": "EXPENSE",
            "icon": "home",
            "color": "#6366F1",
            "budget_limit": "8000.00"
        }, headers=headers)
        assert new_cat_resp.status_code == 201
        new_cat = new_cat_resp.json()
        assert new_cat["name"] == "Hostel Rent"
        assert Decimal(str(new_cat["budget_limit"])) == Decimal("8000.00")
        cat_id = new_cat["id"]

        # 4. Update category
        upd_cat_resp = await ac.put(f"/api/v1/finance/categories/{cat_id}", json={
            "name": "Hostel & Room Rent",
            "budget_limit": "9000.00"
        }, headers=headers)
        assert upd_cat_resp.status_code == 200
        assert upd_cat_resp.json()["name"] == "Hostel & Room Rent"
        assert Decimal(str(upd_cat_resp.json()["budget_limit"])) == Decimal("9000.00")

@pytest.mark.asyncio
async def test_finance_transactions_crud_and_deterministic_math():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        uid = uuid.uuid4().hex[:6]
        # Register User
        reg_resp = await ac.post("/api/v1/auth/register", json={
            "email": f"finance_math_{uid}@webverse.ai",
            "password": "SecurePassword123!",
            "full_name": "Math Auditor"
        })
        assert reg_resp.status_code in (200, 201)
        token = reg_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Validate negative amount rejection
        bad_tx = await ac.post("/api/v1/finance/transactions", json={
            "title": "Invalid Negative Spend",
            "amount": -500.0,
            "type": "EXPENSE"
        }, headers=headers)
        assert bad_tx.status_code == 422 or bad_tx.status_code == 400

        # Create Income: ₹30,000 (e.g. stipend / allowance)
        today_str = date.today().isoformat()
        inc_resp = await ac.post("/api/v1/finance/transactions", json={
            "title": "Monthly Fellowship Stipend",
            "merchant": "University Research Lab",
            "amount": "30000.00",
            "type": "INCOME",
            "date": today_str,
            "payment_method": "BANK_TRANSFER",
            "category_name": "Salary / Allowance"
        }, headers=headers)
        assert inc_resp.status_code == 201
        assert Decimal(str(inc_resp.json()["amount"])) == Decimal("30000.00")

        # Create Expense 1: Food ₹5,200
        exp1_resp = await ac.post("/api/v1/finance/transactions", json={
            "title": "Mess Monthly Mess Fee",
            "merchant": "Hostel Mess",
            "amount": "5200.00",
            "type": "EXPENSE",
            "date": today_str,
            "payment_method": "UPI",
            "category_name": "Food & Dining"
        }, headers=headers)
        assert exp1_resp.status_code == 201

        # Create Expense 2: Books ₹1,500
        exp2_resp = await ac.post("/api/v1/finance/transactions", json={
            "title": "Algorithms & System Design Books",
            "merchant": "BookStore",
            "amount": "1500.00",
            "type": "EXPENSE",
            "date": today_str,
            "payment_method": "CARD",
            "category_name": "Education & Books"
        }, headers=headers)
        assert exp2_resp.status_code == 201
        tx2_id = exp2_resp.json()["id"]

        # Verify summary endpoint deterministic math
        # Total Income = 30,000, Total Expenses = 6,700, Net Balance = 23,300, Savings % = 77.67%
        sum_resp = await ac.get("/api/v1/finance/summary", headers=headers)
        assert sum_resp.status_code == 200
        sum_data = sum_resp.json()
        assert Decimal(str(sum_data["income"])) == Decimal("30000.00")
        assert Decimal(str(sum_data["expenses"])) == Decimal("6700.00")
        assert Decimal(str(sum_data["net_balance"])) == Decimal("23300.00")
        assert round(sum_data["savings_percentage"], 2) == 77.67

        # Verify category analytics breakdown
        cat_analytics_resp = await ac.get("/api/v1/finance/analytics/categories", headers=headers)
        assert cat_analytics_resp.status_code == 200
        ca_data = cat_analytics_resp.json()
        assert Decimal(str(ca_data["total_expenses"])) == Decimal("6700.00")
        # Food is 5200 / 6700 = 77.6%, Education is 1500 / 6700 = 22.4%
        cat_map = {c["category_name"]: c for c in ca_data["categories"]}
        assert "Food & Dining" in cat_map
        assert Decimal(str(cat_map["Food & Dining"]["amount"])) == Decimal("5200.00")
        assert cat_map["Food & Dining"]["percentage"] == 77.6

        # Update Expense 2: change amount to ₹2,000
        upd_tx_resp = await ac.put(f"/api/v1/finance/transactions/{tx2_id}", json={
            "amount": "2000.00",
            "notes": "Added reference workbook"
        }, headers=headers)
        assert upd_tx_resp.status_code == 200
        assert Decimal(str(upd_tx_resp.json()["amount"])) == Decimal("2000.00")

        # Verify updated balance: expenses = 7,200, balance = 22,800
        sum_resp2 = await ac.get("/api/v1/finance/summary", headers=headers)
        assert Decimal(str(sum_resp2.json()["expenses"])) == Decimal("7200.00")
        assert Decimal(str(sum_resp2.json()["net_balance"])) == Decimal("22800.00")

@pytest.mark.asyncio
async def test_finance_budgets_and_over_budget_detection():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        uid = uuid.uuid4().hex[:6]
        reg_resp = await ac.post("/api/v1/auth/register", json={
            "email": f"finance_budget_{uid}@webverse.ai",
            "password": "SecurePassword123!",
            "full_name": "Budget Auditor"
        })
        assert reg_resp.status_code in (200, 201)
        token = reg_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        today = date.today()
        # Set Overall Monthly Budget: ₹10,000
        budget_resp = await ac.post("/api/v1/finance/budgets", json={
            "amount": "10000.00",
            "month": today.month,
            "year": today.year
        }, headers=headers)
        assert budget_resp.status_code == 201
        assert Decimal(str(budget_resp.json()["amount"])) == Decimal("10000.00")

        # Add an expense of ₹6,000
        await ac.post("/api/v1/finance/transactions", json={
            "title": "Semester Registration Fee",
            "amount": "6000.00",
            "type": "EXPENSE",
            "date": today.isoformat()
        }, headers=headers)

        # Check budget summary: spent = 6000, remaining = 4000, percentage_used = 60.0%, is_over_budget = False
        bs_resp1 = await ac.get("/api/v1/finance/budgets/summary", headers=headers)
        assert bs_resp1.status_code == 200
        bs1 = bs_resp1.json()
        assert Decimal(str(bs1["overall_budget"])) == Decimal("10000.00")
        assert Decimal(str(bs1["total_spent"])) == Decimal("6000.00")
        assert Decimal(str(bs1["remaining_budget"])) == Decimal("4000.00")
        assert bs1["percentage_used"] == 60.0
        assert bs1["is_over_budget"] is False

        # Add another expense of ₹6,500 (total = 12,500 -> exceeds 10,000 budget)
        await ac.post("/api/v1/finance/transactions", json={
            "title": "Laptop Repair & RAM Upgrade",
            "amount": "6500.00",
            "type": "EXPENSE",
            "date": today.isoformat()
        }, headers=headers)

        # Check over-budget state: spent = 12500, remaining = -2500, is_over_budget = True
        bs_resp2 = await ac.get("/api/v1/finance/budgets/summary", headers=headers)
        assert bs_resp2.status_code == 200
        bs2 = bs_resp2.json()
        assert Decimal(str(bs2["total_spent"])) == Decimal("12500.00")
        assert Decimal(str(bs2["remaining_budget"])) == Decimal("-2500.00")
        assert bs2["percentage_used"] == 125.0
        assert bs2["is_over_budget"] is True

@pytest.mark.asyncio
async def test_finance_subscriptions_management_and_cycles():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        uid = uuid.uuid4().hex[:6]
        reg_resp = await ac.post("/api/v1/auth/register", json={
            "email": f"finance_subs_{uid}@webverse.ai",
            "password": "SecurePassword123!",
            "full_name": "Subscription Auditor"
        })
        assert reg_resp.status_code in (200, 201)
        token = reg_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        today = date.today()
        renewal = today + timedelta(days=15)

        # Create Monthly Subscription: Spotify ₹119/mo
        sub1 = await ac.post("/api/v1/finance/subscriptions", json={
            "name": "Spotify Premium Student",
            "amount": "119.00",
            "billing_cycle": "MONTHLY",
            "next_billing_date": renewal.isoformat(),
            "payment_method": "UPI",
            "status": "ACTIVE"
        }, headers=headers)
        assert sub1.status_code == 201
        assert Decimal(str(sub1.json()["monthly_equivalent"])) == Decimal("119.00")

        # Create Yearly Subscription: GitHub Copilot Pro ₹1,200/yr -> ₹100.00/mo equivalent
        sub2 = await ac.post("/api/v1/finance/subscriptions", json={
            "name": "GitHub Copilot Pro",
            "amount": "1200.00",
            "billing_cycle": "YEARLY",
            "next_billing_date": renewal.isoformat(),
            "payment_method": "CARD",
            "status": "ACTIVE"
        }, headers=headers)
        assert sub2.status_code == 201
        assert Decimal(str(sub2.json()["monthly_equivalent"])) == Decimal("100.00")
        sub2_id = sub2.json()["id"]

        # Verify subscriptions list and dashboard totals
        subs_list_resp = await ac.get("/api/v1/finance/subscriptions", headers=headers)
        assert subs_list_resp.status_code == 200
        assert len(subs_list_resp.json()) == 2

        # Check Dashboard API aggregation
        dash_resp = await ac.get("/api/v1/finance/dashboard", headers=headers)
        assert dash_resp.status_code == 200
        dash = dash_resp.json()
        assert dash["active_subscriptions_count"] == 2
        assert Decimal(str(dash["monthly_subscription_total"])) == Decimal("219.00")

        # Pause subscription 2
        upd_sub = await ac.put(f"/api/v1/finance/subscriptions/{sub2_id}", json={
            "status": "PAUSED"
        }, headers=headers)
        assert upd_sub.status_code == 200
        assert upd_sub.json()["status"] == "PAUSED"

@pytest.mark.asyncio
async def test_finance_user_isolation_and_security():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        uid = uuid.uuid4().hex[:6]
        # Register User A
        reg_a = await ac.post("/api/v1/auth/register", json={
            "email": f"user_a_fin_{uid}@webverse.ai",
            "password": "Password123!",
            "full_name": "User Alpha"
        })
        assert reg_a.status_code in (200, 201)
        token_a = reg_a.json()["access_token"]
        headers_a = {"Authorization": f"Bearer {token_a}"}

        # Register User B
        reg_b = await ac.post("/api/v1/auth/register", json={
            "email": f"user_b_fin_{uid}@webverse.ai",
            "password": "Password123!",
            "full_name": "User Beta"
        })
        assert reg_b.status_code in (200, 201)
        token_b = reg_b.json()["access_token"]
        headers_b = {"Authorization": f"Bearer {token_b}"}

        # User A creates a transaction
        tx_a = await ac.post("/api/v1/finance/transactions", json={
            "title": "Alpha Secret Expense",
            "amount": "10000.00",
            "type": "EXPENSE",
            "date": date.today().isoformat()
        }, headers=headers_a)
        assert tx_a.status_code == 201
        tx_a_id = tx_a.json()["id"]

        # User B attempts to access User A's transaction -> MUST return 404
        get_b = await ac.get(f"/api/v1/finance/transactions/{tx_a_id}", headers=headers_b)
        assert get_b.status_code == 404

        # User B attempts to update User A's transaction -> MUST return 404
        put_b = await ac.put(f"/api/v1/finance/transactions/{tx_a_id}", json={"amount": "1.00"}, headers=headers_b)
        assert put_b.status_code == 404

        # User B attempts to delete User A's transaction -> MUST return 404
        del_b = await ac.delete(f"/api/v1/finance/transactions/{tx_a_id}", headers=headers_b)
        assert del_b.status_code == 404

        # User A creates a subscription
        sub_a = await ac.post("/api/v1/finance/subscriptions", json={
            "name": "Alpha Private Subscription",
            "amount": "500.00",
            "billing_cycle": "MONTHLY",
            "next_billing_date": (date.today() + timedelta(days=10)).isoformat()
        }, headers=headers_a)
        assert sub_a.status_code == 201
        sub_a_id = sub_a.json()["id"]

        # User B attempts to delete User A's subscription -> MUST return 404
        del_sub_b = await ac.delete(f"/api/v1/finance/subscriptions/{sub_a_id}", headers=headers_b)
        assert del_sub_b.status_code == 404
