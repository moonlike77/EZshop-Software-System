import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.customer_repository import CustomerRepository
from app.repositories.loyalty_card_repository import LoyaltyCardRepository
from app.models.DAO.customer_dao import CustomerDAO
from app.models.DAO.loyalty_card_dao import LoyaltyCardDAO
from app.models.errors.notfound_error import NotFoundError
from app.models.errors.conflict_error import ConflictError
from app.models.errors.internal_server_error import InternalServerError
from init_db import reset, init_db

@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    await reset()
    await init_db()

@pytest.fixture()
def customer_repository():
    return CustomerRepository()

@pytest.fixture()
def card_repository():
    return LoyaltyCardRepository()

@pytest.mark.asyncio
async def test_create_customer_success(customer_repository):
    new_customer = await customer_repository.create_customer("Mario Rossi")
    assert new_customer.id is not None
    assert new_customer.name == "Mario Rossi"

@pytest.mark.asyncio
async def test_create_loyalty_card_success(card_repository):
    new_card = await card_repository.create_loyalty_card()
    assert new_card.card_id is not None
    assert new_card.points == 0

@pytest.mark.asyncio
async def test_create_customer_conflict(customer_repository):
    await customer_repository.create_customer("Mario Rossi")
    with pytest.raises(ConflictError):
        await customer_repository.create_customer("Mario Rossi")

@pytest.mark.asyncio
async def test_get_customer_success(customer_repository):
    new_customer = await customer_repository.create_customer("Mario Rossi")
    assert new_customer.id is not None
    assert new_customer.name == "Mario Rossi"
    retrieved = await customer_repository.get_customer(new_customer.id)
    assert retrieved.name == "Mario Rossi"

@pytest.mark.asyncio
async def test_get_loyalty_card_success(card_repository):
    new_card = await card_repository.create_loyalty_card()
    assert new_card.card_id is not None
    assert new_card.points == 0
    retrieved = await card_repository.get_loyalty_card(1)
    assert retrieved.card_id == 1

@pytest.mark.asyncio
async def test_get_customer_not_found(customer_repository):
    with pytest.raises(NotFoundError):
        await customer_repository.get_customer(999)

@pytest.mark.asyncio
async def test_get_loyalty_card_not_found(card_repository):
    with pytest.raises(NotFoundError):
        await card_repository.get_loyalty_card(999)

@pytest.mark.asyncio
async def test_list_customers_empty(customer_repository):
    customers = await customer_repository.list_customers()
    assert len(customers) == 0

@pytest.mark.asyncio
async def test_list_customers_success(customer_repository):
    await customer_repository.create_customer("Mario Rossi")
    await customer_repository.create_customer("Luca Bianchi")
    customers = await customer_repository.list_customers()
    names = [c.name for c in customers]
    assert "Mario Rossi" in names
    assert "Luca Bianchi" in names

@pytest.mark.asyncio
async def test_update_loyalty_card_points_success(card_repository):
    await card_repository.create_loyalty_card()
    card = await card_repository.get_loyalty_card(1)
    points_before = card.points
    card = await card_repository.update_loyalty_card_points(1, 50)
    points_after = card.points
    assert points_after-points_before == 50

@pytest.mark.asyncio
async def test_update_loyalty_card_points_not_enough_points(card_repository):
    await card_repository.create_loyalty_card()
    with pytest.raises(InternalServerError):
        await card_repository.update_loyalty_card_points(1, -50)

@pytest.mark.asyncio
async def test_update_loyalty_card_points_not_found(card_repository):
    with pytest.raises(NotFoundError):
        await card_repository.update_loyalty_card_points(999, 50)

@pytest.mark.asyncio
async def test_update_customer_card_success(customer_repository, card_repository):
    await customer_repository.create_customer("Mario Rossi")
    card = await card_repository.create_loyalty_card()
    attached = await customer_repository.update_customer_card(1, 1)
    assert attached.card.card_id == card.card_id

@pytest.mark.asyncio
async def test_update_customer_card_customer_not_found(customer_repository, card_repository):
    await card_repository.create_loyalty_card()
    with pytest.raises(NotFoundError):
        await customer_repository.update_customer_card(999, 1)

@pytest.mark.asyncio
async def test_update_customer_card_loyalty_card_not_found(customer_repository, card_repository):
    await customer_repository.create_customer("Mario Rossi")
    with pytest.raises(NotFoundError):
        await customer_repository.update_customer_card(1, 999)

@pytest.mark.asyncio
async def test_update_customer_card_already_attached_to_him(customer_repository, card_repository):
    await customer_repository.create_customer("Mario Rossi")
    card = await card_repository.create_loyalty_card()
    attached = await customer_repository.update_customer_card(1, 1)
    assert attached.card.card_id == card.card_id
    with pytest.raises(ConflictError):
        await customer_repository.update_customer_card(1, 1)

@pytest.mark.asyncio
async def test_update_customer_card_already_attached_to_other(customer_repository, card_repository):
    await customer_repository.create_customer("Mario Rossi")
    await customer_repository.create_customer("Luca Bianchi")
    card = await card_repository.create_loyalty_card()
    attached = await customer_repository.update_customer_card(1, 1)
    assert attached.card.card_id == card.card_id
    with pytest.raises(ConflictError):
        await customer_repository.update_customer_card(2, 1)

@pytest.mark.asyncio
async def test_update_customer_only_name_success(customer_repository):
    await customer_repository.create_customer("Mario Rossi")
    new_name = await customer_repository.update_customer(1, "Luca Bianchi", None)
    assert new_name.name == "Luca Bianchi"

@pytest.mark.asyncio
async def test_update_customer_only_name_not_found(customer_repository):
    with pytest.raises(NotFoundError):
        await customer_repository.update_customer(999, "Mario Rossi", 1)

@pytest.mark.asyncio
async def test_update_customer_only_name_conlfict_on_name(customer_repository):
    await customer_repository.create_customer("Mario Rossi")
    await customer_repository.create_customer("Luca Bianchi")
    with pytest.raises(ConflictError):
        await customer_repository.update_customer(1, "Luca Bianchi", None)

@pytest.mark.asyncio
async def test_update_customer_only_card_success(customer_repository, card_repository):
    await customer_repository.create_customer("Mario Rossi")
    await card_repository.create_loyalty_card()
    card2 = await card_repository.create_loyalty_card()
    await customer_repository.update_customer_card(1, 1)
    result = await customer_repository.update_customer(1, "Mario Rossi", 2)
    assert result.card.card_id == card2.card_id

@pytest.mark.asyncio
async def test_update_customer_detach_card_success(customer_repository, card_repository):
    await customer_repository.create_customer("Mario Rossi")
    await card_repository.create_loyalty_card()
    await customer_repository.update_customer_card(1, 1)
    result = await customer_repository.update_customer(1, "", None)
    assert result.card == None

@pytest.mark.asyncio
async def test_delete_customer_success(customer_repository):
    await customer_repository.create_customer("Mario Rossi")
    customer = await customer_repository.get_customer(1)
    assert customer.name == "Mario Rossi"
    await customer_repository.delete_customer(1)
    with pytest.raises(NotFoundError):
        await customer_repository.get_customer(1)

@pytest.mark.asyncio
async def test_delete_loyalty_card_success(card_repository):
    await card_repository.create_loyalty_card()
    card = await card_repository.get_loyalty_card(1)
    assert card.card_id == 1
    await card_repository.delete_loyalty_card(1)
    with pytest.raises(NotFoundError):
        await card_repository.get_loyalty_card(1)

@pytest.mark.asyncio
async def test_delete_customer_not_found(customer_repository):
    with pytest.raises(NotFoundError):
        await customer_repository.delete_customer(999)

@pytest.mark.asyncio
async def test_delete_loyalty_card_not_found(card_repository):
    with pytest.raises(NotFoundError):
        await card_repository.delete_loyalty_card(999)