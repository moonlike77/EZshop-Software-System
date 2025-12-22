# tests/test_customer_api.py
import pytest
import asyncio
from fastapi.testclient import TestClient
from main import app
from init_db import reset, init_db

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def client():
    from main import app
    with TestClient(app) as c:
        yield c

BASE_URL = "http://127.0.0.1:8000/api/v1"


# ---------------------------
# GLOBAL FIXTURE FOR TOKENS
# ---------------------------

@pytest.fixture(scope="session", autouse=True)
def auth_tokens(event_loop, client):
    """Authenticate customers once and return their JWT tokens."""

    event_loop.run_until_complete(reset())
    event_loop.run_until_complete(init_db())

    users = {
        "admin": {"username": "admin", "password": "admin"},
        "manager": {"username": "ShopManager", "password": "ShManager"},
        "cashier": {"username": "Cashier", "password": "Cashier"},
    }

    tokens = {}
    for role, creds in users.items():
        response = client.post(BASE_URL + "/auth", json=creds)
        assert response.status_code == 200, f"Login failed for {role}"
        tokens[role] = f"Bearer {response.json()['token']}"

    return tokens


def auth_header(tokens, role: str):
    return {"Authorization": tokens[role]}


# ---------------------------
# SAMPLE PAYLOADS
# ---------------------------

CUSTOMER_SAMPLE_1 = {
    "name": "Mario Rossi",
}

CUSTOMER_SAMPLE_2 = {
    "name": "Luigi Bianchi",
}

CUSTOMER_SAMPLE_3 = {
    "name": "Giuseppe Verdi",
}

CUSTOMER_SAMPLE_4 = {
    "name": "Francesco Neri"
}

INITIAL_CARD_1 = {
    "card_id": "0000000001",
    "points": 0,
}

INITIAL_CARD_2 = {
    "card_id": "0000000002",
    "points": 0,
}

UPDATED_CUSTOMER_ONLY_CARD = {
    "name": "Marco Rossi",
    "card": INITIAL_CARD_2,
}

UPDATED_CUSTOMER_DELETION_CARD = {
    "name": "",
    "card": None,
}

# ---------------------------
# CREATE CUSTOMER TESTS
# ---------------------------

def test_create_customer_success_as_admin(client, auth_tokens):
    resp = client.post(BASE_URL + "/customers", json=CUSTOMER_SAMPLE_1, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == CUSTOMER_SAMPLE_1["name"]

def test_create_customer_success_as_manager(client, auth_tokens):
    resp = client.post(BASE_URL + "/customers", json=CUSTOMER_SAMPLE_2, headers=auth_header(auth_tokens, "manager"))
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == CUSTOMER_SAMPLE_2["name"]

def test_create_customer_success_as_cashier(client, auth_tokens):
    resp = client.post(BASE_URL + "/customers", json=CUSTOMER_SAMPLE_3, headers=auth_header(auth_tokens, "cashier"))
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == CUSTOMER_SAMPLE_3["name"]

def test_create_customer_conflict(client, auth_tokens):
    resp = client.post(BASE_URL + "/customers", json=CUSTOMER_SAMPLE_1, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 409

def test_create_customer_missing_fields(client, auth_tokens):
    bad = {"name": ""}
    resp = client.post(BASE_URL + "/customers", json=bad, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code in (400, 422)

def test_create_customer_unauthenticated(client):
    resp = client.post(BASE_URL + "/customers", json=CUSTOMER_SAMPLE_4)
    assert resp.status_code == 401


# ---------------------------
# CREATE LOYALTY CARD TESTS
# ---------------------------

def test_create_loyalty_card_success_as_admin(client, auth_tokens):
    resp = client.post(BASE_URL + "/customers/cards", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 201
    data = resp.json()
    assert data["points"] == 0

def test_create_loyalty_card_success_as_manager(client, auth_tokens):
    resp = client.post(BASE_URL + "/customers/cards", headers=auth_header(auth_tokens, "manager"))
    assert resp.status_code == 201
    data = resp.json()
    assert data["points"] == 0

def test_create_loyalty_card_success_as_cashier(client, auth_tokens):
    resp = client.post(BASE_URL + "/customers/cards", headers=auth_header(auth_tokens, "cashier"))
    assert resp.status_code == 201
    data = resp.json()
    assert data["points"] == 0

def test_create_loyalty_card_unauthenticated(client):
    resp = client.post(BASE_URL + "/customers/cards")
    assert resp.status_code == 401

# -------------------------------------------
# ATTACH LOYALTY CARD TO CUSTOMER TESTS
# -------------------------------------------

def test_attach_loyalty_card_to_customer_success(client, auth_tokens):
    resp = client.patch(BASE_URL + "/customers/1/attach-card/0000000001", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 200
    data = resp.json()
    assert data["card"] == INITIAL_CARD_1

def test_attach_loyalty_card_to_customer_customer_not_found(client, auth_tokens):
    resp = client.patch(BASE_URL + "/customers/9999/attach-card/0000000001", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 404

def test_attach_loyalty_card_to_customer_card_not_found(client, auth_tokens):
    resp = client.patch(BASE_URL + "/customers/1/attach-card/0000009999", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 404

def test_attach_loyalty_card_to_customer_already_attached_to_this_customer(client, auth_tokens):
    resp = client.patch(BASE_URL + "/customers/1/attach-card/0000000001", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 409

def test_attach_loyalty_card_to_customer_already_attached_to_other_customer(client, auth_tokens):
    resp = client.patch(BASE_URL + "/customers/2/attach-card/0000000001", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 409

def test_attach_loyalty_card_to_customer_unauthenticated(client):
    resp = client.patch(BASE_URL + "/customers/1/attach-card/0000000001")
    assert resp.status_code == 401


# ----------------------------------------
# UPDATE LOYALTY CARD POINTS TESTS
# ----------------------------------------

def test_update_loyalty_card_points_success(client, auth_tokens):
    before = client.post(BASE_URL + "/customers/cards", headers=auth_header(auth_tokens, "admin"))
    after = client.patch(BASE_URL + "/customers/cards/4?points=30", headers=auth_header(auth_tokens, "admin"))
    assert after.status_code == 200
    points_before = before.json()
    points_after = after.json()
    assert (points_after["points"]-points_before["points"]) == 30

def test_update_loyalty_card_points_card_not_found(client, auth_tokens):
    resp = client.patch(BASE_URL + "/customers/cards/9999?points=30", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 404

def test_update_loyalty_card_points_unauthenticated(client):
    resp = client.patch(BASE_URL + "/customers/cards/1?points=30")
    assert resp.status_code == 401


# ---------------------------
# LIST CUSTOMERS TESTS
# ---------------------------

def test_list_customers_success_as_admin(client, auth_tokens):
    resp = client.get(BASE_URL + "/customers", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

def test_list_customers_success_as_manager(client, auth_tokens):
    resp = client.get(BASE_URL + "/customers", headers=auth_header(auth_tokens, "manager"))
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

def test_list_customers_success_as_cashier(client, auth_tokens):
    resp = client.get(BASE_URL + "/customers", headers=auth_header(auth_tokens, "cashier"))
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

def test_list_customers_unauthenticated(client):
    resp = client.get(BASE_URL + "/customers")
    assert resp.status_code == 401


# ---------------------------
# GET CUSTOMER BY ID TESTS
# ---------------------------

def test_get_customer_success(client, auth_tokens):
    resp = client.get(BASE_URL + "/customers/1", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code in (200, 404)
    if resp.status_code == 200:
        assert "id" in resp.json()

def test_get_customer_not_found(client, auth_tokens):
    resp = client.get(BASE_URL + "/customers/9999", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 404

def test_get_customer_unauthenticated(client):
    resp = client.get(BASE_URL + "/customers/1")
    assert resp.status_code == 401


# ---------------------------
# UPDATE CUSTOMER TESTS
# ---------------------------

def test_update_customer_name_but_not_card_success(client, auth_tokens):
    payload = CUSTOMER_SAMPLE_1.copy()
    payload["name"] = "Marco Rossi"
    resp = client.put(BASE_URL + "/customers/1", json=payload, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code in (201, 404)
    if resp.status_code == 201:
        assert resp.json()["name"] == "Marco Rossi"
        assert resp.json()["card"] == INITIAL_CARD_1

def test_update_customer_card_but_not_name_success(client, auth_tokens):
    resp = client.put(BASE_URL + "/customers/1", json=UPDATED_CUSTOMER_ONLY_CARD, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code in (201, 404)
    if resp.status_code == 201:
        assert resp.json()["name"] == "Marco Rossi"
        assert resp.json()["card"] == INITIAL_CARD_2

def test_update_customer_deletion_card_success(client, auth_tokens):
    resp = client.put(BASE_URL + "/customers/1", json=UPDATED_CUSTOMER_DELETION_CARD, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code in (201, 404)
    if resp.status_code == 201:
        assert resp.json()["name"] == "Marco Rossi"
        assert resp.json()["card"] == None

def test_update_customer_not_found(client, auth_tokens):
    payload = CUSTOMER_SAMPLE_1.copy()
    resp = client.put(BASE_URL + "/customers/9999", json=payload, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 404

def test_update_customer_card_not_found(client, auth_tokens):
    payload = UPDATED_CUSTOMER_ONLY_CARD.copy()
    payload["card"] = {"card_id": "0000009999", "points": 0}
    resp = client.put(BASE_URL + "/customers/2", json=payload, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 404

def test_update_customer_name_conflict(client, auth_tokens):
    payload = CUSTOMER_SAMPLE_2.copy()
    resp = client.put(BASE_URL + "/customers/1", json=payload, headers=auth_header(auth_tokens, "admin"))
    if resp.status_code != 404:
        assert resp.status_code == 409

def test_update_customer_unauthenticated(client):
    resp = client.put(BASE_URL + "/customers/1", json=CUSTOMER_SAMPLE_1)
    assert resp.status_code == 401


# ---------------------------
# DELETE CUSTOMER TESTS
# ---------------------------

def test_delete_customer_success(client, auth_tokens):
    resp = client.delete(BASE_URL + "/customers/1", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code in (204, 404)

def test_delete_customer_unauthenticated(client):
    resp = client.delete(BASE_URL + "/customers/1")
    assert resp.status_code == 401

def test_delete_customer_not_found(client, auth_tokens):
    resp = client.delete(BASE_URL + "/customers/9999", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 404