from fastapi import APIRouter
from pydantic import BaseModel
from app.controllers.return_controller import ReturnController

# تعریف مدل‌های ورودی برای چک کردن دیتای ارسالی
class StartReturnRequest(BaseModel):
    saleId: int

class AddProductRequest(BaseModel):
    productCode: str
    amount: int

class CloseReturnRequest(BaseModel):
    commit: bool

# اینجا return_bp تعریف می‌شود
return_bp = APIRouter()
controller = ReturnController()

@return_bp.post('/api/returnTransaction', status_code=201)
def start_return_transaction(payload: StartReturnRequest):
    return controller.start_return(payload.saleId)

@return_bp.post('/api/returnTransaction/{return_id}/product')
def add_product_to_return(return_id: int, payload: AddProductRequest):
    return controller.add_product(return_id, payload.productCode, payload.amount)

@return_bp.put('/api/returnTransaction/{return_id}')
def close_return_transaction(return_id: int, payload: CloseReturnRequest):
    return controller.close_return(return_id, payload.commit)

@return_bp.delete('/api/returnTransaction/{return_id}')
def delete_return_transaction(return_id: int):
    return controller.delete_return(return_id)

@return_bp.get('/api/returnTransaction/{return_id}')
def get_return_transaction(return_id: int):
    return controller.get_return(return_id)