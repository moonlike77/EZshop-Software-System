import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from app.controllers.customer_controller import CustomerController
from app.models.DTO.customer_dto import CustomerDTO
from app.models.DTO.loyalty_card_dto import LoyaltyCardDTO

@pytest.mark.asyncio
async def test_create_customer():
    mock_repo_inst = MagicMock()
    mock_repo_inst.create_customer = AsyncMock()

    with patch('app.controllers.customer_controller.CustomerRepository', return_value=mock_repo_inst), \
         patch('app.controllers.customer_controller.LoyaltyCardRepository', return_value=MagicMock()):
        
        controller = CustomerController()

        input_dto = CustomerDTO(name="Mario Rossi")

        cust = MagicMock()
        cust.id = 1
        cust.name = "Mario Rossi"
        cust.card = None

        mock_repo_inst.create_customer.return_value = cust
        result = await controller.create_customer(input_dto)
        mock_repo_inst.create_customer.assert_called_once_with("Mario Rossi")

        assert isinstance(result, CustomerDTO)
        assert result.name == "Mario Rossi"

@pytest.mark.asyncio
async def test_get_customer():
    mock_repo_inst = MagicMock()
    mock_repo_inst.get_customer = AsyncMock()

    with patch('app.controllers.customer_controller.CustomerRepository', return_value=mock_repo_inst), \
         patch('app.controllers.customer_controller.LoyaltyCardRepository', return_value=MagicMock()):
        
        controller = CustomerController()

        cust = MagicMock()
        cust.id = 1
        cust.name = "Mario Rossi"
        cust.card = None

        mock_repo_inst.get_customer.return_value = cust
        result = await controller.get_customer(1)
        mock_repo_inst.get_customer.assert_called_once_with(1)

        assert result.name == "Mario Rossi"

@pytest.mark.asyncio
async def test_get_customer_not_found():
    mock_repo_inst = MagicMock()
    mock_repo_inst.get_customer = AsyncMock()

    with patch('app.controllers.customer_controller.CustomerRepository', return_value=mock_repo_inst), \
         patch('app.controllers.customer_controller.LoyaltyCardRepository', return_value=MagicMock()):
        
        controller = CustomerController()

        mock_repo_inst.get_customer.return_value = None
        result = await controller.get_customer(1)
        mock_repo_inst.get_customer.assert_called_once_with(1)

        assert result is None

@pytest.mark.asyncio
async def test_list_customers():
    mock_repo_inst = MagicMock()
    mock_repo_inst.list_customers = AsyncMock()

    with patch('app.controllers.customer_controller.CustomerRepository', return_value=mock_repo_inst), \
         patch('app.controllers.customer_controller.LoyaltyCardRepository', return_value=MagicMock()):
        
        controller = CustomerController()

        cust1 = MagicMock()
        cust1.id = 1
        cust1.name = "Mario Rossi"
        cust1.card = None

        cust2 = MagicMock()
        cust2.id = 2
        cust2.name = "Luca Bianchi"
        cust2.card = None

        expected_customers = [cust1, cust2]

        mock_repo_inst.list_customers.return_value = expected_customers
        result = await controller.list_customers()
        mock_repo_inst.list_customers.assert_called_once()

        assert result[0].name == expected_customers[0].name
        assert result[1].name == expected_customers[1].name

@pytest.mark.asyncio
async def test_list_customers_empty():
    mock_repo_inst = MagicMock()
    mock_repo_inst.list_customers = AsyncMock()

    with patch('app.controllers.customer_controller.CustomerRepository', return_value=mock_repo_inst), \
         patch('app.controllers.customer_controller.LoyaltyCardRepository', return_value=MagicMock()):
        
        controller = CustomerController()

        expected_customers = []

        mock_repo_inst.list_customers.return_value = expected_customers
        result = await controller.list_customers()
        mock_repo_inst.list_customers.assert_called_once()

        assert len(result) == 0

@pytest.mark.asyncio
async def test_update_customer_name_and_card():
    mock_cust_repo = MagicMock()
    mock_card_repo = MagicMock()
    
    mock_cust_repo.get_customer = AsyncMock()
    mock_cust_repo.update_customer = AsyncMock()
    mock_card_repo.get_loyalty_card = AsyncMock()

    with patch('app.controllers.customer_controller.CustomerRepository', return_value=mock_cust_repo), \
         patch('app.controllers.customer_controller.LoyaltyCardRepository', return_value=mock_card_repo):
        
        controller = CustomerController()

        old_card = MagicMock()
        old_card.card_id = 1
        old_card.points = 0
        
        old_cust = MagicMock()
        old_cust.id = 1
        old_cust.name = "Mario Rossi"
        old_cust.card = old_card
        mock_cust_repo.get_customer.return_value = old_cust

        new_card = MagicMock()
        new_card.card_id = 2
        new_card.points = 0
        mock_card_repo.get_loyalty_card.return_value = new_card

        new_cust = MagicMock()
        new_cust.id = 1
        new_cust.name = "Mario Bianchi"
        new_cust.card = new_card
        mock_cust_repo.update_customer.return_value = new_cust

        input_dto = CustomerDTO(name="Mario Bianchi", card=LoyaltyCardDTO(card_id="0000000002", points=0))
        result = await controller.update_customer(1, input_dto)
        mock_cust_repo.get_customer.assert_called_once_with(1)
        mock_card_repo.get_loyalty_card.assert_called_once_with(2)
        mock_cust_repo.update_customer.assert_called_with(1, "Mario Bianchi", 2)

        assert result.name == "Mario Bianchi"
        assert result.card.card_id == "0000000002"

@pytest.mark.asyncio
async def test_update_customer_name_and_card_customer_not_found():
    mock_cust_repo = MagicMock()
    mock_card_repo = MagicMock()
    
    mock_cust_repo.get_customer = AsyncMock()
    mock_cust_repo.update_customer = AsyncMock()
    mock_card_repo.get_loyalty_card = AsyncMock()

    with patch('app.controllers.customer_controller.CustomerRepository', return_value=mock_cust_repo), \
         patch('app.controllers.customer_controller.LoyaltyCardRepository', return_value=mock_card_repo):
        
        controller = CustomerController()

        old_card = MagicMock()
        old_card.card_id = 1
        old_card.points = 0
        
        old_cust = MagicMock()
        old_cust.id = 1
        old_cust.name = "Mario Rossi"
        old_cust.card = old_card
        mock_cust_repo.get_customer.return_value = old_cust

        new_card = MagicMock()
        new_card.card_id = 2
        new_card.points = 0
        mock_card_repo.get_loyalty_card.return_value = new_card

        new_cust = MagicMock()
        new_cust.id = 1
        new_cust.name = "Mario Bianchi"
        new_cust.card = new_card
        mock_cust_repo.update_customer.return_value = None

        input_dto = CustomerDTO(name="Mario Bianchi", card=LoyaltyCardDTO(card_id="0000000002", points=0))
        result = await controller.update_customer(999, input_dto)
        mock_cust_repo.get_customer.assert_called_once_with(999)
        mock_card_repo.get_loyalty_card.assert_called_once_with(2)
        mock_cust_repo.update_customer.assert_called_with(999, "Mario Bianchi", 2)

        assert result is None

@pytest.mark.asyncio
async def test_update_customer_delete_card():
    mock_cust_repo = MagicMock()
    mock_card_repo = MagicMock()
    
    mock_cust_repo.get_customer = AsyncMock()
    mock_cust_repo.update_customer = AsyncMock()
    mock_card_repo.delete_loyalty_card = AsyncMock()

    with patch('app.controllers.customer_controller.CustomerRepository', return_value=mock_cust_repo), \
         patch('app.controllers.customer_controller.LoyaltyCardRepository', return_value=mock_card_repo):
        
        controller = CustomerController()

        old_card = MagicMock()
        old_card.card_id = 1
        old_card.points = 0
        
        old_cust = MagicMock()
        old_cust.id = 1
        old_cust.name = "Mario Rossi"
        old_cust.card = old_card
        mock_cust_repo.get_customer.return_value = old_cust

        new_cust = MagicMock()
        new_cust.id = 1
        new_cust.name = "Mario Rossi"
        new_cust.card = None
        mock_cust_repo.update_customer.return_value = new_cust

        input_dto = CustomerDTO(name="", card=None)
        result = await controller.update_customer(1, input_dto)
        mock_cust_repo.get_customer.assert_called_once_with(1)
        mock_card_repo.delete_loyalty_card.assert_called_once_with(1)
        mock_cust_repo.update_customer.assert_called_with(1, "", None)

        assert result.name == "Mario Rossi"
        assert result.card is None

@pytest.mark.asyncio
async def test_attach_loyalty_card_to_customer():
    mock_cust_repo = MagicMock()
    mock_card_repo = MagicMock()
    
    mock_cust_repo.update_customer_card = AsyncMock()
    mock_card_repo.get_loyalty_card = AsyncMock()

    with patch('app.controllers.customer_controller.CustomerRepository', return_value=mock_cust_repo), \
         patch('app.controllers.customer_controller.LoyaltyCardRepository', return_value=mock_card_repo):
        
        controller = CustomerController()

        card = MagicMock()
        card.card_id = 1
        card.points = 0
        mock_card_repo.get_loyalty_card.return_value = card

        cust = MagicMock()
        cust.id = 1
        cust.name = "Mario Rossi"
        cust.card = card
        mock_cust_repo.update_customer_card.return_value = cust

        result = await controller.attach_loyality_card_to_customer(1, "0000000001")
        mock_card_repo.get_loyalty_card.assert_called_once_with(1)
        mock_cust_repo.update_customer_card.assert_called_once_with(1, 1)

        assert result.card.card_id == "0000000001"

@pytest.mark.asyncio
async def test_attach_loyalty_card_to_customer_customer_not_found():
    mock_cust_repo = MagicMock()
    mock_card_repo = MagicMock()
    
    mock_cust_repo.update_customer_card = AsyncMock()
    mock_card_repo.get_loyalty_card = AsyncMock()

    with patch('app.controllers.customer_controller.CustomerRepository', return_value=mock_cust_repo), \
         patch('app.controllers.customer_controller.LoyaltyCardRepository', return_value=mock_card_repo):
        
        controller = CustomerController()

        card = MagicMock()
        card.card_id = 1
        card.points = 0
        mock_card_repo.get_loyalty_card.return_value = card

        cust = MagicMock()
        cust.id = 1
        cust.name = "Mario Rossi"
        cust.card = card
        mock_cust_repo.update_customer_card.return_value = None

        result = await controller.attach_loyality_card_to_customer(1, "0000000001")
        mock_card_repo.get_loyalty_card.assert_called_once_with(1)
        mock_cust_repo.update_customer_card.assert_called_once_with(1, 1)

        assert result is None

@pytest.mark.asyncio
async def test_delete_customer():
    mock_cust_repo = MagicMock()
    mock_card_repo = MagicMock()

    mock_cust_repo.delete_customer = AsyncMock()

    with patch('app.controllers.customer_controller.CustomerRepository', return_value=mock_cust_repo), \
         patch('app.controllers.customer_controller.LoyaltyCardRepository', return_value=mock_card_repo):
        
        controller = CustomerController()

    mock_cust_repo.delete_customer.return_value = True
    result = await controller.delete_customer(1)
    mock_cust_repo.delete_customer.assert_called_once_with(1)

    assert result == True