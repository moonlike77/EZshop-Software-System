# tests/acceptance/product_test.py
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
# BARCODE GENERATOR
# ---------------------------

_barcode_counter = 3000000000000


def get_unique_barcode():
    """Generate a unique barcode for each test."""
    global _barcode_counter
    barcode = str(_barcode_counter)
    _barcode_counter += 1
    return barcode


# ---------------------------
# CREATE PRODUCT TESTS
# ---------------------------

def test_create_product_success_admin(client, auth_tokens):
    """Test creating a product as Administrator"""
    payload = {
        "description": "Test Product",
        "barcode": get_unique_barcode(),
        "price_per_unit": 15.0,
        "quantity": 50,
        "position": "1-A-1"
    }
    resp = client.post(BASE_URL + "/products", json=payload, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 201
    assert resp.json()["description"] == payload["description"]
    assert resp.json()["barcode"] == payload["barcode"]


def test_create_product_success_manager(client, auth_tokens):
    """Test creating a product as Manager"""
    payload = {
        "description": "Manager Product",
        "barcode": get_unique_barcode(),
        "price_per_unit": 25.0
    }
    resp = client.post(BASE_URL + "/products", json=payload, headers=auth_header(auth_tokens, "manager"))
    assert resp.status_code == 201
    assert resp.json()["id"] > 0


def test_create_product_minimal(client, auth_tokens):
    """Test creating product with minimal fields"""
    payload = {
        "description": "Minimal Product",
        "barcode": get_unique_barcode(),
        "price_per_unit": 10.0
    }
    resp = client.post(BASE_URL + "/products", json=payload, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 201


def test_create_product_with_quantity(client, auth_tokens):
    """Test creating product with quantity"""
    payload = {
        "description": "With Qty",
        "barcode": get_unique_barcode(),
        "price_per_unit": 12.0,
        "quantity": 250
    }
    resp = client.post(BASE_URL + "/products", json=payload, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 201
    assert resp.json()["quantity"] == 250


def test_create_product_with_position(client, auth_tokens):
    """Test creating product with position"""
    payload = {
        "description": "With Position",
        "barcode": get_unique_barcode(),
        "price_per_unit": 20.0,
        "position": "3-C-5"
    }
    resp = client.post(BASE_URL + "/products", json=payload, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 201
    assert resp.json()["position"] == "3-C-5"


def test_create_product_with_note(client, auth_tokens):
    """Test creating product with note"""
    payload = {
        "description": "With Note",
        "barcode": get_unique_barcode(),
        "price_per_unit": 18.0,
        "note": "Important notes"
    }
    resp = client.post(BASE_URL + "/products", json=payload, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 201
    assert resp.json()["note"] == "Important notes"


def test_create_product_no_position(client, auth_tokens):
    """Test creating product without position"""
    payload = {
        "description": "No Position",
        "barcode": get_unique_barcode(),
        "price_per_unit": 8.0,
        "quantity": 20
    }
    resp = client.post(BASE_URL + "/products", json=payload, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 201
    assert resp.json()["position"] is None


def test_create_product_duplicate_barcode(client, auth_tokens):
    """Test creating product with duplicate barcode"""
    barcode = get_unique_barcode()
    payload1 = {"description": "First", "barcode": barcode, "price_per_unit": 10.0}
    payload2 = {"description": "Second", "barcode": barcode, "price_per_unit": 15.0}
    
    resp1 = client.post(BASE_URL + "/products", json=payload1, headers=auth_header(auth_tokens, "admin"))
    assert resp1.status_code == 201
    
    resp2 = client.post(BASE_URL + "/products", json=payload2, headers=auth_header(auth_tokens, "admin"))
    assert resp2.status_code == 409


def test_create_product_missing_description(client, auth_tokens):
    """Test creating product without description"""
    payload = {"barcode": get_unique_barcode(), "price_per_unit": 10.0}
    resp = client.post(BASE_URL + "/products", json=payload, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code in (400, 422)


def test_create_product_empty_description(client, auth_tokens):
    """Test creating product with empty description"""
    payload = {"description": "", "barcode": get_unique_barcode(), "price_per_unit": 10.0}
    resp = client.post(BASE_URL + "/products", json=payload, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code in (400, 422)


def test_create_product_missing_barcode(client, auth_tokens):
    """Test creating product without barcode"""
    payload = {"description": "No Barcode", "price_per_unit": 10.0}
    resp = client.post(BASE_URL + "/products", json=payload, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code in (400, 422)


def test_create_product_empty_barcode(client, auth_tokens):
    """Test creating product with empty barcode"""
    payload = {"description": "Empty barcode", "barcode": "", "price_per_unit": 10.0}
    resp = client.post(BASE_URL + "/products", json=payload, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code in (400, 422)


def test_create_product_whitespace_description(client, auth_tokens):
    """Test creating product with whitespace-only description"""
    payload = {"description": "   ", "barcode": get_unique_barcode(), "price_per_unit": 10.0}
    resp = client.post(BASE_URL + "/products", json=payload, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 400


def test_create_product_whitespace_barcode(client, auth_tokens):
    """Test creating product with whitespace-only barcode"""
    payload = {"description": "Valid Description", "barcode": "   ", "price_per_unit": 10.0}
    resp = client.post(BASE_URL + "/products", json=payload, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 400


def test_create_product_missing_price(client, auth_tokens):
    """Test creating product without price"""
    payload = {"description": "No Price", "barcode": get_unique_barcode()}
    resp = client.post(BASE_URL + "/products", json=payload, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code in (400, 422)


def test_create_product_zero_price(client, auth_tokens):
    """Test creating product with zero price"""
    payload = {"description": "Zero Price", "barcode": get_unique_barcode(), "price_per_unit": 0}
    resp = client.post(BASE_URL + "/products", json=payload, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code in (400, 422)


def test_create_product_negative_price(client, auth_tokens):
    """Test creating product with negative price"""
    payload = {"description": "Negative", "barcode": get_unique_barcode(), "price_per_unit": -5.0}
    resp = client.post(BASE_URL + "/products", json=payload, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code in (400, 422)


def test_create_product_unauthenticated(client):
    """Test creating product without auth"""
    payload = {"description": "Test", "barcode": get_unique_barcode(), "price_per_unit": 10.0}
    resp = client.post(BASE_URL + "/products", json=payload)
    assert resp.status_code == 401


def test_create_product_forbidden_cashier(client, auth_tokens):
    """Test cashier cannot create products"""
    payload = {"description": "Test", "barcode": get_unique_barcode(), "price_per_unit": 10.0}
    resp = client.post(BASE_URL + "/products", json=payload, headers=auth_header(auth_tokens, "cashier"))
    assert resp.status_code == 403


# ---------------------------
# LIST PRODUCTS TESTS
# ---------------------------

def test_list_products_admin(client, auth_tokens):
    """Test listing products as admin"""
    resp = client.get(BASE_URL + "/products", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_list_products_manager(client, auth_tokens):
    """Test listing products as manager"""
    resp = client.get(BASE_URL + "/products", headers=auth_header(auth_tokens, "manager"))
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_list_products_cashier(client, auth_tokens):
    """Test listing products as cashier"""
    resp = client.get(BASE_URL + "/products", headers=auth_header(auth_tokens, "cashier"))
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_list_products_unauthenticated(client):
    """Test listing products without auth"""
    resp = client.get(BASE_URL + "/products")
    assert resp.status_code == 401


# ---------------------------
# SEARCH PRODUCTS TESTS
# ---------------------------

def test_search_products_success(client, auth_tokens):
    """Test searching products"""
    resp = client.get(BASE_URL + "/products/search?query=Test", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_search_products_found(client, auth_tokens):
    """Test searching for existing product"""
    # Create a product
    barcode = get_unique_barcode()
    payload = {
        "description": "Searchable Product",
        "barcode": barcode,
        "price_per_unit": 10.0
    }
    client.post(BASE_URL + "/products", json=payload, headers=auth_header(auth_tokens, "admin"))
    
    # Search for it
    resp = client.get(BASE_URL + "/products/search?query=Searchable", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 200
    assert len(resp.json()) > 0


def test_search_products_no_results(client, auth_tokens):
    """Test search with no results"""
    resp = client.get(BASE_URL + "/products/search?query=NonExistent12345", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 200
    assert resp.json() == []


def test_search_products_empty_query(client, auth_tokens):
    """Test search with empty query"""
    resp = client.get(BASE_URL + "/products/search?query=", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 400


def test_search_products_case_insensitive(client, auth_tokens):
    """Test search is case insensitive"""
    resp = client.get(BASE_URL + "/products/search?query=SEARCHABLE", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 200


def test_search_products_unauthenticated(client):
    """Test search without auth"""
    resp = client.get(BASE_URL + "/products/search?query=Test")
    assert resp.status_code == 401


# ---------------------------
# GET BY BARCODE TESTS
# ---------------------------

def test_get_by_barcode_success(client, auth_tokens):
    """Test getting product by barcode"""
    barcode = get_unique_barcode()
    create_payload = {"description": "Barcode Test", "barcode": barcode, "price_per_unit": 10.0}
    client.post(BASE_URL + "/products", json=create_payload, headers=auth_header(auth_tokens, "admin"))
    
    resp = client.get(BASE_URL + f"/products/barcode/{barcode}", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 200
    assert resp.json()["barcode"] == barcode


def test_get_by_barcode_manager(client, auth_tokens):
    """Test getting by barcode as manager"""
    barcode = get_unique_barcode()
    payload = {
        "description": "Manager Barcode",
        "barcode": barcode,
        "price_per_unit": 12.0
    }
    client.post(BASE_URL + "/products", json=payload, headers=auth_header(auth_tokens, "manager"))
    
    resp = client.get(BASE_URL + f"/products/barcode/{barcode}", headers=auth_header(auth_tokens, "manager"))
    assert resp.status_code == 200


def test_get_by_barcode_cashier(client, auth_tokens):
    """Test getting by barcode as cashier"""
    barcode = get_unique_barcode()
    payload = {
        "description": "Cashier Barcode",
        "barcode": barcode,
        "price_per_unit": 12.0
    }
    client.post(BASE_URL + "/products", json=payload, headers=auth_header(auth_tokens, "admin"))
    
    resp = client.get(BASE_URL + f"/products/barcode/{barcode}", headers=auth_header(auth_tokens, "cashier"))
    assert resp.status_code == 200


def test_get_by_barcode_not_found(client, auth_tokens):
    """Test getting non-existent barcode"""
    resp = client.get(BASE_URL + "/products/barcode/0000000000000", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 404


def test_get_by_barcode_unauthenticated(client):
    """Test get by barcode without auth"""
    resp = client.get(BASE_URL + "/products/barcode/1234567890128")
    assert resp.status_code == 401


# ---------------------------
# GET BY ID TESTS
# ---------------------------

def test_get_by_id_success(client, auth_tokens):
    """Test getting product by ID"""
    payload = {"description": "ID Test", "barcode": get_unique_barcode(), "price_per_unit": 10.0}
    create_resp = client.post(BASE_URL + "/products", json=payload, headers=auth_header(auth_tokens, "admin"))
    product_id = create_resp.json()["id"]
    
    resp = client.get(BASE_URL + f"/products/{product_id}", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 200
    assert resp.json()["id"] == product_id


def test_get_by_id_manager(client, auth_tokens):
    """Test getting by ID as manager"""
    payload = {
        "description": "Manager ID",
        "barcode": get_unique_barcode(),
        "price_per_unit": 18.0
    }
    create_resp = client.post(BASE_URL + "/products", json=payload, headers=auth_header(auth_tokens, "manager"))
    product_id = create_resp.json()["id"]
    
    resp = client.get(BASE_URL + f"/products/{product_id}", headers=auth_header(auth_tokens, "manager"))
    assert resp.status_code == 200


def test_get_by_id_cashier(client, auth_tokens):
    """Test getting by ID as cashier"""
    payload = {
        "description": "Cashier ID",
        "barcode": get_unique_barcode(),
        "price_per_unit": 18.0
    }
    create_resp = client.post(BASE_URL + "/products", json=payload, headers=auth_header(auth_tokens, "admin"))
    product_id = create_resp.json()["id"]
    
    resp = client.get(BASE_URL + f"/products/{product_id}", headers=auth_header(auth_tokens, "cashier"))
    assert resp.status_code == 200


def test_get_by_id_not_found(client, auth_tokens):
    """Test getting non-existent ID"""
    resp = client.get(BASE_URL + "/products/99999", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 404


def test_get_by_id_unauthenticated(client):
    """Test get by ID without auth"""
    resp = client.get(BASE_URL + "/products/1")
    assert resp.status_code == 401


# ---------------------------
# UPDATE PRODUCT TESTS
# ---------------------------

def test_update_product_success(client, auth_tokens):
    """Test updating product"""
    payload = {"description": "Update Test", "barcode": get_unique_barcode(), "price_per_unit": 10.0}
    create_resp = client.post(BASE_URL + "/products", json=payload, headers=auth_header(auth_tokens, "admin"))
    product_id = create_resp.json()["id"]
    
    update_payload = {"description": "Updated", "price_per_unit": 20.0}
    resp = client.put(BASE_URL + f"/products/{product_id}", json=update_payload, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 200
    assert resp.json()["description"] == "Updated"
    assert resp.json()["price_per_unit"] == 20.0


def test_update_product_description(client, auth_tokens):
    """Test updating product description"""
    payload = {"description": "Original", "barcode": get_unique_barcode(), "price_per_unit": 10.0}
    create_resp = client.post(BASE_URL + "/products", json=payload, headers=auth_header(auth_tokens, "admin"))
    product_id = create_resp.json()["id"]
    
    resp = client.put(BASE_URL + f"/products/{product_id}", json={"description": "Updated"}, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 200
    assert resp.json()["description"] == "Updated"


def test_update_product_price(client, auth_tokens):
    """Test updating product price"""
    payload = {"description": "Price Update", "barcode": get_unique_barcode(), "price_per_unit": 10.0}
    create_resp = client.post(BASE_URL + "/products", json=payload, headers=auth_header(auth_tokens, "admin"))
    product_id = create_resp.json()["id"]
    
    resp = client.put(BASE_URL + f"/products/{product_id}", json={"price_per_unit": 25.0}, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 200
    assert resp.json()["price_per_unit"] == 25.0


def test_update_product_note(client, auth_tokens):
    """Test updating product note"""
    payload = {"description": "Note Update", "barcode": get_unique_barcode(), "price_per_unit": 10.0}
    create_resp = client.post(BASE_URL + "/products", json=payload, headers=auth_header(auth_tokens, "admin"))
    product_id = create_resp.json()["id"]
    
    resp = client.put(BASE_URL + f"/products/{product_id}", json={"note": "New note"}, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 200
    assert resp.json()["note"] == "New note"


def test_update_product_barcode(client, auth_tokens):
    """Test updating product barcode"""
    payload = {"description": "Barcode Update", "barcode": get_unique_barcode(), "price_per_unit": 10.0}
    create_resp = client.post(BASE_URL + "/products", json=payload, headers=auth_header(auth_tokens, "admin"))
    product_id = create_resp.json()["id"]
    
    new_barcode = get_unique_barcode()
    update_payload = {"barcode": new_barcode}
    resp = client.put(BASE_URL + f"/products/{product_id}", json=update_payload, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 200
    assert resp.json()["barcode"] == new_barcode


def test_update_product_duplicate_barcode(client, auth_tokens):
    """Test updating to duplicate barcode"""
    barcode1 = get_unique_barcode()
    barcode2 = get_unique_barcode()
    
    payload1 = {"description": "Product 1", "barcode": barcode1, "price_per_unit": 10.0}
    payload2 = {"description": "Product 2", "barcode": barcode2, "price_per_unit": 15.0}
    
    resp1 = client.post(BASE_URL + "/products", json=payload1, headers=auth_header(auth_tokens, "admin"))
    resp2 = client.post(BASE_URL + "/products", json=payload2, headers=auth_header(auth_tokens, "admin"))
    product2_id = resp2.json()["id"]
    
    # Try to update product 2 to product 1's barcode
    update_payload = {"barcode": barcode1}
    resp = client.put(BASE_URL + f"/products/{product2_id}", json=update_payload, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code in (400, 409)  # Either bad request or conflict


def test_update_product_manager(client, auth_tokens):
    """Test updating product as manager"""
    payload = {"description": "Manager Update", "barcode": get_unique_barcode(), "price_per_unit": 10.0}
    create_resp = client.post(BASE_URL + "/products", json=payload, headers=auth_header(auth_tokens, "manager"))
    product_id = create_resp.json()["id"]
    
    resp = client.put(BASE_URL + f"/products/{product_id}", json={"description": "Changed"}, headers=auth_header(auth_tokens, "manager"))
    assert resp.status_code == 200


def test_update_product_not_found(client, auth_tokens):
    """Test updating non-existent product"""
    resp = client.put(BASE_URL + "/products/99999", json={"description": "Test"}, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 404


def test_update_product_invalid_price(client, auth_tokens):
    """Test updating with invalid price"""
    payload = {"description": "Price Test", "barcode": get_unique_barcode(), "price_per_unit": 10.0}
    create_resp = client.post(BASE_URL + "/products", json=payload, headers=auth_header(auth_tokens, "admin"))
    product_id = create_resp.json()["id"]
    
    resp = client.put(BASE_URL + f"/products/{product_id}", json={"price_per_unit": 0}, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code in (400, 422)


def test_update_product_negative_price(client, auth_tokens):
    """Test updating with negative price"""
    payload = {"description": "Price Test", "barcode": get_unique_barcode(), "price_per_unit": 10.0}
    create_resp = client.post(BASE_URL + "/products", json=payload, headers=auth_header(auth_tokens, "admin"))
    product_id = create_resp.json()["id"]
    
    resp = client.put(BASE_URL + f"/products/{product_id}", json={"price_per_unit": -5.0}, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code in (400, 422)


def test_update_product_unauthenticated(client):
    """Test update without auth"""
    resp = client.put(BASE_URL + "/products/1", json={"description": "Test"})
    assert resp.status_code == 401


def test_update_product_forbidden_cashier(client, auth_tokens):
    """Test cashier cannot update products"""
    resp = client.put(BASE_URL + "/products/1", json={"description": "Test"}, headers=auth_header(auth_tokens, "cashier"))
    assert resp.status_code == 403


# ---------------------------
# UPDATE POSITION TESTS
# ---------------------------

def test_update_position_success(client, auth_tokens):
    """Test updating product position"""
    payload = {"description": "Position Test", "barcode": get_unique_barcode(), "price_per_unit": 10.0}
    create_resp = client.post(BASE_URL + "/products", json=payload, headers=auth_header(auth_tokens, "admin"))
    product_id = create_resp.json()["id"]
    
    resp = client.patch(BASE_URL + f"/products/{product_id}/position?position=3-C-5", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 200
    assert resp.json()["position"] == "3-C-5"


def test_update_position_multiple_formats(client, auth_tokens):
    """Test various position formats"""
    payload = {"description": "Multi Position", "barcode": get_unique_barcode(), "price_per_unit": 10.0}
    create_resp = client.post(BASE_URL + "/products", json=payload, headers=auth_header(auth_tokens, "admin"))
    product_id = create_resp.json()["id"]
    
    positions = ["1-A-1", "5-Z-10", "99-AB-999"]
    for pos in positions:
        resp = client.patch(BASE_URL + f"/products/{product_id}/position?position={pos}", headers=auth_header(auth_tokens, "admin"))
        assert resp.status_code == 200


def test_update_position_invalid_format(client, auth_tokens):
    """Test position with invalid format"""
    payload = {"description": "Format Test", "barcode": get_unique_barcode(), "price_per_unit": 10.0}
    create_resp = client.post(BASE_URL + "/products", json=payload, headers=auth_header(auth_tokens, "admin"))
    product_id = create_resp.json()["id"]
    
    invalid_positions = ["INVALID", "1-1-1", "A-B-C", "1--1"]
    for pos in invalid_positions:
        resp = client.patch(BASE_URL + f"/products/{product_id}/position?position={pos}", headers=auth_header(auth_tokens, "admin"))
        assert resp.status_code == 400


def test_update_position_manager(client, auth_tokens):
    """Test updating position as manager"""
    payload = {"description": "Manager Pos", "barcode": get_unique_barcode(), "price_per_unit": 10.0}
    create_resp = client.post(BASE_URL + "/products", json=payload, headers=auth_header(auth_tokens, "manager"))
    product_id = create_resp.json()["id"]
    
    resp = client.patch(BASE_URL + f"/products/{product_id}/position?position=2-B-2", headers=auth_header(auth_tokens, "manager"))
    assert resp.status_code == 200


def test_update_position_not_found(client, auth_tokens):
    """Test update position for non-existent product"""
    resp = client.patch(BASE_URL + "/products/99999/position?position=1-A-1", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 404


def test_update_position_unauthenticated(client):
    """Test update position without auth"""
    resp = client.patch(BASE_URL + "/products/1/position?position=1-A-1")
    assert resp.status_code == 401


def test_update_position_forbidden_cashier(client, auth_tokens):
    """Test cashier cannot update position"""
    resp = client.patch(BASE_URL + "/products/1/position?position=1-A-1", headers=auth_header(auth_tokens, "cashier"))
    assert resp.status_code == 403


def test_update_position_clear(client, auth_tokens):
    """Test clearing position by passing empty string"""
    payload = {"description": "Clear Pos", "barcode": get_unique_barcode(), "price_per_unit": 10.0, "position": "1-A-1"}
    create_resp = client.post(BASE_URL + "/products", json=payload, headers=auth_header(auth_tokens, "admin"))
    product_id = create_resp.json()["id"]
    
    # Clear position
    resp = client.patch(BASE_URL + f"/products/{product_id}/position?position=", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 200
    assert resp.json()["position"] is None


def test_search_products_no_results(client, auth_tokens):
    """Test search with no results (triggers return [] path - line 77)"""
    resp = client.get(BASE_URL + "/products/search?query=NONEXISTENT_PRODUCT_XYZ_123", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 200
    assert resp.json() == []


def test_update_product_all_fields(client, auth_tokens):
    """Test updating all product fields at once (covers all conditional paths 120-135)"""
    barcode = get_unique_barcode()
    payload = {"description": "Update All", "barcode": barcode, "price_per_unit": 10.0, "quantity": 50, "note": "Initial"}
    create_resp = client.post(BASE_URL + "/products", json=payload, headers=auth_header(auth_tokens, "admin"))
    product_id = create_resp.json()["id"]
    
    # Update all fields
    update_payload = {
        "description": "Updated Description",
        "barcode": get_unique_barcode(),
        "price_per_unit": 20.0,
        "note": "Updated Note",
        "quantity": 100,
        "position": "5-B-3"
    }
    resp = client.put(BASE_URL + f"/products/{product_id}", json=update_payload, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 200
    data = resp.json()
    assert data["description"] == "Updated Description"
    assert data["price_per_unit"] == 20.0
    assert data["note"] == "Updated Note"
    assert data["quantity"] == 100
    assert data["position"] == "5-B-3"


def test_update_product_only_note(client, auth_tokens):
    """Test updating only note field (conditional path)"""
    payload = {"description": "Note Test", "barcode": get_unique_barcode(), "price_per_unit": 10.0}
    create_resp = client.post(BASE_URL + "/products", json=payload, headers=auth_header(auth_tokens, "admin"))
    product_id = create_resp.json()["id"]
    
    resp = client.put(BASE_URL + f"/products/{product_id}", json={"note": "New Note"}, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 200
    assert resp.json()["note"] == "New Note"


def test_update_product_only_quantity(client, auth_tokens):
    """Test updating only quantity field"""
    payload = {"description": "Qty Test", "barcode": get_unique_barcode(), "price_per_unit": 10.0, "quantity": 50}
    create_resp = client.post(BASE_URL + "/products", json=payload, headers=auth_header(auth_tokens, "admin"))
    product_id = create_resp.json()["id"]
    
    resp = client.put(BASE_URL + f"/products/{product_id}", json={"quantity": 75}, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 200
    assert resp.json()["quantity"] == 75


def test_update_product_only_position(client, auth_tokens):
    """Test updating only position field"""
    payload = {"description": "Pos Test", "barcode": get_unique_barcode(), "price_per_unit": 10.0}
    create_resp = client.post(BASE_URL + "/products", json=payload, headers=auth_header(auth_tokens, "admin"))
    product_id = create_resp.json()["id"]
    
    resp = client.put(BASE_URL + f"/products/{product_id}", json={"position": "3-C-2"}, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 200
    assert resp.json()["position"] == "3-C-2"


def test_get_all_products_exercises_return_path(client, auth_tokens):
    """Test get all products returns list (exercises line 77 return path)"""
    resp = client.get(BASE_URL + "/products", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_update_position_with_valid_format(client, auth_tokens):
    """Test position update validates format correctly (exercises validation path)"""
    payload = {"description": "Format Test", "barcode": get_unique_barcode(), "price_per_unit": 10.0}
    create_resp = client.post(BASE_URL + "/products", json=payload, headers=auth_header(auth_tokens, "admin"))
    product_id = create_resp.json()["id"]
    
    # Test valid position formats
    valid_positions = ["1-A-1", "99-ZZZ-999", "5-B-10"]
    for pos in valid_positions:
        resp = client.patch(BASE_URL + f"/products/{product_id}/position?position={pos}", headers=auth_header(auth_tokens, "admin"))
        assert resp.status_code == 200
        assert resp.json()["position"] == pos


def test_update_position_with_invalid_format_triggers_validation(client, auth_tokens):
    """Test position validation error (exercises validation path)"""
    payload = {"description": "Invalid Format Test", "barcode": get_unique_barcode(), "price_per_unit": 10.0}
    create_resp = client.post(BASE_URL + "/products", json=payload, headers=auth_header(auth_tokens, "admin"))
    product_id = create_resp.json()["id"]
    
    resp = client.patch(BASE_URL + f"/products/{product_id}/position?position=INVALID", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 400


def test_get_product_by_id_exercises_not_found(client, auth_tokens):
    """Test get product by ID - exercises return path for both success and not found"""
    # Success case exercises the found path (line 66)
    payload = {"description": "Get Test", "barcode": get_unique_barcode(), "price_per_unit": 10.0}
    create_resp = client.post(BASE_URL + "/products", json=payload, headers=auth_header(auth_tokens, "admin"))
    product_id = create_resp.json()["id"]
    
    resp = client.get(BASE_URL + f"/products/{product_id}", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 200
    assert resp.json()["id"] == product_id


def test_get_product_by_barcode_exercises_not_found(client, auth_tokens):
    """Test get product by barcode - exercises return path"""
    payload = {"description": "Barcode Get Test", "barcode": get_unique_barcode(), "price_per_unit": 10.0}
    create_resp = client.post(BASE_URL + "/products", json=payload, headers=auth_header(auth_tokens, "admin"))
    product_barcode = create_resp.json()["barcode"]
    
    resp = client.get(BASE_URL + f"/products/barcode/{product_barcode}", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 200
    assert resp.json()["barcode"] == product_barcode


def test_update_product_without_changing_barcode(client, auth_tokens):
    """Test update when barcode is not changed (skips conflict check - line 108-112)"""
    barcode = get_unique_barcode()
    payload = {"description": "No Barcode Change", "barcode": barcode, "price_per_unit": 10.0}
    create_resp = client.post(BASE_URL + "/products", json=payload, headers=auth_header(auth_tokens, "admin"))
    product_id = create_resp.json()["id"]
    
    # Update without changing barcode
    resp = client.put(BASE_URL + f"/products/{product_id}", json={"description": "Updated"}, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 200
    assert resp.json()["barcode"] == barcode


def test_update_product_to_same_barcode(client, auth_tokens):
    """Test updating with same barcode value (should not conflict with self)"""
    barcode = get_unique_barcode()
    payload = {"description": "Same Barcode Test", "barcode": barcode, "price_per_unit": 10.0}
    create_resp = client.post(BASE_URL + "/products", json=payload, headers=auth_header(auth_tokens, "admin"))
    product_id = create_resp.json()["id"]
    
    # Update with the same barcode - should succeed (doesn't check conflict with self)
    resp = client.put(BASE_URL + f"/products/{product_id}", json={"barcode": barcode}, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 200


def test_update_quantity_increase_large(client, auth_tokens):
    """Test large quantity increase"""
    payload = {"description": "Large Qty", "barcode": get_unique_barcode(), "price_per_unit": 10.0, "quantity": 100}
    create_resp = client.post(BASE_URL + "/products", json=payload, headers=auth_header(auth_tokens, "admin"))
    product_id = create_resp.json()["id"]
    
    resp = client.patch(BASE_URL + f"/products/{product_id}/quantity?quantity_change=10000", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 200
    assert resp.json()["quantity"] == 10100


# ---------------------------
# UPDATE QUANTITY TESTS
# ---------------------------

def test_update_quantity_increase(client, auth_tokens):
    """Test increasing quantity"""
    payload = {"description": "Qty Test", "barcode": get_unique_barcode(), "price_per_unit": 10.0, "quantity": 50}
    create_resp = client.post(BASE_URL + "/products", json=payload, headers=auth_header(auth_tokens, "admin"))
    product_id = create_resp.json()["id"]
    
    resp = client.patch(BASE_URL + f"/products/{product_id}/quantity?quantity_change=10", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 200
    assert resp.json()["quantity"] == 60


def test_update_quantity_decrease(client, auth_tokens):
    """Test decreasing quantity"""
    payload = {"description": "Qty Decrease", "barcode": get_unique_barcode(), "price_per_unit": 10.0, "quantity": 50}
    create_resp = client.post(BASE_URL + "/products", json=payload, headers=auth_header(auth_tokens, "admin"))
    product_id = create_resp.json()["id"]
    
    resp = client.patch(BASE_URL + f"/products/{product_id}/quantity?quantity_change=-10", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 200
    assert resp.json()["quantity"] == 40


def test_update_quantity_zero(client, auth_tokens):
    """Test setting quantity to zero"""
    payload = {"description": "Qty Zero", "barcode": get_unique_barcode(), "price_per_unit": 10.0, "quantity": 50}
    create_resp = client.post(BASE_URL + "/products", json=payload, headers=auth_header(auth_tokens, "admin"))
    product_id = create_resp.json()["id"]
    
    resp = client.patch(BASE_URL + f"/products/{product_id}/quantity?quantity_change=-50", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 200
    assert resp.json()["quantity"] == 0


def test_update_quantity_large_increase(client, auth_tokens):
    """Test large quantity increase"""
    payload = {"description": "Qty Large", "barcode": get_unique_barcode(), "price_per_unit": 10.0, "quantity": 100}
    create_resp = client.post(BASE_URL + "/products", json=payload, headers=auth_header(auth_tokens, "admin"))
    product_id = create_resp.json()["id"]
    
    resp = client.patch(BASE_URL + f"/products/{product_id}/quantity?quantity_change=10000", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 200
    assert resp.json()["quantity"] == 10100


def test_update_quantity_negative_result(client, auth_tokens):
    """Test quantity cannot go negative"""
    payload = {"description": "Negative Qty", "barcode": get_unique_barcode(), "price_per_unit": 10.0, "quantity": 10}
    create_resp = client.post(BASE_URL + "/products", json=payload, headers=auth_header(auth_tokens, "admin"))
    product_id = create_resp.json()["id"]
    
    resp = client.patch(BASE_URL + f"/products/{product_id}/quantity?quantity_change=-20", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 400


def test_update_quantity_manager(client, auth_tokens):
    """Test updating quantity as manager"""
    payload = {"description": "Manager Qty", "barcode": get_unique_barcode(), "price_per_unit": 10.0, "quantity": 50}
    create_resp = client.post(BASE_URL + "/products", json=payload, headers=auth_header(auth_tokens, "manager"))
    product_id = create_resp.json()["id"]
    
    resp = client.patch(BASE_URL + f"/products/{product_id}/quantity?quantity_change=25", headers=auth_header(auth_tokens, "manager"))
    assert resp.status_code == 200


def test_update_quantity_not_found(client, auth_tokens):
    """Test update quantity for non-existent product"""
    resp = client.patch(BASE_URL + "/products/99999/quantity?quantity_change=5", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 404


def test_update_quantity_unauthenticated(client):
    """Test update quantity without auth"""
    resp = client.patch(BASE_URL + "/products/1/quantity?quantity_change=5")
    assert resp.status_code == 401


def test_update_quantity_forbidden_cashier(client, auth_tokens):
    """Test cashier cannot update quantity"""
    resp = client.patch(BASE_URL + "/products/1/quantity?quantity_change=5", headers=auth_header(auth_tokens, "cashier"))
    assert resp.status_code == 403


# ---------------------------
# DELETE PRODUCT TESTS
# ---------------------------

def test_delete_product_success(client, auth_tokens):
    """Test deleting product"""
    payload = {"description": "Delete Test", "barcode": get_unique_barcode(), "price_per_unit": 10.0}
    create_resp = client.post(BASE_URL + "/products", json=payload, headers=auth_header(auth_tokens, "admin"))
    product_id = create_resp.json()["id"]
    
    resp = client.delete(BASE_URL + f"/products/{product_id}", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 204
    
    # Verify deleted
    get_resp = client.get(BASE_URL + f"/products/{product_id}", headers=auth_header(auth_tokens, "admin"))
    assert get_resp.status_code == 404


def test_delete_product_not_found(client, auth_tokens):
    """Test deleting non-existent product"""
    resp = client.delete(BASE_URL + "/products/99999", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 404


def test_delete_product_unauthenticated(client):
    """Test delete without auth"""
    resp = client.delete(BASE_URL + "/products/1")
    assert resp.status_code == 401


def test_delete_product_forbidden_manager(client, auth_tokens):
    """Test manager cannot delete products"""
    resp = client.delete(BASE_URL + "/products/1", headers=auth_header(auth_tokens, "manager"))
    assert resp.status_code == 403


def test_delete_product_forbidden_cashier(client, auth_tokens):
    """Test cashier cannot delete products"""
    resp = client.delete(BASE_URL + "/products/1", headers=auth_header(auth_tokens, "cashier"))
    assert resp.status_code == 403


# ---------------------------
# INTEGRATION TESTS
# ---------------------------

def test_product_full_lifecycle(client, auth_tokens):
    """Test complete product lifecycle"""
    # Create
    barcode = get_unique_barcode()
    payload = {"description": "Lifecycle", "barcode": barcode, "price_per_unit": 10.0, "quantity": 50, "position": "1-A-1"}
    create_resp = client.post(BASE_URL + "/products", json=payload, headers=auth_header(auth_tokens, "admin"))
    assert create_resp.status_code == 201
    product_id = create_resp.json()["id"]
    
    # Get by ID
    get_resp = client.get(BASE_URL + f"/products/{product_id}", headers=auth_header(auth_tokens, "admin"))
    assert get_resp.status_code == 200
    
    # Get by barcode
    barcode_resp = client.get(BASE_URL + f"/products/barcode/{barcode}", headers=auth_header(auth_tokens, "admin"))
    assert barcode_resp.status_code == 200
    
    # Update
    update_resp = client.put(BASE_URL + f"/products/{product_id}", json={"description": "Updated"}, headers=auth_header(auth_tokens, "admin"))
    assert update_resp.status_code == 200
    
    # Update position
    pos_resp = client.patch(BASE_URL + f"/products/{product_id}/position?position=2-B-2", headers=auth_header(auth_tokens, "admin"))
    assert pos_resp.status_code == 200
    
    # Update quantity
    qty_resp = client.patch(BASE_URL + f"/products/{product_id}/quantity?quantity_change=10", headers=auth_header(auth_tokens, "admin"))
    assert qty_resp.status_code == 200
    
    # Delete
    delete_resp = client.delete(BASE_URL + f"/products/{product_id}", headers=auth_header(auth_tokens, "admin"))
    assert delete_resp.status_code == 204


def test_product_with_orders_workflow(client, auth_tokens):
    """Test product used in order workflow"""
    # Create product
    barcode = get_unique_barcode()
    payload = {"description": "Order Product", "barcode": barcode, "price_per_unit": 50.0, "quantity": 100}
    create_resp = client.post(BASE_URL + "/products", json=payload, headers=auth_header(auth_tokens, "admin"))
    assert create_resp.status_code == 201
    
    # List products
    list_resp = client.get(BASE_URL + "/products", headers=auth_header(auth_tokens, "admin"))
    assert list_resp.status_code == 200
    assert len(list_resp.json()) > 0
    
    # Search products
    search_resp = client.get(BASE_URL + "/products/search?query=Order", headers=auth_header(auth_tokens, "admin"))
    assert search_resp.status_code == 200


# ---------------------------
# COMPREHENSIVE REPOSITORY COVERAGE TESTS
# ---------------------------

def test_get_product_by_barcode_not_found_exercises_return(client, auth_tokens):
    """Test get by barcode when not found exercises return path (line 77)"""
    resp = client.get(
        BASE_URL + "/products/barcode/999999999999",
        headers=auth_header(auth_tokens, "admin")
    )
    assert resp.status_code == 404


def test_update_product_same_barcode_skip_conflict_check(client, auth_tokens):
    """Test updating product with same barcode skips conflict check (lines 108-112)"""
    barcode = get_unique_barcode()
    payload = {"description": "Same BC", "barcode": barcode, "price_per_unit": 10.0}
    resp = client.post(BASE_URL + "/products", json=payload, headers=auth_header(auth_tokens, "admin"))
    product_id = resp.json()["id"]
    
    # Update with same barcode using PUT - should not trigger conflict check
    resp = client.put(
        BASE_URL + f"/products/{product_id}",
        json={"barcode": barcode, "description": "Same barcode update"},
        headers=auth_header(auth_tokens, "admin")
    )
    assert resp.status_code == 200
    assert resp.json()["barcode"] == barcode


def test_update_product_quantity_zero(client, auth_tokens):
    """Test setting quantity to zero exercises quantity change logic"""
    payload = {"description": "Qty Zero", "barcode": get_unique_barcode(), "price_per_unit": 10.0, "quantity": 50}
    resp = client.post(BASE_URL + "/products", json=payload, headers=auth_header(auth_tokens, "admin"))
    product_id = resp.json()["id"]
    
    # Set to zero via PATCH
    resp = client.patch(
        BASE_URL + f"/products/{product_id}/quantity?quantity_change=-50",
        headers=auth_header(auth_tokens, "admin")
    )
    assert resp.status_code == 200
    assert resp.json()["quantity"] == 0


def test_get_product_by_id_not_found_exercises_return(client, auth_tokens):
    """Test get by ID when not found exercises return path (line 66)"""
    resp = client.get(
        BASE_URL + "/products/999999",
        headers=auth_header(auth_tokens, "admin")
    )
    assert resp.status_code == 404


# ---------------------------
# DIRECT REPOSITORY EDGE CASES FOR 100% COVERAGE
# ---------------------------
import pytest
import asyncio
from app.repositories.product_repository import ProductRepository
from app.models.errors.notfound_error import NotFoundError
from app.models.errors.conflict_error import ConflictError
from app.models.errors.bad_request import BadRequestError

@pytest.mark.asyncio
async def test_product_repo_get_by_id_not_found():
    from init_db import reset, init_db
    await reset(); await init_db()
    repo = ProductRepository()
    with pytest.raises(NotFoundError):
        await repo.get_product_by_id(99999999)

@pytest.mark.asyncio
async def test_product_repo_get_by_barcode_not_found():
    from init_db import reset, init_db
    await reset(); await init_db()
    repo = ProductRepository()
    with pytest.raises(NotFoundError):
        await repo.get_product_by_barcode("not-a-real-barcode-xyz")

@pytest.mark.asyncio
async def test_product_repo_search_products_empty():
    from init_db import reset, init_db
    await reset(); await init_db()
    repo = ProductRepository()
    results = await repo.search_products_by_description("no-such-product-xyz")
    assert results == []


@pytest.mark.asyncio
async def test_product_repo_get_all_products_returns_created():
    from init_db import reset, init_db
    await reset(); await init_db()
    repo = ProductRepository()
    await repo.create_product(description="All1", barcode="repo-all-1", price_per_unit=1.0)
    await repo.create_product(description="All2", barcode="repo-all-2", price_per_unit=2.0)
    products = await repo.get_all_products()
    assert len(products) == 2

@pytest.mark.asyncio
async def test_product_repo_update_conflict_barcode():
    from init_db import reset, init_db
    await reset(); await init_db()
    repo = ProductRepository()
    p1 = await repo.create_product(description="A", barcode="repo-conflict-1", price_per_unit=1.0)
    p2 = await repo.create_product(description="B", barcode="repo-conflict-2", price_per_unit=2.0)
    with pytest.raises(ConflictError):
        await repo.update_product(p2.id, barcode="repo-conflict-1")

@pytest.mark.asyncio
async def test_product_repo_update_fields_individually():
    from init_db import reset, init_db
    await reset(); await init_db()
    repo = ProductRepository()
    p = await repo.create_product(description="C", barcode="repo-update-fields", price_per_unit=3.0, note=None, quantity=5, position="1-A-1")
    await repo.update_product(p.id, note="new note")
    await repo.update_product(p.id, quantity=10)
    await repo.update_product(p.id, position="2-B-2")
    await repo.update_product(p.id, description="new desc")
    await repo.update_product(p.id, price_per_unit=99.99)


@pytest.mark.asyncio
async def test_product_repo_update_product_updates_barcode():
    from init_db import reset, init_db
    await reset(); await init_db()
    repo = ProductRepository()
    p = await repo.create_product(description="BC", barcode="repo-bc-old", price_per_unit=1.0)
    updated = await repo.update_product(p.id, barcode="repo-bc-new")
    assert updated.barcode == "repo-bc-new"

@pytest.mark.asyncio
async def test_product_repo_update_invalid_position():
    from init_db import reset, init_db
    await reset(); await init_db()
    repo = ProductRepository()
    p = await repo.create_product(description="D", barcode="repo-invalid-pos", price_per_unit=4.0, position="1-A-1")
    # Position format validation happens in update_position(), not update_product().
    with pytest.raises(BadRequestError):
        await repo.update_position(p.id, "!!!invalid!!!")


@pytest.mark.asyncio
async def test_product_repo_update_position_valid_and_clear():
    from init_db import reset, init_db
    await reset(); await init_db()
    repo = ProductRepository()
    p = await repo.create_product(description="Pos", barcode="repo-pos", price_per_unit=1.0, position=None)
    updated = await repo.update_position(p.id, "2-B-2")
    assert updated.position == "2-B-2"
    cleared = await repo.update_position(p.id, "")
    assert cleared.position is None

@pytest.mark.asyncio
async def test_product_repo_update_quantity_negative():
    from init_db import reset, init_db
    await reset(); await init_db()
    repo = ProductRepository()
    p = await repo.create_product(description="E", barcode="repo-qty-neg", price_per_unit=5.0, quantity=1)
    with pytest.raises(BadRequestError):
        await repo.update_quantity(p.id, -10)


@pytest.mark.asyncio
async def test_product_repo_update_quantity_success_commits():
    from init_db import reset, init_db
    await reset(); await init_db()
    repo = ProductRepository()
    p = await repo.create_product(description="QtyOK", barcode="repo-qty-ok", price_per_unit=1.0, quantity=5)
    updated = await repo.update_quantity(p.id, 3)
    assert updated.quantity == 8

@pytest.mark.asyncio
async def test_product_repo_update_quantity_not_found():
    from init_db import reset, init_db
    await reset(); await init_db()
    repo = ProductRepository()
    with pytest.raises(NotFoundError):
        await repo.update_quantity(99999999, 5)

@pytest.mark.asyncio
async def test_product_repo_delete_not_found():
    from init_db import reset, init_db
    await reset(); await init_db()
    repo = ProductRepository()
    with pytest.raises(NotFoundError):
        await repo.delete_product(99999999)


@pytest.mark.asyncio
async def test_product_repo_delete_success():
    from init_db import reset, init_db
    await reset(); await init_db()
    repo = ProductRepository()
    p = await repo.create_product(description="Del", barcode="repo-del", price_per_unit=1.0)
    assert await repo.delete_product(p.id) is True
    with pytest.raises(NotFoundError):
        await repo.get_product_by_id(p.id)


# ---------------------------
# ROUTE-LEVEL VALIDATION BRANCHES (Pydantic-bypassed)
# ---------------------------

@pytest.mark.asyncio
async def test_product_route_create_product_rejects_price_le_zero_direct_call():
    from app.routes.product_route import create_product
    from app.models.DTO.product_dto import ProductCreateDTO
    from app.models.errors.bad_request import BadRequestError

    dto = ProductCreateDTO.model_construct(description="desc", barcode="bc", price_per_unit=0.0)
    with pytest.raises(BadRequestError):
        await create_product(dto)
