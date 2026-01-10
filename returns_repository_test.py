import pytest
from app.repositories.return_repository import ReturnRepository
from app.models.DAO.return_dao import ReturnDAO

def test_create_return_transaction():
    # پاکسازی دیتابیس حافظه‌ای قبل از تست
    ReturnRepository.clear_db()
    repo = ReturnRepository()
    
    new_return = ReturnDAO(return_id=None, sale_id=1, date="2026-01-08")
    return_id = repo.create_return_transaction(new_return)
    
    assert return_id is not None
    assert repo.get_return_by_id(return_id).sale_id == 1

def test_add_product_to_return_dao():
    ReturnRepository.clear_db()
    repo = ReturnRepository()
    
    new_return = ReturnDAO(return_id=None, sale_id=1, date="2026-01-08")
    return_id = repo.create_return_transaction(new_return)
    
    return_obj = repo.get_return_by_id(return_id)
    return_obj.add_product("123456789012", 2, 10.0)
    repo.update_return(return_obj)
    
    updated_return = repo.get_return_by_id(return_id)
    assert len(updated_return.products) == 1