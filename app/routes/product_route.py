from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from app.models.DTO.product_dto import (
    ProductTypeCreateDTO,
    ProductTypeUpdateDTO,
    ProductTypeResponseDTO
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
    response_model=ProductTypeResponseDTO,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager]))])
async def create_product(product: ProductTypeCreateDTO):
    if not product.description or product.description.strip() == '':
        raise BadRequestError('Description is mandatory')
    if not product.barcode or product.barcode.strip() == '':
        raise BadRequestError('Barcode is mandatory')
    if product.price_per_unit is None or product.price_per_unit <= 0:
        raise BadRequestError('Price per unit must be greater than 0')

    return await controller.create_product(product)


@router.get("/",
    response_model=List[ProductTypeResponseDTO],
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager, UserType.Cashier]))])
async def list_products():
    return await controller.get_all_products()


@router.get("/search",
    response_model=List[ProductTypeResponseDTO],
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager]))])
async def search_products(query: str):
    if not query or query.strip() == '':
        raise BadRequestError('Search query cannot be empty')

    return await controller.search_products_by_description(query)


@router.get("/barcode/{barcode}",
    response_model=ProductTypeResponseDTO,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager]))])
async def get_product_by_barcode(barcode: str):
    try:
        return await controller.get_product_by_barcode(barcode)
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product with barcode '{barcode}' not found")


@router.get("/{product_id}",
    response_model=ProductTypeResponseDTO,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager, UserType.Cashier]))])
async def get_product(product_id: int):
    try:
        return await controller.get_product_by_id(product_id)
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product with id '{product_id}' not found")


@router.put("/{product_id}",
    response_model=ProductTypeResponseDTO,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager]))])
async def update_product(product_id: int, product: ProductTypeUpdateDTO):
    try:
        return await controller.update_product(product_id, product)
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product with id '{product_id}' not found")
    except BadRequestError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/{product_id}/position",
    response_model=ProductTypeResponseDTO,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager]))])
async def update_product_position(product_id: int, position: str):
    try:
        return await controller.update_position(product_id, position)
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product with id '{product_id}' not found")
    except BadRequestError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/{product_id}/quantity",
    response_model=ProductTypeResponseDTO,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager]))])
async def update_product_quantity(product_id: int, quantity: int):
    try:
        return await controller.update_quantity(product_id, quantity)
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product with id '{product_id}' not found")
    except BadRequestError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager]))])
async def delete_product(product_id: int):
    try:
        success = await controller.delete_product(product_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product with id '{product_id}' not found")
