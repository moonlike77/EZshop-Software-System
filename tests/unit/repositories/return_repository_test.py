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
from app.models.errors.invalid_state_error import InvalidStateError
from app.models.errors.notfound_error import NotFoundError
from app.models.errors.bad_request import BadRequestError
from datetime import datetime, timezone

@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    await reset()
    await init_db()

# استفاده از فیکسچر دیتابیس که در conftest.py تعریف شده
@pytest.mark.asyncio
async def test_create_and_get_returns_also_with_invalid_sale_state():
    async with AsyncSessionLocal() as session:
        sale1 = SaleDAO(id=1, status=SaleStatus.PAID, discount_rate=0.0, created_at=datetime.now(timezone.utc), closed_at=datetime.now(timezone.utc))
        session.add(sale1)
        await session.commit()
        await session.refresh(sale1)

        sale2 = SaleDAO(id=2, status=SaleStatus.PAID, discount_rate=0.0, created_at=datetime.now(timezone.utc), closed_at=datetime.now(timezone.utc))
        session.add(sale2)
        await session.commit()
        await session.refresh(sale2)

        sale3 = SaleDAO(id=3, status=SaleStatus.OPEN, discount_rate=0.0, created_at=datetime.now(timezone.utc), closed_at=datetime.now(timezone.utc))
        session.add(sale3)
        await session.commit()
        await session.refresh(sale3)
        
        # تست ایجاد
        return_repository = ReturnRepository(session)
        new_return1 = await return_repository.create_return(sale_id=sale1.id)
        assert new_return1.id is not None
        assert new_return1.status == ReturnStatus.OPEN
        assert new_return1.sale_id == sale1.id

        new_return2 = await return_repository.create_return(sale_id=sale2.id)
        assert new_return2.id is not None
        assert new_return2.status == ReturnStatus.OPEN
        assert new_return2.sale_id == sale2.id

        with pytest.raises(InvalidStateError):
            await return_repository.create_return(sale_id=sale3.id)

        # تست خواندن
        fetched_return1 = await return_repository.get_return(new_return1.id)
        assert fetched_return1 is not None
        assert fetched_return1.id == new_return1.id

        fetched_all = await return_repository.list_returns()
        assert len(fetched_all) == 2
        assert fetched_all[0].id == new_return1.id
        assert fetched_all[1].id == new_return2.id

        fetched_by_sale = await return_repository.get_returns_by_sale(1)
        assert len(fetched_by_sale) == 1
        assert fetched_by_sale[0].id == new_return1.id

@pytest.mark.asyncio
async def test_add_and_remove_line_all_cases():
    async with AsyncSessionLocal() as session:
        repo = ReturnRepository(session)

        prod1 = ProductDAO(id=1, description="Coffe", barcode="000000000001", price_per_unit=5.5,
                          note="Black coffe", quantity=10, position="9-7-B")
        session.add(prod1)
        await session.commit()
        await session.refresh(prod1)

        prod2 = ProductDAO(id=2, description="Milk", barcode="000000000002", price_per_unit=1.5,
                          note="Lactose free milk", quantity=10, position="9-7-C")
        session.add(prod2)
        await session.commit()
        await session.refresh(prod2)

        sale_line = SaleLineDAO(id=1, sale_id=1, product_barcode=prod1.barcode,
                                quantity=3, price_per_unit=prod1.price_per_unit, discount_rate=0.0)
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

        with pytest.raises(NotFoundError):
            await repo.add_line(new_return, "000000000099", 2)

        with pytest.raises(NotFoundError):
            await repo.add_line(new_return, prod2.barcode, 2)

        with pytest.raises(BadRequestError):
            await repo.add_line(new_return, prod1.barcode, 5)
        
        # افزودن آیتم
        await repo.add_line(new_return, prod1.barcode, 2)
        
        # رفرش کردن آبجکت برای دیدن تغییرات
        r = await repo.get_return(new_return.id)
        assert len(r.lines) == 1
        assert r.lines[0].quantity == 2

        await repo.add_line(new_return, prod1.barcode, 1)

        r = await repo.get_return(new_return.id)
        assert len(r.lines) == 1
        assert r.lines[0].quantity == 3

        with pytest.raises(NotFoundError):
            await repo.remove_line_quantity(new_return, "000000000099", 2)

        with pytest.raises(NotFoundError):
            await repo.remove_line_quantity(new_return, prod2.barcode, 2)
        
        # حذف آیتم (کاهش تعداد)
        await repo.remove_line_quantity(new_return, prod1.barcode, 1)
        r = await repo.get_return(new_return.id)
        assert r.lines[0].quantity == 2
        
        # حذف کامل
        await repo.remove_line_quantity(new_return, prod1.barcode, 3)
        r = await repo.get_return(new_return.id)
        assert len(r.lines) == 0

@pytest.mark.asyncio
async def test_update_status():
    async with AsyncSessionLocal() as session:
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

        sale1 = SaleDAO(id=1, status=SaleStatus.PAID, discount_rate=0.0,
                       created_at=datetime.now(timezone.utc), closed_at=datetime.now(timezone.utc),
                       lines=[sale_line])
        session.add(sale1)
        await session.commit()
        await session.refresh(sale1)

        sale2 = SaleDAO(id=2, status=SaleStatus.PAID, discount_rate=0.0, created_at=datetime.now(timezone.utc), closed_at=datetime.now(timezone.utc))
        session.add(sale2)
        await session.commit()
        await session.refresh(sale2)

        repo = ReturnRepository(session)
        r1 = await repo.create_return(sale_id=sale1.id)
        await repo.add_line(r1, prod.barcode, 2)
        r2 = await repo.create_return(sale_id=sale2.id)
        
        updated = await repo.update_status(r1.id, ReturnStatus.CLOSED, None)
        assert updated.status == ReturnStatus.CLOSED
        assert updated.closed_at is not None

        updated = await repo.update_status(r1.id, ReturnStatus.REIMBURSED, 11.0)
        assert updated.status == ReturnStatus.REIMBURSED

        await repo.update_status(r2.id, ReturnStatus.CLOSED, None)

        resp = await repo.delete_return(2)
        assert resp is True

        resp = await repo.delete_return(99)
        assert resp is False