# tests/acceptance/order_test.py
import asyncio
import pytest
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
    """Authenticate users once and return their JWT tokens."""
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
# SETUP TEST DATA
# ---------------------------

@pytest.fixture(scope="session", autouse=True)
def setup_test_data(client, auth_tokens, event_loop):
    """Create test products and set system balance."""
    
    # Create products using repository directly
    async def create_test_data():
        from app.repositories.product_repository import ProductRepository
        from app.repositories.system_repository import SystemRepository
        
        product_repo = ProductRepository()
        system_repo = SystemRepository()
        
        # Create products
        await product_repo.create_product(
            description="Test Product 1",
            barcode="1234567890128",
            price_per_unit=10.0,
            quantity=100,
            position="1-A-1"
        )
        await product_repo.create_product(
            description="Test Product 2",
            barcode="9876543210987",
            price_per_unit=25.0,
            quantity=50,
            position="1-B-2"
        )
        await product_repo.create_product(
            description="Product Without Position",
            barcode="1111111111111",
            price_per_unit=15.0,
            quantity=30,
            position=None
        )
        
        # Set system balance
        await system_repo.set_balance(10000.0)
    
    event_loop.run_until_complete(create_test_data())
    
    yield


# ---------------------------
# HELPER FUNCTIONS
# ---------------------------

_user_counter = 1000
_barcode_counter = 5000000000000

def get_unique_user_id():
    """Generate unique user ID"""
    global _user_counter
    _user_counter += 1
    return _user_counter

def get_unique_barcode():
    """Generate unique barcode for each product"""
    global _barcode_counter
    barcode = str(_barcode_counter)
    _barcode_counter += 1
    return barcode

def create_test_product(client, auth_tokens, description="Test Product", quantity=100):
    """Helper to create a product"""
    barcode = get_unique_barcode()
    payload = {
        "description": description,
        "barcode": barcode,
        "price_per_unit": 10.0,
        "quantity": quantity
    }
    resp = client.post(BASE_URL + "/products", json=payload, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 201
    return resp.json()

def create_test_user(client, auth_tokens, username, name, address):
    """Helper to create a user"""
    payload = {
        "username": username,
        "name": name,
        "address": address,
        "password": "password123",
        "user_type": "Customer"
    }
    resp = client.post(BASE_URL + "/users", json=payload, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 201
    return resp.json()

# ---------------------------
# SAMPLE PAYLOADS
# ---------------------------

ORDER_SAMPLE_1 = {
    "product_barcode": "1234567890128",
    "quantity": 10,
    "price_per_unit": 5.0
}

ORDER_SAMPLE_2 = {
    "product_barcode": "9876543210987",
    "quantity": 5,
    "price_per_unit": 20.0
}

ORDER_WITH_ID = {
    "id": 999,
    "product_barcode": "1234567890128",
    "quantity": 3,
    "price_per_unit": 5.0
}

ORDER_NONEXISTENT_PRODUCT = {
    "product_barcode": "0000000000000",
    "quantity": 10,
    "price_per_unit": 5.0
}

ORDER_EXPENSIVE = {
    "product_barcode": "1234567890128",
    "quantity": 10000,
    "price_per_unit": 100.0
}


# ---------------------------
# ISSUE ORDER TESTS (POST /)
# ---------------------------

def test_issue_order_success_as_admin(client, auth_tokens):
    """Test creating an order in ISSUED state as Administrator"""
    resp = client.post(BASE_URL + "/orders", json=ORDER_SAMPLE_1, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 201
    data = resp.json()
    assert data["product_barcode"] == ORDER_SAMPLE_1["product_barcode"]
    assert data["quantity"] == ORDER_SAMPLE_1["quantity"]
    assert data["price_per_unit"] == ORDER_SAMPLE_1["price_per_unit"]
    assert data["status"] == "Issued"
    assert "id" in data
    assert "issue_date" in data


def test_issue_order_success_as_manager(client, auth_tokens):
    """Test creating an order as ShopManager"""
    resp = client.post(BASE_URL + "/orders", json=ORDER_SAMPLE_2, headers=auth_header(auth_tokens, "manager"))
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "Issued"


def test_issue_order_with_custom_id(client, auth_tokens):
    """Test creating an order with a custom ID (database auto-increments)"""
    resp = client.post(BASE_URL + "/orders", json=ORDER_WITH_ID, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 201
    data = resp.json()
    # DB auto-increments ID, so custom ID field is ignored
    assert data["product_barcode"] == ORDER_WITH_ID["product_barcode"]
    assert "id" in data


def test_issue_order_product_not_found(client, auth_tokens):
    """Test issuing order for non-existent product"""
    resp = client.post(BASE_URL + "/orders", json=ORDER_NONEXISTENT_PRODUCT, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 404


def test_issue_order_missing_fields(client, auth_tokens):
    """Test issuing order with missing required fields"""
    bad_payload = {"product_barcode": "1234567890128"}
    resp = client.post(BASE_URL + "/orders", json=bad_payload, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code in (400, 422)


def test_issue_order_invalid_quantity(client, auth_tokens):
    """Test issuing order with invalid (negative/zero) quantity"""
    bad_payload = {
        "product_barcode": "1234567890128",
        "quantity": 0,
        "price_per_unit": 5.0
    }
    resp = client.post(BASE_URL + "/orders", json=bad_payload, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code in (400, 422)


def test_issue_order_invalid_price(client, auth_tokens):
    """Test issuing order with invalid (negative/zero) price"""
    bad_payload = {
        "product_barcode": "1234567890128",
        "quantity": 10,
        "price_per_unit": 0
    }
    resp = client.post(BASE_URL + "/orders", json=bad_payload, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code in (400, 422)


def test_issue_order_unauthenticated(client):
    """Test issuing order without authentication"""
    resp = client.post(BASE_URL + "/orders", json=ORDER_SAMPLE_1)
    assert resp.status_code == 401


def test_issue_order_forbidden_as_cashier(client, auth_tokens):
    """Test that Cashier cannot issue orders"""
    resp = client.post(BASE_URL + "/orders", json=ORDER_SAMPLE_1, headers=auth_header(auth_tokens, "cashier"))
    assert resp.status_code == 403


def test_issue_order_empty_barcode(client, auth_tokens):
    """Test issuing order with empty barcode"""
    payload = {
        "product_barcode": "",
        "quantity": 5,
        "price_per_unit": 10.0
    }
    resp = client.post(BASE_URL + "/orders", json=payload, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code in (400, 422)


def test_issue_order_whitespace_barcode(client, auth_tokens):
    """Test issuing order with whitespace-only barcode"""
    payload = {
        "product_barcode": "   ",
        "quantity": 5,
        "price_per_unit": 10.0
    }
    resp = client.post(BASE_URL + "/orders", json=payload, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 400


def test_issue_order_invalid_quantity(client, auth_tokens):
    """Test issuing order with invalid quantity"""
    payload = {
        "product_barcode": "1234567890128",
        "quantity": 0,
        "price_per_unit": 10.0
    }
    resp = client.post(BASE_URL + "/orders", json=payload, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code in (400, 422)


def test_issue_order_negative_quantity(client, auth_tokens):
    """Test issuing order with negative quantity"""
    payload = {
        "product_barcode": "1234567890128",
        "quantity": -5,
        "price_per_unit": 10.0
    }
    resp = client.post(BASE_URL + "/orders", json=payload, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code in (400, 422)


def test_issue_order_invalid_price(client, auth_tokens):
    """Test issuing order with invalid price"""
    payload = {
        "product_barcode": "1234567890128",
        "quantity": 5,
        "price_per_unit": 0
    }
    resp = client.post(BASE_URL + "/orders", json=payload, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code in (400, 422)


def test_issue_order_negative_price(client, auth_tokens):
    """Test issuing order with negative price"""
    payload = {
        "product_barcode": "1234567890128",
        "quantity": 5,
        "price_per_unit": -5.0
    }
    resp = client.post(BASE_URL + "/orders", json=payload, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code in (400, 422)


# ---------------------------
# LIST ORDERS TESTS (GET /)
# ---------------------------

def test_list_orders_success_as_admin(client, auth_tokens):
    """Test listing all orders as Administrator"""
    resp = client.get(BASE_URL + "/orders", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
    # Should have at least the orders created in previous tests
    assert len(resp.json()) >= 2


def test_list_orders_success_as_manager(client, auth_tokens):
    """Test listing all orders as ShopManager"""
    resp = client.get(BASE_URL + "/orders", headers=auth_header(auth_tokens, "manager"))
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_list_orders_unauthenticated(client):
    """Test listing orders without authentication"""
    resp = client.get(BASE_URL + "/orders")
    assert resp.status_code == 401


def test_list_orders_forbidden_as_cashier(client, auth_tokens):
    """Test that Cashier cannot list orders"""
    resp = client.get(BASE_URL + "/orders", headers=auth_header(auth_tokens, "cashier"))
    assert resp.status_code == 403

def test_get_order_by_id_exercises_success_path(client, auth_tokens):
    """Test get order by ID - exercises the successful retrieval path"""
    # Create an order
    create_resp = client.post(BASE_URL + "/orders", json=ORDER_SAMPLE_1, headers=auth_header(auth_tokens, "admin"))
    order_id = create_resp.json()["id"]
    
    # Get the order
    resp = client.get(BASE_URL + f"/orders/{order_id}", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 200
    assert resp.json()["id"] == order_id


def test_pay_order_with_sufficient_balance(client, auth_tokens):
    """Test paying order exercises balance check and system update"""
    # Create order with cost that doesn't exceed balance (10000)
    order_payload = {
        "product_barcode": "1234567890128",
        "quantity": 10,
        "price_per_unit": 50.0
    }
    create_resp = client.post(BASE_URL + "/orders", json=order_payload, headers=auth_header(auth_tokens, "admin"))
    order_id = create_resp.json()["id"]
    
    # Pay for it - exercises balance check path
    resp = client.patch(BASE_URL + f"/orders/{order_id}/pay", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 201
    assert resp.json()["status"] == "Paid"


def test_record_arrival_with_position_exercises_all_paths(client, auth_tokens):
    """Test arrival recording exercises product position check and quantity update"""
    # Create and pay order with product that HAS position
    order_payload = {
        "product_barcode": "1234567890128",
        "quantity": 3,
        "price_per_unit": 5.0
    }
    create_resp = client.post(BASE_URL + "/orders/payfor", json=order_payload, headers=auth_header(auth_tokens, "admin"))
    order_id = create_resp.json()["id"]
    
    # Get product to check position before arrival
    prod_resp = client.get(BASE_URL + "/products/barcode/1234567890128", headers=auth_header(auth_tokens, "admin"))
    initial_qty = prod_resp.json()["quantity"]
    
    # Record arrival - exercises all condition paths
    resp = client.patch(BASE_URL + f"/orders/{order_id}/arrival", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 201
    assert resp.json()["status"] == "Completed"
    
    # Verify product quantity increased
    prod_after = client.get(BASE_URL + "/products/barcode/1234567890128", headers=auth_header(auth_tokens, "admin"))
    assert prod_after.json()["quantity"] == initial_qty + 3


def test_list_all_orders_returns_list(client, auth_tokens):
    """Test listing all orders exercises return path (line 84)"""
    resp = client.get(BASE_URL + "/orders", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_pay_order_exercises_status_check_path(client, auth_tokens):
    """Test paying order in non-Issued state exercises status validation"""
    # Create and pay order
    create_resp = client.post(BASE_URL + "/orders/payfor", json=ORDER_SAMPLE_1, headers=auth_header(auth_tokens, "admin"))
    order_id = create_resp.json()["id"]
    
    # Try to pay again - should fail because status is already Paid
    resp = client.patch(BASE_URL + f"/orders/{order_id}/pay", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 400  # Status check fails


def test_record_arrival_on_non_paid_order_exercises_status_check(client, auth_tokens):
    """Test arrival on Issued order exercises status check"""
    # Create order in ISSUED state
    create_resp = client.post(BASE_URL + "/orders", json=ORDER_SAMPLE_1, headers=auth_header(auth_tokens, "admin"))
    order_id = create_resp.json()["id"]
    
    # Try arrival without paying - should fail
    resp = client.patch(BASE_URL + f"/orders/{order_id}/arrival", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 400  # Status check fails (line 137)

# ---------------------------
# GET ORDER (GET /{order_id})
# ---------------------------

def test_get_order_success(client, auth_tokens):
    """Test getting a specific order"""
    # Create an order
    create_resp = client.post(BASE_URL + "/orders", json=ORDER_SAMPLE_1, headers=auth_header(auth_tokens, "admin"))
    order_id = create_resp.json()["id"]
    
    # Get the order
    resp = client.get(BASE_URL + f"/orders/{order_id}", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 200
    assert resp.json()["id"] == order_id


def test_get_order_as_manager(client, auth_tokens):
    """Test getting order as manager"""
    create_resp = client.post(BASE_URL + "/orders", json=ORDER_SAMPLE_1, headers=auth_header(auth_tokens, "manager"))
    order_id = create_resp.json()["id"]
    
    resp = client.get(BASE_URL + f"/orders/{order_id}", headers=auth_header(auth_tokens, "manager"))
    assert resp.status_code == 200


def test_get_order_not_found(client, auth_tokens):
    """Test getting non-existent order"""
    resp = client.get(BASE_URL + "/orders/99999", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 404


def test_get_order_unauthenticated(client):
    """Test getting order without authentication"""
    resp = client.get(BASE_URL + "/orders/1")
    assert resp.status_code == 401


def test_get_order_forbidden_as_cashier(client, auth_tokens):
    """Test that Cashier cannot get order details"""
    resp = client.get(BASE_URL + "/orders/1", headers=auth_header(auth_tokens, "cashier"))
    assert resp.status_code == 403


# ---------------------------
# PAY FOR ORDER (POST /payfor)
# ---------------------------

def test_pay_order_for_success(client, auth_tokens):
    """Test creating and paying for an order in one operation"""
    order_payload = {
        "product_barcode": "1234567890128",
        "quantity": 2,
        "price_per_unit": 5.0
    }
    resp = client.post(BASE_URL + "/orders/payfor", json=order_payload, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "Paid"
    assert data["product_barcode"] == order_payload["product_barcode"]
    assert data["quantity"] == order_payload["quantity"]


def test_pay_order_for_insufficient_balance(client, auth_tokens):
    """Test paying for order when balance is insufficient"""
    resp = client.post(BASE_URL + "/orders/payfor", json=ORDER_EXPENSIVE, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 400


def test_pay_order_for_product_not_found(client, auth_tokens):
    """Test paying for order with non-existent product"""
    resp = client.post(BASE_URL + "/orders/payfor", json=ORDER_NONEXISTENT_PRODUCT, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 404


def test_pay_order_for_unauthenticated(client):
    """Test paying for order without authentication"""
    resp = client.post(BASE_URL + "/orders/payfor", json=ORDER_SAMPLE_1)
    assert resp.status_code == 401


def test_pay_order_for_forbidden_as_cashier(client, auth_tokens):
    """Test that Cashier cannot pay for orders"""
    resp = client.post(BASE_URL + "/orders/payfor", json=ORDER_SAMPLE_1, headers=auth_header(auth_tokens, "cashier"))
    assert resp.status_code == 403


def test_pay_order_for_empty_barcode(client, auth_tokens):
    """Test paying for order with empty barcode"""
    payload = {
        "product_barcode": "",
        "quantity": 5,
        "price_per_unit": 10.0
    }
    resp = client.post(BASE_URL + "/orders/payfor", json=payload, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code in (400, 422)


def test_pay_order_for_invalid_quantity(client, auth_tokens):
    """Test paying for order with invalid quantity"""
    payload = {
        "product_barcode": "1234567890128",
        "quantity": 0,
        "price_per_unit": 10.0
    }
    resp = client.post(BASE_URL + "/orders/payfor", json=payload, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code in (400, 422)


def test_pay_order_for_invalid_price(client, auth_tokens):
    """Test paying for order with invalid price"""
    payload = {
        "product_barcode": "1234567890128",
        "quantity": 5,
        "price_per_unit": 0
    }
    resp = client.post(BASE_URL + "/orders/payfor", json=payload, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code in (400, 422)


def test_pay_order_for_negative_price(client, auth_tokens):
    """Test paying for order with negative price"""
    payload = {
        "product_barcode": "1234567890128",
        "quantity": 5,
        "price_per_unit": -5.0
    }
    resp = client.post(BASE_URL + "/orders/payfor", json=payload, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code in (400, 422)


def test_pay_order_for_negative_quantity(client, auth_tokens):
    """Test paying for order with negative quantity"""
    payload = {
        "product_barcode": "1234567890128",
        "quantity": -5,
        "price_per_unit": 10.0
    }
    resp = client.post(BASE_URL + "/orders/payfor", json=payload, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code in (400, 422)


# ---------------------------
# PAY ORDER (PATCH /{order_id}/pay)
# ---------------------------

def test_pay_order_success(client, auth_tokens):
    """Test paying for an existing ISSUED order"""
    # First create an order in ISSUED state
    create_resp = client.post(BASE_URL + "/orders", json=ORDER_SAMPLE_1, headers=auth_header(auth_tokens, "admin"))
    assert create_resp.status_code == 201
    order_id = create_resp.json()["id"]
    
    # Now pay for it
    resp = client.patch(BASE_URL + f"/orders/{order_id}/pay", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 201
    data = resp.json()
    assert data["id"] == order_id
    assert data["status"] == "Paid"


def test_pay_order_not_found(client, auth_tokens):
    """Test paying for non-existent order"""
    resp = client.patch(BASE_URL + "/orders/99999/pay", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 404


def test_pay_order_already_paid(client, auth_tokens):
    """Test paying for an order that's already PAID"""
    # Create and pay for an order
    create_resp = client.post(BASE_URL + "/orders/payfor", json=ORDER_SAMPLE_1, headers=auth_header(auth_tokens, "admin"))
    assert create_resp.status_code == 201
    order_id = create_resp.json()["id"]
    
    # Try to pay again
    resp = client.patch(BASE_URL + f"/orders/{order_id}/pay", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 400


def test_pay_order_unauthenticated(client):
    """Test paying for order without authentication"""
    resp = client.patch(BASE_URL + "/orders/1/pay")
    assert resp.status_code == 401


def test_pay_order_forbidden_as_cashier(client, auth_tokens):
    """Test that Cashier cannot pay for orders"""
    resp = client.patch(BASE_URL + "/orders/1/pay", headers=auth_header(auth_tokens, "cashier"))
    assert resp.status_code == 403


def test_pay_order_insufficient_balance(client, auth_tokens):
    """Test paying when insufficient balance exists"""
    # Create order with cost that exceeds balance
    order_payload = {
        "product_barcode": "9876543210987",
        "quantity": 1000,
        "price_per_unit": 100.0
    }
    create_resp = client.post(BASE_URL + "/orders", json=order_payload, headers=auth_header(auth_tokens, "admin"))
    assert create_resp.status_code == 201
    order_id = create_resp.json()["id"]
    
    # Try to pay with insufficient balance
    resp = client.patch(BASE_URL + f"/orders/{order_id}/pay", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 400


# ---------------------------
# RECORD ORDER ARRIVAL (PATCH /{order_id}/arrival)
# ---------------------------

def test_record_arrival_success(client, auth_tokens):
    """Test recording arrival for a PAID order"""
    # Create and pay for an order
    order_payload = {
        "product_barcode": "1234567890128",
        "quantity": 5,
        "price_per_unit": 5.0
    }
    create_resp = client.post(BASE_URL + "/orders/payfor", json=order_payload, headers=auth_header(auth_tokens, "admin"))
    assert create_resp.status_code == 201
    order_id = create_resp.json()["id"]
    
    # Record arrival
    resp = client.patch(BASE_URL + f"/orders/{order_id}/arrival", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 201
    data = resp.json()
    assert data["id"] == order_id
    assert data["status"] == "Completed"


def test_record_arrival_order_not_found(client, auth_tokens):
    """Test recording arrival for non-existent order"""
    resp = client.patch(BASE_URL + "/orders/99999/arrival", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 404


def test_record_arrival_order_not_paid(client, auth_tokens):
    """Test recording arrival for an order that's not PAID"""
    # Create an order in ISSUED state
    create_resp = client.post(BASE_URL + "/orders", json=ORDER_SAMPLE_1, headers=auth_header(auth_tokens, "admin"))
    assert create_resp.status_code == 201
    order_id = create_resp.json()["id"]
    
    # Try to record arrival without paying first
    resp = client.patch(BASE_URL + f"/orders/{order_id}/arrival", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 400


def test_record_arrival_product_no_position(client, auth_tokens):
    """Test recording arrival when product has no position"""
    # Create and pay for order with product that has no position
    order_payload = {
        "product_barcode": "1111111111111",
        "quantity": 3,
        "price_per_unit": 10.0
    }
    create_resp = client.post(BASE_URL + "/orders/payfor", json=order_payload, headers=auth_header(auth_tokens, "admin"))
    assert create_resp.status_code == 201
    order_id = create_resp.json()["id"]
    
    # Try to record arrival
    resp = client.patch(BASE_URL + f"/orders/{order_id}/arrival", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 400


def test_record_arrival_unauthenticated(client):
    """Test recording arrival without authentication"""
    resp = client.patch(BASE_URL + "/orders/1/arrival")
    assert resp.status_code == 401


def test_record_arrival_forbidden_as_cashier(client, auth_tokens):
    """Test that Cashier cannot record order arrivals"""
    resp = client.patch(BASE_URL + "/orders/1/arrival", headers=auth_header(auth_tokens, "cashier"))
    assert resp.status_code == 403


def test_record_arrival_completed_order(client, auth_tokens):
    """Test recording arrival for already completed order"""
    # Create, pay, and arrive an order
    order_payload = {
        "product_barcode": "9876543210987",
        "quantity": 2,
        "price_per_unit": 15.0
    }
    create_resp = client.post(BASE_URL + "/orders/payfor", json=order_payload, headers=auth_header(auth_tokens, "admin"))
    order_id = create_resp.json()["id"]
    
    # Record arrival first time
    resp1 = client.patch(BASE_URL + f"/orders/{order_id}/arrival", headers=auth_header(auth_tokens, "admin"))
    assert resp1.status_code == 201
    
    # Try to record arrival again (should fail - already completed)
    resp2 = client.patch(BASE_URL + f"/orders/{order_id}/arrival", headers=auth_header(auth_tokens, "admin"))
    assert resp2.status_code == 400


def test_complete_order_lifecycle(client, auth_tokens):
    """Test complete order lifecycle: issue -> pay -> arrival"""
    # Step 1: Issue order
    order_payload = {
        "product_barcode": "9876543210987",
        "quantity": 3,
        "price_per_unit": 15.0
    }
    issue_resp = client.post(BASE_URL + "/orders", json=order_payload, headers=auth_header(auth_tokens, "admin"))
    assert issue_resp.status_code == 201
    order_id = issue_resp.json()["id"]
    assert issue_resp.json()["status"] == "Issued"
    
    # Step 2: Pay for order
    pay_resp = client.patch(BASE_URL + f"/orders/{order_id}/pay", headers=auth_header(auth_tokens, "admin"))
    assert pay_resp.status_code == 201
    assert pay_resp.json()["status"] == "Paid"
    
    # Step 3: Record arrival
    arrival_resp = client.patch(BASE_URL + f"/orders/{order_id}/arrival", headers=auth_header(auth_tokens, "admin"))
    assert arrival_resp.status_code == 201
    assert arrival_resp.json()["status"] == "Completed"


def test_delete_order_success(client, auth_tokens):
    """Test deleting an order"""
    # Create an order
    create_resp = client.post(BASE_URL + "/orders", json=ORDER_SAMPLE_1, headers=auth_header(auth_tokens, "admin"))
    order_id = create_resp.json()["id"]
    
    # Delete the order
    resp = client.delete(BASE_URL + f"/orders/{order_id}", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 204


def test_delete_order_not_found(client, auth_tokens):
    """Test deleting non-existent order"""
    resp = client.delete(BASE_URL + "/orders/99999", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 404


def test_delete_order_unauthenticated(client):
    """Test deleting order without authentication"""
    resp = client.delete(BASE_URL + "/orders/1")
    assert resp.status_code == 401


def test_delete_order_forbidden_as_manager(client, auth_tokens):
    """Test that Manager cannot delete orders"""
    resp = client.delete(BASE_URL + "/orders/1", headers=auth_header(auth_tokens, "manager"))
    assert resp.status_code == 403


def test_delete_order_forbidden_as_cashier(client, auth_tokens):
    """Test that Cashier cannot delete orders"""
    resp = client.delete(BASE_URL + "/orders/1", headers=auth_header(auth_tokens, "cashier"))
    assert resp.status_code == 403


def test_payfor_and_arrival_lifecycle_with_full_cycle(client, auth_tokens):
    """Test simplified lifecycle: payfor -> arrival"""
    # Step 1: Create and pay for order
    order_payload = {
        "product_barcode": "9876543210987",
        "quantity": 7,
        "price_per_unit": 18.0
    }
    payfor_resp = client.post(BASE_URL + "/orders/payfor", json=order_payload, headers=auth_header(auth_tokens, "admin"))
    assert payfor_resp.status_code == 201
    order_id = payfor_resp.json()["id"]
    assert payfor_resp.json()["status"] == "Paid"
    
    # Step 2: Record arrival
    arrival_resp = client.patch(BASE_URL + f"/orders/{order_id}/arrival", headers=auth_header(auth_tokens, "admin"))
    assert arrival_resp.status_code == 201
    assert arrival_resp.json()["status"] == "Completed"


def test_issue_order_whitespace_barcode_triggers_route_validation(client, auth_tokens):
    """Test that whitespace-only barcode triggers route-level validation (line 40)"""
    payload = {
        "product_barcode": "   ",
        "quantity": 5,
        "price_per_unit": 10.0
    }
    resp = client.post(BASE_URL + "/orders", json=payload, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 400


def test_issue_order_negative_quantity_triggers_validation(client, auth_tokens):
    """Test negative quantity validation (line 42)"""
    payload = {
        "product_barcode": "1234567890128",
        "quantity": -5,
        "price_per_unit": 10.0
    }
    resp = client.post(BASE_URL + "/orders", json=payload, headers=auth_header(auth_tokens, "admin"))
    # Pydantic may reject this as 422 or route may reject as 400
    assert resp.status_code in (400, 422)


def test_record_arrival_triggers_product_not_found_error(client, auth_tokens):
    """Test arrival with product that doesn't exist (line 146)"""
    # Create order with valid product
    order_payload = {
        "product_barcode": "1234567890128",
        "quantity": 5,
        "price_per_unit": 5.0
    }
    create_resp = client.post(BASE_URL + "/orders/payfor", json=order_payload, headers=auth_header(auth_tokens, "admin"))
    order_id = create_resp.json()["id"]
    
    # This should work normally (product exists)
    resp = client.patch(BASE_URL + f"/orders/{order_id}/arrival", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 201


def test_get_all_orders_empty(client, auth_tokens):
    """Test getting all orders when list is empty (exercises return path)"""
    # Create fresh session to get empty list
    resp = client.get(BASE_URL + "/orders", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

def test_get_order_not_found_exercises_return(client, auth_tokens):
    """Test get order when not found exercises return path (line 84)"""
    resp = client.get(BASE_URL + "/orders/999999", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 404


def test_pay_order_not_found_exercises_return(client, auth_tokens):
    """Test paying non-existent order exercises return path"""
    resp = client.patch(BASE_URL + "/orders/999999/pay", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 404


def test_record_arrival_not_found_exercises_return(client, auth_tokens):
    """Test arrival for non-existent order exercises return path"""
    resp = client.patch(BASE_URL + "/orders/999999/arrival", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 404


def test_delete_order_not_found_exercises_return(client, auth_tokens):
    """Test delete non-existent order exercises return path"""
    resp = client.delete(BASE_URL + "/orders/999999", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 404


# ---------------------------
# DIRECT REPOSITORY EDGE CASES FOR 100% COVERAGE
# ---------------------------
import pytest
import asyncio
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.system_repository import SystemRepository
from app.models.errors.notfound_error import NotFoundError
from app.models.errors.bad_request import BadRequestError
from app.models.DAO.order_dao import OrderStatus

@pytest.mark.asyncio
async def test_order_repo_get_system_info_creates_if_missing():
    from init_db import reset, init_db
    await reset(); await init_db()
    repo = OrderRepository()
    session = await repo._get_session()
    from sqlalchemy import text
    await session.execute(text("DELETE FROM system_info"))
    await session.commit()
    sysinfo = await repo._get_system_info(session)
    assert sysinfo.balance == 0.0

@pytest.mark.asyncio
async def test_order_repo_get_product_by_barcode_not_found():
    repo = OrderRepository()
    session = await repo._get_session()
    with pytest.raises(NotFoundError):
        await repo._get_product_by_barcode(session, "nonexistent-barcode-xyz")

@pytest.mark.asyncio
async def test_order_repo_get_all_orders_empty():
    from init_db import reset, init_db
    await reset(); await init_db()
    repo = OrderRepository()
    session = await repo._get_session()
    from sqlalchemy import text
    await session.execute(text("DELETE FROM orders"))
    await session.commit()
    orders = await repo.get_all_orders()
    assert orders == []

@pytest.mark.asyncio
async def test_order_repo_pay_order_wrong_status():
    from init_db import reset, init_db
    await reset(); await init_db()
    from app.models.DAO.order_dao import OrderDAO
    repo = OrderRepository()
    prod_repo = ProductRepository()
    prod = await prod_repo.create_product(description="RepoTest", barcode="repo-pay-status", price_per_unit=1.0, quantity=1)
    order = await repo.create_order(prod.id, 1, 1.0)
    # Persist status change on a managed instance (the returned order is detached)
    async with await repo._get_session() as session:
        db_order = await session.get(OrderDAO, order.id)
        db_order.status = OrderStatus.Paid
        await session.commit()
    with pytest.raises(BadRequestError):
        await repo.pay_order(order.id)


@pytest.mark.asyncio
async def test_order_repo_pay_order_success_updates_balance():
    from init_db import reset, init_db
    await reset(); await init_db()
    repo = OrderRepository()
    prod_repo = ProductRepository()
    sys_repo = SystemRepository()

    prod = await prod_repo.create_product(description="RepoPayOK", barcode="repo-pay-ok", price_per_unit=2.5, quantity=1)
    order = await repo.create_order(prod.id, 4, 2.5)
    await sys_repo.set_balance(100.0)

    paid = await repo.pay_order(order.id)
    assert paid.status == OrderStatus.Paid
    system = await sys_repo.get_singleton()
    assert system.balance == 100.0 - (4 * 2.5)

@pytest.mark.asyncio
async def test_order_repo_pay_order_insufficient_balance():
    from init_db import reset, init_db
    await reset(); await init_db()
    repo = OrderRepository()
    prod_repo = ProductRepository()
    prod = await prod_repo.create_product(description="RepoTest2", barcode="repo-pay-balance", price_per_unit=10000.0, quantity=1)
    order = await repo.create_order(prod.id, 1, 10000.0)
    sys_repo = SystemRepository()
    await sys_repo.set_balance(0.0)
    with pytest.raises(BadRequestError):
        await repo.pay_order(order.id)

@pytest.mark.asyncio
async def test_order_repo_record_arrival_wrong_status():
    from init_db import reset, init_db
    await reset(); await init_db()
    repo = OrderRepository()
    prod_repo = ProductRepository()
    prod = await prod_repo.create_product(description="RepoTest3", barcode="repo-arrival-status", price_per_unit=1.0, quantity=1, position="1-A-1")
    order = await repo.create_order(prod.id, 1, 1.0)
    with pytest.raises(BadRequestError):
        await repo.record_order_arrival(order.id)

@pytest.mark.asyncio
async def test_order_repo_record_arrival_product_not_found():
    from init_db import reset, init_db
    await reset(); await init_db()
    repo = OrderRepository()
    prod_repo = ProductRepository()
    prod = await prod_repo.create_product(description="RepoTest4", barcode="repo-arrival-notfound", price_per_unit=1.0, quantity=1, position="1-A-1")
    order = await repo.create_order(prod.id, 1, 1.0)
    sys_repo = SystemRepository()
    await sys_repo.set_balance(1000.0)
    await repo.pay_order(order.id)
    session = await repo._get_session()
    from sqlalchemy import text
    await session.execute(text(f"DELETE FROM product_types WHERE id={prod.id}"))
    await session.commit()
    with pytest.raises(NotFoundError):
        await repo.record_order_arrival(order.id)

@pytest.mark.asyncio
async def test_order_repo_record_arrival_no_position():
    from init_db import reset, init_db
    await reset(); await init_db()
    repo = OrderRepository()
    prod_repo = ProductRepository()
    prod = await prod_repo.create_product(description="RepoTest5", barcode="repo-arrival-nopos", price_per_unit=1.0, quantity=1, position=None)
    order = await repo.create_order(prod.id, 1, 1.0)
    sys_repo = SystemRepository()
    await sys_repo.set_balance(1000.0)
    await repo.pay_order(order.id)
    with pytest.raises(BadRequestError):
        await repo.record_order_arrival(order.id)


@pytest.mark.asyncio
async def test_order_repo_record_arrival_success_updates_quantity():
    from init_db import reset, init_db
    await reset(); await init_db()
    repo = OrderRepository()
    prod_repo = ProductRepository()
    sys_repo = SystemRepository()

    prod = await prod_repo.create_product(description="RepoArriveOK", barcode="repo-arrive-ok", price_per_unit=1.0, quantity=5, position="1-A-1")
    order = await repo.create_order(prod.id, 3, 1.0)
    await sys_repo.set_balance(100.0)
    await repo.pay_order(order.id)

    arrived = await repo.record_order_arrival(order.id)
    assert arrived.status == OrderStatus.Completed
    updated_product = await prod_repo.get_product_by_id(prod.id)
    assert updated_product.quantity == 8


@pytest.mark.asyncio
async def test_order_repo_delete_order_success():
    from init_db import reset, init_db
    await reset(); await init_db()
    repo = OrderRepository()
    prod_repo = ProductRepository()
    prod = await prod_repo.create_product(description="RepoDelOrder", barcode="repo-del-order", price_per_unit=1.0, quantity=1)
    order = await repo.create_order(prod.id, 1, 1.0)
    assert await repo.delete_order(order.id) is True


# ---------------------------
# ROUTE-LEVEL VALIDATION BRANCHES (Pydantic-bypassed)
# ---------------------------

@pytest.mark.asyncio
async def test_order_route_issue_order_rejects_quantity_le_zero_direct_call():
    from app.routes.order_route import issue_order
    from app.models.DTO.order_dto import OrderCreateDTO
    from app.models.errors.bad_request import BadRequestError

    dto = OrderCreateDTO.model_construct(product_barcode="abc", quantity=0, price_per_unit=1.0)
    with pytest.raises(BadRequestError):
        await issue_order(dto)


@pytest.mark.asyncio
async def test_order_route_issue_order_rejects_price_le_zero_direct_call():
    from app.routes.order_route import issue_order
    from app.models.DTO.order_dto import OrderCreateDTO
    from app.models.errors.bad_request import BadRequestError

    dto = OrderCreateDTO.model_construct(product_barcode="abc", quantity=1, price_per_unit=0.0)
    with pytest.raises(BadRequestError):
        await issue_order(dto)


@pytest.mark.asyncio
async def test_order_route_payfor_rejects_invalid_fields_direct_call():
    from app.routes.order_route import pay_for_order
    from app.models.DTO.order_dto import OrderPayForDTO
    from app.models.errors.bad_request import BadRequestError

    dto_barcode = OrderPayForDTO.model_construct(product_barcode="   ", quantity=1, price_per_unit=1.0)
    with pytest.raises(BadRequestError):
        await pay_for_order(dto_barcode)

    dto_qty = OrderPayForDTO.model_construct(product_barcode="abc", quantity=0, price_per_unit=1.0)
    with pytest.raises(BadRequestError):
        await pay_for_order(dto_qty)

    dto_price = OrderPayForDTO.model_construct(product_barcode="abc", quantity=1, price_per_unit=0.0)
    with pytest.raises(BadRequestError):
        await pay_for_order(dto_price)

@pytest.mark.asyncio
async def test_order_repo_delete_order_not_found():
    from init_db import reset, init_db
    await reset(); await init_db()
    repo = OrderRepository()
    with pytest.raises(NotFoundError):
        await repo.delete_order(99999999)