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

        # -------------------------------------------------
    # CREATE A TEST PRODUCT (needed by sales tests)
    # -------------------------------------------------
    create_product_resp = client.post(
        PRODUCTS_URL + "/",
        headers={"Authorization": tokens["admin"]},
        json={
            "description": "Test product",
            "barcode": PRODUCT_BARCODE,
            "price_per_unit": 10.0,
            "note": None,
            "quantity": 100,
            "position": None,
        },
    )

    # 201 = created, 409 = already exists (both OK)
    assert create_product_resp.status_code in (201, 409), create_product_resp.text

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

# ---------------------------
# REPOSITORY TESTS
# ---------------------------

import pytest

from init_db import reset, init_db
from sqlalchemy import select

from app.repositories.sale_repository import SaleRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.system_repository import SystemRepository

from app.models.errors.notfound_error import NotFoundError
from app.models.errors.bad_request import BadRequestError
from app.models.errors.conflict_error import ConflictError
from app.models.errors.invalid_state_error import InvalidStateError

from app.models.sale_status import SaleStatus
from app.models.DAO.sale_dao import SaleDAO
from app.models.DAO.sale_line_dao import SaleLineDAO
from app.models.DAO.system_dao import SystemInfoDAO

@pytest.mark.asyncio
async def _create_product(barcode: str, qty: int = 100, price: float = 10.0):
    prod_repo = ProductRepository()
    return await prod_repo.create_product(
        description=f"TestProd-{barcode}",
        barcode=barcode,
        price_per_unit=price,
        quantity=qty,
        position="1-A-1"
    )

@pytest.mark.asyncio
async def _create_sale_and_add_item(repo: SaleRepository, barcode: str, amount: int):
    sale = await repo.create_sale()
    await repo.add_product_to_sale(sale.id, barcode, amount)
    return sale.id

@pytest.mark.asyncio
async def test_sale_repo_create_sale_success():
    await reset(); await init_db()
    repo = SaleRepository()

    sale = await repo.create_sale()
    assert sale.id is not None
    assert sale.status == SaleStatus.OPEN
    assert sale.discount_rate == 0.0


@pytest.mark.asyncio
async def test_sale_repo_list_sales_returns_list():
    await reset(); await init_db()
    repo = SaleRepository()

    await repo.create_sale()
    await repo.create_sale()

    sales = await repo.list_sales()
    assert isinstance(sales, list)
    assert len(sales) >= 2


@pytest.mark.asyncio
async def test_sale_repo_get_sale_not_found():
    await reset(); await init_db()
    repo = SaleRepository()

    with pytest.raises(NotFoundError):
        await repo.get_sale(99999999)


@pytest.mark.asyncio
async def test_sale_repo_get_sale_pending_no_lines_is_considered_cancelled():

    await reset(); await init_db()
    repo = SaleRepository()

    sale = await repo.create_sale()

    async with await repo._get_session() as session:
        db_sale = await session.get(SaleDAO, sale.id)
        db_sale.status = SaleStatus.PENDING
        await session.commit()

    with pytest.raises(NotFoundError):
        await repo.get_sale(sale.id)


@pytest.mark.asyncio
async def test_sale_repo_delete_sale_not_found():
    await reset(); await init_db()
    repo = SaleRepository()

    with pytest.raises(NotFoundError):
        await repo.delete_sale(99999999)


@pytest.mark.asyncio
async def test_sale_repo_delete_paid_sale_conflict():
    await reset(); await init_db()
    repo = SaleRepository()

    sale = await repo.create_sale()
    async with await repo._get_session() as session:
        db_sale = await session.get(SaleDAO, sale.id)
        db_sale.status = SaleStatus.PAID
        await session.commit()

    with pytest.raises(ConflictError):
        await repo.delete_sale(sale.id)


@pytest.mark.asyncio
async def test_sale_repo_delete_sale_restores_stock_quantities():

    await reset(); await init_db()
    repo = SaleRepository()
    prod_repo = ProductRepository()

    barcode = "sale-del-restore"
    prod = await _create_product(barcode, qty=10, price=2.0)

    sale_id = await _create_sale_and_add_item(repo, barcode, 3)

    prod_after_add = await prod_repo.get_product_by_id(prod.id)
    assert prod_after_add.quantity == 7

    ok = await repo.delete_sale(sale_id)
    assert ok is True

    prod_after_del = await prod_repo.get_product_by_id(prod.id)
    assert prod_after_del.quantity == 10


@pytest.mark.asyncio
async def test_sale_repo_add_product_bad_amount():
    await reset(); await init_db()
    repo = SaleRepository()

    sale = await repo.create_sale()
    with pytest.raises(BadRequestError):
        await repo.add_product_to_sale(sale.id, "any", 0)


@pytest.mark.asyncio
async def test_sale_repo_add_product_sale_not_found():
    await reset(); await init_db()
    repo = SaleRepository()

    with pytest.raises(NotFoundError):
        await repo.add_product_to_sale(999999, "any", 1)


@pytest.mark.asyncio
async def test_sale_repo_add_product_wrong_status():
    await reset(); await init_db()
    repo = SaleRepository()

    sale = await repo.create_sale()
    async with await repo._get_session() as session:
        db_sale = await session.get(SaleDAO, sale.id)
        db_sale.status = SaleStatus.PENDING
        await session.commit()

    with pytest.raises(InvalidStateError):
        await repo.add_product_to_sale(sale.id, "any", 1)


@pytest.mark.asyncio
async def test_sale_repo_add_product_product_not_found():
    await reset(); await init_db()
    repo = SaleRepository()

    sale = await repo.create_sale()
    with pytest.raises(NotFoundError):
        await repo.add_product_to_sale(sale.id, "nonexistent-barcode", 1)


@pytest.mark.asyncio
async def test_sale_repo_add_product_insufficient_stock_conflict():
    await reset(); await init_db()
    repo = SaleRepository()

    barcode = "sale-insuff"
    await _create_product(barcode, qty=1, price=1.0)
    sale = await repo.create_sale()

    with pytest.raises(ConflictError):
        await repo.add_product_to_sale(sale.id, barcode, 2)


@pytest.mark.asyncio
async def test_sale_repo_add_product_success_decreases_stock_and_creates_line():
    await reset(); await init_db()
    repo = SaleRepository()
    prod_repo = ProductRepository()

    barcode = "sale-add-ok"
    prod = await _create_product(barcode, qty=10, price=3.0)

    sale = await repo.create_sale()
    ok = await repo.add_product_to_sale(sale.id, barcode, 4)
    assert ok is True

    updated_prod = await prod_repo.get_product_by_id(prod.id)
    assert updated_prod.quantity == 6

    async with await repo._get_session() as session:
        res = await session.execute(
            select(SaleLineDAO).where(
                SaleLineDAO.sale_id == sale.id,
                SaleLineDAO.product_barcode == barcode
            )
        )
        line = res.scalars().first()
        assert line is not None
        assert line.quantity == 4
        assert line.price_per_unit == 3.0


@pytest.mark.asyncio
async def test_sale_repo_remove_product_bad_amount():
    await reset(); await init_db()
    repo = SaleRepository()

    sale = await repo.create_sale()
    with pytest.raises(BadRequestError):
        await repo.remove_product_from_sale(sale.id, "any", 0)


@pytest.mark.asyncio
async def test_sale_repo_remove_product_sale_not_found():
    await reset(); await init_db()
    repo = SaleRepository()

    with pytest.raises(NotFoundError):
        await repo.remove_product_from_sale(999999, "any", 1)


@pytest.mark.asyncio
async def test_sale_repo_remove_product_wrong_status():
    await reset(); await init_db()
    repo = SaleRepository()

    barcode = "sale-rem-status"
    await _create_product(barcode, qty=10, price=1.0)
    sale_id = await _create_sale_and_add_item(repo, barcode, 1)

    async with await repo._get_session() as session:
        db_sale = await session.get(SaleDAO, sale_id)
        db_sale.status = SaleStatus.PENDING
        await session.commit()

    with pytest.raises(InvalidStateError):
        await repo.remove_product_from_sale(sale_id, barcode, 1)


@pytest.mark.asyncio
async def test_sale_repo_remove_product_line_not_found():
    await reset(); await init_db()
    repo = SaleRepository()

    barcode = "sale-rem-lnf"
    await _create_product(barcode, qty=10, price=1.0)
    sale = await repo.create_sale()

    with pytest.raises(NotFoundError):
        await repo.remove_product_from_sale(sale.id, barcode, 1)


@pytest.mark.asyncio
async def test_sale_repo_remove_product_success_partial_restores_stock_and_decreases_line_qty():
    await reset(); await init_db()
    repo = SaleRepository()
    prod_repo = ProductRepository()

    barcode = "sale-rem-partial"
    prod = await _create_product(barcode, qty=10, price=1.0)
    sale_id = await _create_sale_and_add_item(repo, barcode, 5) 

    ok = await repo.remove_product_from_sale(sale_id, barcode, 2)
    assert ok is True

    updated_prod = await prod_repo.get_product_by_id(prod.id)
    assert updated_prod.quantity == 7

    async with await repo._get_session() as session:
        from sqlalchemy import select
        res = await session.execute(
            select(SaleLineDAO).where(
                SaleLineDAO.sale_id == sale_id,
                SaleLineDAO.product_barcode == barcode
            )
        )
        line = res.scalars().first()
        assert line is not None
        assert line.quantity == 3


@pytest.mark.asyncio
async def test_sale_repo_remove_product_success_delete_line_when_amount_ge_line_qty():
    await reset(); await init_db()
    repo = SaleRepository()
    prod_repo = ProductRepository()

    barcode = "sale-rem-delete"
    prod = await _create_product(barcode, qty=10, price=1.0)
    sale_id = await _create_sale_and_add_item(repo, barcode, 3)

    ok = await repo.remove_product_from_sale(sale_id, barcode, 10)
    assert ok is True

    updated_prod = await prod_repo.get_product_by_id(prod.id)
    assert updated_prod.quantity == 10

    async with await repo._get_session() as session:
        from sqlalchemy import select
        res = await session.execute(
            select(SaleLineDAO).where(
                SaleLineDAO.sale_id == sale_id,
                SaleLineDAO.product_barcode == barcode
            )
        )
        line = res.scalars().first()
        assert line is None


@pytest.mark.asyncio
async def test_sale_repo_apply_discount_invalid_rate():
    await reset(); await init_db()
    repo = SaleRepository()

    sale = await repo.create_sale()
    with pytest.raises(BadRequestError):
        await repo.apply_discount(sale.id, 1.0)


@pytest.mark.asyncio
async def test_sale_repo_apply_discount_wrong_status():
    await reset(); await init_db()
    repo = SaleRepository()

    sale = await repo.create_sale()
    async with await repo._get_session() as session:
        db_sale = await session.get(SaleDAO, sale.id)
        db_sale.status = SaleStatus.PENDING
        await session.commit()

    with pytest.raises(InvalidStateError):
        await repo.apply_discount(sale.id, 0.1)


@pytest.mark.asyncio
async def test_sale_repo_apply_product_discount_line_not_found():
    await reset(); await init_db()
    repo = SaleRepository()

    barcode = "sale-disc-line"
    await _create_product(barcode, qty=10, price=1.0)
    sale = await repo.create_sale()

    with pytest.raises(NotFoundError):
        await repo.apply_product_discount(sale.id, barcode, 0.1)


@pytest.mark.asyncio
async def test_sale_repo_close_sale_wrong_status():
    await reset(); await init_db()
    repo = SaleRepository()

    sale = await repo.create_sale()
    async with await repo._get_session() as session:
        db_sale = await session.get(SaleDAO, sale.id)
        db_sale.status = SaleStatus.PAID
        await session.commit()

    with pytest.raises(InvalidStateError):
        await repo.close_sale(sale.id)


@pytest.mark.asyncio
async def test_sale_repo_pay_sale_wrong_state():
    await reset(); await init_db()
    repo = SaleRepository()

    sale = await repo.create_sale()
    with pytest.raises(InvalidStateError):
        await repo.pay_sale(sale.id, 10.0)


@pytest.mark.asyncio
async def test_sale_repo_pay_sale_insufficient_cash():
    await reset(); await init_db()
    repo = SaleRepository()

    barcode = "sale-pay-bad"
    await _create_product(barcode, qty=10, price=10.0)
    sale_id = await _create_sale_and_add_item(repo, barcode, 1)
    await repo.close_sale(sale_id)

    with pytest.raises(BadRequestError):
        await repo.pay_sale(sale_id, 0.5)


@pytest.mark.asyncio
async def test_sale_repo_pay_sale_success_updates_status_and_balance():
    await reset(); await init_db()
    repo = SaleRepository()
    sys_repo = SystemRepository()

    await sys_repo.set_balance(0.0)

    barcode = "sale-pay-ok"
    await _create_product(barcode, qty=10, price=10.0)
    sale_id = await _create_sale_and_add_item(repo, barcode, 2)
    await repo.close_sale(sale_id)

    change = await repo.pay_sale(sale_id, 50.0)
    assert change == 30.0

    sale = await repo.get_sale(sale_id)
    assert sale.status == SaleStatus.PAID

    system = await sys_repo.get_singleton()
    assert system.balance == 20.0


@pytest.mark.asyncio
async def test_sale_repo_get_points_wrong_state():
    await reset(); await init_db()
    repo = SaleRepository()

    sale = await repo.create_sale()
    with pytest.raises(InvalidStateError):
        await repo.get_sale_points(sale.id)


@pytest.mark.asyncio
async def test_sale_repo_get_points_success_equals_floor_total():

    await reset(); await init_db()
    repo = SaleRepository()
    sys_repo = SystemRepository()
    await sys_repo.set_balance(0.0)

    barcode = "sale-points-ok"
    await _create_product(barcode, qty=10, price=12.7)
    sale_id = await _create_sale_and_add_item(repo, barcode, 1)
    await repo.close_sale(sale_id)
    await repo.pay_sale(sale_id, 20.0)

    points = await repo.get_sale_points(sale_id)
    assert points == 12


@pytest.mark.asyncio
async def test_sale_repo_apply_product_discount_invalid_rate_raises():
    await reset(); await init_db()
    repo = SaleRepository()

    with pytest.raises(BadRequestError):
        await repo.apply_product_discount(sale_id=1, product_barcode="any", discount_rate=-0.1)

    with pytest.raises(BadRequestError):
        await repo.apply_product_discount(sale_id=1, product_barcode="any", discount_rate=1.0)


@pytest.mark.asyncio
async def test_sale_repo_pay_sale_invalid_cash_amount_raises():
    await reset(); await init_db()
    repo = SaleRepository()

    with pytest.raises(BadRequestError):
        await repo.pay_sale(sale_id=1, cash_amount=0.0)

    with pytest.raises(BadRequestError):
        await repo.pay_sale(sale_id=1, cash_amount=-10.0)


import pytest
from app.models.errors.bad_request import BadRequestError
from app.routes.sale_route import remove_product_from_sale
from app.routes.sale_route import apply_product_discount_to_sale

# ---------------------------
# ROUTE-LEVEL VALIDATION BRANCHES
# ---------------------------

@pytest.mark.asyncio
async def test_sale_route_get_sale_rejects_id_le_zero_direct_call():
    from app.routes.sale_route import get_sale
    with pytest.raises(BadRequestError):
        await get_sale(0)

@pytest.mark.asyncio
async def test_sale_route_delete_sale_rejects_id_le_zero_direct_call():
    from app.routes.sale_route import delete_sale
    with pytest.raises(BadRequestError):
        await delete_sale(0)

@pytest.mark.asyncio
async def test_sale_route_add_product_rejects_sale_id_le_zero_direct_call():
    from app.routes.sale_route import add_product_to_sale
    with pytest.raises(BadRequestError):
        await add_product_to_sale(sale_id=0, barcode="123", amount=1)

@pytest.mark.asyncio
async def test_sale_route_add_product_rejects_amount_le_zero_direct_call():
    from app.routes.sale_route import add_product_to_sale
    with pytest.raises(BadRequestError):
        await add_product_to_sale(sale_id=1, barcode="123", amount=0)

@pytest.mark.asyncio
async def test_sale_route_remove_product_rejects_amount_le_zero_direct_call():
    from app.routes.sale_route import remove_product_from_sale
    with pytest.raises(BadRequestError):
        await remove_product_from_sale(sale_id=1, barcode="123", amount=0)

@pytest.mark.asyncio
async def test_sale_route_apply_discount_rejects_invalid_rate_direct_call():
    from app.routes.sale_route import apply_discount_to_sale
    with pytest.raises(BadRequestError):
        await apply_discount_to_sale(sale_id=1, discount_rate=1.0)

@pytest.mark.asyncio
async def test_sale_route_apply_product_discount_rejects_invalid_rate_direct_call():
    from app.routes.sale_route import apply_product_discount_to_sale
    with pytest.raises(BadRequestError):
        await apply_product_discount_to_sale(sale_id=1, product_barcode="123", discount_rate=-0.1)

@pytest.mark.asyncio
async def test_sale_route_pay_sale_rejects_cash_amount_le_zero_direct_call():
    from app.routes.sale_route import pay_sale
    with pytest.raises(BadRequestError):
        await pay_sale(sale_id=1, cash_amount=0.0)

@pytest.mark.asyncio
async def test_sale_route_get_points_rejects_sale_id_le_zero_direct_call():
    from app.routes.sale_route import get_sale_points
    with pytest.raises(BadRequestError):
        await get_sale_points(0)


@pytest.mark.asyncio
async def test_sale_route_remove_product_rejects_sale_id_le_zero_direct_call():
    with pytest.raises(BadRequestError):
        await remove_product_from_sale(sale_id=0, barcode="abc", amount=1)

@pytest.mark.asyncio
async def test_sale_route_apply_product_discount_rejects_sale_id_le_zero_direct_call():
    with pytest.raises(BadRequestError):
        await apply_product_discount_to_sale(sale_id=0, product_barcode="abc", discount_rate=0.1)