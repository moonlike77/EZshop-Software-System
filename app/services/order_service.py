from app.repositories.order_repository import OrderRepository
from app.models.DAO.order_dao import OrderDAO, OrderStatusEnum
from app.models.DTO.order_dto import (
    OrderCreateDTO,
    OrderPayForDTO,
    OrderResponseDTO
)
from typing import Optional


class OrderService:

    def __init__(self, repository: Optional[OrderRepository] = None):
        self.repository = repository or OrderRepository()

    async def create_order(self, order_dto: OrderCreateDTO) -> OrderResponseDTO:
        # Validate quantity
        if order_dto.quantity <= 0:
            from app.models.errors.bad_request import BadRequestError
            raise BadRequestError("Quantity must be greater than 0")

        # Validate price
        if order_dto.price_per_unit <= 0:
            from app.models.errors.bad_request import BadRequestError
            raise BadRequestError("Price per unit must be greater than 0")

        order_dao = await self.repository.create_order(
            product_barcode=order_dto.product_barcode,
            quantity=order_dto.quantity,
            price_per_unit=order_dto.price_per_unit,
            status=OrderStatusEnum.ISSUED
        )

        return self._dao_to_response_dto(order_dao)

    async def create_and_pay_order(self, order_dto: OrderPayForDTO) -> OrderResponseDTO:
        # Validate quantity
        if order_dto.quantity <= 0:
            from app.models.errors.bad_request import BadRequestError
            raise BadRequestError("Quantity must be greater than 0")

        # Validate price
        if order_dto.price_per_unit <= 0:
            from app.models.errors.bad_request import BadRequestError
            raise BadRequestError("Price per unit must be greater than 0")

        order_dao = await self.repository.create_order(
            product_barcode=order_dto.product_barcode,
            quantity=order_dto.quantity,
            price_per_unit=order_dto.price_per_unit,
            status=OrderStatusEnum.PAID
        )

        return self._dao_to_response_dto(order_dao)

    async def get_order_by_id(self, order_id: int) -> OrderResponseDTO:
        order_dao = await self.repository.get_order_by_id(order_id)
        return self._dao_to_response_dto(order_dao)

    async def get_all_orders(self) -> list[OrderResponseDTO]:
        orders_dao = await self.repository.get_all_orders()
        return [self._dao_to_response_dto(o) for o in orders_dao]

    async def get_orders_by_status(self, status: str) -> list[OrderResponseDTO]:
        try:
            status_enum = OrderStatusEnum[status.upper()]
        except KeyError:
            from app.models.errors.bad_request import BadRequestError
            raise BadRequestError(f"Invalid status. Must be one of: ISSUED, PAID, COMPLETED")

        orders_dao = await self.repository.get_orders_by_status(status_enum)
        return [self._dao_to_response_dto(o) for o in orders_dao]

    async def pay_order(self, order_id: int) -> OrderResponseDTO:
        order_dao = await self.repository.pay_order(order_id)
        return self._dao_to_response_dto(order_dao)

    async def record_order_arrival(self, order_id: int) -> OrderResponseDTO:
        order_dao = await self.repository.record_order_arrival(order_id)
        return self._dao_to_response_dto(order_dao)

    async def delete_order(self, order_id: int) -> bool:
        return await self.repository.delete_order(order_id)

    def _dao_to_response_dto(self, order_dao: OrderDAO) -> OrderResponseDTO:
        return OrderResponseDTO(
            id=order_dao.id,
            product_barcode=order_dao.product_barcode,
            quantity=order_dao.quantity,
            price_per_unit=order_dao.price_per_unit,
            status=order_dao.status.value,
            issue_date=order_dao.issue_date
        )
