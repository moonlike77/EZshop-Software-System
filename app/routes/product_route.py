from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from app.models.DTO.product_dto import (
    ProductCreateDTO,
    ProductUpdateDTO,
    ProductResponseDTO
)
from app.models.user_type import UserType
from app.controllers.product_controller import ProductController
from app.middleware.auth_middleware import authenticate_user
from app.config.config import ROUTES
from fastapi import Response
from app.models.errors.notfound_error import NotFoundError
from app.models.errors.bad_request import BadRequestError


router = APIRouter(prefix=ROUTES['V1_PRODUCTS'], tags=["Products"])
controller = ProductController()


@router.post("/",
    response_model=ProductResponseDTO,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager]))])
async def create_product(product: ProductCreateDTO):
    """
    Create a new product type.

    - Permissions: Administrator, ShopManager
    - Request body: ProductCreateDTO (contains description, barcode, price_per_unit, ...)
    - Returns: Created product as ProductResponseDTO
    - Raises:
      - BadRequestError: when mandatory fields are missing or invalid
      - ConflictError: when barcode already exists
    - Status code: 201 Created
    """
    try:
        return await controller.create_product(product)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/",
    response_model=List[ProductResponseDTO],
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager, UserType.Cashier]))])
async def list_products():
    """
    List all product types.

    - Permissions: Administrator, ShopManager, Cashier
    - Returns: List of ProductResponseDTO
    - Status code: 200 OK
    """
    return await controller.get_all_products()


@router.get("/search",
    response_model=List[ProductResponseDTO],
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager]))])
async def search_products(query: str):
    """
    Search product types by description.

    - Permissions: Administrator, ShopManager
    - Query parameter: query (search string)
    - Returns: List of matching ProductResponseDTO
    - Status code: 200 OK
    """
    return await controller.search_products_by_description(query)


@router.get("/barcode/{barcode}",
    response_model=ProductResponseDTO,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager, UserType.Cashier]))])
async def get_product_by_barcode(barcode: str):
    """
    Get product type by barcode.

    - Permissions: Administrator, ShopManager, Cashier
    - Path parameter: barcode (string)
    - Returns: ProductResponseDTO
    - Raises:
      - NotFoundError: when product with barcode not found
    - Status code: 200 OK
    """
    try:
        return await controller.get_product_by_barcode(barcode)
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product with barcode '{barcode}' not found")


@router.get("/{product_id}",
    response_model=ProductResponseDTO,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager, UserType.Cashier]))])
async def get_product(product_id: int):
    """
    Get product type by ID.

    - Permissions: Administrator, ShopManager, Cashier
    - Path parameter: product_id (int)
    - Returns: ProductResponseDTO
    - Raises:
      - NotFoundError: when product not found
    - Status code: 200 OK
    """
    try:
        return await controller.get_product_by_id(product_id)
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product with id {product_id} not found")


@router.put("/{product_id}",
    response_model=ProductResponseDTO,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager]))])
async def update_product(product_id: int, product: ProductUpdateDTO):
    """
    Update product type by ID.

    - Permissions: Administrator, ShopManager
    - Path parameter: product_id (int)
    - Request body: ProductUpdateDTO (all fields optional)
    - Returns: Updated ProductResponseDTO
    - Raises:
      - NotFoundError: when product not found
      - BadRequestError: when data validation fails
    - Status code: 200 OK
    """
    try:
        return await controller.update_product(product_id, product)
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product with id {product_id} not found")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/{product_id}/position",
    response_model=ProductResponseDTO,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager]))])
async def update_product_position(product_id: int, position: str):
    """
    Update product type position.

    - Permissions: Administrator, ShopManager
    - Path parameter: product_id (int)
    - Query parameter: position (format: digits-letters-digits, e.g., '1-A-2')
    - Returns: Updated ProductResponseDTO
    - Raises:
      - NotFoundError: when product not found
      - BadRequestError: when position format invalid
    - Status code: 200 OK
    """
    try:
        return await controller.update_position(product_id, position)
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product with id {product_id} not found")
    except BadRequestError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/{product_id}/quantity",
    response_model=ProductResponseDTO,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager]))])
async def update_product_quantity(product_id: int, quantity: int):
    """
    Update product type quantity.

    - Permissions: Administrator, ShopManager
    - Path parameter: product_id (int)
    - Query parameter: quantity (int, positive or negative)
    - Returns: Updated ProductResponseDTO
    - Raises:
      - NotFoundError: when product not found
      - BadRequestError: when quantity would become negative
    - Status code: 200 OK
    """
    try:
        return await controller.update_quantity(product_id, quantity)
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product with id {product_id} not found")
    except BadRequestError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(authenticate_user([UserType.Administrator]))])
async def delete_product(product_id: int):
    """
    Delete product type by ID.

    - Permissions: Administrator
    - Path parameter: product_id (int)
    - Returns: No content
    - Raises:
      - NotFoundError: when product not found
    - Status code: 204 No Content
    """
    try:
        await controller.delete_product(product_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product with id {product_id} not found")
