from fastapi import APIRouter, HTTPException, status, Depends, Path
from typing import List
from app.models.DTO.order_dto import (
    OrderCreateDTO,
    OrderPayForDTO,
    OrderResponseDTO,
    ReorderWarningCreateDTO
)
from app.models.user_type import UserType
from app.controllers.order_controller import OrderController
from app.middleware.auth_middleware import authenticate_user
from app.config.config import ROUTES
from fastapi import Response
from app.models.errors.notfound_error import NotFoundError
from app.models.errors.bad_request import BadRequestError
from app.models.errors.app_error import AppError


router = APIRouter(prefix=ROUTES['V1_ORDERS'], tags=["Orders"])
controller = OrderController()


@router.post("/",
    response_model=OrderResponseDTO,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager]))])
async def issue_order(order: OrderCreateDTO):
    try:
        return await controller.create_order(order)
    except AppError as e:
        raise HTTPException(status_code=e.status, detail=str(e))


@router.get("/",
    response_model=List[OrderResponseDTO],
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager]))])
async def list_orders():
    return await controller.get_all_orders()


@router.get("/{order_id}",
    response_model=OrderResponseDTO,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager]))])
async def get_order(order_id: int = Path(..., gt=0)):
    try:
        return await controller.get_order_by_id(order_id)
    except AppError as e:
        raise HTTPException(status_code=e.status, detail=str(e))


@router.post("/payfor",
    response_model=OrderResponseDTO,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager]))])
async def pay_for_order(order: OrderPayForDTO):
    try:
        return await controller.create_and_pay_order(order)
    except AppError as e:
        raise HTTPException(status_code=e.status, detail=str(e))


@router.patch("/{order_id}/pay",
    response_model=OrderResponseDTO,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager]))])
async def pay_order(order_id: int = Path(..., gt=0)):
    try:
        return await controller.pay_order(order_id)
    except AppError as e:
        raise HTTPException(status_code=e.status, detail=str(e))


@router.patch("/{order_id}/arrival",
    response_model=OrderResponseDTO,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager]))])
async def record_order_arrival(order_id: int = Path(..., gt=0)):
    try:
        return await controller.record_order_arrival(order_id)
    except AppError as e:
        raise HTTPException(status_code=e.status, detail=str(e))


@router.delete("/{order_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(authenticate_user([UserType.Administrator]))])
async def delete_order(order_id: int = Path(..., gt=0)):
    try:
        await controller.delete_order(order_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Order with id '{order_id}' not found")


@router.post("/reorder",
    response_model=OrderResponseDTO,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager]))])
async def issue_reorder_warning(reorder: ReorderWarningCreateDTO):
    try:
        return await controller.issue_reorder_warning(reorder)
    except AppError as e:
        raise HTTPException(status_code=e.status, detail=str(e))


@router.patch("/{order_id}/pay-reorder",
    response_model=OrderResponseDTO,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager]))])
async def pay_reorder_warning(order_id: int = Path(..., gt=0)):
    try:
        return await controller.pay_reorder_warning(order_id)
    except AppError as e:
        raise HTTPException(status_code=e.status, detail=str(e))
