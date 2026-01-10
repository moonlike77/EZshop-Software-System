import pytest
from fastapi.testclient import TestClient
from main import app
from init_db import reset, init_db
import asyncio
from app.database.database import AsyncSessionLocal
from app.models.DAO.sale_dao import SaleDAO
from app.models.DAO.sale_line_dao import SaleLineDAO
from app.models.DAO.product_dao import ProductDAO
from app.models.sale_status import SaleStatus
from datetime import datetime, timezone

BASE_URL = "/api/v1"

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="session", autouse=True)
def auth_tokens(event_loop, client):
    """کاربرها رو میسازیم و توکن هاشون رو میگیریم"""
    event_loop.run_until_complete(reset())
    event_loop.run_until_complete(init_db())
    
    users = {
        "admin": {"username": "admin", "password": "admin"},
        "manager": {"username": "ShopManager", "password": "ShManager"},
        "cashier": {"username": "Cashier", "password": "Cashier"},
    }
    tokens = {}
    for role, creds in users.items():
        resp = client.post(BASE_URL + "/auth", json=creds)
        if resp.status_code == 200:
            tokens[role] = resp.json()["token"]
    return tokens

def auth_header(tokens, role):
    return {"Authorization": f"Bearer {tokens[role]}"}

# --- شروع تست‌های Return ---

@pytest.mark.asyncio
async def test_full_return_lifecycle(client, auth_tokens):
    """
    سناریوی کامل:
    1. ایجاد مرجوعی (Start Return)
    2. اضافه کردن آیتم
    3. بستن مرجوعی (Close)
    4. بازپرداخت (Reimburse)
    """
    
    # 1. Start Return
    # نکته: sale_id رو به عنوان Query Param میفرستیم چون توی Route اینطور تعریف کردیم
    async with AsyncSessionLocal() as session:
        prod = ProductDAO(id=1, description="Coffe", barcode="000000000001", price_per_unit=5.5,
                          note="Black coffe", quantity=10, position="9-7-B")
        session.add(prod)
        await session.commit()
        await session.refresh(prod)

        sale_line = SaleLineDAO(id=1, sale_id=1, product_barcode=prod.barcode,
                                quantity=3, price_per_unit=prod.price_per_unit, discount_rate=0.0)
        session.add(sale_line)
        await session.commit()
        await session.refresh(sale_line)

        sale = SaleDAO(id=1, status=SaleStatus.PAID, discount_rate=0.0,
                       created_at=datetime.now(timezone.utc), closed_at=datetime.now(timezone.utc),
                       lines=[sale_line])
        session.add(sale)
        await session.commit()
        await session.refresh(sale)

    resp = client.post(f"{BASE_URL}/returns/?sale_id=1", headers=auth_header(auth_tokens, "cashier"))
    assert resp.status_code == 201
    return_data = resp.json()
    return_id = return_data["id"]
    assert return_data["status"] == "OPEN"
    assert return_data["sale_id"] == sale.id

    # 2. Add Item
    # بارکد و مقدار هم کوئری پارامتر هستن
    resp = client.post(f"{BASE_URL}/returns/{return_id}/items?barcode=000000000001&amount=2", headers=auth_header(auth_tokens, "cashier"))
    assert resp.status_code == 201
    assert resp.json()["success"] is True

    # چک کنیم آیتم اضافه شده؟
    resp = client.get(f"{BASE_URL}/returns/{return_id}", headers=auth_header(auth_tokens, "cashier"))
    assert len(resp.json()["lines"]) == 1
    assert resp.json()["lines"][0]["quantity"] == 2

    # 3. Close Return
    resp = client.patch(f"{BASE_URL}/returns/{return_id}/close", headers=auth_header(auth_tokens, "cashier"))
    assert resp.status_code == 200
    assert resp.json()["success"] is True
    
    # چک کنیم وضعیت بسته شده
    resp = client.get(f"{BASE_URL}/returns/{return_id}", headers=auth_header(auth_tokens, "cashier"))
    assert resp.json()["status"] == "CLOSED"

    # 4. Reimburse Return (فقط ادمین یا منیجر میتونه)
    resp = client.patch(f"{BASE_URL}/returns/{return_id}/reimburse", headers=auth_header(auth_tokens, "manager"))
    assert resp.status_code == 200
    assert "refund_amount" in resp.json()
    
    # چک نهایی که وضعیت REIMBURSED شده
    resp = client.get(f"{BASE_URL}/returns/{return_id}", headers=auth_header(auth_tokens, "manager"))
    assert resp.json()["status"] == "REIMBURSED"
@pytest.mark.asyncio
async def test_delete_return(client, auth_tokens):

    # ایجاد یک مرجوعی الکی
    resp = client.post(f"{BASE_URL}/returns/?sale_id=1", headers=auth_header(auth_tokens, "cashier"))
    r_id = resp.json()["id"]
    
    # حذف
    resp = client.delete(f"{BASE_URL}/returns/{r_id}", headers=auth_header(auth_tokens, "cashier"))
    assert resp.status_code == 204 # No Content
    
    # باید دیگه پیدا نشه
    resp = client.get(f"{BASE_URL}/returns/{r_id}", headers=auth_header(auth_tokens, "cashier"))
    assert resp.status_code == 404