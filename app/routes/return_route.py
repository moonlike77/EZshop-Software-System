# app/routes/return_route.py
from fastapi import APIRouter, Depends, status, Query
from typing import List
from app.controllers.return_controller import ReturnController
from app.models.DTO.return_dto import ReturnDTO
from app.models.user_type import UserType
from app.middleware.auth_middleware import authenticate_user
from app.config.config import APP_V1_BASE_URL
from app.models.DTO.error_dto import ErrorDTO # برای داکیومنت سازی اگر لازم شد

# آدرس پایه: /api/v1/returns
router = APIRouter(prefix=f"{APP_V1_BASE_URL}/returns", tags=["returns"])
controller = ReturnController()

# دسترسی‌های مجاز
ALL_ROLES = [UserType.Administrator, UserType.ShopManager, UserType.Cashier]
ADMIN_MANAGER = [UserType.Administrator, UserType.ShopManager]

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ReturnDTO, dependencies=[Depends(authenticate_user(ALL_ROLES))])
async def start_return(sale_id: int = Query(..., description="ID of the paid sale")):
    """Start a return transaction for a sale"""
    return await controller.start_return(sale_id)

@router.get("/", response_model=List[ReturnDTO], dependencies=[Depends(authenticate_user(ALL_ROLES))])
async def get_all_returns():
    """Get all return transactions"""
    return await controller.list_returns()

@router.get("/{return_id}", response_model=ReturnDTO, dependencies=[Depends(authenticate_user(ALL_ROLES))])
async def get_return(return_id: int):
    """Get a return transaction by ID"""
    return await controller.get_return(return_id)

@router.delete("/{return_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(authenticate_user(ALL_ROLES))])
async def delete_return(return_id: int):
    """Delete a return transaction"""
    await controller.delete_return(return_id)
    return # 204 requires no content

@router.get("/sale/{sale_id}", response_model=List[ReturnDTO], dependencies=[Depends(authenticate_user(ALL_ROLES))])
async def get_returns_by_sale(sale_id: int):
    """Get returns for a specific sale"""
    return await controller.get_returns_by_sale(sale_id)

@router.post("/{return_id}/items", status_code=status.HTTP_201_CREATED, dependencies=[Depends(authenticate_user(ALL_ROLES))])
async def add_product_to_return(return_id: int, barcode: str = Query(...), amount: int = Query(...)):
    """Add a product to a return transaction"""
    success = await controller.add_item(return_id, barcode, amount)
    return {"success": success} # طبق Swagger BooleanResponse

@router.delete("/{return_id}/items", status_code=status.HTTP_202_ACCEPTED, dependencies=[Depends(authenticate_user(ALL_ROLES))])
async def remove_product_from_return(return_id: int, barcode: str = Query(...), amount: int = Query(...)):
    """Remove a product from a return transaction"""
    success = await controller.remove_item(return_id, barcode, amount)
    return {"success": success}

@router.patch("/{return_id}/close", status_code=status.HTTP_200_OK, dependencies=[Depends(authenticate_user(ALL_ROLES))])
async def close_return(return_id: int):
    """Close a return transaction"""
    success = await controller.close_return(return_id)
    return {"success": success}

@router.patch("/{return_id}/reimburse", status_code=status.HTTP_200_OK, dependencies=[Depends(authenticate_user(ADMIN_MANAGER))])
async def reimburse_return(return_id: int):
    """Reimburse a return transaction (Marks as REIMBURSED)"""
    # توجه: فقط Admin و Manager دسترسی دارند
    return await controller.reimburse_return(return_id)