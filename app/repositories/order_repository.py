from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.DAO.order_dao import OrderDAO, OrderStatusEnum
from app.utils import find_or_throw_not_found
from app.database.database import AsyncSessionLocal
from typing import Optional


class OrderRepository:

    def __init__(self, session: Optional[AsyncSession] = None):
        self._session = session

    async def _get_session(self) -> AsyncSession:
        return self._session or AsyncSessionLocal()

    async def create_order(
        self,
        product_barcode: str,
        quantity: int,
        price_per_unit: float,
        status: OrderStatusEnum = OrderStatusEnum.ISSUED
    ) -> OrderDAO:
        
        async with await self._get_session() as session:
            order = OrderDAO(
                product_barcode=product_barcode,
                quantity=quantity,
                price_per_unit=price_per_unit,
                status=status
            )
            session.add(order)
            await session.commit()
            await session.refresh(order)
            return order

    async def get_order_by_id(self, order_id: int) -> OrderDAO:
        
        async with await self._get_session() as session:
            order = await session.get(OrderDAO, order_id)
            return find_or_throw_not_found(
                [order] if order else [],
                lambda _: True,
                f"Order with id '{order_id}' not found"
            )

    async def get_all_orders(self) -> list[OrderDAO]:
        async with await self._get_session() as session:
            result = await session.execute(select(OrderDAO))
            return result.scalars().all()

    async def get_orders_by_status(self, status: OrderStatusEnum) -> list[OrderDAO]:
        async with await self._get_session() as session:
            result = await session.execute(
                select(OrderDAO).filter(OrderDAO.status == status)
            )
            return result.scalars().all()

    async def get_orders_by_product_barcode(self, barcode: str) -> list[OrderDAO]:
        async with await self._get_session() as session:
            result = await session.execute(
                select(OrderDAO).filter(OrderDAO.product_barcode == barcode)
            )
            return result.scalars().all()

    async def update_order_status(self, order_id: int, status: OrderStatusEnum) -> OrderDAO:
        
        async with await self._get_session() as session:
            db_order = await session.get(OrderDAO, order_id)
            
            find_or_throw_not_found(
                [db_order] if db_order else [],
                lambda _: True,
                f"Order with id '{order_id}' not found"
            )

            db_order.status = status
            await session.commit()
            await session.refresh(db_order)
            return db_order

    async def pay_order(self, order_id: int) -> OrderDAO:
   
        async with await self._get_session() as session:
            db_order = await session.get(OrderDAO, order_id)
            
            find_or_throw_not_found(
                [db_order] if db_order else [],
                lambda _: True,
                f"Order with id '{order_id}' not found"
            )

            if db_order.status != OrderStatusEnum.ISSUED:
                from app.models.errors.bad_request import BadRequestError
                raise BadRequestError(f"Only ISSUED orders can be paid. Current status: {db_order.status}")

            db_order.status = OrderStatusEnum.PAID
            await session.commit()
            await session.refresh(db_order)
            return db_order

    async def record_order_arrival(self, order_id: int) -> OrderDAO:
        
        async with await self._get_session() as session:
            db_order = await session.get(OrderDAO, order_id)
            
            find_or_throw_not_found(
                [db_order] if db_order else [],
                lambda _: True,
                f"Order with id '{order_id}' not found"
            )

            if db_order.status != OrderStatusEnum.PAID:
                from app.models.errors.bad_request import BadRequestError
                raise BadRequestError(f"Only PAID orders can have arrival recorded. Current status: {db_order.status}")

            db_order.status = OrderStatusEnum.COMPLETED
            await session.commit()
            await session.refresh(db_order)
            return db_order

    async def delete_order(self, order_id: int) -> bool:
        
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
