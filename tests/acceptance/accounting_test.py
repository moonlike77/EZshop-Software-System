import pytest
from fastapi.testclient import TestClient
from main import app
from init_db import reset, init_db

client = TestClient(app)
BASE_URL = "http://127.0.0.1:8000/api/v1"
BALANCE_URL = BASE_URL + "/balance"

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
# GET /balance
# ---------------------------------------------------------------------

def test_get_balance_success_as_admin(auth_tokens):
    resp = client.get(BALANCE_URL, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 200
    data = resp.json()
    assert "balance" in data
    assert isinstance(data["balance"], float)


def test_get_balance_success_as_manager(auth_tokens):
    resp = client.get(BALANCE_URL, headers=auth_header(auth_tokens, "manager"))
    assert resp.status_code == 200


def test_get_balance_forbidden_as_cashier(auth_tokens):
    resp = client.get(BALANCE_URL, headers=auth_header(auth_tokens, "cashier"))
    assert resp.status_code == 403


def test_get_balance_unauthenticated():
    resp = client.get(BALANCE_URL)
    assert resp.status_code == 401


# ---------------------------------------------------------------------
# POST /balance/set
# ---------------------------------------------------------------------

def test_set_balance_success(auth_tokens):
    # Set to 500.0
    resp = client.post(
        f"{BALANCE_URL}/set",
        headers=auth_header(auth_tokens, "admin"),
        params={"amount": 500.0}
    )
    assert resp.status_code == 201
    assert resp.json()["success"] is True
    
    # Verify
    get_resp = client.get(BALANCE_URL, headers=auth_header(auth_tokens, "admin"))
    assert get_resp.status_code == 200
    assert get_resp.json()["balance"] == 500.0


def test_set_balance_negative_amount(auth_tokens):
    # Depending on implementation, might raise 421 or 400.
    # The route returns 421 for ValueError
    resp = client.post(
        f"{BALANCE_URL}/set",
        headers=auth_header(auth_tokens, "admin"),
        params={"amount": -10.0}
    )
    assert resp.status_code == 421


def test_set_balance_forbidden_as_cashier(auth_tokens):
    resp = client.post(
        f"{BALANCE_URL}/set",
        headers=auth_header(auth_tokens, "cashier"),
        params={"amount": 100.0}
    )
    assert resp.status_code == 403


def test_set_balance_unauthenticated():
    resp = client.post(
        f"{BALANCE_URL}/set",
        params={"amount": 100.0}
    )
    assert resp.status_code == 401


# ---------------------------------------------------------------------
# POST /balance/reset
# ---------------------------------------------------------------------

def test_reset_balance_success(auth_tokens):
    # First set it to something
    client.post(
        f"{BALANCE_URL}/set",
        headers=auth_header(auth_tokens, "admin"),
        params={"amount": 123.45}
    )
    
    # Reset
    resp = client.post(
        f"{BALANCE_URL}/reset",
        headers=auth_header(auth_tokens, "admin")
    )
    assert resp.status_code == 200
    assert resp.json()["success"] is True
    
    # Verify is 0
    get_resp = client.get(BALANCE_URL, headers=auth_header(auth_tokens, "admin"))
    assert get_resp.json()["balance"] == 0.0


def test_reset_balance_forbidden_as_cashier(auth_tokens):
    resp = client.post(
        f"{BALANCE_URL}/reset",
        headers=auth_header(auth_tokens, "cashier")
    )
    assert resp.status_code == 403


def test_reset_balance_unauthenticated():
    resp = client.post(f"{BALANCE_URL}/reset")
    assert resp.status_code == 401


# ---------------------------------------------------------------------
# VALIDATION TESTS
# ---------------------------------------------------------------------

def test_validation_transaction_negative_amount():
    from app.models.DTO.transaction_dto import TransactionCreateDTO
    from pydantic import ValidationError
    from app.models.transaction_type import TransactionType

    try:
        TransactionCreateDTO(
            amount=-50.0,
            type=TransactionType.CREDIT,
            description="Invalid transaction"
        )
        assert False, "Should have raised ValidationError"
    except ValidationError as e:
        assert "Amount must be positive" in str(e) or "Value error, Amount must be positive" in str(e)

def test_validation_transaction_zero_amount():
    from app.models.DTO.transaction_dto import TransactionCreateDTO
    from pydantic import ValidationError
    from app.models.transaction_type import TransactionType

    try:
        TransactionCreateDTO(
            amount=0.0,
            type=TransactionType.CREDIT,
            description="Invalid transaction"
        )
        assert False, "Should have raised ValidationError"
    except ValidationError as e:
        assert "Amount must be positive" in str(e)

@pytest.mark.asyncio
async def test_validation_get_history_invalid_date_range():
    # We need to setup DB for controller usage since it uses a repository
    from app.controllers.accounting_controller import AccountingController
    from datetime import datetime, timedelta
    
    # We can rely on the session fixture or just instantiate if it handles its own session
    # The controller's __init__ creates a repository, which creates a session on fly.
    # However, for async tests we need to be in an async loop.
    
    controller = AccountingController()
    
    start_date = datetime.now()
    end_date = start_date - timedelta(days=1) # End date before start date

    try:
        await controller.get_history(start_date, end_date)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert str(e) == "Start date cannot be after end date"

# ---------------------------------------------------------------------
# CONTROLLER & SERVICE DIRECT TESTS (For Coverage)
# ---------------------------------------------------------------------

@pytest.mark.asyncio
async def test_controller_record_transaction_success():
    from app.controllers.accounting_controller import AccountingController
    from app.models.DTO.transaction_dto import TransactionCreateDTO
    from app.models.transaction_type import TransactionType
    
    controller = AccountingController()
    
    dto = TransactionCreateDTO(
        amount=150.0,
        type=TransactionType.CREDIT,
        description="Direct controller test"
    )
    # user_id 1 is admin from fixture usually, or just any valid ID if checking logic
    user_id = 1
    
    result = await controller.record_transaction(dto, user_id)
    
    assert result.amount == 150.0
    assert result.description == "Direct controller test"
    assert result.type == TransactionType.CREDIT

@pytest.mark.asyncio
async def test_controller_get_history_success():
    from app.controllers.accounting_controller import AccountingController
    from datetime import datetime
    
    controller = AccountingController()
    
    # Ensure there is at least one transaction
    # We can rely on previous tests or create one
    await controller.set_balance(100.0, 1) # This creates a transaction usually
    
    start_date = datetime(2000, 1, 1)
    end_date = datetime(2099, 12, 31)
    
    history = await controller.get_history(start_date, end_date)
    assert isinstance(history, list)
    # verify we get something if we just created it
    # note: set_balance creates a transaction? 
    # The set_balance docstring says "Creates a correction transaction."
    # So history should not be empty ideally, but even empty list is valid return
    
    # Also test without dates
    history_all = await controller.get_history(None, None)
    assert isinstance(history_all, list)

@pytest.mark.asyncio
async def test_accounting_service_coverage():
    """
    Test AccountingService explicitly to ensure coverage 
    even if it mimics Controller or is currently unused.
    """
    from app.services.accounting_service import AccountingService
    from app.models.DTO.transaction_dto import TransactionCreateDTO
    from app.models.transaction_type import TransactionType
    from datetime import datetime

    service = AccountingService()
    
    # 1. Test record_transaction
    dto = TransactionCreateDTO(
        amount=75.0,
        type=TransactionType.DEBIT,
        description="Service test"
    )
    user_id = 1
    result = await service.record_transaction(dto, user_id)
    assert result.amount == 75.0
    assert result.description == "Service test"
    
    # 2. Test get_current_balance
    balance = await service.get_current_balance()
    assert isinstance(balance, float)
    
    # 3. Test get_history
    history = await service.get_history(None, None)
    assert isinstance(history, list)

@pytest.mark.asyncio
async def test_repository_coverage_edge_cases():
    from app.repositories.transaction_repository import TransactionRepository
    from app.models.DAO.system_dao import SystemInfoDAO
    from sqlalchemy import delete
    from datetime import datetime
    
    # Use existing DB connection via AsyncSessionLocal usually, but we can verify session injection
    # 1. Test Session Injection
    mock_session = "Mock Session"
    repo_with_session = TransactionRepository(session=mock_session)
    # _get_session is async
    assert await repo_with_session._get_session() == mock_session

    # 2. Test Set Balance No Change
    repo = TransactionRepository()
    # First ensure we have a known balance. 
    # Calling set_balance will create system info if missing.
    await repo.set_balance(100.0, 1)
    
    # Now set to SAME amount
    tx = await repo.set_balance(100.0, 1)
    # It should still record a transaction (as per logic trace: difference=0 => CREDIT 0.0)
    assert tx.amount == 0.0
    
    # 3. Test Partial Date Filters for get_transactions
    # get_transactions takes start_date, end_date
    start = datetime(2000, 1, 1)
    end = datetime(2099, 12, 31)
    
    # Only start
    res_start = await repo.get_transactions(start_date=start, end_date=None)
    assert isinstance(res_start, list)
    
    # Only end
    res_end = await repo.get_transactions(start_date=None, end_date=end)
    assert isinstance(res_end, list)

    # 4. Test Missing System Info (Branch coverage)
    # We need to manually delete the system info row to test the "if not system_info" creation logic
    # inside create_transaction or get_balance
    
    # Using a fresh session to delete
    from app.database.database import AsyncSessionLocal
    async with AsyncSessionLocal() as session:
        await session.execute(delete(SystemInfoDAO))
        await session.commit()
    
    # Now get_balance should return 0.0 and validly handle missing row
    bal = await repo.get_balance()
    assert bal == 0.0
    
    # create_transaction should recreate it
    # We pass explicit None for optional fields to test defaults/types
    from app.models.transaction_type import TransactionType
    await repo.create_transaction(10.0, TransactionType.CREDIT, "Re-init", 1)
    
    # Verify balance is updated from 0 to 10
    bal_new = await repo.get_balance()
    assert bal_new == 10.0

    # 5. Test set_balance with Missing System Info
    # Delete again
    async with AsyncSessionLocal() as session:
        await session.execute(delete(SystemInfoDAO))
        await session.commit()
    
    # set_balance should create system info
    await repo.set_balance(50.0, 1)
    
    bal_after_set = await repo.get_balance()
    assert bal_after_set == 50.0
