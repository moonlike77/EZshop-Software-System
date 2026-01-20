import pytest
from app.controllers.customer_controller import CustomerController
from app.controllers.loyalty_card_controller import LoyaltyCardController
from app.models.errors.notfound_error import NotFoundError
from app.models.errors.conflict_error import ConflictError
from app.models.DTO.customer_dto import CustomerDTO
from app.models.DTO.loyalty_card_dto import LoyaltyCardDTO
from app.database.database import AsyncSessionLocal, init_db, reset_db

@pytest.mark.asyncio
async def test_create_customer_without_card():
    await reset_db()
    await init_db()

    async with AsyncSessionLocal() as session:
        
        controller = CustomerController()
        controller.repo._session = session

        input_dto = CustomerDTO(name="Mario Rossi")

        result = await controller.create_customer(input_dto)

        assert isinstance(result, CustomerDTO)
        assert result.name == "Mario Rossi"
        assert result.id is not None

        catch = await controller.repo.get_customer(result.id)

        assert catch is not None
        assert catch.id == result.id
        assert catch.name == result.name

@pytest.mark.asyncio
async def test_create_loyalty_card():
    await reset_db()
    await init_db()

    async with AsyncSessionLocal() as session:
        
        controller = LoyaltyCardController()
        controller.repo._session = session

        result = await controller.create_loyalty_card()

        assert isinstance(result, LoyaltyCardDTO)
        assert result.card_id == "0000000001"
        assert result.points == 0

        catch = await controller.repo.get_loyalty_card(result.card_id)

        assert catch is not None
        assert catch.card_id == 1

@pytest.mark.asyncio
async def test_create_customer_with_card():
    await reset_db()
    await init_db()

    async with AsyncSessionLocal() as session:
        
        controller = CustomerController()
        card_controller = LoyaltyCardController()
        card_controller.repo._session = session
        controller.repo._session = session
        controller.card_repo._session = session

        await card_controller.create_loyalty_card()

        input_dto = CustomerDTO(name="Mario Rossi", card=LoyaltyCardDTO(card_id="0000000001", points=0))

        result = await controller.create_customer(input_dto)

        assert isinstance(result, CustomerDTO)
        assert result.name == "Mario Rossi"
        assert result.card.card_id == "0000000001"

@pytest.mark.asyncio
async def test_get_customer():
    await reset_db()
    await init_db()

    async with AsyncSessionLocal() as session:
        
        controller = CustomerController()
        controller.repo._session = session

        input_dto = CustomerDTO(name="Mario Rossi")

        await controller.create_customer(input_dto)

        result = await controller.get_customer(1)

        assert result.name == "Mario Rossi"

@pytest.mark.asyncio
async def test_get_loyalty_card():
    await reset_db()
    await init_db()

    async with AsyncSessionLocal() as session:
        
        controller = LoyaltyCardController()
        controller.repo._session = session

        await controller.create_loyalty_card()

        result = await controller.get_loyalty_card(1)

        assert result.card_id == "0000000001"

@pytest.mark.asyncio
async def test_get_loyalty_card_not_found():
    await reset_db()
    await init_db()

    async with AsyncSessionLocal() as session:
        
        controller = LoyaltyCardController()
        controller.repo._session = session

        with pytest.raises(NotFoundError):
            await controller.get_loyalty_card(1)

@pytest.mark.asyncio
async def test_get_customer_not_found():
    await reset_db()
    await init_db()

    async with AsyncSessionLocal() as session:
        
        controller = CustomerController()
        controller.repo._session = session

        with pytest.raises(NotFoundError):
            await controller.get_customer(1)

@pytest.mark.asyncio
async def test_list_customers():
    await reset_db()
    await init_db()

    async with AsyncSessionLocal() as session:
        
        controller = CustomerController()
        controller.repo._session = session

        input1_dto = CustomerDTO(name="Mario Rossi")
        input2_dto = CustomerDTO(name="Luigi Bianchi")

        await controller.create_customer(input1_dto)
        await controller.create_customer(input2_dto)

        result = await controller.list_customers()

        assert result[0].name == "Mario Rossi"
        assert result[1].name == "Luigi Bianchi"

@pytest.mark.asyncio
async def test_list_customers_empty():
    await reset_db()
    await init_db()

    async with AsyncSessionLocal() as session:
        
        controller = CustomerController()
        controller.repo._session = session

        result = await controller.list_customers()

        assert len(result) == 0

@pytest.mark.asyncio
async def test_update_loyalty_card_points():
    await reset_db()
    await init_db()

    async with AsyncSessionLocal() as session:
        
        controller = LoyaltyCardController()
        controller.repo._session = session

        await controller.create_loyalty_card()

        result = await controller.update_loyalty_card_points(1, 30)

        assert result.points == 30

@pytest.mark.asyncio
async def test_update_loyalty_card_points_not_found():
    await reset_db()
    await init_db()

    async with AsyncSessionLocal() as session:
        
        controller = LoyaltyCardController()
        controller.repo._session = session

        with pytest.raises(NotFoundError):
            await controller.update_loyalty_card_points(1, 30)

@pytest.mark.asyncio
async def test_update_customer_name_and_card_fixed():
    await reset_db()
    await init_db()

    controller = CustomerController()
    card_controller = LoyaltyCardController()

    await card_controller.create_loyalty_card()
    await card_controller.create_loyalty_card()

    input_dto = CustomerDTO(name="Mario Rossi", card=LoyaltyCardDTO(card_id="0000000001", points=0))
    await controller.create_customer(input_dto)

    new_input_dto = CustomerDTO(name="Mario Bianchi", card=LoyaltyCardDTO(card_id="0000000002", points=0))
    
    result = await controller.update_customer(1, new_input_dto)

    assert result.name == "Mario Bianchi"
    assert result.card.card_id == "0000000002"

    async with AsyncSessionLocal() as session:
        from app.models.DAO.customer_dao import CustomerDAO
        from sqlalchemy.orm import selectinload
        from sqlalchemy import select

        stmt = (select(CustomerDAO)
                .filter(CustomerDAO.id == 1)
                .options(selectinload(CustomerDAO.card)))
        
        db_res = await session.execute(stmt)
        db_customer = db_res.scalar_one_or_none()
        
        assert db_customer.name == "Mario Bianchi"
        assert db_customer.card.card_id == 2

@pytest.mark.asyncio
async def test_update_customer_name_and_card_customer_not_found():
    await reset_db()
    await init_db()

    async with AsyncSessionLocal() as session:
        
        controller = CustomerController()
        card_controller = LoyaltyCardController()
        card_controller.repo._session = session
        controller.repo._session = session
        controller.card_repo._session = session

        await card_controller.create_loyalty_card()
        await card_controller.create_loyalty_card()

        input_dto = CustomerDTO(name="Mario Bianchi", card=LoyaltyCardDTO(card_id="0000000002", points=0))
        with pytest.raises(NotFoundError):
            await controller.update_customer(999, input_dto)

@pytest.mark.asyncio
async def test_update_customer_delete_card():
    await reset_db()
    await init_db()

    async with AsyncSessionLocal() as session:
        
        controller = CustomerController()
        card_controller = LoyaltyCardController()
        card_controller.repo._session = session
        controller.repo._session = session
        controller.card_repo._session = session

        await card_controller.create_loyalty_card()

        input_dto = CustomerDTO(name="Mario Rossi", card=LoyaltyCardDTO(card_id="0000000001", points=0))

        await controller.create_customer(input_dto)

        input_dto = CustomerDTO(name="", card=None)
        result = await controller.update_customer(1, input_dto)

        assert result.name == "Mario Rossi"
        assert result.card is None

@pytest.mark.asyncio
async def test_attach_loyalty_card_to_customer():
    await reset_db()
    await init_db()

    async with AsyncSessionLocal() as session:
        
        controller = CustomerController()
        card_controller = LoyaltyCardController()
        card_controller.repo._session = session
        controller.repo._session = session
        controller.card_repo._session = session

        await card_controller.create_loyalty_card()

        input_dto = CustomerDTO(name="Mario Rossi", card=None)

        await controller.create_customer(input_dto)

        result = await controller.attach_loyalty_card_to_customer(1, "0000000001")

        assert result.card.card_id == "0000000001"

@pytest.mark.asyncio
async def test_attach_loyalty_card_to_customer_customer_not_found():
    await reset_db()
    await init_db()

    async with AsyncSessionLocal() as session:
        
        controller = CustomerController()
        card_controller = LoyaltyCardController()
        card_controller.repo._session = session
        controller.repo._session = session
        controller.card_repo._session = session

        await card_controller.create_loyalty_card()

        with pytest.raises(NotFoundError):
            await controller.attach_loyalty_card_to_customer(1, "0000000001")

@pytest.mark.asyncio
async def test_delete_customer():
    await reset_db()
    await init_db()

    async with AsyncSessionLocal() as session:
        
        controller = CustomerController()
        controller.repo._session = session

        input_dto = CustomerDTO(name="Mario Rossi")

        await controller.create_customer(input_dto)

        result = await controller.delete_customer(1)

        assert result == True

@pytest.mark.asyncio
async def test_delete_customer_not_found():
    await reset_db()
    await init_db()

    async with AsyncSessionLocal() as session:
        
        controller = CustomerController()
        controller.repo._session = session
        with pytest.raises(NotFoundError):
            await controller.delete_customer(1)

@pytest.mark.asyncio
async def test_delete_loyalty_card():
    await reset_db()
    await init_db()

    async with AsyncSessionLocal() as session:
        
        controller = LoyaltyCardController()
        controller.repo._session = session

        await controller.create_loyalty_card()

        result = await controller.delete_loyalty_card(1)

        assert result == True

@pytest.mark.asyncio
async def test_delete_loyalty_card_not_found():
    await reset_db()
    await init_db()

    async with AsyncSessionLocal() as session:
        
        controller = LoyaltyCardController()
        controller.repo._session = session

        with pytest.raises(NotFoundError):
            await controller.delete_loyalty_card(1)
