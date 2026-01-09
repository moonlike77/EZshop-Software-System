# app/models/DAO/return_dao.py

class ReturnLineDAO:
    def __init__(self, product_code, amount, price_per_unit):
        self.product_code = product_code
        self.amount = amount
        self.price_per_unit = price_per_unit

    def to_dict(self):
        return {
            "product_code": self.product_code,
            "amount": self.amount,
            "price_per_unit": self.price_per_unit
        }

# تغییر مهم اینجاست: (Base) حذف شد
class ReturnDAO:
    def __init__(self, return_id, sale_id, date, status="OPEN"):
        self.return_id = return_id
        self.sale_id = sale_id
        self.date = date
        self.status = status
        self.products = []
        self.total_amount = 0.0

    def add_product(self, product_code, amount, price_per_unit):
        self.products.append(ReturnLineDAO(product_code, amount, price_per_unit))
        self.total_amount += (amount * price_per_unit)

    def to_dict(self):
        return {
            "return_id": self.return_id,
            "sale_id": self.sale_id,
            "date": self.date,
            "status": self.status,
            "products": [p.to_dict() for p in self.products],
            "total_amount": self.total_amount
        }