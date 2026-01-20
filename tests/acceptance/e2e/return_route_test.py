import pytest
import asyncio
from init_db import reset, init_db
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from main import app
from app.models.DTO.return_dto import ReturnDTO
from app.models.return_status import ReturnStatus
from app.models.DAO.sale_dao import SaleDAO
from app.models.DAO.sale_line_dao import SaleLineDAO
from app.models.sale_status import SaleStatus
from app.models.DAO.product_dao import ProductDAO
from datetime import datetime, timezone
from app.models.user_type import UserType
from app.database.database import AsyncSessionLocal

client = TestClient(app)

@pytest.fixture(scope="session")
def client():
    from main import app
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="session", autouse=True)
def auth_tokens(client):
    """Authenticate customers once and return their JWT tokens."""

    asyncio.run(reset())
    asyncio.run(init_db())

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

@pytest.fixture
async def setup_sale_for_return():
    async with AsyncSessionLocal() as session:

        p1 = ProductDAO(id=1, description="Coffe", barcode="000000000001",
                        price_per_unit=2.5, note="Black Coffe",
                        quantity=20, position="9-B-1")
        session.add(p1)
        await session.commit()
        await session.refresh(p1)

        p2 = ProductDAO(id=2, description="Milk", barcode="000000000002",
                        price_per_unit=5.5, note="Lactose free milk",
                        quantity=20, position="9-B-2")
        session.add(p2)
        await session.commit()
        await session.refresh(p2)

        sl1 = SaleLineDAO(id=1, sale_id=1, product_barcode="000000000001",
                         quantity=5, price_per_unit=2.5, discount_rate=0.0)
        session.add(sl1)
        await session.commit()
        await session.refresh(sl1)
        
        s1 = SaleDAO(id=1, status=SaleStatus.PAID, discount_rate=0.0,
                    created_at=datetime.now(timezone.utc), closed_at = None, lines=[sl1])
        session.add(s1)
        await session.commit()
        await session.refresh(s1)

        sl2 = SaleLineDAO(id=2, sale_id=2, product_barcode="000000000002",
                         quantity=7, price_per_unit=5.5, discount_rate=0.0)
        session.add(sl2)
        await session.commit()
        await session.refresh(sl2)
        
        s2 = SaleDAO(id=2, status=SaleStatus.PAID, discount_rate=0.0,
                    created_at=datetime.now(timezone.utc), closed_at = None, lines=[sl2])
        session.add(s2)
        await session.commit()
        await session.refresh(s2)

def auth_header(tokens, role: str):
    return {"Authorization": tokens[role]}

BASE_URL = "http://127.0.0.1:8000/api/v1"

@pytest.mark.asyncio
async def test_start_return_route(client, auth_tokens, setup_sale_for_return):
    # فراخوانی API با هدر فیک
    # نکته کلیدی: ارسال هدر Authorization ضروری است تا میدل‌ور ارور 401 ندهد

    response = client.post(
        BASE_URL + "/returns/?sale_id=1", 
        headers=auth_header(auth_tokens, "admin")
    )

    # بررسی
    assert response.status_code == 201
    assert response.json()["id"] == 1

@pytest.mark.asyncio
async def test_start_return_route_sale_not_found(client, auth_tokens):
    # فراخوانی API با هدر فیک
    # نکته کلیدی: ارسال هدر Authorization ضروری است تا میدل‌ور ارور 401 ندهد

    response = client.post(
        BASE_URL + "/returns/?sale_id=999", 
        headers=auth_header(auth_tokens, "admin")
    )

    # بررسی
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_get_all_returns_route(client, auth_tokens):
    # فراخوانی API با هدر فیک
    # نکته کلیدی: ارسال هدر Authorization ضروری است تا میدل‌ور ارور 401 ندهد

    client.post(
        BASE_URL + "/returns/?sale_id=2", 
        headers=auth_header(auth_tokens, "admin")
    )

    response = client.get(
        BASE_URL + "/returns/", 
        headers=auth_header(auth_tokens, "admin")
    )

    # بررسی
    assert response.status_code == 200
    assert response.json()[0]["id"] == 1
    assert response.json()[1]["id"] == 2

@pytest.mark.asyncio
async def test_get_all_returns_by_sale_route(client, auth_tokens):
    # فراخوانی API با هدر فیک
    # نکته کلیدی: ارسال هدر Authorization ضروری است تا میدل‌ور ارور 401 ندهد

    response = client.get(
        BASE_URL + "/returns/sale/1", 
        headers=auth_header(auth_tokens, "admin")
    )

    # بررسی
    assert response.status_code == 200
    assert response.json()[0]["id"] == 1

@pytest.mark.asyncio
async def test_get_return_route(client, auth_tokens):
    # فراخوانی API با هدر فیک
    # نکته کلیدی: ارسال هدر Authorization ضروری است تا میدل‌ور ارور 401 ندهد

    response = client.get(
        BASE_URL + "/returns/1", 
        headers=auth_header(auth_tokens, "admin")
    )

    # بررسی
    assert response.status_code == 200
    assert response.json()["id"] == 1

@pytest.mark.asyncio
async def test_get_return_route_not_found(client, auth_tokens):
    # فراخوانی API با هدر فیک
    # نکته کلیدی: ارسال هدر Authorization ضروری است تا میدل‌ور ارور 401 ندهد

    response = client.get(
        BASE_URL + "/returns/999", 
        headers=auth_header(auth_tokens, "admin")
    )

    # بررسی
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_add_product_to_return_route(client, auth_tokens):
    # فراخوانی API با هدر فیک
    # نکته کلیدی: ارسال هدر Authorization ضروری است تا میدل‌ور ارور 401 ندهد

    stat = client.post(
        BASE_URL + "/returns/1/items?barcode=000000000001&amount=3", 
        headers=auth_header(auth_tokens, "admin")
    )

    assert stat.status_code == 201

    response = client.get(
        BASE_URL + "/returns/1", 
        headers=auth_header(auth_tokens, "admin")
    )

    # بررسی
    assert response.json()["lines"][0]["product_barcode"] == "000000000001"
    assert response.json()["lines"][0]["quantity"] == 3

@pytest.mark.asyncio
async def test_add_product_to_return_route_not_found(client, auth_tokens):
    # فراخوانی API با هدر فیک
    # نکته کلیدی: ارسال هدر Authorization ضروری است تا میدل‌ور ارور 401 ندهد

    response = client.post(
        BASE_URL + "/returns/999/items?barcode=000000000001&amount=3", 
        headers=auth_header(auth_tokens, "admin")
    )

    assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_product_from_return_route(client, auth_tokens):
    # فراخوانی API با هدر فیک
    # نکته کلیدی: ارسال هدر Authorization ضروری است تا میدل‌ور ارور 401 ندهد

    stat = client.delete(
        BASE_URL + "/returns/1/items?barcode=000000000001&amount=1", 
        headers=auth_header(auth_tokens, "admin")
    )

    assert stat.status_code == 202

    response = client.get(
        BASE_URL + "/returns/1", 
        headers=auth_header(auth_tokens, "admin")
    )

    # بررسی
    assert response.json()["lines"][0]["quantity"] == 2

@pytest.mark.asyncio
async def test_delete_product_from_return_route_not_found(client, auth_tokens):
    # فراخوانی API با هدر فیک
    # نکته کلیدی: ارسال هدر Authorization ضروری است تا میدل‌ور ارور 401 ندهد

    response = client.delete(
        BASE_URL + "/returns/999/items?barcode=000000000001&amount=1", 
        headers=auth_header(auth_tokens, "admin")
    )

    assert response.status_code == 404

@pytest.mark.asyncio
async def test_close_return_route(client, auth_tokens):
    
    response = client.patch(
        BASE_URL + "/returns/1/close",
        headers=auth_header(auth_tokens, "admin")
    )
    
    assert response.status_code == 200
    assert response.json()["success"] is True

@pytest.mark.asyncio
async def test_close_return_route_not_found(client, auth_tokens):
    
    response = client.patch(
        BASE_URL + "/returns/999/close",
        headers=auth_header(auth_tokens, "admin")
    )
    
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_reimburse_return_route(client, auth_tokens):
    
    response = client.patch(
        BASE_URL + "/returns/1/reimburse",
        headers=auth_header(auth_tokens, "admin")
    )
    
    assert response.status_code == 200
    assert response.json()["refund_amount"] == 5.0

@pytest.mark.asyncio
async def test_reimburse_return_route_not_found(client, auth_tokens):
    
    response = client.patch(
        BASE_URL + "/returns/999/reimburse",
        headers=auth_header(auth_tokens, "admin")
    )
    
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_return_route(client, auth_tokens):
    
    response = client.delete(
        BASE_URL + "/returns/2",
        headers=auth_header(auth_tokens, "admin")
    )
    
    assert response.status_code == 204

@pytest.mark.asyncio
async def test_delete_return_route_not_found(client, auth_tokens):
    
    response = client.delete(
        BASE_URL + "/returns/2",
        headers=auth_header(auth_tokens, "admin")
    )
    
    assert response.status_code == 404