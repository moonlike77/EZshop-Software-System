# app/services/return_service.py
from app.repositories.return_repository import ReturnRepository
from app.models.DAO.return_dao import ReturnDAO
from datetime import datetime

class ReturnService:
    def __init__(self):
        self.return_repository = ReturnRepository()

    def start_return_transaction(self, sale_id):
        # ساخت یک تراکنش جدید با تاریخ امروز
        date_str = datetime.now().strftime("%Y-%m-%d")
        # توجه: اینجا دیگر نیازی به ایمپورت Base نیست چون DAO را اصلاح کردیم
        new_return = ReturnDAO(return_id=None, sale_id=sale_id, date=date_str)
        return_id = self.return_repository.create_return_transaction(new_return)
        return return_id

    def add_product_to_return(self, return_id, product_code, amount):
        return_trans = self.return_repository.get_return_by_id(return_id)
        if not return_trans:
            return False, "Return transaction not found"
        
        if return_trans.status != "OPEN":
            return False, "Transaction is not OPEN"

        # فعلاً قیمت را ۱۰.۰ فرض می‌کنیم
        price_per_unit = 10.0 
        
        return_trans.add_product(product_code, amount, price_per_unit)
        self.return_repository.update_return(return_trans)
        return True, "Product added"

    def close_return_transaction(self, return_id, commit):
        return_trans = self.return_repository.get_return_by_id(return_id)
        if not return_trans:
            return False
        
        if commit:
            return_trans.status = "CLOSED"
        else:
            self.return_repository.delete_return(return_id)
            
        return True

    def delete_return_transaction(self, return_id):
        return self.return_repository.delete_return(return_id)

    def get_return_transaction(self, return_id):
        return_trans = self.return_repository.get_return_by_id(return_id)
        if return_trans:
            return return_trans.to_dict()
        return None