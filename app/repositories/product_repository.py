import re
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.DAO.product_dao import ProductDAO
from app.utils import throw_conflict_if_found, find_or_throw_not_found
from app.database.database import AsyncSessionLocal
from app.models.errors.bad_request import BadRequestError
from typing import Optional, List


class ProductRepository:

    def __init__(self, session: Optional[AsyncSession] = None):
        self._session = session

    async def _get_session(self) -> AsyncSession:
        return self._session or AsyncSessionLocal()

    async def create_product(
        self,
        description: str,
        barcode: str,
        price_per_unit: float,
        note: Optional[str] = None,
        quantity: int = 0,
        position: Optional[str] = None
    ) -> ProductDAO:
        async with await self._get_session() as session:
            result = await session.execute(select(ProductDAO).filter(ProductDAO.barcode == barcode))
            existing_products = result.scalars().all()

            throw_conflict_if_found(
                existing_products,
                lambda _: True,
                f"Product with barcode '{barcode}' already exists"
            )

            product = ProductDAO(
                description=description,
                barcode=barcode,
                price_per_unit=price_per_unit,
                note=note,
                quantity=quantity,
                position=position
            )
            session.add(product)
            await session.commit()
            await session.refresh(product)
            return product

    async def get_product_by_id(self, product_id: int) -> ProductDAO:
        async with await self._get_session() as session:
            product = await session.get(ProductDAO, product_id)
            return find_or_throw_not_found(
                [product] if product else [],
                lambda _: True,
                f"Product with id '{product_id}' not found"
            )

    async def get_product_by_barcode(self, barcode: str) -> ProductDAO:
        async with await self._get_session() as session:
            result = await session.execute(select(ProductDAO).filter(ProductDAO.barcode == barcode))
            product = result.scalars().first()
            return find_or_throw_not_found(
                [product] if product else [],
                lambda _: True,
                f"Product with barcode '{barcode}' not found"
            )

    async def get_all_products(self) -> List[ProductDAO]:
        async with await self._get_session() as session:
            result = await session.execute(select(ProductDAO))
            return result.scalars().all()

    async def search_products_by_description(self, query: str) -> List[ProductDAO]:
        async with await self._get_session() as session:
            result = await session.execute(
                select(ProductDAO).filter(ProductDAO.description.ilike(f"%{query}%"))
            )
            return result.scalars().all()

    async def update_product(
        self,
        product_id: int,
        description: Optional[str] = None,
        barcode: Optional[str] = None,
        price_per_unit: Optional[float] = None,
        note: Optional[str] = None,
        quantity: Optional[int] = None,
        position: Optional[str] = None
    ) -> ProductDAO:
        async with await self._get_session() as session:
            db_product = await session.get(ProductDAO, product_id)

            find_or_throw_not_found(
                [db_product] if db_product else [],
                lambda _: True,
                f"Product with id '{product_id}' not found"
            )

            # Check if new barcode conflicts with existing product (excluding current product)
            if barcode and barcode != db_product.barcode:
                result = await session.execute(
                    select(ProductDAO).filter(ProductDAO.barcode == barcode)
                )
                conflicting_products = result.scalars().all()
                throw_conflict_if_found(
                    conflicting_products,
                    lambda _: True,
                    f"Product with barcode '{barcode}' already exists"
                )

            # Update only provided fields
            if description is not None:
                db_product.description = description
            if barcode is not None:
                db_product.barcode = barcode
            if price_per_unit is not None:
                db_product.price_per_unit = price_per_unit
            if note is not None:
                db_product.note = note
            if quantity is not None:
                db_product.quantity = quantity
            if position is not None:
                db_product.position = position

            await session.commit()
            await session.refresh(db_product)
            return db_product

    async def update_quantity(self, product_id: int, quantity_change: int) -> ProductDAO:
        async with await self._get_session() as session:
            db_product = await session.get(ProductDAO, product_id)

            find_or_throw_not_found(
                [db_product] if db_product else [],
                lambda _: True,
                f"Product with id '{product_id}' not found"
            )

            final_quantity = db_product.quantity + quantity_change
            if final_quantity < 0:
                raise BadRequestError(
                    f"Quantity cannot be negative. Current: {db_product.quantity}, Change: {quantity_change}"
                )

            db_product.quantity = final_quantity
            await session.commit()
            await session.refresh(db_product)
            return db_product

    async def update_position(self, product_id: int, position: str) -> ProductDAO:
        async with await self._get_session() as session:
            db_product = await session.get(ProductDAO, product_id)

            find_or_throw_not_found(
                [db_product] if db_product else [],
                lambda _: True,
                f"Product with id '{product_id}' not found"
            )

            if position and position != "":
                if not self._validate_position_format(position):
                    raise BadRequestError(
                        "Position must match pattern <digits>-<letters>-<digits> (e.g., 1-A-3)"
                    )

                # Position must be unique across products
                result = await session.execute(
                    select(ProductDAO).filter(
                        ProductDAO.position == position,
                        ProductDAO.id != product_id,
                    )
                )
                conflicting_products = result.scalars().all()
                throw_conflict_if_found(
                    conflicting_products,
                    lambda _: True,
                    f"Position '{position}' is already assigned to another product",
                )

            db_product.position = position if position != "" else None
            await session.commit()
            await session.refresh(db_product)
            return db_product

    async def delete_product(self, product_id: int) -> bool:
        async with await self._get_session() as session:
            product = await session.get(ProductDAO, product_id)

            find_or_throw_not_found(
                [product] if product else [],
                lambda _: True,
                f"Product with id '{product_id}' not found"
            )

            await session.delete(product)
            await session.commit()
            return True

    def _validate_position_format(self, position: str) -> bool:
        pattern = r"^\d+-[A-Za-z]+-\d+$"
        return bool(re.match(pattern, position))
