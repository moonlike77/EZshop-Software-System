from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from app.controllers.return_controller import ReturnController
from app.config.config import ROUTES
from app.models.DTO.return_dto import ReturnDTO
from app.middleware.auth_middleware import authenticate_user
from app.models.user_type import UserType

# تعریف مدل‌های ورودی برای چک کردن دیتای ارسالی
class StartReturnRequest(BaseModel):
    saleId: int

class AddProductRequest(BaseModel):
    productCode: str
    amount: int

class CloseReturnRequest(BaseModel):
    commit: bool

# اینجا return_bp تعریف می‌شود
return_bp = APIRouter(prefix=ROUTES['V1_RETURNS'], tags=["returns"])
controller = ReturnController()

@return_bp.post('/',
    response_model=ReturnDTO, 
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.Cashier, UserType.ShopManager]))]
    )
def start_return_transaction(sale_id: int):
    return controller.start_return(sale_id)

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