from typing import List, Optional
from app.services.order_service import OrderService
from app.models.DTO.order_dto import (
    OrderCreateDTO,
    OrderPayForDTO,
    OrderResponseDTO
)


class OrderController:
    def __init__(self):
        self.service = OrderService()

    async def create_order(self, order_dto: OrderCreateDTO) -> OrderResponseDTO:
        return await self.service.create_order(order_dto)

    async def create_and_pay_order(self, order_dto: OrderPayForDTO) -> OrderResponseDTO:
        return await self.service.create_and_pay_order(order_dto)

    async def get_order_by_id(self, order_id: int) -> OrderResponseDTO:
        return await self.service.get_order_by_id(order_id)

    async def get_all_orders(self) -> List[OrderResponseDTO]:
        return await self.service.get_all_orders()

    async def get_orders_by_status(self, status: str) -> List[OrderResponseDTO]:
        return await self.service.get_orders_by_status(status)

    async def pay_order(self, order_id: int) -> OrderResponseDTO:
        return await self.service.pay_order(order_id)

    async def record_order_arrival(self, order_id: int) -> OrderResponseDTO:
        return await self.service.record_order_arrival(order_id)

    async def delete_order(self, order_id: int) -> bool:
        return await self.service.delete_order(order_id)
