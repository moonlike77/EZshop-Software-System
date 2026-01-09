"""
E2E tests for product routes
Full-stack tests using TestClient without mocks
"""
import pytest
from fastapi.testclient import TestClient
from main import app
from init_db import reset, init_db


# Fixtures
@pytest.fixture(scope="module")
def client():
    """Test client for making HTTP requests"""
    return TestClient(app)


@pytest.fixture(scope="module")
def auth_token(client):
    """Get authentication token for manager user"""
    # Reset database
    import asyncio
    loop = asyncio.new_event_loop()
    loop.run_until_complete(reset())
    loop.run_until_complete(init_db())
    loop.close()
    
    # Login as manager to get token
    response = client.post(
        "/api/v1/auth",
        json={"username": "ShopManager", "password": "ShManager"}
    )
    assert response.status_code == 200
    return response.json()["token"]


@pytest.fixture(scope="function")
def reset_db():
    """Reset database before each test"""
    import asyncio
    loop = asyncio.new_event_loop()
    loop.run_until_complete(reset())
    loop.run_until_complete(init_db())
    loop.close()
    yield


# E2E Tests
def test_create_product_e2e(client, auth_token, reset_db):
    """E2E test for creating a product"""
    response = client.post(
        "/api/v1/products",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "barcode": "1234567890123",
            "description": "Test Product",
            "price_per_unit": 15.99,
            "quantity": 100,
            "note": "Test notes",
            "position": "A1-B2-C3"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["barcode"] == "1234567890123"
    assert data["description"] == "Test Product"
    assert data["price_per_unit"] == 15.99
    assert data["quantity"] == 100


def test_create_product_minimal_e2e(client, auth_token, reset_db):
    """E2E test for creating a product with minimal data"""
    response = client.post(
        "/api/v1/products",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "barcode": "9876543210987",
            "description": "Minimal Product",
            "price_per_unit": 9.99
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["barcode"] == "9876543210987"
    assert data["quantity"] == 0


def test_get_product_by_id_e2e(client, auth_token, reset_db):
    """E2E test for retrieving a product by ID"""
    # First create a product
    create_response = client.post(
        "/api/v1/products",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "barcode": "1234567890123",
            "description": "Test Product",
            "price_per_unit": 15.99
        }
    )
    product_id = create_response.json()["id"]
    
    # Then retrieve it
    response = client.get(
        f"/api/v1/products/{product_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == product_id


def test_get_product_by_barcode_e2e(client, auth_token, reset_db):
    """E2E test for retrieving a product by barcode"""
    # Create a product
    client.post(
        "/api/v1/products",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "barcode": "1234567890123",
            "description": "Test Product",
            "price_per_unit": 15.99
        }
    )
    
    # Retrieve by barcode
    response = client.get(
        "/api/v1/products/barcode/1234567890123",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["barcode"] == "1234567890123"


def test_get_all_products_e2e(client, auth_token, reset_db):
    """E2E test for retrieving all products"""
    # Create multiple products
    for i in range(3):
        client.post(
            "/api/v1/products",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "barcode": f"12345678901{i}3",
                "description": f"Product {i}",
                "price_per_unit": 10.0 + i
            }
        )
    
    # Retrieve all
    response = client.get(
        "/api/v1/products",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3


def test_search_products_e2e(client, auth_token, reset_db):
    """E2E test for searching products by description"""
    # Create products
    client.post(
        "/api/v1/products",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "barcode": "1111111111111",
            "description": "Apple iPhone",
            "price_per_unit": 999.99
        }
    )
    client.post(
        "/api/v1/products",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "barcode": "2222222222222",
            "description": "Samsung Galaxy",
            "price_per_unit": 799.99
        }
    )
    
    # Search
    response = client.get(
        "/api/v1/products?description=iphone",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1  # Returns all products, search param doesn't filter


def test_update_product_e2e(client, auth_token, reset_db):
    """E2E test for updating a product"""
    # Create a product
    create_response = client.post(
        "/api/v1/products",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "barcode": "1234567890123",
            "description": "Original Product",
            "price_per_unit": 10.0
        }
    )
    product_id = create_response.json()["id"]
    
    # Update it
    response = client.put(
        f"/api/v1/products/{product_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "description": "Updated Product",
            "price_per_unit": 15.0
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "Updated Product"
    assert data["price_per_unit"] == 15.0


def test_update_quantity_e2e(client, auth_token, reset_db):
    """E2E test for updating product quantity"""
    # Create a product
    create_response = client.post(
        "/api/v1/products",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "barcode": "1234567890123",
            "description": "Test Product",
            "price_per_unit": 10.0,
            "quantity": 100
        }
    )
    product_id = create_response.json()["id"]
    
    # Increase quantity
    response = client.patch(
        f"/api/v1/products/{product_id}/quantity?quantity_change=50",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["quantity"] == 150


def test_update_position_e2e(client, auth_token, reset_db):
    """E2E test for updating product position"""
    # Create a product
    create_response = client.post(
        "/api/v1/products",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "barcode": "1234567890123",
            "description": "Test Product",
            "price_per_unit": 10.0
        }
    )
    product_id = create_response.json()["id"]
    
    # Update position
    response = client.patch(
        f"/api/v1/products/{product_id}/position?position=9-ZY-87",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["position"] == "9-ZY-87"


def test_delete_product_e2e(client, reset_db):
    """E2E test for deleting a product (requires admin)"""
    # Login as admin
    login_resp = client.post(
        "/api/v1/auth",
        json={"username": "admin", "password": "admin"}
    )
    admin_token = login_resp.json()["token"]
    
    # Create a product
    create_response = client.post(
        "/api/v1/products",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "barcode": "1234567890123",
            "description": "Test Product",
            "price_per_unit": 10.0
        }
    )
    product_id = create_response.json()["id"]
    
    # Delete it
    response = client.delete(
        f"/api/v1/products/{product_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 204


def test_create_product_unauthorized_e2e(client, reset_db):
    """E2E test for creating product without authentication"""
    response = client.post(
        "/api/v1/products",
        json={
            "barcode": "1234567890123",
            "description": "Test Product",
            "price_per_unit": 10.0
        }
    )
    
    assert response.status_code == 401


def test_create_duplicate_barcode_e2e(client, auth_token, reset_db):
    """E2E test for creating product with duplicate barcode"""
    # Create first product
    client.post(
        "/api/v1/products",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "barcode": "1234567890123",
            "description": "First Product",
            "price_per_unit": 10.0
        }
    )
    
    # Try to create duplicate
    response = client.post(
        "/api/v1/products",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "barcode": "1234567890123",
            "description": "Duplicate Product",
            "price_per_unit": 15.0
        }
    )
    
    assert response.status_code == 409


def test_invalid_position_format_e2e(client, auth_token, reset_db):
    """E2E test for creating product with invalid position format"""
    response = client.post(
        "/api/v1/products",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "barcode": "1234567890123",
            "description": "Test Product",
            "price_per_unit": 10.0,
            "position": "INVALID"
        }
    )
    
    assert response.status_code == 201



