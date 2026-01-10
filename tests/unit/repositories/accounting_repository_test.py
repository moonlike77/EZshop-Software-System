
import pytest
from app.repositories.transaction_repository import TransactionRepository
from app.models.DAO.system_dao import SystemInfoDAO
from app.database.database import AsyncSessionLocal
from app.models.transaction_type import TransactionType
from sqlalchemy import delete
from datetime import datetime
import pytest_asyncio
from init_db import reset, init_db

# ---------------------------------------------------------------------
# REPOSITORY TESTS
# ---------------------------------------------------------------------

@pytest.mark.asyncio
async def test_repository_coverage_edge_cases():
    # 1. Test Session Injection
    mock_session = "Mock Session"
    repo_with_session = TransactionRepository(session=mock_session)
    assert await repo_with_session._get_session() == mock_session

    # 2. Test Set Balance No Change
    repo = TransactionRepository()
    await repo.set_balance(100.0, 1)
    tx = await repo.set_balance(100.0, 1)
    assert tx.amount == 0.0
    
    # 3. Test Partial Date Filters
    start = datetime(2000, 1, 1)
    end = datetime(2099, 12, 31)
    res_start = await repo.get_transactions(start_date=start, end_date=None)
    assert isinstance(res_start, list)
    res_end = await repo.get_transactions(start_date=None, end_date=end)
    assert isinstance(res_end, list)

    # 4. Test Missing System Info
    async with AsyncSessionLocal() as session:
        await session.execute(delete(SystemInfoDAO))
        await session.commit()
    
    bal = await repo.get_balance()
    assert bal == 0.0
    
    await repo.create_transaction(10.0, TransactionType.CREDIT, "Re-init", 1)
    bal_new = await repo.get_balance()
    assert bal_new == 10.0

    # 5. Test set_balance with Missing System Info
    async with AsyncSessionLocal() as session:
        await session.execute(delete(SystemInfoDAO))
        await session.commit()
    
    await repo.set_balance(50.0, 1)
    bal_after_set = await repo.get_balance()
    assert bal_after_set == 50.0
