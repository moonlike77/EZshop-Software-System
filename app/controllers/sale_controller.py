from app.repositories.sale_repository import SaleRepository
from app.models.DTO.sale_dto import SaleDTO
from app.services.mapper_service import saledao_to_dto
from typing import List


class SaleController:
    def __init__(self):
        self.repo = SaleRepository()

    async def start_sale(self) -> SaleDTO: 
        """Start a new sale transaction with initial status OPEN"""
        sale_dao = await self.repo.create_sale()
        return saledao_to_dto(sale_dao)


    async def list_sales(self) -> List[SaleDTO]:
        """Get all sale transactions."""
        sale_daos = await self.repo.list_sales()
        return [saledao_to_dto(sale) for sale in sale_daos]
    

    async def get_sale(self, sale_id: int) -> SaleDTO:
        """ Get a single sale by id."""
        sale_dao = await self.repo.get_sale(sale_id)
        return saledao_to_dto(sale_dao)
    

    async def delete_sale(self, sale_id: int) -> bool:
        """Delete a sale by id."""
        return await self.repo.delete_sale(sale_id)
    

    async def add_product_to_sale(self, sale_id: int, barcode: str, amount: int) -> bool:
        """Add a product to an OPEN sale."""
        return await self.repo.add_product_to_sale(sale_id, barcode, amount)
    

    async def remove_product_from_sale(self, sale_id: int, barcode: str, amount: int) -> bool:
        """Remove or decrease quantity of a product from an OPEN sale."""
        return await self.repo.remove_product_from_sale(sale_id, barcode, amount)


    async def apply_discount(self, sale_id: int, discount_rate: float) -> bool:
        """Apply a discount to an OPEN sale."""
        return await self.repo.apply_discount(sale_id, discount_rate)
    

    async def apply_product_discount(self, sale_id: int, product_barcode: str, discount_rate: float) -> bool:
        """Apply a discount to a single product in an OPEN sale."""
        return await self.repo.apply_product_discount(sale_id, product_barcode, discount_rate)


    async def close_sale(self, sale_id: int) -> bool:
        """Close an OPEN sale (set status to PENDING)."""
        return await self.repo.close_sale(sale_id)


    async def pay_sale(self, sale_id: int, cash_amount: float) -> float:
        """Pay a PENDING sale and return the change."""
        return await self.repo.pay_sale(sale_id, cash_amount)


    async def get_sale_points(self, sale_id: int) -> int:
        """Compute loyalty points for a PAID sale."""
        return await self.repo.get_sale_points(sale_id)
