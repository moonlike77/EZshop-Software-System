import pytest
from fastapi.testclient import TestClient
from main import app
from init_db import reset, init_db
import asyncio

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

def test_full_return_lifecycle(client, auth_tokens):
    """
    سناریوی کامل:
    1. ایجاد مرجوعی (Start Return)
    2. اضافه کردن آیتم
    3. بستن مرجوعی (Close)
    4. بازپرداخت (Reimburse)
    """
    
    # 1. Start Return
    # نکته: sale_id رو به عنوان Query Param میفرستیم چون توی Route اینطور تعریف کردیم
    resp = client.post(f"{BASE_URL}/returns/?sale_id=500", headers=auth_header(auth_tokens, "cashier"))
    assert resp.status_code == 201
    return_data = resp.json()
    return_id = return_data["id"]
    assert return_data["status"] == "OPEN"

    # 2. Add Item
    # بارکد و مقدار هم کوئری پارامتر هستن
    item_params = {"barcode": "123456", "amount": 2}
    resp = client.post(f"{BASE_URL}/returns/{return_id}/items", params=item_params, headers=auth_header(auth_tokens, "cashier"))
    assert resp.status_code == 201
    assert resp.json()["success"] is True

    # چک کنیم آیتم اضافه شده؟
    resp = client.get(f"{BASE_URL}/returns/{return_id}", headers=auth_header(auth_tokens, "cashier"))
    assert len(resp.json()["lines"]) == 1
    assert resp.json()["lines"][0]["quantity"] == 2

    # 3. Close Return
    resp = client.patch(f"{BASE_URL}/returns/{return_id}/close", headers=auth_header(auth_tokens, "cashier"))
    assert resp.status_code == 200
    
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

def test_delete_return(client, auth_tokens):
    # ایجاد یک مرجوعی الکی
    resp = client.post(f"{BASE_URL}/returns/?sale_id=600", headers=auth_header(auth_tokens, "cashier"))
    r_id = resp.json()["id"]
    
    # حذف
    resp = client.delete(f"{BASE_URL}/returns/{r_id}", headers=auth_header(auth_tokens, "cashier"))
    assert resp.status_code == 204 # No Content
    
    # باید دیگه پیدا نشه
    resp = client.get(f"{BASE_URL}/returns/{r_id}", headers=auth_header(auth_tokens, "cashier"))
    assert resp.status_code == 404