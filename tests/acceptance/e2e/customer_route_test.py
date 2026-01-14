import pytest
import asyncio
from init_db import reset, init_db
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi.testclient import TestClient
from main import app
from app.models.DTO.customer_dto import CustomerDTO
from app.models.DTO.loyalty_card_dto import LoyaltyCardDTO
from app.models.errors.conflict_error import ConflictError
from app.models.errors.notfound_error import NotFoundError

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

def auth_header(tokens, role: str):
    return {"Authorization": tokens[role]}

BASE_URL = "http://127.0.0.1:8000/api/v1"

@pytest.mark.asyncio
async def test_create_customer_success(client, auth_tokens):

    mock_controller = MagicMock()
    mock_controller.create_customer = AsyncMock()

    cust = CustomerDTO(id=1, name="Mario Rossi", card=None)
    mock_controller.create_customer.return_value = cust

    with patch('app.routes.customer_route.controller', mock_controller):

        payload = {"name": "Mario Rossi"}
        resp = client.post(BASE_URL + "/customers", json=payload, headers=auth_header(auth_tokens, "admin"))

        assert resp.status_code == 201
        assert resp.json()["name"] == "Mario Rossi"
        mock_controller.create_customer.assert_called_once()

@pytest.mark.asyncio
async def test_create_customer_bad_request(client, auth_tokens):
    
    payload = {"name": ""}
    resp = client.post(BASE_URL + "/customers", json=payload, headers=auth_header(auth_tokens, "admin"))
    
    assert resp.status_code == 400

@pytest.mark.asyncio
async def test_get_all_customers_success(client, auth_tokens):

    mock_controller = MagicMock()
    mock_controller.list_customers = AsyncMock()

    cust1 = CustomerDTO(id=1, name="Mario Rossi", card=None)
    cust2 = CustomerDTO(id=2, name="Luca Bianchi", card=None)
    mock_controller.list_customers.return_value = [cust1, cust2]

    with patch('app.routes.customer_route.controller', mock_controller):

        resp = client.get(BASE_URL + "/customers", headers=auth_header(auth_tokens, "admin"))

        assert resp.status_code == 200
        assert resp.json()[0]["name"] == "Mario Rossi"
        assert resp.json()[1]["name"] == "Luca Bianchi"
        mock_controller.list_customers.assert_called_once()

@pytest.mark.asyncio
async def test_get_customer_success(client, auth_tokens):

    mock_controller = MagicMock()
    mock_controller.get_customer = AsyncMock()

    cust = CustomerDTO(id=1, name="Mario Rossi", card=None)
    mock_controller.get_customer.return_value = cust

    with patch('app.routes.customer_route.controller', mock_controller):

        resp = client.get(BASE_URL + "/customers/1", headers=auth_header(auth_tokens, "admin"))

        assert resp.status_code == 200
        assert resp.json()["name"] == "Mario Rossi"
        mock_controller.get_customer.assert_called_once_with(1)
        
@pytest.mark.asyncio
async def test_get_customer_invalid_id(client, auth_tokens):

    mock_controller = MagicMock()
    mock_controller.get_customer = AsyncMock()

    cust = CustomerDTO(id=1, name="Mario Rossi", card=None)
    mock_controller.get_customer.return_value = cust

    with patch('app.routes.customer_route.controller', mock_controller):

        resp = client.get(BASE_URL + "/customers/-1", headers=auth_header(auth_tokens, "admin"))

        assert resp.status_code == 400

@pytest.mark.asyncio
async def test_get_customer_not_found(client, auth_tokens):

    mock_controller = MagicMock()
    mock_controller.get_customer = AsyncMock()

    mock_controller.get_customer.return_value = None

    with patch('app.routes.customer_route.controller', mock_controller):

        resp = client.get(BASE_URL + "/customers/999", headers=auth_header(auth_tokens, "admin"))

        assert resp.status_code == 404
        mock_controller.get_customer.assert_called_once_with(999)

@pytest.mark.asyncio
async def test_update_customer_success(client, auth_tokens):

    mock_controller = MagicMock()
    mock_controller.update_customer = AsyncMock()

    cust = CustomerDTO(id=1, name="Mario Rossi", card=None)
    mock_controller.update_customer.return_value = cust

    with patch('app.routes.customer_route.controller', mock_controller):

        payload = {"name": "Mario Rossi", "card": None}
        resp = client.put(BASE_URL + "/customers/1", json=payload, headers=auth_header(auth_tokens, "admin"))

        assert resp.status_code == 201
        assert resp.json()["name"] == "Mario Rossi"
        mock_controller.update_customer.assert_called_once()

@pytest.mark.asyncio
async def test_update_customer_invalid_id(client, auth_tokens):

    mock_controller = MagicMock()
    mock_controller.update_customer = AsyncMock()

    cust = CustomerDTO(id=1, name="Mario Rossi", card=None)
    mock_controller.update_customer.return_value = cust

    with patch('app.routes.customer_route.controller', mock_controller):

        payload = {"name": "Mario Rossi", "card": None}
        resp = client.put(BASE_URL + "/customers/-1", json=payload, headers=auth_header(auth_tokens, "admin"))

        assert resp.status_code == 400

@pytest.mark.asyncio
async def test_update_customer_invalid_payload(client, auth_tokens):

    mock_controller = MagicMock()
    mock_controller.update_customer = AsyncMock()

    cust = CustomerDTO(id=1, name="Mario Rossi", card=None)
    mock_controller.update_customer.return_value = cust

    with patch('app.routes.customer_route.controller', mock_controller):

        payload = {"name": "", "card": None}
        resp = client.put(BASE_URL + "/customers/1", json=payload, headers=auth_header(auth_tokens, "admin"))

        assert resp.status_code == 400

@pytest.mark.asyncio
async def test_update_customer_not_found(client, auth_tokens):

    mock_controller = MagicMock()
    mock_controller.update_customer = AsyncMock()

    mock_controller.update_customer.return_value = None

    with patch('app.routes.customer_route.controller', mock_controller):

        payload = {"name": "Mario Rossi", "card": None}
        resp = client.put(BASE_URL + "/customers/1", json=payload, headers=auth_header(auth_tokens, "admin"))

        assert resp.status_code == 404
        mock_controller.update_customer.assert_called_once()

@pytest.mark.asyncio
async def test_delete_customer_success(client, auth_tokens):

    mock_controller = MagicMock()
    mock_controller.delete_customer = AsyncMock()

    mock_controller.delete_customer.return_value = True

    with patch('app.routes.customer_route.controller', mock_controller):

        resp = client.delete(BASE_URL + "/customers/1", headers=auth_header(auth_tokens, "admin"))

        assert resp.status_code == 204
        mock_controller.delete_customer.assert_called_once()

@pytest.mark.asyncio
async def test_delete_customer_not_found(client, auth_tokens):

    mock_controller = MagicMock()
    mock_controller.delete_customer = AsyncMock()

    mock_controller.delete_customer.return_value = None

    with patch('app.routes.customer_route.controller', mock_controller):

        resp = client.delete(BASE_URL + "/customers/1", headers=auth_header(auth_tokens, "admin"))

        assert resp.status_code == 404
        mock_controller.delete_customer.assert_called_once()

@pytest.mark.asyncio
async def test_create_loyalty_card_success(client, auth_tokens):

    mock_card_controller = MagicMock()
    mock_card_controller.create_loyalty_card = AsyncMock()

    card = LoyaltyCardDTO(card_id="0000000001", points=0)
    mock_card_controller.create_loyalty_card.return_value = card

    with patch('app.routes.customer_route.card_controller', mock_card_controller):

        resp = client.post(BASE_URL + "/customers/cards", headers=auth_header(auth_tokens, "admin"))

        assert resp.status_code == 201
        mock_card_controller.create_loyalty_card.assert_called_once()

@pytest.mark.asyncio
async def test_attach_loyalty_card_to_customer_success(client, auth_tokens):

    mock_controller = MagicMock()
    mock_controller.attach_loyalty_card_to_customer = AsyncMock()

    card = LoyaltyCardDTO(card_id="0000000001", points=0)
    cust = CustomerDTO(id=1, name="Mario Rossi", card=card)
    mock_controller.attach_loyalty_card_to_customer.return_value = cust

    with patch('app.routes.customer_route.controller', mock_controller):

        resp = client.patch(BASE_URL + "/customers/1/attach-card/0000000001", headers=auth_header(auth_tokens, "admin"))

        assert resp.status_code == 201
        assert resp.json()["card"]["card_id"] == "0000000001"
        mock_controller.attach_loyalty_card_to_customer.assert_called_once()

@pytest.mark.asyncio
async def test_attach_card_not_found_error(client, auth_tokens):
    mock_controller = MagicMock()
    mock_controller.attach_loyalty_card_to_customer = AsyncMock(
        side_effect=NotFoundError("Customer not found")
    )

    with patch('app.routes.customer_route.controller', mock_controller):

        resp = client.patch(f"{BASE_URL}/customers/999/attach-card/001", headers=auth_header(auth_tokens, "admin"))

        assert resp.status_code == 404

@pytest.mark.asyncio
async def test_attach_card_conflict_error(client, auth_tokens):
    mock_controller = MagicMock()

    mock_controller.attach_loyalty_card_to_customer = AsyncMock(
        side_effect=ConflictError("Card already attached")
    )

    with patch('app.routes.customer_route.controller', mock_controller):

        resp = client.patch(f"{BASE_URL}/customers/1/attach-card/001", headers=auth_header(auth_tokens, "admin"))

        assert resp.status_code == 409

@pytest.mark.asyncio
async def test_attach_card_return_none_logic(client, auth_tokens):
    mock_controller = MagicMock()

    mock_controller.attach_loyalty_card_to_customer = AsyncMock()
    mock_controller.attach_loyalty_card_to_customer.return_value = None

    with patch('app.routes.customer_route.controller', mock_controller):

        resp = client.patch(f"{BASE_URL}/customers/1/attach-card/001", headers=auth_header(auth_tokens, "admin"))

        assert resp.status_code == 409

@pytest.mark.asyncio
async def test_update_loyalty_card_points_success(client, auth_tokens):

    mock_card_controller = MagicMock()
    mock_card_controller.update_loyalty_card_points = AsyncMock()

    card = LoyaltyCardDTO(card_id="0000000001", points=30)
    mock_card_controller.update_loyalty_card_points.return_value = card

    with patch('app.routes.customer_route.card_controller', mock_card_controller):

        resp = client.patch(BASE_URL + "/customers/cards/1?points=30", headers=auth_header(auth_tokens, "admin"))

        assert resp.status_code == 201
        assert resp.json()["points"] == 30
        mock_card_controller.update_loyalty_card_points.assert_called_once()