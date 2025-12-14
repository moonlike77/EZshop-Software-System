from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from app.models.DTO.order_dto import (
    OrderCreateDTO,
    OrderPayForDTO,
    OrderResponseDTO
)
from app.models.user_type import UserType
from app.controllers.order_controller import OrderController
from app.middleware.auth_middleware import authenticate_user
from app.config.config import ROUTES
from fastapi import Response
from app.models.errors.notfound_error import NotFoundError
from app.models.errors.bad_request import BadRequestError


router = APIRouter(prefix=ROUTES['V1_ORDERS'], tags=["Orders"])
controller = OrderController()


@router.post("/",
    response_model=OrderResponseDTO,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager]))])
async def issue_order(order: OrderCreateDTO):
    if not order.product_barcode or order.product_barcode.strip() == '':
        raise BadRequestError('Product barcode is mandatory')
    if order.quantity is None or order.quantity <= 0:
        raise BadRequestError('Quantity must be greater than 0')
    if order.price_per_unit is None or order.price_per_unit <= 0:
        raise BadRequestError('Price per unit must be greater than 0')

    try:
        return await controller.create_order(order)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/",
    response_model=List[OrderResponseDTO],
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager]))])
async def list_orders():
    return await controller.get_all_orders()


@router.post("/payfor",
    response_model=OrderResponseDTO,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager]))])
async def pay_for_order(order: OrderPayForDTO):
    if not order.product_barcode or order.product_barcode.strip() == '':
        raise BadRequestError('Product barcode is mandatory')
    if order.quantity is None or order.quantity <= 0:
        raise BadRequestError('Quantity must be greater than 0')
    if order.price_per_unit is None or order.price_per_unit <= 0:
        raise BadRequestError('Price per unit must be greater than 0')

    try:
        return await controller.create_and_pay_order(order)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.patch("/{order_id}/pay",
    response_model=OrderResponseDTO,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager]))])
async def pay_order(order_id: int):
    try:
        return await controller.pay_order(order_id)
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Order with id '{order_id}' not found")
    except BadRequestError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/{order_id}/arrival",
    response_model=OrderResponseDTO,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager]))])
async def record_order_arrival(order_id: int):
    try:
        return await controller.record_order_arrival(order_id)
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Order with id '{order_id}' not found")
    except BadRequestError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
