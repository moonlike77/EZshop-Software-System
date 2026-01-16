from fastapi import APIRouter, Depends, status, Query, Path, HTTPException
from typing import List
from app.controllers.return_controller import ReturnController
from app.models.DTO.return_dto import ReturnDTO
from app.models.user_type import UserType
from app.middleware.auth_middleware import authenticate_user
from app.config.config import ROUTES
from app.models.errors.app_error import AppError
from app.models.errors.bad_request import BadRequestError

router = APIRouter(prefix=ROUTES["V1_RETURNS"], tags=["returns"])
controller = ReturnController()

# دسترسی‌های مجاز
ALL_ROLES = [UserType.Administrator, UserType.ShopManager, UserType.Cashier]
ADMIN_MANAGER = [UserType.Administrator, UserType.ShopManager]

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ReturnDTO, dependencies=[Depends(authenticate_user(ALL_ROLES))])
async def start_return(sale_id: int = Query(..., gt=0, description="ID of the paid sale")):
    """Start a return transaction for a sale"""
    try:
        return await controller.start_return(sale_id)
    except AppError as e:
        raise HTTPException(status_code=e.status, detail=e.message)

@router.get("/", response_model=List[ReturnDTO], dependencies=[Depends(authenticate_user(ALL_ROLES))])
async def get_all_returns():
    """Get all return transactions"""
    return await controller.list_returns()

@router.get("/{return_id}", response_model=ReturnDTO, dependencies=[Depends(authenticate_user(ALL_ROLES))])
async def get_return(return_id: int = Path(..., gt=0)):
    """Get a specific return transaction"""
    try:
        return await controller.get_return(return_id)
    except AppError as e:
        raise HTTPException(status_code=e.status, detail=e.message)

@router.delete("/{return_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(authenticate_user(ALL_ROLES))])
async def delete_return(return_id: int = Path(..., gt=0)):
    """Delete a return transaction"""
    try:
        await controller.delete_return(return_id)
    except AppError as e:
        raise HTTPException(status_code=e.status, detail=e.message)

@router.post("/{return_id}/items", status_code=status.HTTP_201_CREATED, dependencies=[Depends(authenticate_user(ALL_ROLES))])
async def add_product_to_return(
    return_id: int = Path(..., gt=0), 
    barcode: str = Query(...), 
    amount: int = Query(..., gt=0)
):
    """Add a product to a return transaction"""
    try:
        success = await controller.add_item(return_id, barcode, amount)
        return {"success": success}
    except AppError as e:
        raise HTTPException(status_code=e.status, detail=e.message)
# فقط status_code را تغییر بده به HTTP_202_ACCEPTED
@router.delete("/{return_id}/items", status_code=status.HTTP_202_ACCEPTED, dependencies=[Depends(authenticate_user(ALL_ROLES))])
async def remove_product_from_return(
    return_id: int = Path(..., gt=0), 
    barcode: str = Query(...), 
    amount: int = Query(..., gt=0)
):
    """Remove a product from a return transaction"""
    try:
        success = await controller.remove_item(return_id, barcode, amount)
        return {"success": success}
    except AppError as e:
        raise HTTPException(status_code=e.status, detail=e.message)


@router.patch("/{return_id}/close", status_code=status.HTTP_200_OK, dependencies=[Depends(authenticate_user(ALL_ROLES))])
async def close_return(return_id: int = Path(..., gt=0)):
    """Close a return transaction"""
    try:
        success = await controller.close_return(return_id)
        return {"success": success}
    except AppError as e:
        raise HTTPException(status_code=e.status, detail=e.message)

@router.patch("/{return_id}/reimburse", status_code=status.HTTP_200_OK, dependencies=[Depends(authenticate_user(ADMIN_MANAGER))])
async def reimburse_return(return_id: int = Path(..., gt=0)):
    """Reimburse a closed return transaction"""
    try:
        return await controller.reimburse_return(return_id)
    except AppError as e:
        raise HTTPException(status_code=e.status, detail=e.message)