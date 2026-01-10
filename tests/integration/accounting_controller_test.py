import pytest
import pytest_asyncio
from datetime import datetime, timedelta

from app.controllers.accounting_controller import AccountingController
from app.services.accounting_service import AccountingService
from app.models.DTO.transaction_dto import TransactionCreateDTO
from app.models.transaction_type import TransactionType
from app.repositories.transaction_repository import TransactionRepository
from init_db import reset, init_db as init_database

@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    """Initialize DB locally for integration tests (function scoped)."""
    await reset()
    await init_database()

# ---------------------------------------------------------------------
# CONTROLLER TESTS
# ---------------------------------------------------------------------

@pytest.mark.asyncio
async def test_validation_get_history_invalid_date_range():
    controller = AccountingController()
    start_date = datetime.now()
    end_date = start_date - timedelta(days=1)
    try:
        await controller.get_history(start_date, end_date)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert str(e) == "Start date cannot be after end date"

@pytest.mark.asyncio
async def test_controller_record_transaction_success():
    controller = AccountingController()
    dto = TransactionCreateDTO(
        amount=150.0,
        type=TransactionType.CREDIT,
        description="Direct controller test"
    )
    user_id = 1
    result = await controller.record_transaction(dto, user_id)
    assert result.amount == 150.0
    assert result.description == "Direct controller test"
    assert result.type == TransactionType.CREDIT

@pytest.mark.asyncio
async def test_controller_get_history_success():
    controller = AccountingController()
    await controller.set_balance(100.0, 1)
    start_date = datetime(2000, 1, 1)
    end_date = datetime(2099, 12, 31)
    history = await controller.get_history(start_date, end_date)
    assert isinstance(history, list)
    history_all = await controller.get_history(None, None)
    assert isinstance(history_all, list)

# ---------------------------------------------------------------------
# SERVICE TESTS
# ---------------------------------------------------------------------

@pytest.mark.asyncio
async def test_accounting_service_coverage():
    service = AccountingService()
    dto = TransactionCreateDTO(
        amount=75.0,
        type=TransactionType.DEBIT,
        description="Service test"
    )
    user_id = 1
    result = await service.record_transaction(dto, user_id)
    assert result.amount == 75.0
    assert result.description == "Service test"
    balance = await service.get_current_balance()
    assert isinstance(balance, float)
    history = await service.get_history(None, None)
    assert isinstance(history, list)
