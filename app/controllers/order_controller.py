from typing import List, Optional
from app.repositories.order_repository import OrderRepository
from app.models.DTO.order_dto import (
    OrderCreateDTO,
    OrderPayForDTO,
    OrderResponseDTO
)


class OrderController:
    def __init__(self):
        self.repository = OrderRepository()

    async def create_order(self, order_dto: OrderCreateDTO) -> OrderResponseDTO:
        return await self.repository.create_order_from_dto(order_dto)

    async def create_and_pay_order(self, order_dto: OrderPayForDTO) -> OrderResponseDTO:
        return await self.repository.create_and_pay_order_from_dto(order_dto)

    async def get_order_by_id(self, order_id: int) -> OrderResponseDTO:
        return await self.repository.get_order_by_id_dto(order_id)

    async def get_all_orders(self) -> List[OrderResponseDTO]:
        return await self.repository.get_all_orders_dto()

    async def get_orders_by_status(self, status: str) -> List[OrderResponseDTO]:
        return await self.repository.get_orders_by_status_dto(status)

    async def pay_order(self, order_id: int) -> OrderResponseDTO:
        return await self.repository.pay_order_dto(order_id)

    async def record_order_arrival(self, order_id: int) -> OrderResponseDTO:
        return await self.repository.record_order_arrival_dto(order_id)

    async def delete_order(self, order_id: int) -> bool:
        return await self.repository.delete_order(order_id)
