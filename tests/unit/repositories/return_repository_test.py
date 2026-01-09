import pytest
from app.repositories.return_repository import ReturnRepository
from app.models.return_status import ReturnStatus

# استفاده از فیکسچر دیتابیس که در conftest.py تعریف شده
@pytest.mark.asyncio
async def test_create_and_get_return(setup_test_db):
    repo = ReturnRepository()
    sale_id_sample = 100
    
    # تست ایجاد
    new_return = await repo.create_return(sale_id=sale_id_sample)
    assert new_return.id is not None
    assert new_return.status == ReturnStatus.OPEN
    assert new_return.sale_id == sale_id_sample

    # تست خواندن
    fetched_return = await repo.get_return(new_return.id)
    assert fetched_return is not None
    assert fetched_return.id == new_return.id

@pytest.mark.asyncio
async def test_add_and_remove_line(setup_test_db):
    repo = ReturnRepository()
    new_return = await repo.create_return(sale_id=101)
    
    # افزودن آیتم
    await repo.add_line(new_return.id, "123456789", 5, 10.0)
    
    # رفرش کردن آبجکت برای دیدن تغییرات
    r = await repo.get_return(new_return.id)
    assert len(r.lines) == 1
    assert r.lines[0].quantity == 5
    
    # حذف آیتم (کاهش تعداد)
    await repo.remove_line_quantity(new_return.id, "123456789", 2)
    r = await repo.get_return(new_return.id)
    assert r.lines[0].quantity == 3
    
    # حذف کامل
    await repo.remove_line_quantity(new_return.id, "123456789", 3)
    r = await repo.get_return(new_return.id)
    assert len(r.lines) == 0

@pytest.mark.asyncio
async def test_update_status(setup_test_db):
    repo = ReturnRepository()
    r = await repo.create_return(sale_id=102)
    
    updated = await repo.update_status(r.id, ReturnStatus.CLOSED)
    assert updated.status == ReturnStatus.CLOSED
    assert updated.closed_at is not None