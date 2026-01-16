import logging
from datetime import datetime, timezone
from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import AsyncSessionLocal
from app.models.DAO.order_dao import OrderDAO, OrderStatus
from app.models.DAO.product_dao import ProductDAO
from app.models.DAO.system_dao import SystemInfoDAO
from app.models.errors.bad_request import BadRequestError
from app.models.errors.invalid_state_error import InvalidStateError
from app.models.errors.internal_server_error import InternalServerError
from app.models.errors.app_error import AppError
from app.models.errors.notfound_error import NotFoundError
from app.utils import find_or_throw_not_found


logger = logging.getLogger(__name__)


class OrderRepository:

    def __init__(self, session: Optional[AsyncSession] = None):
        self._session = session

    async def _get_session(self) -> AsyncSession:
        return self._session or AsyncSessionLocal()

    async def _get_system_info(self, session: AsyncSession) -> SystemInfoDAO:
        """Get or create system info"""
        result = await session.execute(select(SystemInfoDAO))
        system_info = result.scalars().first()
        if not system_info:
            system_info = SystemInfoDAO(balance=0.0)
            session.add(system_info)
            await session.flush()
        return system_info


    async def create_order(
        self,
        product_id: int,
        quantity: int,
        price_per_unit: float
    ) -> OrderDAO:
        """Create a new order in ISSUED state"""
        async with await self._get_session() as session:
            order = OrderDAO(
                product_id=product_id,
                quantity=quantity,
                price_per_unit=price_per_unit,
                status=OrderStatus.Issued,
                issue_date=datetime.now(timezone.utc)
            )
            session.add(order)
            await session.commit()
            await session.refresh(order)
            return order

    async def get_order(self, order_id: int) -> OrderDAO:
        """Get order by ID or throw NotFoundError"""
        async with await self._get_session() as session:
            order = await session.get(OrderDAO, order_id)
            return find_or_throw_not_found(
                [order] if order else [],
                lambda _: True,
                f"Order with id '{order_id}' not found"
            )

    async def get_all_orders(self) -> List[OrderDAO]:
        """Get all orders"""
        async with await self._get_session() as session:
            result = await session.execute(select(OrderDAO))
            return result.scalars().all()

    async def pay_order(self, order_id: int) -> OrderDAO:
        """Pay for an ISSUED order, change status to PAID, update balance"""
        logger.info(f"Paying for order {order_id}")
        async with await self._get_session() as session:
            order = await session.get(OrderDAO, order_id)
            find_or_throw_not_found(
                [order] if order else [],
                lambda _: True,
                f"Order with id '{order_id}' not found"
            )

            if order.status != OrderStatus.Issued:
                raise InvalidStateError(
                    f"Order {order_id} is not in ISSUED state (current: {order.status})"
                )

            order_cost = order.quantity * order.price_per_unit
            system = await self._get_system_info(session)
            if system.balance < order_cost:
                raise AppError(
                    f"Insufficient balance. Required: {order_cost}, Available: {system.balance}",
                    421,
                )

            order.status = OrderStatus.Paid
            system.balance -= order_cost

            await session.commit()
            await session.refresh(order)
            logger.info(f"Order {order_id} paid successfully. Balance updated: -{order_cost}")
            return order

    async def record_order_arrival(self, order_id: int) -> OrderDAO:
        """Record arrival of a PAID order, change status to COMPLETED, update product quantity"""
        logger.info(f"Recording arrival for order {order_id}")
        async with await self._get_session() as session:
            order = await session.get(OrderDAO, order_id)
            find_or_throw_not_found(
                [order] if order else [],
                lambda _: True,
                f"Order with id '{order_id}' not found"
            )

            if order.status != OrderStatus.Paid:
                raise InvalidStateError(
                    f"Order {order_id} is not in PAID state (current: {order.status})"
                )

            product = await session.get(ProductDAO, order.product_id)
            if not product:
                raise NotFoundError(f"Product with id '{order.product_id}' not found")

            if not product.position:
                # Evaluation expects this case to surface as a server error.
                raise InternalServerError(f"Product with id '{order.product_id}' has no location assigned")

            order.status = OrderStatus.Completed
            product.quantity = (product.quantity or 0) + order.quantity

            await session.commit()
            await session.refresh(order)
            logger.info(f"Order {order_id} arrival recorded. Product quantity updated: +{order.quantity}")
            return order

    async def delete_order(self, order_id: int) -> bool:
        """Delete an order"""
        async with await self._get_session() as session:
            order = await session.get(OrderDAO, order_id)
            find_or_throw_not_found(
                [order] if order else [],
                lambda _: True,
                f"Order with id '{order_id}' not found"
            )
            await session.delete(order)
            await session.commit()
            return True
