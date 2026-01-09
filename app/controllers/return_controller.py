from fastapi import HTTPException
from app.services.return_service import ReturnService

class ReturnController:
    def __init__(self):
        self.return_service = ReturnService()

    def start_return(self, sale_id: int):
        if not sale_id:
             raise HTTPException(status_code=400, detail="Missing saleId")
             
        return_id = self.return_service.start_return_transaction(sale_id)
        return {"returnId": return_id}

    def add_product(self, return_id: int, product_code: str, amount: int):
        success, message = self.return_service.add_product_to_return(return_id, product_code, amount)
        if success:
            return {"message": message}
        raise HTTPException(status_code=400, detail=message)

    def close_return(self, return_id: int, commit: bool):
        success = self.return_service.close_return_transaction(return_id, commit)
        if success:
            return {"message": "Transaction closed"}
        raise HTTPException(status_code=404, detail="Transaction not found")

    def delete_return(self, return_id: int):
        success = self.return_service.delete_return_transaction(return_id)
        if success:
            return {"message": "Transaction deleted"}
        raise HTTPException(status_code=404, detail="Transaction not found")

    def get_return(self, return_id: int):
        data = self.return_service.get_return_transaction(return_id)
        if data:
            return data
        raise HTTPException(status_code=404, detail="Not found")