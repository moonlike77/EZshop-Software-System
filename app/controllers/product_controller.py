from typing import List, Optional
from app.services.product_service import ProductService
from app.models.DTO.product_dto import (
    ProductTypeCreateDTO,
    ProductTypeUpdateDTO,
    ProductTypeResponseDTO
)


class ProductController:
    def __init__(self):
        self.service = ProductService()

    async def create_product(self, product_dto: ProductTypeCreateDTO) -> ProductTypeResponseDTO:
        return await self.service.create_product(product_dto)

    async def get_product_by_id(self, product_id: int) -> ProductTypeResponseDTO:
        return await self.service.get_product_by_id(product_id)

    async def get_product_by_barcode(self, barcode: str) -> ProductTypeResponseDTO:
        return await self.service.get_product_by_barcode(barcode)

    async def get_all_products(self) -> List[ProductTypeResponseDTO]:
        return await self.service.get_all_products()

    async def search_products_by_description(self, query: str) -> List[ProductTypeResponseDTO]:
        return await self.service.search_products_by_description(query)

    async def update_product(
        self,
        product_id: int,
        product_dto: ProductTypeUpdateDTO
    ) -> ProductTypeResponseDTO:
        return await self.service.update_product(product_id, product_dto)

    async def update_quantity(self, product_id: int, quantity_change: int) -> ProductTypeResponseDTO:
        return await self.service.update_quantity(product_id, quantity_change)

    async def update_position(self, product_id: int, position: str) -> ProductTypeResponseDTO:
        return await self.service.update_position(product_id, position)

    async def delete_product(self, product_id: int) -> bool:
        return await self.service.delete_product(product_id)
