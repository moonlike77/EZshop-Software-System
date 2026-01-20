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
# SETUP TEST PRODUCT
# ---------------------------

@pytest.fixture(scope="session", autouse=True)
def test_product(client, auth_tokens):
    product_data = {
        "barcode": "1234567890123",
        "description": "Test Product for Orders",
        "price_per_unit": 10.0,
        "quantity": 100,
        "note": "Test product",
        "position": "A1-B2-C3"
    }
    resp = client.post(BASE_URL + "/products", json=product_data, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 201
    return resp.json()


# ---------------------------
# SAMPLE PAYLOADS
# ---------------------------

ORDER_SAMPLE_1 = {
    "product_barcode": "1234567890123",
    "quantity": 10,
    "price_per_unit": 8.0
}

ORDER_SAMPLE_2 = {
    "product_barcode": "1234567890123",
    "quantity": 5,
    "price_per_unit": 9.0
}

ORDER_SAMPLE_3 = {
    "product_barcode": "1234567890123",
    "quantity": 15,
    "price_per_unit": 7.5
}

PAYFOR_ORDER_SAMPLE = {
    "product_barcode": "1234567890123",
    "quantity": 20,
    "price_per_unit": 8.5
}


# ---------------------------
# CREATE ORDER TESTS
# ---------------------------

def test_create_order_success_as_admin(client, auth_tokens):
    resp = client.post(BASE_URL + "/orders", json=ORDER_SAMPLE_1, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 201
    data = resp.json()
    assert data["quantity"] == ORDER_SAMPLE_1["quantity"]
    assert data["price_per_unit"] == ORDER_SAMPLE_1["price_per_unit"]
    assert data["status"] == "ISSUED"


def test_create_order_success_as_manager(client, auth_tokens):
    resp = client.post(BASE_URL + "/orders", json=ORDER_SAMPLE_2, headers=auth_header(auth_tokens, "manager"))
    assert resp.status_code == 201
    data = resp.json()
    assert data["quantity"] == ORDER_SAMPLE_2["quantity"]
    assert data["status"] == "ISSUED"


def test_create_order_forbidden_as_cashier(client, auth_tokens):
    resp = client.post(BASE_URL + "/orders", json=ORDER_SAMPLE_3, headers=auth_header(auth_tokens, "cashier"))
    assert resp.status_code == 403


def test_create_order_unauthenticated(client):
    resp = client.post(BASE_URL + "/orders", json=ORDER_SAMPLE_1)
    assert resp.status_code == 401


def test_create_order_invalid_product(client, auth_tokens):
    invalid_order = {
        "product_barcode": "9999999999999",
        "quantity": 10,
        "price_per_unit": 8.0
    }
    resp = client.post(BASE_URL + "/orders", json=invalid_order, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 404


def test_create_order_missing_fields(client, auth_tokens):
    bad_order = {"quantity": 10}
    resp = client.post(BASE_URL + "/orders", json=bad_order, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code in (400, 422)


def test_create_order_invalid_quantity(client, auth_tokens):
    invalid_order = {
        "product_barcode": "1234567890123",
        "quantity": -5,
        "price_per_unit": 8.0
    }
    resp = client.post(BASE_URL + "/orders", json=invalid_order, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code in (400, 422)


# ---------------------------
# CREATE AND PAY ORDER TESTS
# ---------------------------

def test_payfor_order_success_as_admin(client, auth_tokens):
    # Set balance first
    client.post(BASE_URL + "/balance/set?amount=10000.0", headers=auth_header(auth_tokens, "admin"))
    resp = client.post(BASE_URL + "/orders/payfor", json=PAYFOR_ORDER_SAMPLE, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "PAID"
    assert data["quantity"] == PAYFOR_ORDER_SAMPLE["quantity"]


def test_payfor_order_success_as_manager(client, auth_tokens):
    # Set balance first
    client.post(BASE_URL + "/balance/set?amount=10000.0", headers=auth_header(auth_tokens, "admin"))
    payfor_data = {
        "product_barcode": "1234567890123",
        "quantity": 8,
        "price_per_unit": 9.5
    }
    resp = client.post(BASE_URL + "/orders/payfor", json=payfor_data, headers=auth_header(auth_tokens, "manager"))
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "PAID"


def test_payfor_order_forbidden_as_cashier(client, auth_tokens):
    resp = client.post(BASE_URL + "/orders/payfor", json=PAYFOR_ORDER_SAMPLE, headers=auth_header(auth_tokens, "cashier"))
    assert resp.status_code == 403


def test_payfor_order_unauthenticated(client):
    resp = client.post(BASE_URL + "/orders/payfor", json=PAYFOR_ORDER_SAMPLE)
    assert resp.status_code == 401


def test_payfor_order_invalid_product(client, auth_tokens):
    invalid_payfor = {
        "product_barcode": "9999999999999",
        "quantity": 10,
        "price_per_unit": 8.0
    }
    resp = client.post(BASE_URL + "/orders/payfor", json=invalid_payfor, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 404


# ---------------------------
# GET ORDER TESTS
# ---------------------------

def test_get_all_orders_success_as_admin(client, auth_tokens):
    resp = client.get(BASE_URL + "/orders", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_get_all_orders_success_as_manager(client, auth_tokens):
    resp = client.get(BASE_URL + "/orders", headers=auth_header(auth_tokens, "manager"))
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_get_all_orders_forbidden_as_cashier(client, auth_tokens):
    resp = client.get(BASE_URL + "/orders", headers=auth_header(auth_tokens, "cashier"))
    assert resp.status_code == 403


def test_get_all_orders_unauthenticated(client):
    resp = client.get(BASE_URL + "/orders")
    assert resp.status_code == 401


def test_get_order_by_id_success(client, auth_tokens):
    # Create an order first
    create_resp = client.post(BASE_URL + "/orders", json=ORDER_SAMPLE_1, headers=auth_header(auth_tokens, "admin"))
    order_id = create_resp.json()["id"]
    
    # Get the order
    resp = client.get(f"{BASE_URL}/orders/{order_id}", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == order_id


def test_get_order_by_id_not_found(client, auth_tokens):
    resp = client.get(f"{BASE_URL}/orders/99999", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 404


def test_get_order_by_id_invalid_id(client, auth_tokens):
    resp = client.get(f"{BASE_URL}/orders/0", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code in (400, 422)


def test_get_order_by_id_unauthenticated(client):
    resp = client.get(f"{BASE_URL}/orders/1")
    assert resp.status_code == 401


# ---------------------------
# PAY ORDER TESTS
# ---------------------------

def test_pay_order_success(client, auth_tokens):
    # Set balance first
    client.post(BASE_URL + "/balance/set?amount=10000.0", headers=auth_header(auth_tokens, "admin"))
    # Create an order first
    create_resp = client.post(BASE_URL + "/orders", json=ORDER_SAMPLE_1, headers=auth_header(auth_tokens, "admin"))
    order_id = create_resp.json()["id"]
    
    # Pay for it
    resp = client.patch(f"{BASE_URL}/orders/{order_id}/pay", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "PAID"


def test_pay_order_not_found(client, auth_tokens):
    resp = client.patch(f"{BASE_URL}/orders/99999/pay", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 404


def test_pay_order_wrong_status(client, auth_tokens):
    # Set balance first
    client.post(BASE_URL + "/balance/set?amount=10000.0", headers=auth_header(auth_tokens, "admin"))
    # Create and pay an order
    create_resp = client.post(BASE_URL + "/orders/payfor", json=PAYFOR_ORDER_SAMPLE, headers=auth_header(auth_tokens, "admin"))
    order_id = create_resp.json()["id"]
    
    # Try to pay again
    resp = client.patch(f"{BASE_URL}/orders/{order_id}/pay", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 420


def test_pay_order_forbidden_as_cashier(client, auth_tokens):
    # Create an order as admin
    create_resp = client.post(BASE_URL + "/orders", json=ORDER_SAMPLE_1, headers=auth_header(auth_tokens, "admin"))
    order_id = create_resp.json()["id"]
    
    # Try to pay as cashier
    resp = client.patch(f"{BASE_URL}/orders/{order_id}/pay", headers=auth_header(auth_tokens, "cashier"))
    assert resp.status_code == 403


def test_pay_order_unauthenticated(client):
    resp = client.patch(f"{BASE_URL}/orders/1/pay")
    assert resp.status_code == 401


# ---------------------------
# RECORD ORDER ARRIVAL TESTS
# ---------------------------

def test_record_arrival_success(client, auth_tokens):
    # Set balance first
    client.post(BASE_URL + "/balance/set?amount=10000.0", headers=auth_header(auth_tokens, "admin"))
    # Create and pay for an order
    create_resp = client.post(BASE_URL + "/orders/payfor", json=PAYFOR_ORDER_SAMPLE, headers=auth_header(auth_tokens, "admin"))
    order_id = create_resp.json()["id"]
    
    # Record arrival
    resp = client.patch(f"{BASE_URL}/orders/{order_id}/arrival", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "COMPLETED"


def test_record_arrival_not_found(client, auth_tokens):
    resp = client.patch(f"{BASE_URL}/orders/99999/arrival", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 404


def test_record_arrival_wrong_status(client, auth_tokens):
    # Create an issued order (not paid)
    create_resp = client.post(BASE_URL + "/orders", json=ORDER_SAMPLE_1, headers=auth_header(auth_tokens, "admin"))
    order_id = create_resp.json()["id"]
    
    # Try to record arrival
    resp = client.patch(f"{BASE_URL}/orders/{order_id}/arrival", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 420


def test_record_arrival_forbidden_as_cashier(client, auth_tokens):
    # Set balance first
    client.post(BASE_URL + "/balance/set?amount=10000.0", headers=auth_header(auth_tokens, "admin"))
    # Create and pay for an order as admin
    create_resp = client.post(BASE_URL + "/orders/payfor", json=PAYFOR_ORDER_SAMPLE, headers=auth_header(auth_tokens, "admin"))
    order_id = create_resp.json()["id"]
    
    # Try to record arrival as cashier
    resp = client.patch(f"{BASE_URL}/orders/{order_id}/arrival", headers=auth_header(auth_tokens, "cashier"))
    assert resp.status_code == 403


def test_record_arrival_unauthenticated(client):
    resp = client.patch(f"{BASE_URL}/orders/1/arrival")
    assert resp.status_code == 401


# ---------------------------
# DELETE ORDER TESTS
# ---------------------------

def test_delete_order_success(client, auth_tokens):
    # Create an order
    create_resp = client.post(BASE_URL + "/orders", json=ORDER_SAMPLE_1, headers=auth_header(auth_tokens, "admin"))
    order_id = create_resp.json()["id"]
    
    # Delete it
    resp = client.delete(f"{BASE_URL}/orders/{order_id}", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 204


def test_delete_order_not_found(client, auth_tokens):
    resp = client.delete(f"{BASE_URL}/orders/99999", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 404


def test_delete_order_forbidden_as_cashier(client, auth_tokens):
    # Create an order as admin
    create_resp = client.post(BASE_URL + "/orders", json=ORDER_SAMPLE_1, headers=auth_header(auth_tokens, "admin"))
    order_id = create_resp.json()["id"]
    
    # Try to delete as cashier
    resp = client.delete(f"{BASE_URL}/orders/{order_id}", headers=auth_header(auth_tokens, "cashier"))
    assert resp.status_code == 403


def test_delete_order_unauthenticated(client):
    resp = client.delete(f"{BASE_URL}/orders/1")
    assert resp.status_code == 401


# ---------------------------
# COVERAGE TESTS
# ---------------------------

# ---------------------------
# COVERAGE TESTS - Unreachable validations in routes are handled by Pydantic
# ---------------------------

def test_payfor_invalid_barcode(client, auth_tokens):
    client.post(BASE_URL + "/balance/set?amount=10000.0", headers=auth_header(auth_tokens, "admin"))
    
    invalid_order = {
        "product_barcode": "NONEXISTENTBARCODE",
        "quantity": 5,
        "price_per_unit": 10.0
    }
    resp = client.post(BASE_URL + "/orders/payfor", json=invalid_order, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 422


def test_record_arrival_product_without_position(client, auth_tokens):
    # Create product without position
    product_data = {
        "description": "No Position Product",
        "barcode": "7777777777777",
        "price_per_unit": 10.0
    }
    client.post(BASE_URL + "/products", json=product_data, headers=auth_header(auth_tokens, "admin"))
    
    # Set balance
    client.post(BASE_URL + "/balance/set?amount=10000.0", headers=auth_header(auth_tokens, "admin"))
    
    # Create and pay for order
    order_data = {
        "product_barcode": "7777777777777",
        "quantity": 5,
        "price_per_unit": 10.0
    }
    create_resp = client.post(BASE_URL + "/orders/payfor", json=order_data, headers=auth_header(auth_tokens, "admin"))
    order_id = create_resp.json()["id"]
    
    # Try to record arrival - should fail because product has no position
    resp = client.patch(f"{BASE_URL}/orders/{order_id}/arrival", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 500
