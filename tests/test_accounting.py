import pytest
from fastapi.testclient import TestClient
from main import app
from init_db import reset, init_db

client = TestClient(app)
BASE_URL = "http://127.0.0.1:8000/api/v1"

# Re-using the auth fixture concept from user_test.py
# Since that fixture is session-scoped in user_test.py, it's not automatically here unless strictly in conftest.
# However, conftest.py in `tests/` has `setup_test_db`.
# The `auth_tokens` fixture in `user_test.py` is local to that file? No, it's in `tests/acceptance/user_test.py`.
# I should duplicate the auth helper or move it to conftest if I wanted to refactor, but for this task I will keep it simple and self-contained or import if possible.
# `tests/acceptance/user_test.py` is not a module I can easily import from for fixtures usually.
# So I will copy the minimal auth setup needed.

@pytest.fixture(scope="module")
async def auth_headers(setup_test_db):
    """Authenticate admin and return header."""
    # Ensure DB is ready. setup_test_db (from conftest) should handle init.
    # However, setup_test_db is session scoped.
    # We might need to ensure data exists (admin user).
    # init_db() in this project usually seeds data? 
    # Let's check init_db.py content if needed, but assuming user_test.py works, init_db() does the job.
    # But wait, setup_test_db calls database.init_db().
    
    # We need to ensure we are in an async context if we call async functions, 
    # but here we use TestClient which is synchronous usually (calling async app via portal).
    # The fixture itself matches the scope.
    
    # Login as admin
    admin_creds = {"username": "admin", "password": "admin"} 
    resp = client.post(BASE_URL + "/auth", json=admin_creds)
    
    if resp.status_code != 200:
        # If login fails despite init, maybe seed is missing or something.
        # But let's assume init_db() creates admin.
        # If 401/404, we might need to manually run init_db logic if setup_test_db is insufficient 
        # (e.g. if it creates tables but doesn't seed).
        # Let's import init_db from init_db.py and run it if needed.
        from init_db import init_db
        await init_db()
        resp = client.post(BASE_URL + "/auth", json=admin_creds)
        assert resp.status_code == 200, f"Failed to login as admin. Status: {resp.status_code}, Body: {resp.text}"

    token = resp.json()["token"]
    return {"Authorization": f"Bearer {token}"}

def test_get_balance_initial(auth_headers):
    # Depending on seed, might be 0 or something else.
    resp = client.get(BASE_URL + "/accounting/balance", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "balance" in data
    assert isinstance(data["balance"], float)

def test_set_balance_admin(auth_headers):
    new_balance = 1000.50
    # Note: query param 'amount'
    resp = client.post(f"{BASE_URL}/accounting/balance/set?amount={new_balance}", headers=auth_headers)
    assert resp.status_code == 201
    
    # Verify
    resp = client.get(BASE_URL + "/accounting/balance", headers=auth_headers)
    assert resp.json()["balance"] == new_balance

def test_reset_balance_admin(auth_headers):
    # Set to something first
    client.post(f"{BASE_URL}/accounting/balance/set?amount=500", headers=auth_headers)
    
    # Reset
    resp = client.post(f"{BASE_URL}/accounting/balance/reset", headers=auth_headers)
    assert resp.status_code == 205
    
    # Verify
    resp = client.get(BASE_URL + "/accounting/balance", headers=auth_headers)
    assert resp.json()["balance"] == 0.0

def test_set_balance_negative_error(auth_headers):
    resp = client.post(f"{BASE_URL}/accounting/balance/set?amount=-100", headers=auth_headers)
    # Controller raises ValueError, route catches usage? 
    # The route code has:
    # except ValueError as e: raise HTTPException(status_code=421, detail=str(e))
    assert resp.status_code == 421
