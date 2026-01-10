import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.return_repository import ReturnRepository
from app.models.return_status import ReturnStatus
from init_db import reset, init_db
from app.database.database import AsyncSessionLocal
from app.models.DAO.sale_dao import SaleDAO
from app.models.DAO.sale_line_dao import SaleLineDAO
from app.models.DAO.product_dao import ProductDAO
from app.models.sale_status import SaleStatus
from datetime import datetime, timezone

@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    await reset()
    await init_db()

# استفاده از فیکسچر دیتابیس که در conftest.py تعریف شده
@pytest.mark.asyncio
async def test_create_and_get_return():
    async with AsyncSessionLocal() as session:
        sale = SaleDAO(id=1, status=SaleStatus.PAID, discount_rate=0.0, created_at=datetime.now(timezone.utc), closed_at=datetime.now(timezone.utc))
        session.add(sale)
        await session.commit()
        await session.refresh(sale)
        
        # تست ایجاد
        return_repository = ReturnRepository(session)
        new_return = await return_repository.create_return(sale_id=sale.id)
        assert new_return.id is not None
        assert new_return.status == ReturnStatus.OPEN
        assert new_return.sale_id == sale.id

        # تست خواندن
        fetched_return = await return_repository.get_return(new_return.id)
        assert fetched_return is not None
        assert fetched_return.id == new_return.id

@pytest.mark.asyncio
async def test_add_and_remove_line():
    async with AsyncSessionLocal() as session:
        repo = ReturnRepository(session)

        prod = ProductDAO(id=1, description="Coffe", barcode="000000000001", price_per_unit=5.5,
                          note="Black coffe", quantity=10, position="9-7-B")
        session.add(prod)
        await session.commit()
        await session.refresh(prod)

        sale_line = SaleLineDAO(id=1, sale_id=1, product_barcode=prod.barcode,
                                quantity=3, price_per_unit=prod.price_per_unit, discount_rate=0.0)
        session.add(sale_line)
        await session.commit()
        await session.refresh(sale_line)

        sale = SaleDAO(id=1, status=SaleStatus.PAID, discount_rate=0.0,
                       created_at=datetime.now(timezone.utc), closed_at=datetime.now(timezone.utc),
                       lines=[sale_line])
        session.add(sale)
        await session.commit()
        await session.refresh(sale)

        new_return = await repo.create_return(sale_id=sale.id)
        
        # افزودن آیتم
        await repo.add_line(new_return, prod.barcode, 2)
        
        # رفرش کردن آبجکت برای دیدن تغییرات
        r = await repo.get_return(new_return.id)
        assert len(r.lines) == 1
        assert r.lines[0].quantity == 2
        
        # حذف آیتم (کاهش تعداد)
        await repo.remove_line_quantity(new_return, prod.barcode, 1)
        r = await repo.get_return(new_return.id)
        assert r.lines[0].quantity == 1
        
        # حذف کامل
        await repo.remove_line_quantity(new_return, prod.barcode, 3)
        r = await repo.get_return(new_return.id)
        assert len(r.lines) == 0

@pytest.mark.asyncio
async def test_update_status():
    async with AsyncSessionLocal() as session:
        sale = SaleDAO(id=1, status=SaleStatus.PAID, discount_rate=0.0, created_at=datetime.now(timezone.utc), closed_at=datetime.now(timezone.utc))
        session.add(sale)
        await session.commit()
        await session.refresh(sale)

        repo = ReturnRepository(session)
        r = await repo.create_return(sale_id=sale.id)
        
        updated = await repo.update_status(r.id, ReturnStatus.CLOSED, None)
        assert updated.status == ReturnStatus.CLOSED
        assert updated.closed_at is not None