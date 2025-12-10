import pytest
from fastapi.testclient import TestClient
from main import app
from init_db import reset, init_db

client = TestClient(app)
BASE_URL = "http://127.0.0.1:8000/api/v1"
SALES_URL = BASE_URL + "/sales"
PRODUCTS_URL = BASE_URL + "/products"

# Example of a product barcode
PRODUCT_BARCODE = "ABC123"


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
# CREATE AN OPEN SALE WITH AT LEAST ONE LINE
# ---------------------------------------------------------------------

def create_open_sale_with_item(tokens, role="admin", amount: int = 1) -> int:
    # Create a sale
    sale_resp = client.post(SALES_URL + "/", headers=auth_header(tokens, role))
    assert sale_resp.status_code == 201
    sale_id = sale_resp.json()["id"]

    # Add at least one product
    add_resp = client.post(
        f"{SALES_URL}/{sale_id}/items",
        headers=auth_header(tokens, role),
        params={"barcode": PRODUCT_BARCODE, "amount": amount},
    )
    assert add_resp.status_code == 201

    return sale_id


# ---------------------------------------------------------------------
# POST /sales/  (start sale)
# ---------------------------------------------------------------------

def test_start_sale_success_as_admin(auth_tokens):
    resp = client.post(SALES_URL + "/", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 201
    body = resp.json()
    assert "id" in body
    assert body["status"] == "OPEN"


def test_start_sale_success_as_cashier(auth_tokens):
    resp = client.post(SALES_URL + "/", headers=auth_header(auth_tokens, "cashier"))
    assert resp.status_code == 201


def test_start_sale_unauthenticated():
    resp = client.post(SALES_URL + "/")
    assert resp.status_code == 401


# ---------------------------------------------------------------------
# GET /sales/  (list)
# ---------------------------------------------------------------------

def test_list_sales_success_as_admin(auth_tokens):
    resp = client.get(SALES_URL + "/", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_list_sales_unauthenticated():
    resp = client.get(SALES_URL + "/")
    assert resp.status_code == 401


# ---------------------------------------------------------------------
# GET /sales/{sale_id}
# ---------------------------------------------------------------------

def test_get_sale_success(auth_tokens):
    # Create a sale
    create_resp = client.post(SALES_URL + "/", headers=auth_header(auth_tokens, "admin"))
    sale_id = create_resp.json()["id"]

    resp = client.get(f"{SALES_URL}/{sale_id}", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == sale_id


def test_get_sale_not_found(auth_tokens):
    resp = client.get(f"{SALES_URL}/99999", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 404


def test_get_sale_bad_id(auth_tokens):
    resp = client.get(f"{SALES_URL}/0", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 400


def test_get_sale_unauthenticated():
    resp = client.get(f"{SALES_URL}/1")
    assert resp.status_code == 401


# ---------------------------------------------------------------------
# DELETE /sales/{sale_id}
# ---------------------------------------------------------------------

def test_delete_sale_success(auth_tokens):
    # Create a sale and then delete it
    create_resp = client.post(SALES_URL + "/", headers=auth_header(auth_tokens, "admin"))
    sale_id = create_resp.json()["id"]

    resp = client.delete(f"{SALES_URL}/{sale_id}", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 200
    assert resp.json()["success"] is True


def test_delete_sale_bad_id(auth_tokens):
    resp = client.delete(f"{SALES_URL}/0", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 400


def test_delete_sale_not_found(auth_tokens):
    resp = client.delete(f"{SALES_URL}/99999", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code in (400, 404)


def test_delete_sale_unauthenticated():
    resp = client.delete(f"{SALES_URL}/1")
    assert resp.status_code == 401


def test_delete_paid_sale_cannot_be_deleted(auth_tokens):
    # Create a sale with an item, close it and pay it -> PAID
    sale_id = create_open_sale_with_item(auth_tokens)

    close_resp = client.patch(
        f"{SALES_URL}/{sale_id}/close",
        headers=auth_header(auth_tokens, "admin"),
    )
    assert close_resp.status_code == 200

    pay_resp = client.patch(
        f"{SALES_URL}/{sale_id}/pay",
        headers=auth_header(auth_tokens, "admin"),
        params={"cash_amount": 100.0},
    )
    assert pay_resp.status_code == 200

    # the DELETE must fail (sale not deletable)
    delete_resp = client.delete(
        f"{SALES_URL}/{sale_id}",
        headers=auth_header(auth_tokens, "admin"),
    )
    assert delete_resp.status_code == 409 



# ---------------------------------------------------------------------
# POST /sales/{sale_id}/items  (add product to sale)
# ---------------------------------------------------------------------

def test_add_item_to_sale_success(auth_tokens):
    sale_id = create_open_sale_with_item(auth_tokens, amount=1)

    get_resp = client.get(
        f"{SALES_URL}/{sale_id}",
        headers=auth_header(auth_tokens, "admin"),
    )
    assert get_resp.status_code == 200
    body = get_resp.json()
    assert body["id"] == sale_id
    assert body["status"] in ("OPEN", "PENDING", "PAID")



def test_add_item_invalid_amount(auth_tokens):
    create_resp = client.post(SALES_URL + "/", headers=auth_header(auth_tokens, "admin"))
    sale_id = create_resp.json()["id"]

    resp = client.post(
        f"{SALES_URL}/{sale_id}/items",
        headers=auth_header(auth_tokens, "admin"),
        params={"barcode": PRODUCT_BARCODE, "amount": 0},
    )
    assert resp.status_code == 400


def test_add_item_unauthenticated():
    resp = client.post(
        f"{SALES_URL}/1/items",
        params={"barcode": PRODUCT_BARCODE, "amount": 1},
    )
    assert resp.status_code == 401


def test_add_item_sale_not_found(auth_tokens):
    resp = client.post(
        f"{SALES_URL}/99999/items",
        headers=auth_header(auth_tokens, "admin"),
        params={"barcode": PRODUCT_BARCODE, "amount": 1},
    )
    assert resp.status_code == 404


def test_add_item_invalid_status(auth_tokens):
    sale_id = create_open_sale_with_item(auth_tokens)

    close_resp = client.patch(
        f"{SALES_URL}/{sale_id}/close",
        headers=auth_header(auth_tokens, "admin"),
    )
    assert close_resp.status_code == 200

    resp = client.post(
        f"{SALES_URL}/{sale_id}/items",
        headers=auth_header(auth_tokens, "admin"),
        params={"barcode": PRODUCT_BARCODE, "amount": 1},
    )
    assert resp.status_code == 420


# ---------------------------------------------------------------------
# DELETE /sales/{sale_id}/items  (remove product from sale)
# ---------------------------------------------------------------------

def test_remove_item_from_sale_success(auth_tokens):
    sale_id = create_open_sale_with_item(auth_tokens, amount=2)

    resp = client.delete(
        f"{SALES_URL}/{sale_id}/items",
        headers=auth_header(auth_tokens, "admin"),
        params={"barcode": PRODUCT_BARCODE, "amount": 1},
    )
    assert resp.status_code == 200
    assert resp.json()["success"] is True


def test_remove_item_not_in_sale(auth_tokens):
    sale_id = create_open_sale_with_item(auth_tokens, amount=1)

    resp = client.delete(
        f"{SALES_URL}/{sale_id}/items",
        headers=auth_header(auth_tokens, "admin"),
        params={"barcode": "NONEXISTENT", "amount": 1},
    )
    assert resp.status_code in (404, 400)


def test_remove_item_invalid_amount(auth_tokens):
    sale_id = create_open_sale_with_item(auth_tokens, amount=1)

    resp = client.delete(
        f"{SALES_URL}/{sale_id}/items",
        headers=auth_header(auth_tokens, "admin"),
        params={"barcode": PRODUCT_BARCODE, "amount": 0},
    )
    assert resp.status_code == 400


def test_remove_item_unauthenticated():
    resp = client.delete(
        f"{SALES_URL}/1/items",
        params={"barcode": PRODUCT_BARCODE, "amount": 1},
    )
    assert resp.status_code == 401


def test_remove_item_sale_not_found(auth_tokens):
    resp = client.delete(
        f"{SALES_URL}/99999/items",
        headers=auth_header(auth_tokens, "admin"),
        params={"barcode": PRODUCT_BARCODE, "amount": 1},
    )
    assert resp.status_code == 404


def test_remove_item_invalid_status(auth_tokens):
    sale_id = create_open_sale_with_item(auth_tokens, amount=1)

    close_resp = client.patch(
        f"{SALES_URL}/{sale_id}/close",
        headers=auth_header(auth_tokens, "admin"),
    )
    assert close_resp.status_code == 200

    resp = client.delete(
        f"{SALES_URL}/{sale_id}/items",
        headers=auth_header(auth_tokens, "admin"),
        params={"barcode": PRODUCT_BARCODE, "amount": 1},
    )
    assert resp.status_code == 420


# ---------------------------------------------------------------------
# PATCH /sales/{sale_id}/discount  (discount on whole sale)
# ---------------------------------------------------------------------

def test_apply_discount_to_sale_success(auth_tokens):
    sale_id = create_open_sale_with_item(auth_tokens)

    resp = client.patch(
        f"{SALES_URL}/{sale_id}/discount",
        headers=auth_header(auth_tokens, "admin"),
        params={"discount_rate": 0.1},
    )
    assert resp.status_code == 200
    assert resp.json()["success"] is True


def test_apply_discount_invalid_rate(auth_tokens):
    sale_id = create_open_sale_with_item(auth_tokens)

    resp = client.patch(
        f"{SALES_URL}/{sale_id}/discount",
        headers=auth_header(auth_tokens, "admin"),
        params={"discount_rate": 1.5},
    )
    assert resp.status_code == 400


def test_apply_discount_to_sale_unauthenticated():
    resp = client.patch(
        f"{SALES_URL}/1/discount",
        params={"discount_rate": 0.1},
    )
    assert resp.status_code == 401


def test_apply_discount_to_sale_not_found(auth_tokens):
    resp = client.patch(
        f"{SALES_URL}/99999/discount",
        headers=auth_header(auth_tokens, "admin"),
        params={"discount_rate": 0.1},
    )
    assert resp.status_code == 404


def test_apply_discount_to_sale_invalid_id(auth_tokens):
    resp = client.patch(
        f"{SALES_URL}/0/discount",
        headers=auth_header(auth_tokens, "admin"),
        params={"discount_rate": 0.1},
    )
    assert resp.status_code == 400


def test_apply_discount_to_sale_invalid_status(auth_tokens):
    sale_id = create_open_sale_with_item(auth_tokens)

    close_resp = client.patch(
        f"{SALES_URL}/{sale_id}/close",
        headers=auth_header(auth_tokens, "admin"),
    )
    assert close_resp.status_code == 200

    resp = client.patch(
        f"{SALES_URL}/{sale_id}/discount",
        headers=auth_header(auth_tokens, "admin"),
        params={"discount_rate": 0.1},
    )
    assert resp.status_code == 420


# ---------------------------------------------------------------------
# PATCH /sales/{sale_id}/items/{product_barcode}/discount
# ---------------------------------------------------------------------

def test_apply_discount_to_item_success(auth_tokens):
    sale_id = create_open_sale_with_item(auth_tokens)

    resp = client.patch(
        f"{SALES_URL}/{sale_id}/items/{PRODUCT_BARCODE}/discount",
        headers=auth_header(auth_tokens, "admin"),
        params={"discount_rate": 0.2},
    )
    assert resp.status_code == 200
    assert resp.json()["success"] is True


def test_apply_discount_to_item_not_found(auth_tokens):
    sale_id = create_open_sale_with_item(auth_tokens)

    resp = client.patch(
        f"{SALES_URL}/{sale_id}/items/NOTHERE/discount",
        headers=auth_header(auth_tokens, "admin"),
        params={"discount_rate": 0.2},
    )
    assert resp.status_code == 404


def test_apply_discount_to_item_invalid_rate(auth_tokens):
    sale_id = create_open_sale_with_item(auth_tokens)

    resp = client.patch(
        f"{SALES_URL}/{sale_id}/items/{PRODUCT_BARCODE}/discount",
        headers=auth_header(auth_tokens, "admin"),
        params={"discount_rate": -0.1},
    )
    assert resp.status_code == 400


def test_apply_discount_to_item_unauthenticated():
    resp = client.patch(
        f"{SALES_URL}/1/items/{PRODUCT_BARCODE}/discount",
        params={"discount_rate": 0.1},
    )
    assert resp.status_code == 401


def test_apply_discount_to_item_sale_not_found(auth_tokens):
    resp = client.patch(
        f"{SALES_URL}/99999/items/{PRODUCT_BARCODE}/discount",
        headers=auth_header(auth_tokens, "admin"),
        params={"discount_rate": 0.1},
    )
    assert resp.status_code == 404


def test_apply_discount_to_item_invalid_status(auth_tokens):
    sale_id = create_open_sale_with_item(auth_tokens)

    close_resp = client.patch(
        f"{SALES_URL}/{sale_id}/close",
        headers=auth_header(auth_tokens, "admin"),
    )
    assert close_resp.status_code == 200

    resp = client.patch(
        f"{SALES_URL}/{sale_id}/items/{PRODUCT_BARCODE}/discount",
        headers=auth_header(auth_tokens, "admin"),
        params={"discount_rate": 0.1},
    )
    assert resp.status_code == 420


# ---------------------------------------------------------------------
# PATCH /sales/{sale_id}/close
# ---------------------------------------------------------------------

def test_close_sale_success(auth_tokens):
    create_resp = client.post(SALES_URL + "/", headers=auth_header(auth_tokens, "admin"))
    sale_id = create_resp.json()["id"]

    resp = client.patch(
        f"{SALES_URL}/{sale_id}/close",
        headers=auth_header(auth_tokens, "admin"),
    )
    assert resp.status_code == 200
    assert resp.json()["success"] is True


def test_close_sale_invalid_id(auth_tokens):
    resp = client.patch(
        f"{SALES_URL}/0/close",
        headers=auth_header(auth_tokens, "admin"),
    )
    assert resp.status_code == 400


def test_close_sale_not_found(auth_tokens):
    resp = client.patch(
        f"{SALES_URL}/99999/close",
        headers=auth_header(auth_tokens, "admin"),
    )
    assert resp.status_code == 404


def test_close_sale_unauthenticated():
    resp = client.patch(f"{SALES_URL}/1/close")
    assert resp.status_code == 401


def test_close_sale_already_closed(auth_tokens):
    create_resp = client.post(SALES_URL + "/", headers=auth_header(auth_tokens, "admin"))
    sale_id = create_resp.json()["id"]

    first_close = client.patch(
        f"{SALES_URL}/{sale_id}/close",
        headers=auth_header(auth_tokens, "admin"),
    )
    assert first_close.status_code == 200

    second_close = client.patch(
        f"{SALES_URL}/{sale_id}/close",
        headers=auth_header(auth_tokens, "admin"),
    )
    assert second_close.status_code == 420

def test_close_empty_sale_deletes_sale(auth_tokens):
    resp = client.post(SALES_URL + "/", headers=auth_header(auth_tokens, "admin"))
    sale_id = resp.json()["id"]

    close_resp = client.patch(
        f"{SALES_URL}/{sale_id}/close",
        headers=auth_header(auth_tokens, "admin"),
    )
    assert close_resp.status_code == 200

    get_resp = client.get(
        f"{SALES_URL}/{sale_id}",
        headers=auth_header(auth_tokens, "admin"),
    )
    assert get_resp.status_code == 404


# ---------------------------------------------------------------------
# PATCH /sales/{sale_id}/pay
# ---------------------------------------------------------------------

def test_pay_sale_success_and_points(auth_tokens):
    sale_id = create_open_sale_with_item(auth_tokens, amount=2)

    close_resp = client.patch(
        f"{SALES_URL}/{sale_id}/close",
        headers=auth_header(auth_tokens, "admin"),
    )
    assert close_resp.status_code == 200

    pay_resp = client.patch(
        f"{SALES_URL}/{sale_id}/pay",
        headers=auth_header(auth_tokens, "admin"),
        params={"cash_amount": 100.0},
    )
    assert pay_resp.status_code == 200
    data = pay_resp.json()
    assert "change" in data

    points_resp = client.get(
        f"{SALES_URL}/{sale_id}/points",
        headers=auth_header(auth_tokens, "admin"),
    )
    assert points_resp.status_code == 200
    assert isinstance(points_resp.json()["points"], int)


def test_pay_sale_wrong_state(auth_tokens):
    create_resp = client.post(SALES_URL + "/", headers=auth_header(auth_tokens, "admin"))
    sale_id = create_resp.json()["id"]

    resp = client.patch(
        f"{SALES_URL}/{sale_id}/pay",
        headers=auth_header(auth_tokens, "admin"),
        params={"cash_amount": 10.0},
    )
    assert resp.status_code == 420


def test_pay_sale_invalid_cash_amount(auth_tokens):
    sale_id = create_open_sale_with_item(auth_tokens)

    close_resp = client.patch(
        f"{SALES_URL}/{sale_id}/close",
        headers=auth_header(auth_tokens, "admin"),
    )
    assert close_resp.status_code == 200

    resp = client.patch(
        f"{SALES_URL}/{sale_id}/pay",
        headers=auth_header(auth_tokens, "admin"),
        params={"cash_amount": 0.0},
    )
    assert resp.status_code == 400


def test_pay_sale_not_found(auth_tokens):
    resp = client.patch(
        f"{SALES_URL}/99999/pay",
        headers=auth_header(auth_tokens, "admin"),
        params={"cash_amount": 10.0},
    )
    assert resp.status_code == 404


def test_pay_sale_invalid_id(auth_tokens):
    resp = client.patch(
        f"{SALES_URL}/0/pay",
        headers=auth_header(auth_tokens, "admin"),
        params={"cash_amount": 10.0},
    )
    assert resp.status_code == 400


def test_pay_sale_unauthenticated():
    resp = client.patch(
        f"{SALES_URL}/1/pay",
        params={"cash_amount": 10.0},
    )
    assert resp.status_code == 401


# ---------------------------------------------------------------------
# GET /sales/{sale_id}/points
# ---------------------------------------------------------------------

def test_get_points_success(auth_tokens):
    sale_id = create_open_sale_with_item(auth_tokens, amount=2)

    close_resp = client.patch(
        f"{SALES_URL}/{sale_id}/close",
        headers=auth_header(auth_tokens, "admin"),
    )
    assert close_resp.status_code == 200

    pay_resp = client.patch(
        f"{SALES_URL}/{sale_id}/pay",
        headers=auth_header(auth_tokens, "admin"),
        params={"cash_amount": 100.0},
    )
    assert pay_resp.status_code == 200

    points_resp = client.get(
        f"{SALES_URL}/{sale_id}/points",
        headers=auth_header(auth_tokens, "admin"),
    )
    assert points_resp.status_code == 200
    assert isinstance(points_resp.json()["points"], int)


def test_get_points_invalid_id(auth_tokens):
    resp = client.get(
        f"{SALES_URL}/0/points",
        headers=auth_header(auth_tokens, "admin"),
    )
    assert resp.status_code == 400


def test_get_points_not_found(auth_tokens):
    resp = client.get(
        f"{SALES_URL}/99999/points",
        headers=auth_header(auth_tokens, "admin"),
    )
    assert resp.status_code == 404


def test_get_points_wrong_state(auth_tokens):
    sale_id = create_open_sale_with_item(auth_tokens, amount=1)

    close_resp = client.patch(
        f"{SALES_URL}/{sale_id}/close",
        headers=auth_header(auth_tokens, "admin"),
    )
    assert close_resp.status_code == 200

    points_resp = client.get(
        f"{SALES_URL}/{sale_id}/points",
        headers=auth_header(auth_tokens, "admin"),
    )
    assert points_resp.status_code == 420


def test_get_points_unauthenticated():
    resp = client.get(f"{SALES_URL}/1/points")
    assert resp.status_code == 401