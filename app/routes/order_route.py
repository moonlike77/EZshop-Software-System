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
    """
    Issue a new order.

    - Permissions: Administrator, ShopManager
    - Request body: OrderCreateDTO (contains product_barcode, quantity, price_per_unit)
    - Returns: Created order as OrderResponseDTO with status ISSUED
    - Raises:
      - BadRequestError: when mandatory fields are missing or invalid
      - NotFoundError: when product with barcode not found
    - Status code: 201 Created
    """

    try:
        return await controller.create_order(order)
    except AppError as e:
        raise HTTPException(status_code=e.status, detail=str(e))


@router.get("/",
    response_model=List[OrderResponseDTO],
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager]))])
async def list_orders():
    """
    List all orders.

    - Permissions: Administrator, ShopManager
    - Returns: List of OrderResponseDTO
    - Status code: 200 OK
    """
    return await controller.get_all_orders()


@router.get("/{order_id}",
    response_model=OrderResponseDTO,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager]))])
async def get_order(order_id: int = Path(..., gt=0)):
    """
    Get a specific order by ID.

    - Permissions: Administrator, ShopManager
    - Path parameter: order_id (int)
    - Returns: OrderResponseDTO
    - Raises:
      - NotFoundError: when order not found
    - Status code: 200 OK
    """
    try:
        return await controller.get_order_by_id(order_id)
    except AppError as e:
        raise HTTPException(status_code=e.status, detail=str(e))


@router.post("/payfor",
    response_model=OrderResponseDTO,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager]))])
async def pay_for_order(order: OrderPayForDTO):
    """
    Create and immediately pay for an order.

    - Permissions: Administrator, ShopManager
    - Request body: OrderPayForDTO (contains product_barcode, quantity, price_per_unit)
    - Returns: Created order as OrderResponseDTO with status PAID
    - Raises:
      - BadRequestError: when mandatory fields invalid or insufficient balance
      - NotFoundError: when product with barcode not found
    - Status code: 201 Created
    """
    try:
        return await controller.create_and_pay_order(order)
    except AppError as e:
        raise HTTPException(status_code=e.status, detail=str(e))


@router.patch("/{order_id}/pay",
    response_model=OrderResponseDTO,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager]))])
async def pay_order(order_id: int = Path(..., gt=0)):
    """
    Pay for an existing ISSUED order.

    - Permissions: Administrator, ShopManager
    - Path parameter: order_id (int)
    - Returns: Updated order as OrderResponseDTO with status PAID
    - Raises:
      - NotFoundError: when order not found
      - BadRequestError: when order not in ISSUED state or insufficient balance
    - Status code: 201 Created
    """
    try:
        return await controller.pay_order(order_id)
    except AppError as e:
        raise HTTPException(status_code=e.status, detail=str(e))


@router.patch("/{order_id}/arrival",
    response_model=OrderResponseDTO,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager]))])
async def record_order_arrival(order_id: int = Path(..., gt=0)):
    """
    Record the arrival of a PAID order.

    - Permissions: Administrator, ShopManager
    - Path parameter: order_id (int)
    - Returns: Updated order as OrderResponseDTO with status COMPLETED
    - Raises:
      - NotFoundError: when order or product not found
      - BadRequestError: when order not in PAID state or product has no location assigned
    - Status code: 201 Created
    """
    try:
        return await controller.record_order_arrival(order_id)
    except AppError as e:
        raise HTTPException(status_code=e.status, detail=str(e))


@router.delete("/{order_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(authenticate_user([UserType.Administrator]))])
async def delete_order(order_id: int = Path(..., gt=0)):
    """
    Delete an order by ID.

    - Permissions: Administrator only
    - Path parameter: order_id (int)
    - Returns: No content
    - Raises:
      - NotFoundError: when order not found
    - Status code: 204 No Content
    """
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
    """
    FR4.3: Issue a reorder warning for a product type.

    - Permissions: Administrator, ShopManager
    - Request body: ReorderWarningCreateDTO (contains product_barcode, quantity, price_per_unit)
    - Returns: Created reorder warning as OrderResponseDTO with status ISSUED and is_reorder_warning=True
    - Raises:
      - BadRequestError: when mandatory fields are missing or invalid
      - NotFoundError: when product with barcode not found
    - Status code: 201 Created
    """
    try:
        return await controller.issue_reorder_warning(reorder)
    except AppError as e:
        raise HTTPException(status_code=e.status, detail=str(e))


@router.patch("/{order_id}/pay-reorder",
    response_model=OrderResponseDTO,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager]))])
async def pay_reorder_warning(order_id: int = Path(..., gt=0)):
    """
    FR4.5: Pay for an issued reorder warning.

    - Permissions: Administrator, ShopManager
    - Path parameter: order_id (int)
    - Returns: Updated reorder warning as OrderResponseDTO with status PAID
    - Raises:
      - NotFoundError: when order not found
      - BadRequestError: when order is not a reorder warning or not in ISSUED state or insufficient balance
    - Status code: 201 Created
    """
    try:
        return await controller.pay_reorder_warning(order_id)
    except AppError as e:
        raise HTTPException(status_code=e.status, detail=str(e))
