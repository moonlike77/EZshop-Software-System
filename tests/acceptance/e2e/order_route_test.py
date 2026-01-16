"""
E2E tests for order routes
Tests complete order workflows from creation to completion
"""
import pytest
from fastapi.testclient import TestClient
from main import app
from init_db import reset, init_db


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def event_loop():
    import asyncio
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
def auth_token(client, event_loop):
    """Get authentication token for manager user"""
    # Reset database
    event_loop.run_until_complete(reset())
    event_loop.run_until_complete(init_db())

    # Login as manager to get token
    response = client.post(
        "/api/v1/auth",
        json={"username": "ShopManager", "password": "ShManager"}
    )
    assert response.status_code == 200
    return response.json()["token"]


@pytest.fixture(scope="module")
def reset_db(event_loop):
    """Reset database before each test module"""
    event_loop.run_until_complete(reset())
    event_loop.run_until_complete(init_db())
    yield


@pytest.fixture(scope="module")
def test_product(client, auth_token):
    """Create a test product for order tests"""
    response = client.post(
        "/api/v1/products",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "barcode": "1234567890123",
            "description": "Test Product for Orders",
            "price_per_unit": 10.0,
            "quantity": 100,
            "note": "Test product",
            "position": "1-A-3"
        }
    )
    assert response.status_code == 201
    return response.json()


# E2E Tests
def test_create_and_pay_order_e2e(client, auth_token, reset_db, test_product):
    """E2E test for creating and paying for an order"""
    # Set balance first (admin-only endpoint)
    admin_login = client.post(
        "/api/v1/auth",
        json={"username": "admin", "password": "admin"}
    )
    assert admin_login.status_code == 200
    admin_token = admin_login.json()["token"]
    client.post(
        "/api/v1/balance/set?amount=10000.0",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    response = client.post(
        "/api/v1/orders/payfor",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "product_barcode": "1234567890123",
            "quantity": 5,
            "price_per_unit": 9.0
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["product_barcode"] == "1234567890123"
    assert data["quantity"] == 5
    assert data["price_per_unit"] == 9.0


def test_create_and_pay_order_insufficient_balance_e2e(client, auth_token, reset_db, test_product):
    """E2E test for payfor with insufficient balance"""
    # Reset balance to 0 (admin-only endpoint)
    admin_login = client.post(
        "/api/v1/auth",
        json={"username": "admin", "password": "admin"}
    )
    assert admin_login.status_code == 200
    admin_token = admin_login.json()["token"]
    client.post(
        "/api/v1/balance/set?amount=0.0",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    response = client.post(
        "/api/v1/orders/payfor",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "product_barcode": "1234567890123",
            "quantity": 100,
            "price_per_unit": 100.0
        }
    )
    
    assert response.status_code == 421
