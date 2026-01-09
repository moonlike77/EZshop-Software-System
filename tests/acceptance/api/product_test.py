"""
API tests for product routes
Tests the API layer with authentication and request/response validation
"""
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
# SAMPLE PAYLOADS
# ---------------------------

PRODUCT_SAMPLE_1 = {
    "barcode": "1234567890123",
    "description": "Apple iPhone 14",
    "price_per_unit": 999.99,
    "quantity": 50,
    "note": "Latest model",
    "position": "A1-B2-C3"
}

PRODUCT_SAMPLE_2 = {
    "barcode": "2345678901234",
    "description": "Samsung Galaxy S23",
    "price_per_unit": 899.99,
    "quantity": 30,
    "note": "Android flagship",
    "position": "A2-B3-C4"
}

PRODUCT_SAMPLE_3 = {
    "barcode": "3456789012345",
    "description": "Google Pixel 8",
    "price_per_unit": 699.99,
    "quantity": 20
}

PRODUCT_MINIMAL = {
    "barcode": "4567890123456",
    "description": "Minimal Product",
    "price_per_unit": 49.99
}

PRODUCT_UPDATE = {
    "description": "Updated Product Description",
    "price_per_unit": 1099.99,
    "note": "Updated notes"
}


# ---------------------------
# CREATE PRODUCT TESTS
# ---------------------------

def test_create_product_success_as_admin(client, auth_tokens):
    resp = client.post(BASE_URL + "/products", json=PRODUCT_SAMPLE_1, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 201
    data = resp.json()
    assert data["barcode"] == PRODUCT_SAMPLE_1["barcode"]
    assert data["description"] == PRODUCT_SAMPLE_1["description"]
    assert data["price_per_unit"] == PRODUCT_SAMPLE_1["price_per_unit"]


def test_create_product_success_as_manager(client, auth_tokens):
    resp = client.post(BASE_URL + "/products", json=PRODUCT_SAMPLE_2, headers=auth_header(auth_tokens, "manager"))
    assert resp.status_code == 201
    data = resp.json()
    assert data["barcode"] == PRODUCT_SAMPLE_2["barcode"]


def test_create_product_forbidden_as_cashier(client, auth_tokens):
    resp = client.post(BASE_URL + "/products", json=PRODUCT_SAMPLE_3, headers=auth_header(auth_tokens, "cashier"))
    assert resp.status_code == 403


def test_create_product_unauthenticated(client):
    resp = client.post(BASE_URL + "/products", json=PRODUCT_SAMPLE_3)
    assert resp.status_code == 401


def test_create_product_duplicate_barcode(client, auth_tokens):
    # Try to create with same barcode as PRODUCT_SAMPLE_1
    resp = client.post(BASE_URL + "/products", json=PRODUCT_SAMPLE_1, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 409


def test_create_product_missing_fields(client, auth_tokens):
    bad_product = {"barcode": "5555555555555"}
    resp = client.post(BASE_URL + "/products", json=bad_product, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code in (400, 422)


def test_create_product_invalid_barcode(client, auth_tokens):
    invalid_product = {
        "barcode": "123",  # Too short
        "description": "Invalid Product",
        "sell_price": 10.0
    }
    resp = client.post(BASE_URL + "/products", json=invalid_product, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code in (400, 422)


def test_create_product_invalid_position(client, auth_tokens):
    invalid_product = {
        "barcode": "6666666666666",
        "description": "Invalid Position Product",
        "price_per_unit": 10.0,
        "position": "INVALID"
    }
    resp = client.post(BASE_URL + "/products", json=invalid_product, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 201  # Position is not validated on create


def test_create_product_minimal_fields(client, auth_tokens):
    resp = client.post(BASE_URL + "/products", json=PRODUCT_MINIMAL, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 201
    data = resp.json()
    assert data["quantity"] == 0


# ---------------------------
# GET PRODUCT TESTS
# ---------------------------

def test_get_all_products_success_as_admin(client, auth_tokens):
    resp = client.get(BASE_URL + "/products", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_get_all_products_success_as_manager(client, auth_tokens):
    resp = client.get(BASE_URL + "/products", headers=auth_header(auth_tokens, "manager"))
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_get_all_products_success_as_cashier(client, auth_tokens):
    resp = client.get(BASE_URL + "/products", headers=auth_header(auth_tokens, "cashier"))
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_get_all_products_unauthenticated(client):
    resp = client.get(BASE_URL + "/products")
    assert resp.status_code == 401


def test_get_product_by_id_success(client, auth_tokens):
    # Create a product first
    create_resp = client.post(BASE_URL + "/products", json=PRODUCT_SAMPLE_3, headers=auth_header(auth_tokens, "admin"))
    product_id = create_resp.json()["id"]
    
    # Get the product
    resp = client.get(f"{BASE_URL}/products/{product_id}", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == product_id


def test_get_product_by_id_not_found(client, auth_tokens):
    resp = client.get(f"{BASE_URL}/products/99999", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 404


def test_get_product_by_id_invalid_id(client, auth_tokens):
    resp = client.get(f"{BASE_URL}/products/0", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code in (400, 404)


def test_get_product_by_id_unauthenticated(client):
    resp = client.get(f"{BASE_URL}/products/1")
    assert resp.status_code == 401


def test_get_product_by_barcode_success(client, auth_tokens):
    resp = client.get(f"{BASE_URL}/products/barcode/{PRODUCT_SAMPLE_1['barcode']}", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 200
    data = resp.json()
    assert data["barcode"] == PRODUCT_SAMPLE_1["barcode"]


def test_get_product_by_barcode_not_found(client, auth_tokens):
    resp = client.get(f"{BASE_URL}/products/barcode/9999999999999", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 404


def test_get_product_by_barcode_invalid_format(client, auth_tokens):
    resp = client.get(f"{BASE_URL}/products/barcode/123", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code in (400, 404)


def test_get_product_by_barcode_unauthenticated(client):
    resp = client.get(f"{BASE_URL}/products/barcode/1234567890123")
    assert resp.status_code == 401


# ---------------------------
# SEARCH PRODUCTS TESTS
# ---------------------------

def test_search_products_success(client, auth_tokens):
    resp = client.get(f"{BASE_URL}/products/search?query=iphone", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any("iPhone" in p["description"] for p in data)


def test_search_products_no_results(client, auth_tokens):
    resp = client.get(f"{BASE_URL}/products/search?query=nonexistent", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_search_products_case_insensitive(client, auth_tokens):
    resp = client.get(f"{BASE_URL}/products/search?query=SAMSUNG", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) > 0


def test_search_products_unauthenticated(client):
    resp = client.get(f"{BASE_URL}/products/search?query=test")
    assert resp.status_code == 401


# ---------------------------
# UPDATE PRODUCT TESTS
# ---------------------------

def test_update_product_success(client, auth_tokens):
    # Create a product
    create_resp = client.post(BASE_URL + "/products", json={
        "barcode": "7777777777777",
        "description": "Original Product",
        "price_per_unit": 10.0
    }, headers=auth_header(auth_tokens, "admin"))
    product_id = create_resp.json()["id"]
    
    # Update it
    resp = client.put(f"{BASE_URL}/products/{product_id}", json=PRODUCT_UPDATE, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 200
    data = resp.json()
    assert data["description"] == PRODUCT_UPDATE["description"]
    assert data["price_per_unit"] == PRODUCT_UPDATE["price_per_unit"]


def test_update_product_not_found(client, auth_tokens):
    resp = client.put(f"{BASE_URL}/products/99999", json=PRODUCT_UPDATE, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 404


def test_update_product_barcode_conflict(client, auth_tokens):
    # Try to update to an existing barcode
    create_resp = client.post(BASE_URL + "/products", json={
        "barcode": "8888888888888",
        "description": "Another Product",
        "price_per_unit": 20.0
    }, headers=auth_header(auth_tokens, "admin"))
    product_id = create_resp.json()["id"]
    
    update_data = {"barcode": PRODUCT_SAMPLE_1["barcode"]}
    resp = client.put(f"{BASE_URL}/products/{product_id}", json=update_data, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 400


def test_update_product_forbidden_as_cashier(client, auth_tokens):
    # Create a product as admin
    create_resp = client.post(BASE_URL + "/products", json={
        "barcode": "9999999999999",
        "description": "Test Product",
        "price_per_unit": 10.0
    }, headers=auth_header(auth_tokens, "admin"))
    product_id = create_resp.json()["id"]
    
    # Try to update as cashier
    resp = client.put(f"{BASE_URL}/products/{product_id}", json=PRODUCT_UPDATE, headers=auth_header(auth_tokens, "cashier"))
    assert resp.status_code == 403


def test_update_product_unauthenticated(client):
    resp = client.put(f"{BASE_URL}/products/1", json=PRODUCT_UPDATE)
    assert resp.status_code == 401


# ---------------------------
# UPDATE QUANTITY TESTS
# ---------------------------

def test_update_quantity_increase(client, auth_tokens):
    # Create a product
    create_resp = client.post(BASE_URL + "/products", json={
        "barcode": "1111111111111",
        "description": "Quantity Test",
        "price_per_unit": 10.0,
        "quantity": 100
    }, headers=auth_header(auth_tokens, "admin"))
    product_id = create_resp.json()["id"]
    
    # Increase quantity
    resp = client.patch(f"{BASE_URL}/products/{product_id}/quantity?quantity=50", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 200
    data = resp.json()
    assert data["quantity"] == 150


def test_update_quantity_decrease(client, auth_tokens):
    # Create a product
    create_resp = client.post(BASE_URL + "/products", json={
        "barcode": "2222222222222",
        "description": "Quantity Test 2",
        "price_per_unit": 10.0,
        "quantity": 100
    }, headers=auth_header(auth_tokens, "admin"))
    product_id = create_resp.json()["id"]
    
    # Decrease quantity
    resp = client.patch(f"{BASE_URL}/products/{product_id}/quantity?quantity=-30", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 200
    data = resp.json()
    assert data["quantity"] == 70


def test_update_quantity_not_found(client, auth_tokens):
    resp = client.patch(f"{BASE_URL}/products/99999/quantity?quantity=10", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 404


def test_update_quantity_negative_result(client, auth_tokens):
    """Test update_quantity when result would be negative - covers BadRequestError exception"""
    import time
    unique_barcode = f"NEG{int(time.time()*1000)}"
    
    # Create product with quantity 10
    create_resp = client.post(BASE_URL + "/products", json={
        "description": "Low Stock Product",
        "barcode": unique_barcode,
        "price_per_unit": 5.0,
        "quantity": 10
    }, headers=auth_header(auth_tokens, "admin"))
    assert create_resp.status_code == 201
    product_id = create_resp.json()["id"]
    
    # Try to decrease by 20 (would make it -10)
    resp = client.patch(f"{BASE_URL}/products/{product_id}/quantity?quantity=-20", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 400


def test_update_quantity_forbidden_as_cashier(client, auth_tokens):
    resp = client.patch(f"{BASE_URL}/products/1/quantity?quantity=10", headers=auth_header(auth_tokens, "cashier"))
    assert resp.status_code == 403


def test_update_quantity_unauthenticated(client):
    resp = client.patch(f"{BASE_URL}/products/1/quantity?quantity=10")
    assert resp.status_code == 401


# ---------------------------
# UPDATE POSITION TESTS
# ---------------------------

def test_update_position_success(client, auth_tokens):
    # Create a product
    create_resp = client.post(BASE_URL + "/products", json={
        "barcode": "3333333333333",
        "description": "Position Test",
        "price_per_unit": 10.0
    }, headers=auth_header(auth_tokens, "admin"))
    product_id = create_resp.json()["id"]
    
    # Update position
    resp = client.patch(f"{BASE_URL}/products/{product_id}/position?position=9-ZY-87", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 200
    data = resp.json()
    assert data["position"] == "9-ZY-87"


def test_update_position_clear(client, auth_tokens):
    # Create a product with position
    create_resp = client.post(BASE_URL + "/products", json={
        "barcode": "4444444444444",
        "description": "Position Test 2",
        "price_per_unit": 10.0,
        "position": "A1-B2-C3"
    }, headers=auth_header(auth_tokens, "admin"))
    product_id = create_resp.json()["id"]
    
    # Clear position
    resp = client.patch(f"{BASE_URL}/products/{product_id}/position?position=", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 200
    data = resp.json()
    assert data["position"] is None or data["position"] == ""


def test_update_position_invalid_format(client, auth_tokens):
    # Create a product
    create_resp = client.post(BASE_URL + "/products", json={
        "barcode": "5555555555555",
        "description": "Position Test 3",
        "price_per_unit": 10.0
    }, headers=auth_header(auth_tokens, "admin"))
    product_id = create_resp.json()["id"]
    
    # Try invalid position
    resp = client.patch(f"{BASE_URL}/products/{product_id}/position?position=INVALID", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 400


def test_update_position_not_found(client, auth_tokens):
    resp = client.patch(f"{BASE_URL}/products/99999/position?position=A1-B2-C3", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 404


def test_update_position_forbidden_as_cashier(client, auth_tokens):
    resp = client.patch(f"{BASE_URL}/products/1/position?position=A1-B2-C3", headers=auth_header(auth_tokens, "cashier"))
    assert resp.status_code == 403


def test_update_position_unauthenticated(client):
    resp = client.patch(f"{BASE_URL}/products/1/position?position=A1-B2-C3")
    assert resp.status_code == 401


# ---------------------------
# DELETE PRODUCT TESTS
# ---------------------------

def test_delete_product_success(client, auth_tokens):
    # Create a product with unique barcode
    import time
    unique_barcode = f"{int(time.time() * 1000000) % 10000000000000}"
    create_resp = client.post(BASE_URL + "/products", json={
        "barcode": unique_barcode,
        "description": "Delete Test",
        "price_per_unit": 10.0
    }, headers=auth_header(auth_tokens, "admin"))
    assert create_resp.status_code == 201, f"Create failed: {create_resp.json()}"
    product_id = create_resp.json()["id"]
    
    # Delete it
    resp = client.delete(f"{BASE_URL}/products/{product_id}", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 204


def test_delete_product_not_found(client, auth_tokens):
    resp = client.delete(f"{BASE_URL}/products/99999", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 404


def test_delete_product_forbidden_as_cashier(client, auth_tokens):
    # Create a product as admin
    create_resp = client.post(BASE_URL + "/products", json={
        "barcode": "7777777777778",
        "description": "Delete Test 2",
        "price_per_unit": 10.0
    }, headers=auth_header(auth_tokens, "admin"))
    product_id = create_resp.json()["id"]
    
    # Try to delete as cashier
    resp = client.delete(f"{BASE_URL}/products/{product_id}", headers=auth_header(auth_tokens, "cashier"))
    assert resp.status_code == 403


def test_delete_product_unauthenticated(client):
    resp = client.delete(f"{BASE_URL}/products/1")
    assert resp.status_code == 401
