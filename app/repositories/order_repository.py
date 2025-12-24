import logging
from datetime import datetime
from typing import Optional, List, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import AsyncSessionLocal
from app.models.DAO.order_dao import OrderDAO, OrderStatus
from app.models.DAO.product_type_dao import ProductTypeDAO
from app.models.DAO.system_dao import SystemInfoDAO
from app.models.DTO.order_dto import OrderCreateDTO, OrderResponseDTO
from app.models.errors.bad_request import BadRequestError
from app.models.errors.notfound_error import NotFoundError
from app.utils import find_or_throw_not_found


logger = logging.getLogger(__name__)


class OrderRepository:

    def __init__(self, session: Optional[AsyncSession] = None):
        self._session = session

    async def _get_session(self) -> AsyncSession:
        return self._session or AsyncSessionLocal()

    async def _get_system_info(self, session: AsyncSession) -> SystemInfoDAO:
        result = await session.execute(select(SystemInfoDAO))
        system_info = result.scalars().first()
        if not system_info:
            system_info = SystemInfoDAO(balance=0.0)
            session.add(system_info)
            await session.flush()
        return system_info

    @staticmethod
    def _to_response(order: OrderDAO, product_barcode: str) -> OrderResponseDTO:
        return OrderResponseDTO(
            id=order.id,
            product_barcode=product_barcode,
            quantity=order.quantity,
            price_per_unit=order.price_per_unit,
            status=order.status,
            issue_date=order.issue_date,
        )

    async def _get_order_and_barcode(self, session: AsyncSession, order_id: int) -> Tuple[OrderDAO, str]:
        stmt = (
            select(OrderDAO, ProductTypeDAO.barcode)
            .join(ProductTypeDAO, ProductTypeDAO.id == OrderDAO.product_id)
            .where(OrderDAO.id == order_id)
        )
        result = await session.execute(stmt)
        row = result.first()
        if not row:
            raise NotFoundError(f"Order with id '{order_id}' not found")
        order, barcode = row
        return order, barcode

    async def issue_order(self, dto: OrderCreateDTO) -> OrderResponseDTO:
        async with await self._get_session() as session:
            result = await session.execute(
                select(ProductTypeDAO).where(ProductTypeDAO.barcode == dto.product_barcode)
            )
            product = result.scalars().first()
            if not product:
                raise NotFoundError(f"Product with barcode '{dto.product_barcode}' not found")

            order = OrderDAO(
                product_id=product.id,
                quantity=dto.quantity,
                price_per_unit=dto.price_per_unit,
                status=OrderStatus.Issued,
                issue_date=datetime.utcnow(),
            )
            session.add(order)
            await session.commit()
            await session.refresh(order)
            return self._to_response(order, product.barcode)

    async def pay_order_for(self, dto: OrderCreateDTO) -> OrderResponseDTO:
        logger.info(
            f"Paying for order: product {dto.product_barcode}, qty {dto.quantity}"
        )
        async with await self._get_session() as session:
            result = await session.execute(
                select(ProductTypeDAO).where(ProductTypeDAO.barcode == dto.product_barcode)
            )
            product = result.scalars().first()
            if not product:
                raise NotFoundError(f"Product with barcode '{dto.product_barcode}' not found")

            order_cost = dto.quantity * dto.price_per_unit
            system = await self._get_system_info(session)
            if system.balance < order_cost:
                raise BadRequestError(
                    f"Insufficient balance. Required: {order_cost}, Available: {system.balance}"
                )

            order = OrderDAO(
                product_id=product.id,
                quantity=dto.quantity,
                price_per_unit=dto.price_per_unit,
                status=OrderStatus.Paid,
                issue_date=datetime.utcnow(),
            )
            session.add(order)
            system.balance -= order_cost

            await session.commit()
            await session.refresh(order)
            logger.info(
                f"Order {order.id} paid successfully. Balance updated: -{order_cost}"
            )
            return self._to_response(order, product.barcode)

    async def pay_order(self, order_id: int) -> OrderResponseDTO:
        logger.info(f"Paying for order {order_id}")
        async with await self._get_session() as session:
            order, barcode = await self._get_order_and_barcode(session, order_id)

            if order.status != OrderStatus.Issued:
                raise BadRequestError(
                    f"Order {order_id} is not in Issued state (current: {order.status})"
                )

            order_cost = order.quantity * order.price_per_unit
            system = await self._get_system_info(session)
            if system.balance < order_cost:
                raise BadRequestError(
                    f"Insufficient balance. Required: {order_cost}, Available: {system.balance}"
                )

            order.status = OrderStatus.Paid
            system.balance -= order_cost

            await session.commit()
            await session.refresh(order)
            logger.info(
                f"Order {order_id} paid successfully. Balance updated: -{order_cost}"
            )
            return self._to_response(order, barcode)

    async def record_order_arrival(self, order_id: int) -> OrderResponseDTO:
        logger.info(f"Recording arrival for order {order_id}")
        async with await self._get_session() as session:
            order, barcode = await self._get_order_and_barcode(session, order_id)

            if order.status != OrderStatus.Paid:
                raise BadRequestError(
                    f"Order {order_id} is not in Paid state (current: {order.status})"
                )

            product = await session.get(ProductTypeDAO, order.product_id)
            if not product:
                raise NotFoundError(f"Product with id '{order.product_id}' not found")

            if not product.position:
                raise BadRequestError(f"Product {barcode} has no location assigned")

            order.status = OrderStatus.Completed
            product.quantity = (product.quantity or 0) + order.quantity

            await session.commit()
            await session.refresh(order)
            logger.info(
                f"Order {order_id} arrival recorded. Product quantity updated: +{order.quantity}"
            )
            return self._to_response(order, barcode)

    async def list_order_responses(self) -> List[OrderResponseDTO]:
        logger.info("Listing all orders")
        async with await self._get_session() as session:
            stmt = (
                select(OrderDAO, ProductTypeDAO.barcode)
                .join(ProductTypeDAO, ProductTypeDAO.id == OrderDAO.product_id)
            )
            result = await session.execute(stmt)
            rows = result.all()
            return [self._to_response(order, barcode) for order, barcode in rows]

    async def create_order(
        self,
        product_id: int,
        quantity: int,
        price_per_unit: float
    ) -> OrderDAO:
        async with await self._get_session() as session:
            order = OrderDAO(
                product_id=product_id,
                quantity=quantity,
                price_per_unit=price_per_unit,
                status=OrderStatus.Issued,
                issue_date=datetime.utcnow()
            )
            session.add(order)
            await session.commit()
            await session.refresh(order)
            return order

    async def get_order(self, order_id: int) -> OrderDAO:
        async with await self._get_session() as session:
            order = await session.get(OrderDAO, order_id)
            return find_or_throw_not_found(
                [order] if order else [],
                lambda _: True,
                f"Order with id '{order_id}' not found"
            )

    async def list_orders(self) -> List[OrderDAO]:
        async with await self._get_session() as session:
            result = await session.execute(select(OrderDAO))
            return result.scalars().all()

    async def update_order_status(self, order_id: int, new_status: str) -> OrderDAO:
        async with await self._get_session() as session:
            order = await session.get(OrderDAO, order_id)
            order = find_or_throw_not_found(
                [order] if order else [],
                lambda _: True,
                f"Order with id '{order_id}' not found",
            )
            order.status = new_status
            session.add(order)
            await session.commit()
            await session.refresh(order)
            return order
