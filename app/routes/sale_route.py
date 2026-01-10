from fastapi import APIRouter, status, Depends, Path, Query
from app.config.config import ROUTES
from app.controllers.sale_controller import SaleController
from app.models.DTO.sale_dto import SaleDTO
from app.middleware.auth_middleware import authenticate_user
from app.models.user_type import UserType
from typing import List
from app.models.errors.bad_request import BadRequestError

router = APIRouter(prefix=ROUTES["V1_SALES"], tags=["Sales"])
controller = SaleController()


@router.post("/",
    response_model=SaleDTO,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager, UserType.Cashier]))])
async def start_sale():
    """Starts a new sale transaction with initial status OPEN. Permissions: Administrator, ShopManager, Cashier"""
    return await controller.start_sale()


@router.get("/",
    response_model=List[SaleDTO],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager, UserType.Cashier]))])
async def list_sales():
    """Returns all sale transactions. Permissions: Administrator, ShopManager, Cashier"""
    return await controller.list_sales()


@router.get("/{sale_id}",
    response_model=SaleDTO,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager, UserType.Cashier]))])
async def get_sale(sale_id: int = Path(..., description="Sale ID")):
    """Retrieve details of a specific sale. Permissions: Administrator, ShopManager, Cashier"""
    if sale_id <= 0:
        raise BadRequestError("Invalid or missing id")
    return await controller.get_sale(sale_id)


@router.delete("/{sale_id}",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager, UserType.Cashier]))])
async def delete_sale(sale_id: int = Path(..., description="Sale ID")):
    """Delete a sale by its ID, unless it has been PAID. Returns {"success": true} on success. Permissions: Administrator, ShopManager, Cashier"""
    if sale_id <= 0:
        raise BadRequestError("Invalid sale ID")
    await controller.delete_sale(sale_id)
    return {"success": True}


@router.post("/{sale_id}/items",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager, UserType.Cashier]))])
async def add_product_to_sale(
    sale_id: int = Path(..., description="Sale ID"),
    barcode: str = Query(..., description="Product barcode"),
    amount: int = Query(..., description="Quantity to add"),):
    """Add a product to an OPEN sale with a specified quantity. Permissions: Administrator, ShopManager, Cashier"""
    if sale_id <= 0:
        raise BadRequestError("Invalid sale ID")
    if amount <= 0:
        raise BadRequestError("Amount must be a positive integer")
    await controller.add_product_to_sale(sale_id, barcode, amount)
    return {"success": True}


@router.delete("/{sale_id}/items",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager, UserType.Cashier]))])
async def remove_product_from_sale(
    sale_id: int = Path(..., description="Sale ID"),
    barcode: str = Query(..., description="Product barcode"),
    amount: int = Query(..., description="Quantity to remove"),):
    """Remove or decrease the quantity of a product from an OPEN sale. Permissions: Administrator, ShopManager, Cashier"""
    if sale_id <= 0:
        raise BadRequestError("Invalid sale ID")
    if amount <= 0:
        raise BadRequestError("Amount must be a positive integer")
    await controller.remove_product_from_sale(sale_id, barcode, amount)
    return {"success": True}


@router.patch("/{sale_id}/discount",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(
        authenticate_user([
            UserType.Administrator,
            UserType.ShopManager,
            UserType.Cashier]))])
async def apply_discount_to_sale(
    sale_id: int = Path(..., description="Sale ID"),
    discount_rate: float = Query(..., description="Discount rate between 0 and 1")):
    """Apply a discount to the entire OPEN sale. Permissions: Administrator, ShopManager, Cashier"""
    if sale_id <= 0:
        raise BadRequestError("Invalid sale ID")
    if discount_rate < 0 or discount_rate >= 1:
        raise BadRequestError("Invalid discount rate")
    await controller.apply_discount(sale_id, discount_rate)
    return {"success": True}


@router.patch("/{sale_id}/items/{product_barcode}/discount",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(
        authenticate_user([
            UserType.Administrator,
            UserType.ShopManager,
            UserType.Cashier]))])
async def apply_product_discount_to_sale(
    sale_id: int = Path(..., description="Sale ID"),
    product_barcode: str = Path(..., description="Product barcode"),
    discount_rate: float = Query(..., description="Discount rate between 0 and 1"),):
    """Apply a discount to a specific product in an OPEN sale. Permissions: Administrator, ShopManager, Cashier"""
    if sale_id <= 0:
        raise BadRequestError("Invalid sale ID")
    if discount_rate < 0 or discount_rate >= 1:
        raise BadRequestError("Invalid discount rate")
    await controller.apply_product_discount(sale_id, product_barcode, discount_rate)
    return {"success": True}


@router.patch("/{sale_id}/close",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(
        authenticate_user([
            UserType.Administrator,
            UserType.ShopManager,
            UserType.Cashier]))])
async def close_sale(
    sale_id: int = Path(..., description="Sale ID"),):
    """Close an OPEN sale, changing its status to PENDING. Permissions: Administrator, ShopManager, Cashier"""
    if sale_id <= 0:
        raise BadRequestError("Invalid sale ID")
    await controller.close_sale(sale_id)
    return {"success": True}


@router.patch("/{sale_id}/pay",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(
        authenticate_user([
            UserType.Administrator,
            UserType.ShopManager,
            UserType.Cashier]))])
async def pay_sale(
    sale_id: int = Path(..., description="Sale ID"),
    cash_amount: float = Query(..., description="Cash amount received"),):
    """Pay a PENDING sale in cash. Marks the sale as PAID and updates the system balance. Returns the change to give back."""
    if sale_id <= 0:
        raise BadRequestError("Invalid sale ID")
    if cash_amount <= 0:
        raise BadRequestError("Invalid cash amount")
    change = await controller.pay_sale(sale_id, cash_amount)
    return {"success": True, "change": change}


@router.get("/{sale_id}/points",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(
        authenticate_user([
            UserType.Administrator,
            UserType.ShopManager,
            UserType.Cashier]))])
async def get_sale_points(
    sale_id: int = Path(..., description="Sale ID"),):
    """Compute loyalty points for a PAID sale. Permissions: Administrator, ShopManager, Cashier"""
    if sale_id <= 0:
        raise BadRequestError("Invalid sale ID")
    points = await controller.get_sale_points(sale_id)
    return {"points": points}

