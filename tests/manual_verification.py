import asyncio
import httpx
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database.database import AsyncSessionLocal
from app.repositories.user_repository import UserRepository
from app.models.user_type import UserType
from app.config.config import APP_PORT

BASE_URL = f"http://127.0.0.1:8000/api/v1"

async def setup_users():
    """Ensure we have an Accounting user."""
    repo = UserRepository()
    try:
        # Try to create, ignore if exists (repo throws conflict, we catch it or check before)
        # Actually repo.create_user throws Conflict if exists.
        # But we need to know the password.
        # Let's try to create 'accountant' with 'password'
        print("Setting up 'accountant' user...")
        user = await repo.create_user("accountant", "password", UserType.Accounting)
        print("Created 'accountant'.")
    except Exception as e:
        print(f"User 'accountant' might already exist or error: {e}")

    try:
        print("Setting up 'admin_test' user...")
        user = await repo.create_user("admin_test", "password", UserType.Administrator)
        print("Created 'admin_test'.")
    except:
        pass

async def get_token(username, password):
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{BASE_URL}/auth", json={"username": username, "password": password})
        if resp.status_code == 200:
            return resp.json()["token"]
        print(f"Login failed for {username}: {resp.text}")
        return None

async def run_verification():
    # 1. Setup Data
    await setup_users()

    # 2. Login
    token = await get_token("accountant", "password")
    if not token:
        print("Could not log in as accountant. Aborting.")
        return

    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient(headers=headers, base_url=BASE_URL) as client:
        # 3. Check Initial Balance
        print("Checking initial balance...")
        resp = await client.get("/accounting/balance")
        print(f"Initial Balance: {resp.text}")
        initial_balance = float(resp.json())

        # 4. Record Credit
        print("Recording Credit of 100.0...")
        credit_data = {
            "amount": 100.0,
            "type": "CREDIT",
            "description": "Initial Capital"
        }
        resp = await client.post("/accounting/transaction", json=credit_data)
        print(f"Credit Response: {resp.status_code} {resp.text}")
        assert resp.status_code == 201

        # 5. Check Balance
        resp = await client.get("/accounting/balance")
        new_balance = float(resp.json())
        print(f"New Balance (should be +100): {new_balance}")
        assert new_balance == initial_balance + 100.0

        # 6. Record Debit
        print("Recording Debit of 50.0...")
        debit_data = {
            "amount": 50.0,
            "type": "DEBIT",
            "description": "Expense"
        }
        resp = await client.post("/accounting/transaction", json=debit_data)
        print(f"Debit Response: {resp.status_code} {resp.text}")
        assert resp.status_code == 201

        # 7. Check Balance
        resp = await client.get("/accounting/balance")
        final_balance = float(resp.json())
        print(f"Final Balance (should be -50): {final_balance}")
        assert final_balance == new_balance - 50.0

        # 8. List Transactions
        print("Listing Transactions...")
        resp = await client.get("/accounting/transactions")
        transactions = resp.json()
        print(f"Found {len(transactions)} transactions.")
        assert len(transactions) >= 2
        print("Verification Successful!")

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(run_verification())
