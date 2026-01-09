# app/repositories/return_repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime, timezone

from app.database.database import AsyncSessionLocal
from app.models.DAO.return_dao import ReturnDAO, ReturnLineDAO
from app.models.return_status import ReturnStatus

class ReturnRepository:
    def __init__(self, session: Optional[AsyncSession] = None):
        self._session = session

    async def _get_session(self) -> AsyncSession:
        return self._session or AsyncSessionLocal()

    async def create_return(self, sale_id: int) -> ReturnDAO:
        async with await self._get_session() as session:
            new_return = ReturnDAO(sale_id=sale_id, status=ReturnStatus.OPEN)
            session.add(new_return)
            await session.commit()
            await session.refresh(new_return, ["lines"])
            return new_return

    async def get_return(self, return_id: int) -> Optional[ReturnDAO]:
        async with await self._get_session() as session:
            query = select(ReturnDAO).where(ReturnDAO.id == return_id)
            result = await session.execute(query)
            return_dao = result.scalars().first()
            if return_dao:
                await session.refresh(return_dao, ["lines"]) 
            return return_dao

    async def list_returns(self) -> List[ReturnDAO]:
        async with await self._get_session() as session:
            query = select(ReturnDAO)
            result = await session.execute(query)
            returns = result.scalars().unique().all()
            for r in returns:
                await session.refresh(r, ["lines"])
            return returns

    async def get_returns_by_sale(self, sale_id: int) -> List[ReturnDAO]:
        async with await self._get_session() as session:
            query = select(ReturnDAO).where(ReturnDAO.sale_id == sale_id)
            result = await session.execute(query)
            returns = result.scalars().unique().all()
            for r in returns:
                await session.refresh(r, ["lines"])
            return returns

    async def add_line(self, return_id: int, barcode: str, quantity: int, price: float) -> bool:
        async with await self._get_session() as session:
            query = select(ReturnLineDAO).where(
                ReturnLineDAO.return_id == return_id,
                ReturnLineDAO.product_barcode == barcode
            )
            result = await session.execute(query)
            existing_line = result.scalars().first()

            if existing_line:
                existing_line.quantity += quantity
            else:
                new_line = ReturnLineDAO(
                    return_id=return_id,
                    product_barcode=barcode,
                    quantity=quantity,
                    price_per_unit=price
                )
                session.add(new_line)
            
            await session.commit()
            return True

    async def remove_line_quantity(self, return_id: int, barcode: str, amount: int) -> bool:
        async with await self._get_session() as session:
            query = select(ReturnLineDAO).where(
                ReturnLineDAO.return_id == return_id,
                ReturnLineDAO.product_barcode == barcode
            )
            result = await session.execute(query)
            line = result.scalars().first()
            
            if not line:
                return False

            if line.quantity <= amount:
                await session.delete(line)
            else:
                line.quantity -= amount
            
            await session.commit()
            return True

    async def update_status(self, return_id: int, status: ReturnStatus) -> Optional[ReturnDAO]:
        async with await self._get_session() as session:
            return_dao = await session.get(ReturnDAO, return_id)
            if return_dao:
                return_dao.status = status
                if status == ReturnStatus.CLOSED:
                    # اصلاح شده: استفاده از timezone aware datetime
                    return_dao.closed_at = datetime.now(timezone.utc)
                await session.commit()
                await session.refresh(return_dao)
            return return_dao
            
    async def delete_return(self, return_id: int) -> bool:
        async with await self._get_session() as session:
            return_dao = await session.get(ReturnDAO, return_id)
            if return_dao:
                await session.delete(return_dao)
                await session.commit()
                return True
            return False