import pytest
from fastapi.testclient import TestClient
from main import app
from init_db import reset, init_db

client = TestClient(app)
BASE_URL = "http://127.0.0.1:8000/api/v1"
BALANCE_URL = BASE_URL + "/balance"

# ---------------------------
# GLOBAL FIXTURE FOR TOKENS
# ---------------------------

@pytest.fixture(scope="session", autouse=True)
def auth_tokens():
    """Authenticate users once and return their JWT tokens."""
    import asyncio

    loop = asyncio.new_event_loop()
    loop.run_until_complete(reset())
    loop.run_until_complete(init_db())

    users = {
        "admin": {"username": "admin", "password": "admin"},
        "manager": {"username": "ShopManager", "password": "ShManager"},
        "cashier": {"username": "Cashier", "password": "Cashier"},
    }

    tokens = {}
    for role, creds in users.items():
        resp = client.post(BASE_URL + "/auth", json=creds)
        assert resp.status_code == 200, f"Login failed for {role}"
        tokens[role] = f"Bearer {resp.json()['token']}"

    return tokens


def auth_header(tokens, role: str):
    return {"Authorization": tokens[role]}


# ---------------------------------------------------------------------
# GET /balance
# ---------------------------------------------------------------------

def test_get_balance_success_as_admin(auth_tokens):
    resp = client.get(BALANCE_URL, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 200
    data = resp.json()
    assert "balance" in data
    assert isinstance(data["balance"], float)


def test_get_balance_success_as_manager(auth_tokens):
    resp = client.get(BALANCE_URL, headers=auth_header(auth_tokens, "manager"))
    assert resp.status_code == 200


def test_get_balance_forbidden_as_cashier(auth_tokens):
    resp = client.get(BALANCE_URL, headers=auth_header(auth_tokens, "cashier"))
    assert resp.status_code == 403


def test_get_balance_unauthenticated():
    resp = client.get(BALANCE_URL)
    assert resp.status_code == 401


# ---------------------------------------------------------------------
# POST /balance/set
# ---------------------------------------------------------------------

def test_set_balance_success(auth_tokens):
    # Set to 500.0
    resp = client.post(
        f"{BALANCE_URL}/set",
        headers=auth_header(auth_tokens, "admin"),
        params={"amount": 500.0}
    )
    assert resp.status_code == 201
    assert resp.json()["success"] is True
    
    # Verify
    get_resp = client.get(BALANCE_URL, headers=auth_header(auth_tokens, "admin"))
    assert get_resp.status_code == 200
    assert get_resp.json()["balance"] == 500.0


def test_set_balance_negative_amount(auth_tokens):
    # Depending on implementation, might raise 421 or 400.
    # The route returns 421 for ValueError
    resp = client.post(
        f"{BALANCE_URL}/set",
        headers=auth_header(auth_tokens, "admin"),
        params={"amount": -10.0}
    )
    assert resp.status_code == 421


def test_set_balance_forbidden_as_cashier(auth_tokens):
    resp = client.post(
        f"{BALANCE_URL}/set",
        headers=auth_header(auth_tokens, "cashier"),
        params={"amount": 100.0}
    )
    assert resp.status_code == 403


def test_set_balance_unauthenticated():
    resp = client.post(
        f"{BALANCE_URL}/set",
        params={"amount": 100.0}
    )
    assert resp.status_code == 401


# ---------------------------------------------------------------------
# POST /balance/reset
# ---------------------------------------------------------------------

def test_reset_balance_success(auth_tokens):
    # First set it to something
    client.post(
        f"{BALANCE_URL}/set",
        headers=auth_header(auth_tokens, "admin"),
        params={"amount": 123.45}
    )
    
    # Reset
    resp = client.post(
        f"{BALANCE_URL}/reset",
        headers=auth_header(auth_tokens, "admin")
    )
    assert resp.status_code == 200
    assert resp.json()["success"] is True
    
    # Verify is 0
    get_resp = client.get(BALANCE_URL, headers=auth_header(auth_tokens, "admin"))
    assert get_resp.json()["balance"] == 0.0


def test_reset_balance_forbidden_as_cashier(auth_tokens):
    resp = client.post(
        f"{BALANCE_URL}/reset",
        headers=auth_header(auth_tokens, "cashier")
    )
    assert resp.status_code == 403


def test_reset_balance_unauthenticated():
    resp = client.post(f"{BALANCE_URL}/reset")
    assert resp.status_code == 401
