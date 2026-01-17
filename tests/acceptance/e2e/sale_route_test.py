import pytest
from fastapi.testclient import TestClient
from main import app
from init_db import reset, init_db


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


@pytest.fixture(scope="module")
def auth_token(client):
    import asyncio
    loop = asyncio.new_event_loop()
    loop.run_until_complete(reset())
    loop.run_until_complete(init_db())
    loop.close()

    resp = client.post(
        "/api/v1/auth",
        json={"username": "Cashier", "password": "Cashier"}
    )
    assert resp.status_code == 200
    return resp.json()["token"]


@pytest.fixture(scope="function")
def reset_db():
    import asyncio
    loop = asyncio.new_event_loop()
    loop.run_until_complete(reset())
    loop.run_until_complete(init_db())
    loop.close()
    yield


@pytest.fixture(scope="module")
def manager_token(client):
    resp = client.post(
        "/api/v1/auth",
        json={"username": "ShopManager", "password": "ShManager"}
    )
    assert resp.status_code == 200
    return resp.json()["token"]


def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _start_sale(client: TestClient, token: str) -> int:
    resp = client.post("/api/v1/sales/", headers=_auth_headers(token))
    assert resp.status_code == 201
    return resp.json()["id"]


def _close_sale(client: TestClient, token: str, sale_id: int) -> None:
    resp = client.patch(f"/api/v1/sales/{sale_id}/close", headers=_auth_headers(token))
    assert resp.status_code == 200


BARCODE = "1234567890123"

def _ensure_product_exists(client: TestClient, manager_token: str) -> None:
    resp = client.post(
        "/api/v1/products",
        headers={"Authorization": f"Bearer {manager_token}"},
        json={
            "barcode": BARCODE,
            "description": "E2E Product",
            "price_per_unit": 10.0,
            "quantity": 100
        }
    )
    assert resp.status_code in (201, 409)


# ----------------------------
# POST /sales
# ----------------------------

def test_start_sale_success(client, auth_token, reset_db):
    resp = client.post("/api/v1/sales/", headers=_auth_headers(auth_token))
    assert resp.status_code == 201
    body = resp.json()
    assert "id" in body
    assert isinstance(body["id"], int)
    assert body["id"] > 0


def test_start_sale_unauthorized(client, reset_db):
    resp = client.post("/api/v1/sales/")
    assert resp.status_code == 401


# ----------------------------
# GET /sales
# ----------------------------


def test_get_all_sales_success(client, auth_token, reset_db):
    sale_id1 = _start_sale(client, auth_token)
    sale_id2 = _start_sale(client, auth_token)

    resp = client.get(
        "/api/v1/sales/",
        headers=_auth_headers(auth_token),
    )
    assert resp.status_code == 200

    body = resp.json()
    assert isinstance(body, list)

    ids = [sale["id"] for sale in body]
    assert sale_id1 in ids
    assert sale_id2 in ids


def test_get_all_sales_empty(client, auth_token, reset_db):
    resp = client.get(
        "/api/v1/sales/",
        headers=_auth_headers(auth_token),
    )
    assert resp.status_code == 200
    assert resp.json() == []


def test_get_all_sales_unauthorized(client, reset_db):
    resp = client.get("/api/v1/sales/")
    assert resp.status_code in (401, 403)


# ----------------------------
# GET /sale/{sale_id}
# ----------------------------


def test_get_sale_success(client, auth_token, reset_db):
    sale_id = _start_sale(client, auth_token)
    resp = client.get(f"/api/v1/sales/{sale_id}", headers=_auth_headers(auth_token))
    assert resp.status_code == 200
    assert resp.json()["id"] == sale_id


def test_get_sale_invalid_id(client, auth_token, reset_db):
    resp = client.get("/api/v1/sales/0", headers=_auth_headers(auth_token))
    assert resp.status_code == 400


# ----------------------------
# DELETE /sales/{sale_id}
# ----------------------------


def test_delete_sale_success(client, auth_token, reset_db):
    sale_id = _start_sale(client, auth_token)
    resp = client.delete(f"/api/v1/sales/{sale_id}", headers=_auth_headers(auth_token))
    assert resp.status_code == 204


def test_delete_sale_invalid_id(client, auth_token, reset_db):
    resp = client.delete("/api/v1/sales/0", headers=_auth_headers(auth_token))
    assert resp.status_code == 400


# ----------------------------
# POST /sales/{sale_id}/items
# ----------------------------


def test_add_product_success(client, auth_token, manager_token, reset_db):
    _ensure_product_exists(client, manager_token)
    sale_id = _start_sale(client, auth_token)

    resp = client.post(
        f"/api/v1/sales/{sale_id}/items",
        headers=_auth_headers(auth_token),
        params={"barcode": BARCODE, "amount": 1},
    )
    assert resp.status_code == 201
    assert resp.json().get("success") is True


def test_add_product_invalid_sale_id(client, auth_token, reset_db):
    resp = client.post(
        "/api/v1/sales/0/items",
        headers=_auth_headers(auth_token),
        params={"barcode": "123", "amount": 1},
    )
    assert resp.status_code == 400


def test_add_product_invalid_amount(client, auth_token, reset_db):
    resp = client.post(
        "/api/v1/sales/1/items",
        headers=_auth_headers(auth_token),
        params={"barcode": "123", "amount": 0},
    )
    assert resp.status_code == 400


# ----------------------------
# DELETE /sales/{sale_id}/items
# ----------------------------


def test_remove_product_success(client, auth_token, manager_token, reset_db):
    _ensure_product_exists(client, manager_token)
    sale_id = _start_sale(client, auth_token)

    add = client.post(
        f"/api/v1/sales/{sale_id}/items",
        headers=_auth_headers(auth_token),
        params={"barcode": BARCODE, "amount": 2},
    )
    assert add.status_code == 201

    rm = client.delete(
        f"/api/v1/sales/{sale_id}/items",
        headers=_auth_headers(auth_token),
        params={"barcode": BARCODE, "amount": 1},
    )
    assert rm.status_code == 202


def test_remove_product_invalid_sale_id(client, auth_token, reset_db):
    resp = client.delete(
        "/api/v1/sales/0/items",
        headers=_auth_headers(auth_token),
        params={"barcode": "123", "amount": 1},
    )
    assert resp.status_code == 400


def test_remove_product_invalid_amount(client, auth_token, reset_db):
    resp = client.delete(
        "/api/v1/sales/1/items",
        headers=_auth_headers(auth_token),
        params={"barcode": "123", "amount": 0},
    )
    assert resp.status_code == 400


# ----------------------------
# PATCH /sales/{sale_id}/discount
# ----------------------------


def test_apply_discount_success(client, auth_token, reset_db):
    sale_id = _start_sale(client, auth_token)

    resp = client.patch(
        f"/api/v1/sales/{sale_id}/discount",
        headers=_auth_headers(auth_token),
        params={"discount_rate": 0.2},
    )
    assert resp.status_code == 200
    assert resp.json().get("success") is True


def test_apply_discount_invalid_rate(client, auth_token, reset_db):
    resp = client.patch(
        "/api/v1/sales/1/discount",
        headers=_auth_headers(auth_token),
        params={"discount_rate": 1.0},
    )
    assert resp.status_code == 400


# ----------------------------
# PATCH /sales/{sale_id}/items/{product_barcode}/discount
# ----------------------------


def test_apply_product_discount_success(client, auth_token, manager_token, reset_db):
    _ensure_product_exists(client, manager_token)
    sale_id = _start_sale(client, auth_token)

    add = client.post(
        f"/api/v1/sales/{sale_id}/items",
        headers=_auth_headers(auth_token),
        params={"barcode": BARCODE, "amount": 1},
    )
    assert add.status_code == 201

    resp = client.patch(
        f"/api/v1/sales/{sale_id}/items/{BARCODE}/discount",
        headers=_auth_headers(auth_token),
        params={"discount_rate": 0.1},
    )
    assert resp.status_code == 200
    assert resp.json().get("success") is True


def test_apply_product_discount_invalid_rate(client, auth_token, reset_db):
    resp = client.patch(
        "/api/v1/sales/1/items/123/discount",
        headers=_auth_headers(auth_token),
        params={"discount_rate": -0.1},
    )
    assert resp.status_code == 400


def test_apply_product_discount_invalid_sale_id(client, auth_token, reset_db):
    resp = client.patch(
        "/api/v1/sales/0/items/123/discount",
        headers=_auth_headers(auth_token),
        params={"discount_rate": 0.1},
    )
    assert resp.status_code == 400


# ----------------------------
# PATCH /sales/{sale_id}/close
# ----------------------------

def test_close_sale_success(client, auth_token, reset_db):
    sale_id = _start_sale(client, auth_token)

    resp = client.patch(
        f"/api/v1/sales/{sale_id}/close",
        headers=_auth_headers(auth_token),
    )
    assert resp.status_code == 200
    assert resp.json().get("success") is True


def test_close_sale_invalid_id(client, auth_token, reset_db):
    resp = client.patch(
        "/api/v1/sales/0/close",
        headers=_auth_headers(auth_token),
    )
    assert resp.status_code == 400


def test_close_sale_unauthorized(client, reset_db):
    resp = client.patch("/api/v1/sales/1/close")
    assert resp.status_code == 401


# ----------------------------
# PATCH /sales/{sale_id}/pay
# ----------------------------


def test_pay_sale_success(client, auth_token, manager_token, reset_db):
    _ensure_product_exists(client, manager_token)
    sale_id = _start_sale(client, auth_token)

    add = client.post(
        f"/api/v1/sales/{sale_id}/items",
        headers=_auth_headers(auth_token),
        params={"barcode": BARCODE, "amount": 1},
    )
    assert add.status_code == 201

    _close_sale(client, auth_token, sale_id)

    resp = client.patch(
        f"/api/v1/sales/{sale_id}/pay",
        headers=_auth_headers(auth_token),
        params={"cash_amount": 100.0},
    )
    assert resp.status_code == 200
    assert resp.json().get("success") is True
    assert "change" in resp.json()


def test_pay_sale_invalid_cash(client, auth_token, reset_db):
    resp = client.patch(
        "/api/v1/sales/1/pay",
        headers=_auth_headers(auth_token),
        params={"cash_amount": 0.0},
    )
    assert resp.status_code == 400


# ----------------------------
# GET /sales/{sale_id}/points
# ----------------------------


def test_get_sale_points_success(client, auth_token, manager_token, reset_db):
    _ensure_product_exists(client, manager_token)
    sale_id = _start_sale(client, auth_token)

    add = client.post(
        f"/api/v1/sales/{sale_id}/items",
        headers=_auth_headers(auth_token),
        params={"barcode": BARCODE, "amount": 1},
    )
    assert add.status_code == 201

    _close_sale(client, auth_token, sale_id)

    pay = client.patch(
        f"/api/v1/sales/{sale_id}/pay",
        headers=_auth_headers(auth_token),
        params={"cash_amount": 100.0},
    )
    assert pay.status_code == 200

    resp = client.get(
        f"/api/v1/sales/{sale_id}/points",
        headers=_auth_headers(auth_token),
    )
    assert resp.status_code == 200
    assert "points" in resp.json()


def test_get_sale_points_invalid_id(client, auth_token, reset_db):
    resp = client.get("/api/v1/sales/0/points", headers=_auth_headers(auth_token))
    assert resp.status_code == 400