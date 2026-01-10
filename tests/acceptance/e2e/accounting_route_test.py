import pytest
import asyncio
import pytest_asyncio
from fastapi.testclient import TestClient
from main import app
from init_db import reset, init_db
from app.database import database

# Local fixtures since global conftest is restricted

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def client():
    """Global test client."""
    with TestClient(app) as c:
        yield c

@pytest_asyncio.fixture(scope="session")
async def setup_test_db():
    """
    Shadowing global setup_test_db to avoid strict mode errors.
    """
    await database.init_db()
    yield
    await database.reset_db()

@pytest_asyncio.fixture(scope="session")
async def auth_tokens(client, setup_test_db):
    """authenticate users once and return their JWT tokens."""
    import init_db as db_init_module
    await db_init_module.reset()
    await db_init_module.init_db()

    base_url = "http://127.0.0.1:8000/api/v1"
    users = {
        "admin": {"username": "admin", "password": "admin"},
        "manager": {"username": "ShopManager", "password": "ShManager"},
        "cashier": {"username": "Cashier", "password": "Cashier"},
    }

    tokens = {}
    for role, creds in users.items():
        resp = client.post(base_url + "/auth", json=creds)
        assert resp.status_code == 200, f"Login failed for {role}"
        tokens[role] = f"Bearer {resp.json()['token']}"

    return tokens

@pytest.fixture
def auth_header_helper():
    def _make_header(tokens, role: str):
        return {"Authorization": tokens[role]}
    return _make_header

BASE_URL = "http://127.0.0.1:8000/api/v1"
BALANCE_URL = BASE_URL + "/balance"

# ---------------------------------------------------------------------
# GET /balance
# ---------------------------------------------------------------------

def test_get_balance_success_as_admin(client, auth_tokens, auth_header_helper):
    resp = client.get(BALANCE_URL, headers=auth_header_helper(auth_tokens, "admin"))
    assert resp.status_code == 200
    data = resp.json()
    assert "balance" in data
    assert isinstance(data["balance"], float)


def test_get_balance_success_as_manager(client, auth_tokens, auth_header_helper):
    resp = client.get(BALANCE_URL, headers=auth_header_helper(auth_tokens, "manager"))
    assert resp.status_code == 200


def test_get_balance_forbidden_as_cashier(client, auth_tokens, auth_header_helper):
    resp = client.get(BALANCE_URL, headers=auth_header_helper(auth_tokens, "cashier"))
    assert resp.status_code == 403


def test_get_balance_unauthenticated(client):
    resp = client.get(BALANCE_URL)
    assert resp.status_code == 401


# ---------------------------------------------------------------------
# POST /balance/set
# ---------------------------------------------------------------------

def test_set_balance_success(client, auth_tokens, auth_header_helper):
    # Set to 500.0
    resp = client.post(
        f"{BALANCE_URL}/set",
        headers=auth_header_helper(auth_tokens, "admin"),
        params={"amount": 500.0}
    )
    assert resp.status_code == 201
    assert resp.json()["success"] is True
    
    # Verify
    get_resp = client.get(BALANCE_URL, headers=auth_header_helper(auth_tokens, "admin"))
    assert get_resp.status_code == 200
    assert get_resp.json()["balance"] == 500.0


def test_set_balance_negative_amount(client, auth_tokens, auth_header_helper):
    resp = client.post(
        f"{BALANCE_URL}/set",
        headers=auth_header_helper(auth_tokens, "admin"),
        params={"amount": -10.0}
    )
    assert resp.status_code == 421


def test_set_balance_forbidden_as_cashier(client, auth_tokens, auth_header_helper):
    resp = client.post(
        f"{BALANCE_URL}/set",
        headers=auth_header_helper(auth_tokens, "cashier"),
        params={"amount": 100.0}
    )
    assert resp.status_code == 403


def test_set_balance_unauthenticated(client):
    resp = client.post(
        f"{BALANCE_URL}/set",
        params={"amount": 100.0}
    )
    assert resp.status_code == 401


# ---------------------------------------------------------------------
# POST /balance/reset
# ---------------------------------------------------------------------

def test_reset_balance_success(client, auth_tokens, auth_header_helper):
    # First set it to something
    client.post(
        f"{BALANCE_URL}/set",
        headers=auth_header_helper(auth_tokens, "admin"),
        params={"amount": 123.45}
    )
    
    # Reset
    resp = client.post(
        f"{BALANCE_URL}/reset",
        headers=auth_header_helper(auth_tokens, "admin")
    )
    assert resp.status_code == 200
    assert resp.json()["success"] is True
    
    # Verify is 0
    get_resp = client.get(BALANCE_URL, headers=auth_header_helper(auth_tokens, "admin"))
    assert get_resp.json()["balance"] == 0.0


def test_reset_balance_forbidden_as_cashier(client, auth_tokens, auth_header_helper):
    resp = client.post(
        f"{BALANCE_URL}/reset",
        headers=auth_header_helper(auth_tokens, "cashier")
    )
    assert resp.status_code == 403


def test_reset_balance_unauthenticated(client):
    resp = client.post(f"{BALANCE_URL}/reset")
    assert resp.status_code == 401
