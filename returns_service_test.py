import pytest
from app.services.return_service import ReturnService
from app.repositories.return_repository import ReturnRepository

@pytest.fixture
def return_service():
    # پاکسازی دیتابیس برای هر تست
    ReturnRepository.clear_db()
    return ReturnService()

def test_start_return_transaction_service(return_service):
    return_id = return_service.start_return_transaction(sale_id=50)
    assert return_id is not None

def test_add_product_success(return_service):
    return_id = return_service.start_return_transaction(sale_id=50)
    success, msg = return_service.add_product_to_return(return_id, "123", 5)
    assert success is True

def test_close_return_transaction(return_service):
    return_id = return_service.start_return_transaction(sale_id=50)
    success = return_service.close_return_transaction(return_id, commit=True)
    assert success is True