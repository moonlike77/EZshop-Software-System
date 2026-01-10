# app/repositories/return_repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime, timezone
from app.models.DAO.product_dao import ProductDAO
from app.models.DAO.sale_dao import SaleDAO
from app.models.DAO.sale_line_dao import SaleLineDAO
from app.models.DAO.system_dao import SystemInfoDAO
from app.utils import find_or_throw_not_found
from app.database.database import AsyncSessionLocal
from app.models.DAO.return_dao import ReturnDAO, ReturnLineDAO
from app.models.return_status import ReturnStatus
from app.models.sale_status import SaleStatus
from app.models.errors.bad_request import BadRequestError

class ReturnRepository:
    def __init__(self, session: Optional[AsyncSession] = None):
        self._session = session

    async def _get_session(self) -> AsyncSession:
        return self._session or AsyncSessionLocal()

    async def create_return(self, sale_id: int) -> ReturnDAO:
        async with await self._get_session() as session:
            sale_res = await session.execute(
                select(SaleDAO).where(SaleDAO.id == sale_id)
            )
            sale = sale_res.scalars().first()

            sale = find_or_throw_not_found(
                [sale] if sale else [],
                lambda _: True,
                f"Sale with id '{sale_id}' not found"
            )

            if sale.status != SaleStatus.PAID:
                raise BadRequestError(f"Sale with id '{sale.id}' is not paid")
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

    async def add_line(self, return_dao: ReturnDAO, barcode: str, quantity: int) -> bool:
        async with await self._get_session() as session:
            prod_res = await session.execute(
                select(ProductDAO).where(ProductDAO.barcode == barcode)
            )
            product = prod_res.scalars().first()

            product = find_or_throw_not_found(
                [product] if product else [],
                lambda _: True,
                f"Product with barcode '{barcode}' not found"
            )

            sale_res = await session.execute(
                select(SaleDAO).where(SaleDAO.id == return_dao.sale_id)
            )
            sale = sale_res.scalars().first()

            sale_line_res = await session.execute(
                select(SaleLineDAO).where(SaleLineDAO.sale_id == sale.id, SaleLineDAO.product_barcode == product.barcode)
            )
            sale_line = sale_line_res.scalars().first()
            
            sale_line = find_or_throw_not_found(
                [sale_line] if sale_line else [],
                lambda _: True,
                f"Product with barcode '{barcode}' is not in sale with id '{sale.id}'"
            )

            if sale_line.quantity < quantity:
                raise BadRequestError(f"'{quantity}' is higher than quantity bought '{sale_line.quantity}'")

            return_line_res = await session.execute(
                select(ReturnLineDAO).where(ReturnLineDAO.return_id == return_dao.id, ReturnLineDAO.product_barcode == product.barcode)
            )
            return_line = return_line_res.scalars().first()

            if return_line:
                return_line.quantity += quantity
            else:
                new_line = ReturnLineDAO(
                    return_id=return_dao.id,
                    product_barcode=barcode,
                    quantity=quantity,
                    price_per_unit=product.price_per_unit
                )
                session.add(new_line)
            sale_line.quantity -= quantity
            
            await session.commit()
            return True

    async def remove_line_quantity(self, return_dao: ReturnDAO, barcode: str, amount: int) -> bool:
        async with await self._get_session() as session:
            prod_res = await session.execute(
                select(ProductDAO).where(ProductDAO.barcode == barcode)
            )
            product = prod_res.scalars().first()

            product = find_or_throw_not_found(
                [product] if product else [],
                lambda _: True,
                f"Product with barcode '{barcode}' not found"
            )

            query = select(ReturnLineDAO).where(
                ReturnLineDAO.return_id == return_dao.id,
                ReturnLineDAO.product_barcode == barcode
            )
            result = await session.execute(query)
            line = result.scalars().first()
            
            line = find_or_throw_not_found(
                [line] if line else [],
                lambda _: True,
                f"Product with barcode '{barcode}' is not in return with id '{return_dao.id}'"
            )

            if line.quantity <= amount:
                await session.delete(line)
            else:
                line.quantity -= amount
            
            sale_line_res = await session.execute(
                select(SaleLineDAO).where(SaleLineDAO.sale_id == return_dao.sale_id, SaleLineDAO.product_barcode == product.barcode)
            )
            sale_line = sale_line_res.scalars().first()
            sale_line.quantity += amount
            
            await session.commit()
            return True

    async def update_status(self, return_id: int, status: ReturnStatus, refound: int | None) -> Optional[ReturnDAO]:
        async with await self._get_session() as session:
            return_dao = await session.get(ReturnDAO, return_id)
            if return_dao:
                return_dao.status = status
                if status == ReturnStatus.CLOSED:
                    # اصلاح شده: استفاده از timezone aware datetime
                    return_dao.closed_at = datetime.now(timezone.utc)
                if status == ReturnStatus.REIMBURSED:
                    result_sys = await session.execute(select(SystemInfoDAO))
                    system_info = result_sys.scalars().first()
                    if not system_info:
                        system_info = SystemInfoDAO(balance=0.0)
                        session.add(system_info)
                    system_info.balance -= round(refound, 2)
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