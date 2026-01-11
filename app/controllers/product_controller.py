from typing import List, Optional
from app.repositories.product_repository import ProductRepository
from app.models.DTO.product_dto import ProductCreateDTO, ProductUpdateDTO, ProductResponseDTO
from app.services.mapper_service import productdao_to_responsedto


class ProductController:
    def __init__(self):
        self.repo = ProductRepository()

    async def create_product(self, product_dto: ProductCreateDTO) -> ProductResponseDTO:
        """Create product - throws ConflictError if barcode exists"""
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
        """Get product by ID - throws NotFoundError if not found"""
        dao = await self.repo.get_product_by_id(product_id)
        return productdao_to_responsedto(dao)

    async def get_product_by_barcode(self, barcode: str) -> ProductResponseDTO:
        """Get product by barcode - throws NotFoundError if not found"""
        dao = await self.repo.get_product_by_barcode(barcode)
        return productdao_to_responsedto(dao)

    async def get_all_products(self) -> List[ProductResponseDTO]:
        """Get all products"""
        daos = await self.repo.get_all_products()
        return [productdao_to_responsedto(dao) for dao in daos]

    async def search_products_by_description(self, query: str) -> List[ProductResponseDTO]:
        """Search products by description"""
        daos = await self.repo.search_products_by_description(query)
        return [productdao_to_responsedto(dao) for dao in daos]

    async def update_product(
        self,
        product_id: int,
        product_dto: ProductUpdateDTO
    ) -> ProductResponseDTO:
        """Update product - throws NotFoundError if not found, ConflictError if new barcode exists"""
        updated = await self.repo.update_product(
            product_id=product_id,
            description=product_dto.description,
            barcode=product_dto.barcode,
            price_per_unit=product_dto.price_per_unit,
            note=product_dto.note,
            quantity=product_dto.quantity,
            position=product_dto.position
        )
        return productdao_to_responsedto(updated) if updated else None

    async def update_quantity(self, product_id: int, quantity_change: int) -> ProductResponseDTO:
        """Update product quantity"""
        updated = await self.repo.update_quantity(product_id, quantity_change)
        return productdao_to_responsedto(updated)

    async def update_position(self, product_id: int, position: str) -> ProductResponseDTO:
        """Update product position"""
        updated = await self.repo.update_position(product_id, position)
        return productdao_to_responsedto(updated)

    async def delete_product(self, product_id: int) -> bool:
        """Delete product - throws NotFoundError if not found"""
        return await self.repo.delete_product(product_id)
