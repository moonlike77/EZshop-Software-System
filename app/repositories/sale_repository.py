from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database.database import AsyncSessionLocal
from app.models.DAO.sale_dao import SaleDAO
from app.models.DAO.sale_line_dao import SaleLineDAO
from app.models.sale_status import SaleStatus
from app.utils import find_or_throw_not_found
from app.models.errors.conflict_error import ConflictError
from app.models.errors.notfound_error import NotFoundError
from app.models.errors.invalid_state_error import InvalidStateError
from app.models.errors.bad_request import BadRequestError
from app.models.DAO.system_dao import SystemInfoDAO
from app.models.DAO.product_dao import ProductDAO 


class SaleRepository:
    def __init__(self, session: Optional[AsyncSession] = None):
        self._session = session

    async def _get_session(self) -> AsyncSession:
        return self._session or AsyncSessionLocal()


    async def create_sale(self) -> SaleDAO:
        """Create a new sale with OPEN status and no rows"""
        async with await self._get_session() as session:
            sale = SaleDAO(
                status=SaleStatus.OPEN,
                discount_rate=0.0,
            )
            session.add(sale)
            await session.commit()
            await session.refresh(sale)
            return sale


    async def list_sales(self) -> list[SaleDAO]:
        """Return all sales."""
        async with await self._get_session() as session:
            result = await session.execute(select(SaleDAO))
            return result.scalars().all()


    async def get_sale(self, sale_id: int) -> SaleDAO:
        """Get a sale by id."""
        async with await self._get_session() as session:
            sale = await session.get(SaleDAO, sale_id)
            sale = find_or_throw_not_found(
                [sale] if sale else [],
                lambda _: True,
                f"Sale with id '{sale_id}' not found"
            )

            # If the sale is NOT OPEN and has no lines, we consider it "cancelled"
            if sale.status != SaleStatus.OPEN:
                result = await session.execute(
                    select(func.count())
                    .select_from(SaleLineDAO)
                    .where(SaleLineDAO.sale_id == sale_id)
                )
                lines_count = result.scalar_one()

                if lines_count == 0:
                    raise NotFoundError(f"Sale with id '{sale_id}' not found")

            return sale
        

    async def delete_sale(self, sale_id: int) -> bool:
        """Delete a sale by id"""
        async with await self._get_session() as session:
            sale = await session.get(SaleDAO, sale_id)

            sale = find_or_throw_not_found(
                [sale] if sale else [],
                lambda _: True,
                f"Sale with id '{sale_id}' not found"
            )

            if sale.status == SaleStatus.PAID:
                raise ConflictError("Sale cannot be deleted because it is already PAID")

            # restore stock quantities for all lines in the sale
            result = await session.execute(
                select(SaleLineDAO).where(SaleLineDAO.sale_id == sale.id)
            )
            lines = result.scalars().all()

            for line in lines:
                prod_res = await session.execute(
                    select(ProductDAO).where(ProductDAO.barcode == line.product_barcode)
                )
                product = prod_res.scalars().first()
 
                product = find_or_throw_not_found(
                    [product] if product else [],
                    lambda _: True,
                    f"Product with barcode '{line.product_barcode}' not found"
                )

                product.quantity += line.quantity

            await session.delete(sale)
            await session.commit()
            return True


    async def add_product_to_sale(self, sale_id: int, barcode: str, amount: int) -> bool:
        """Add a product to an OPEN sale."""
        if amount <= 0:
            raise BadRequestError("Amount must be a positive integer")

        async with await self._get_session() as session:
            sale = await session.get(SaleDAO, sale_id)
            sale = find_or_throw_not_found(
                [sale] if sale else [],
                lambda _: True,
                f"Sale with id '{sale_id}' not found"
            )

            if sale.status != SaleStatus.OPEN:
               raise InvalidStateError("Cannot modify a closed sale")

            # product exists + stock check + decrease stock
            prod_res = await session.execute(
                select(ProductDAO).where(ProductDAO.barcode == barcode)
            )
            product = prod_res.scalars().first()

            product = find_or_throw_not_found(
                [product] if product else [],
                lambda _: True,
                f"Product with barcode '{barcode}' not found"
            )

            if product.quantity < amount:
                raise ConflictError("Insufficient stock")

            product.quantity -= amount

            line = SaleLineDAO(
                sale_id=sale.id,
                product_barcode=barcode,
                quantity=amount,
                price_per_unit=product.price_per_unit,  
                discount_rate=0.0
            )
            session.add(line)
            await session.commit()
            return True


    async def remove_product_from_sale(self, sale_id: int, barcode: str, amount: int) -> bool:
        """Remove or decrease quantity of a product from an OPEN sale."""
        if amount <= 0:
            raise BadRequestError("Amount must be a positive integer")

        async with await self._get_session() as session:
            sale = await session.get(SaleDAO, sale_id)
            sale = find_or_throw_not_found(
                [sale] if sale else [],
                lambda _: True,
                f"Sale with id '{sale_id}' not found"
            )

            if sale.status != SaleStatus.OPEN:
                raise InvalidStateError("Cannot modify a closed sale")

            result = await session.execute(
                select(SaleLineDAO).where(
                    SaleLineDAO.sale_id == sale.id,
                    SaleLineDAO.product_barcode == barcode
                )
            )
            line = result.scalars().first()

            if not line:
                raise NotFoundError("Product not found in sale")

            # restore stock
            prod_res = await session.execute(
                select(ProductDAO).where(ProductDAO.barcode == barcode)
            )
            product = prod_res.scalars().first()

            product = find_or_throw_not_found(
                [product] if product else [],
                lambda _: True,
                f"Product with barcode '{barcode}' not found"
            )

            restore_qty = min(amount, line.quantity)
            product.quantity += restore_qty

            if amount >= line.quantity:
                await session.delete(line)
            else:
                line.quantity -= amount

            await session.commit()
            return True
        

    async def apply_discount(self, sale_id: int, discount_rate: float) -> bool:
        """Apply a discount to an OPEN sale."""
        if discount_rate < 0 or discount_rate >= 1:
            raise BadRequestError("Invalid discount rate")

        async with await self._get_session() as session:
            sale = await session.get(SaleDAO, sale_id)
            sale = find_or_throw_not_found(
                [sale] if sale else [],
                lambda _: True,
                f"Sale with id '{sale_id}' not found"
            )

            if sale.status != SaleStatus.OPEN:
                raise InvalidStateError("Cannot modify a closed sale")

            sale.discount_rate = discount_rate
            await session.commit()
            return True
        

    async def apply_product_discount(self, sale_id: int, product_barcode: str, discount_rate: float) -> bool:
        """Apply a discount to a single product line in an OPEN sale."""
        if discount_rate < 0 or discount_rate >= 1:
            raise BadRequestError("Invalid discount rate")

        async with await self._get_session() as session:
            sale = await session.get(SaleDAO, sale_id)
            sale = find_or_throw_not_found(
                [sale] if sale else [],
                lambda _: True,
                f"Sale with id '{sale_id}' not found"
            )

            if sale.status != SaleStatus.OPEN:
                raise InvalidStateError("Cannot modify a closed sale")

            result = await session.execute(
                select(SaleLineDAO).where(
                    SaleLineDAO.sale_id == sale.id,
                    SaleLineDAO.product_barcode == product_barcode
                )
            )
            line = result.scalars().first()

            if not line:
                raise NotFoundError("Product not found in sale")

            line.discount_rate = discount_rate
            await session.commit()
            return True


    async def close_sale(self, sale_id: int) -> bool:
        """Close an OPEN sale, setting its status to PENDING."""
        async with await self._get_session() as session:
            sale = await session.get(SaleDAO, sale_id)
            sale = find_or_throw_not_found(
                [sale] if sale else [],
                lambda _: True,
                f"Sale with id '{sale_id}' not found"
            )

            if sale.status != SaleStatus.OPEN:
                raise InvalidStateError("Cannot modify a closed sale")

            sale.status = SaleStatus.PENDING
            await session.commit()
            return True


    async def pay_sale(self, sale_id: int, cash_amount: float) -> float:
        """ Pay a PENDING sale in cash."""
        if cash_amount <= 0:
            raise BadRequestError("Invalid cash amount")

        async with await self._get_session() as session:
            sale = await session.get(SaleDAO, sale_id)
            sale = find_or_throw_not_found(
                [sale] if sale else [],
                lambda _: True,
                f"Sale with id '{sale_id}' not found"
            )

            if sale.status != SaleStatus.PENDING:
                raise InvalidStateError("Sale must be closed before payment")

            result = await session.execute(
                select(SaleLineDAO).where(SaleLineDAO.sale_id == sale.id)
            )
            lines = result.scalars().all()

            base_total = 0.0
            for line in lines:
                line_price = line.price_per_unit or 0.0
                line_discount = line.discount_rate or 0.0
                base_total += line_price * line.quantity * (1 - line_discount)

            sale_discount = sale.discount_rate or 0.0
            total = base_total * (1 - sale_discount)

            if cash_amount < total:
                raise BadRequestError("Insufficient cash amount")

            change = round(cash_amount - total, 2)

            sale.status = SaleStatus.PAID

            result_sys = await session.execute(select(SystemInfoDAO))
            system_info = result_sys.scalars().first()
            if not system_info:
                system_info = SystemInfoDAO(balance=0.0)
                session.add(system_info)

            system_info.balance += total

            await session.commit()
            return change


    async def get_sale_points(self, sale_id: int) -> int:
        """Compute loyalty points for a PAID sale."""
        async with await self._get_session() as session:

            sale = await session.get(SaleDAO, sale_id)
            sale = find_or_throw_not_found(
                [sale] if sale else [],
                lambda _: True,
                f"Sale with id '{sale_id}' not found"
            )

            if sale.status != SaleStatus.PAID:
                raise InvalidStateError("Sale must be paid before computing points")

            result = await session.execute(
                select(SaleLineDAO).where(SaleLineDAO.sale_id == sale.id)
            )
            lines = result.scalars().all()

            base_total = 0.0
            for line in lines:
                line_price = line.price_per_unit or 0.0
                line_discount = line.discount_rate or 0.0
                base_total += line_price * line.quantity * (1 - line_discount)

            sale_discount = sale.discount_rate or 0.0
            total = base_total * (1 - sale_discount)

            # POINTS RULE: 1 POINT FOR EACH UNIT OF TOTAL (ROUNDED DOWN)
            points = int(total)

            return points

    

