from typing import List, Optional
from app.repositories.product_repository import ProductRepository
from app.models.DTO.product_dto import (
    ProductTypeCreateDTO,
    ProductTypeUpdateDTO,
    ProductTypeResponseDTO
)


class ProductController:
    def __init__(self):
        self.repository = ProductRepository()

    async def create_product(self, product_dto: ProductTypeCreateDTO) -> ProductTypeResponseDTO:
        return await self.repository.create_product_from_dto(product_dto)

    async def get_product_by_id(self, product_id: int) -> ProductTypeResponseDTO:
        return await self.repository.get_product_by_id_dto(product_id)

    async def get_product_by_barcode(self, barcode: str) -> ProductTypeResponseDTO:
        return await self.repository.get_product_by_barcode_dto(barcode)

    async def get_all_products(self) -> List[ProductTypeResponseDTO]:
        return await self.repository.get_all_products_dto()

    async def search_products_by_description(self, query: str) -> List[ProductTypeResponseDTO]:
        return await self.repository.search_products_by_description_dto(query)

    async def update_product(
        self,
        product_id: int,
        product_dto: ProductTypeUpdateDTO
    ) -> ProductTypeResponseDTO:
        return await self.repository.update_product_from_dto(product_id, product_dto)

    async def update_quantity(self, product_id: int, quantity_change: int) -> ProductTypeResponseDTO:
        return await self.repository.update_quantity_dto(product_id, quantity_change)

    async def update_position(self, product_id: int, position: str) -> ProductTypeResponseDTO:
        return await self.repository.update_position_dto(product_id, position)

    async def delete_product(self, product_id: int) -> bool:
        return await self.repository.delete_product(product_id)
