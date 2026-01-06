from typing import List
from app.repositories.order_repository import OrderRepository
from app.models.DAO.product_dao import ProductDAO
from app.models.DTO.order_dto import OrderCreateDTO, OrderPayForDTO, OrderResponseDTO
from app.services.mapper_service import orderdao_to_responsedto
from app.models.errors.notfound_error import NotFoundError
from app.models.errors.bad_request import BadRequestError


class OrderController:
    def __init__(self):
        self.repository = OrderRepository()

    async def create_order(self, order_dto: OrderCreateDTO) -> OrderResponseDTO:
        """Create a new order from DTO"""
        # Get repository for product lookup
        from app.repositories.product_repository import ProductRepository
        product_repo = ProductRepository()
        
        # Get product by barcode
        product = await product_repo.get_product_by_barcode(order_dto.product_barcode)
        
        # Create order in repository
        order_dao = await self.repository.create_order(
            product_id=product.id,
            quantity=order_dto.quantity,
            price_per_unit=order_dto.price_per_unit
        )
        
        # Convert DAO to DTO
        return orderdao_to_responsedto(order_dao, product.barcode)

    async def create_and_pay_order(self, order_dto: OrderPayForDTO) -> OrderResponseDTO:
        """Create and immediately pay for an order"""
        from app.repositories.product_repository import ProductRepository
        product_repo = ProductRepository()
        
        # Get product by barcode
        product = await product_repo.get_product_by_barcode(order_dto.product_barcode)
        
        # Create order
        order_dao = await self.repository.create_order(
            product_id=product.id,
            quantity=order_dto.quantity,
            price_per_unit=order_dto.price_per_unit
        )
        
        # Pay for order
        paid_order = await self.repository.pay_order(order_dao.id)
        
        # Convert to DTO
        return orderdao_to_responsedto(paid_order, product.barcode)

    async def get_order_by_id(self, order_id: int) -> OrderResponseDTO:
        """Get order by ID and convert to DTO"""
        order_dao = await self.repository.get_order(order_id)
        
        # Get product barcode from the relationship
        product = order_dao.product
        return orderdao_to_responsedto(order_dao, product.barcode)

    async def get_all_orders(self) -> List[OrderResponseDTO]:
        """Get all orders and convert to DTOs"""
        orders_dao = await self.repository.get_all_orders()
        return [orderdao_to_responsedto(order, order.product.barcode) for order in orders_dao]

    async def pay_order(self, order_id: int) -> OrderResponseDTO:
        """Pay for an order"""
        order_dao = await self.repository.pay_order(order_id)
        product = order_dao.product
        return orderdao_to_responsedto(order_dao, product.barcode)

    async def record_order_arrival(self, order_id: int) -> OrderResponseDTO:
        """Record arrival for an order"""
        order_dao = await self.repository.record_order_arrival(order_id)
        product = order_dao.product
        return orderdao_to_responsedto(order_dao, product.barcode)

    async def delete_order(self, order_id: int) -> bool:
        """Delete an order"""
        return await self.repository.delete_order(order_id)
