import pytest
from app.controllers.return_controller import ReturnController
from app.models.return_status import ReturnStatus
from app.models.DAO.sale_dao import SaleDAO
from app.models.DAO.sale_line_dao import SaleLineDAO
from app.models.sale_status import SaleStatus
from app.models.DAO.product_dao import ProductDAO
from app.models.DAO.order_dao import OrderDAO
from datetime import datetime, timezone
from app.models.errors.app_error import AppError
from app.models.errors.invalid_state_error import InvalidStateError
from app.models.errors.notfound_error import NotFoundError
from app.database.database import AsyncSessionLocal, init_db, reset_db

@pytest.fixture
async def setup_sale_for_return():
    await reset_db()
    await init_db()
    async with AsyncSessionLocal() as session:

        p1 = ProductDAO(id=1, description="Coffe", barcode="000000000001",
                        price_per_unit=2.5, note="Black Coffe",
                        quantity=20, position="9-B-1")
        session.add(p1)
        await session.commit()
        await session.refresh(p1)

        p2 = ProductDAO(id=2, description="Milk", barcode="000000000002",
                        price_per_unit=5.5, note="Lactose free milk",
                        quantity=20, position="9-B-2")
        session.add(p2)
        await session.commit()
        await session.refresh(p2)

        sl1 = SaleLineDAO(id=1, sale_id=1, product_barcode="000000000001",
                         quantity=5, price_per_unit=2.5, discount_rate=0.0)
        session.add(sl1)
        await session.commit()
        await session.refresh(sl1)
        
        s1 = SaleDAO(id=1, status=SaleStatus.PAID, discount_rate=0.0,
                    created_at=datetime.now(timezone.utc), closed_at = None, lines=[sl1])
        session.add(s1)
        await session.commit()
        await session.refresh(s1)

        sl2 = SaleLineDAO(id=2, sale_id=2, product_barcode="000000000002",
                         quantity=7, price_per_unit=5.5, discount_rate=0.0)
        session.add(sl2)
        await session.commit()
        await session.refresh(sl2)
        
        s2 = SaleDAO(id=2, status=SaleStatus.PAID, discount_rate=0.0,
                    created_at=datetime.now(timezone.utc), closed_at = None, lines=[sl2])
        session.add(s2)
        await session.commit()
        await session.refresh(s2)

@pytest.mark.asyncio
async def test_start_return(setup_sale_for_return):
    # تنظیم رفتار ماک

    async with AsyncSessionLocal() as session:
        controller = ReturnController()
        controller.repo._session = session

        # اجرای متد
        result = await controller.start_return(sale_id=1)

        # بررسی نتیجه
        assert result.id == 1
        assert result.status == ReturnStatus.OPEN

@pytest.mark.asyncio
async def test_get_return_success():

    async with AsyncSessionLocal() as session:
        controller = ReturnController()
        controller.repo._session = session
    
         # اجرا
        result = await controller.get_return(return_id=1)
        
        # بررسی
        assert result.id == 1

@pytest.mark.asyncio
async def test_get_return_not_found():

    async with AsyncSessionLocal() as session:
        controller = ReturnController()
        controller.repo._session = session
        
        with pytest.raises(NotFoundError):
            await controller.get_return(return_id=999)

@pytest.mark.asyncio
async def test_list_all_returns_success():

    async with AsyncSessionLocal() as session:
        controller = ReturnController()
        controller.repo._session = session
        await controller.start_return(sale_id=2)
    
         # اجرا
        result = await controller.list_returns()
        
        # بررسی
        assert result[0].id == 1
        assert result[1].id == 2

@pytest.mark.asyncio
async def test_get_all_returns_by_sale_success():

    async with AsyncSessionLocal() as session:
        controller = ReturnController()
        controller.repo._session = session
    
         # اجرا
        result = await controller.get_returns_by_sale(1)
        
        # بررسی
        assert result[0].id == 1

@pytest.mark.asyncio
async def test_add_product_to_return_success():

    async with AsyncSessionLocal() as session:
        controller = ReturnController()
        controller.repo._session = session

        result = await controller.add_item(1, "000000000001", 3)

        assert result is True

        catch = await controller.get_return(1)

        assert catch.lines[0].product_barcode == "000000000001"
        assert catch.lines[0].quantity == 3

@pytest.mark.asyncio
async def test_remove_product_from_return_success():

    async with AsyncSessionLocal() as session:
        controller = ReturnController()
        controller.repo._session = session

        result = await controller.remove_item(1, "000000000001", 1)

        assert result is True

        catch = await controller.get_return(1)

        assert catch.lines[0].quantity == 2

@pytest.mark.asyncio
async def test_add_product_to_return_not_found():

    async with AsyncSessionLocal() as session:
        controller = ReturnController()
        controller.repo._session = session

        with pytest.raises(NotFoundError):
            await controller.add_item(999, "000000000001", 3)

@pytest.mark.asyncio
async def test_remove_product_from_return_not_found():

    async with AsyncSessionLocal() as session:
        controller = ReturnController()
        controller.repo._session = session

        with pytest.raises(NotFoundError):
            await controller.remove_item(999, "000000000001", 1)

@pytest.mark.asyncio
async def test_close_return_success():

    async with AsyncSessionLocal() as session:
        controller = ReturnController()
        controller.repo._session = session
    
         # اجرا
        result = await controller.close_return(return_id=1)
        
        # بررسی
        assert result is True

@pytest.mark.asyncio
async def test_add_product_to_return_invalid_state():

    async with AsyncSessionLocal() as session:
        controller = ReturnController()
        controller.repo._session = session

        with pytest.raises(InvalidStateError):
            await controller.add_item(1, "000000000001", 3)

@pytest.mark.asyncio
async def test_remove_product_from_return_invalid_state():

    async with AsyncSessionLocal() as session:
        controller = ReturnController()
        controller.repo._session = session

        with pytest.raises(InvalidStateError):
            await controller.remove_item(1, "000000000001", 1)

@pytest.mark.asyncio
async def test_close_return_fail_if_not_open(): 
    async with AsyncSessionLocal() as session:
        controller = ReturnController()
        controller.repo._session = session
        
        with pytest.raises(InvalidStateError):
            await controller.close_return(return_id=1)

@pytest.mark.asyncio
async def test_close_return_not_found(): 
    async with AsyncSessionLocal() as session:
        controller = ReturnController()
        controller.repo._session = session
        
        with pytest.raises(NotFoundError):
            await controller.close_return(return_id=999)

@pytest.mark.asyncio
async def test_reimburse_return_success():

    async with AsyncSessionLocal() as session:
        controller = ReturnController()
        controller.repo._session = session
    
         # اجرا
        result = await controller.reimburse_return(return_id=1)

        assert result["refund_amount"] == 5.0

@pytest.mark.asyncio
async def test_reimburse_return_not_found():

    async with AsyncSessionLocal() as session:
        controller = ReturnController()
        controller.repo._session = session
    
        with pytest.raises(NotFoundError):
            await controller.reimburse_return(return_id=999)

@pytest.mark.asyncio
async def test_reimburse_return_invalid_state():

    async with AsyncSessionLocal() as session:
        controller = ReturnController()
        controller.repo._session = session
    
        with pytest.raises(InvalidStateError):
            await controller.reimburse_return(return_id=2)

@pytest.mark.asyncio
async def test_close_empty_return_with_deletion(): 
    async with AsyncSessionLocal() as session:
        controller = ReturnController()
        controller.repo._session = session
        
        result = await controller.close_return(return_id=2)

        assert result is True

        with pytest.raises(NotFoundError):
            await controller.get_return(2)
        
@pytest.mark.asyncio
async def test_delete_return_success():

    async with AsyncSessionLocal() as session:
        controller = ReturnController()
        controller.repo._session = session
        await controller.start_return(2)
    
         # اجرا
        await controller.delete_return(return_id=2)

        with pytest.raises(NotFoundError):
            await controller.get_return(2)

@pytest.mark.asyncio
async def test_delete_return_not_found():

    async with AsyncSessionLocal() as session:
        controller = ReturnController()
        controller.repo._session = session

        with pytest.raises(NotFoundError):
            await controller.delete_return(return_id=999)

@pytest.mark.asyncio
async def test_delete_return_fail_if_reimbursed():

    async with AsyncSessionLocal() as session:
        controller = ReturnController()
        controller.repo._session = session

        with pytest.raises(InvalidStateError):
            await controller.delete_return(return_id=1)