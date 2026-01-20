from typing import List, Optional
from app.repositories.product_repository import ProductRepository
from app.models.DTO.product_dto import ProductCreateDTO, ProductUpdateDTO, ProductResponseDTO
from app.services.mapper_service import productdao_to_responsedto
from app.models.errors.bad_request import BadRequestError


class ProductController:
    def __init__(self):
        self.repo = ProductRepository()

    async def create_product(self, product_dto: ProductCreateDTO) -> ProductResponseDTO:
        created = await self.repo.create_product(
            description=product_dto.description,
            barcode=product_dto.barcode,
            price_per_unit=product_dto.price_per_unit,
            note=product_dto.note,
            quantity=product_dto.quantity or 0,
            position=product_dto.position
        )
        return productdao_to_responsedto(created)

    async def get_product_by_id(self, product_id: int) -> ProductResponseDTO:
        dao = await self.repo.get_product_by_id(product_id)
        return productdao_to_responsedto(dao)

    async def get_product_by_barcode(self, barcode: str) -> ProductResponseDTO:
        dao = await self.repo.get_product_by_barcode(barcode)
        return productdao_to_responsedto(dao)

    async def get_all_products(self) -> List[ProductResponseDTO]:
        daos = await self.repo.get_all_products()
        return [productdao_to_responsedto(dao) for dao in daos]

    async def search_products_by_description(self, query: str) -> List[ProductResponseDTO]:
        daos = await self.repo.search_products_by_description(query)
        return [productdao_to_responsedto(dao) for dao in daos]

    async def update_product(
        self,
        product_id: int,
        product_dto: ProductUpdateDTO
    ) -> ProductResponseDTO:
        if product_dto.quantity is not None:
            raise BadRequestError("Quantity cannot be updated with PUT /products; use PATCH /products/{id}/quantity")
        if product_dto.position is not None:
            raise BadRequestError("Position cannot be updated with PUT /products; use PATCH /products/{id}/position")

        updated = await self.repo.update_product(
            product_id=product_id,
            description=product_dto.description,
            barcode=product_dto.barcode,
            price_per_unit=product_dto.price_per_unit,
            note=product_dto.note,
            quantity=product_dto.quantity,
            position=product_dto.position
        )
        return productdao_to_responsedto(updated)

    async def update_quantity(self, product_id: int, quantity_change: int) -> ProductResponseDTO:
        updated = await self.repo.update_quantity(product_id, quantity_change)
        return productdao_to_responsedto(updated)

    async def update_position(self, product_id: int, position: str) -> ProductResponseDTO:
        updated = await self.repo.update_position(product_id, position)
        return productdao_to_responsedto(updated)

    async def delete_product(self, product_id: int) -> bool:
        return await self.repo.delete_product(product_id)
