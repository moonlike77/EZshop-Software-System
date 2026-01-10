import os
import pytest
import pytest_asyncio
from app.database import database

# تنظیم محیط تست
os.environ["TESTING"] = "1"

# استفاده از دکوریتور مخصوص pytest-asyncio برای فیکسچرهای async
@pytest_asyncio.fixture(scope="function")
async def setup_test_db():
    """
    این فیکسچر قبل از هر تست دیتابیس رو میسازه و بعدش پاک میکنه.
    """
    await database.init_db()
    yield
    await database.reset_db()