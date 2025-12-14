from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.DAO.product_type_dao import ProductTypeDAO
from app.utils import throw_conflict_if_found, find_or_throw_not_found
from app.database.database import AsyncSessionLocal
from typing import Optional


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
    ) -> ProductTypeDAO:
        
        async with await self._get_session() as session:
            result = await session.execute(select(ProductTypeDAO).filter(ProductTypeDAO.barcode == barcode))
            existing_products = result.scalars().all()

            throw_conflict_if_found(
                existing_products,
                lambda _: True,
                f"Product with barcode '{barcode}' already exists"
            )

            product = ProductTypeDAO(
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

    async def get_product_by_id(self, product_id: int) -> ProductTypeDAO:
        
        async with await self._get_session() as session:
            product = await session.get(ProductTypeDAO, product_id)
            return find_or_throw_not_found(
                [product] if product else [],
                lambda _: True,
                f"Product with id '{product_id}' not found"
            )

    async def get_product_by_barcode(self, barcode: str) -> ProductTypeDAO:
        
        async with await self._get_session() as session:
            result = await session.execute(select(ProductTypeDAO).filter(ProductTypeDAO.barcode == barcode))
            products = result.scalars().all()
            return find_or_throw_not_found(
                products,
                lambda _: True,
                f"Product with barcode '{barcode}' not found"
            )

    async def get_all_products(self) -> list[ProductTypeDAO]:
       
        async with await self._get_session() as session:
            result = await session.execute(select(ProductTypeDAO))
            return result.scalars().all()

    async def search_products_by_description(self, query: str) -> list[ProductTypeDAO]:
        async with await self._get_session() as session:
            result = await session.execute(
                select(ProductTypeDAO).filter(ProductTypeDAO.description.ilike(f"%{query}%"))
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
    ) -> ProductTypeDAO:
        
        async with await self._get_session() as session:
            db_product = await session.get(ProductTypeDAO, product_id)
            
            find_or_throw_not_found(
                [db_product] if db_product else [],
                lambda _: True,
                f"Product with id '{product_id}' not found"
            )

            # Check if new barcode conflicts with existing product (excluding current product)
            if barcode and barcode != db_product.barcode:
                result = await session.execute(
                    select(ProductTypeDAO).filter(ProductTypeDAO.barcode == barcode)
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

    async def update_quantity(self, product_id: int, quantity_change: int) -> ProductTypeDAO:
       
        async with await self._get_session() as session:
            db_product = await session.get(ProductTypeDAO, product_id)
            
            find_or_throw_not_found(
                [db_product] if db_product else [],
                lambda _: True,
                f"Product with id '{product_id}' not found"
            )

            db_product.quantity += quantity_change
            await session.commit()
            await session.refresh(db_product)
            return db_product

    async def update_position(self, product_id: int, position: str) -> ProductTypeDAO:
    
        async with await self._get_session() as session:
            db_product = await session.get(ProductTypeDAO, product_id)
            
            find_or_throw_not_found(
                [db_product] if db_product else [],
                lambda _: True,
                f"Product with id '{product_id}' not found"
            )

            # Clear position if empty string, otherwise set it
            db_product.position = position if position else None
            await session.commit()
            await session.refresh(db_product)
            return db_product

    async def delete_product(self, product_id: int) -> bool:
        
        async with await self._get_session() as session:
            product = await session.get(ProductTypeDAO, product_id)

            find_or_throw_not_found(
                [product] if product else [],
                lambda _: True,
                f"Product with id '{product_id}' not found"
            )

            await session.delete(product)
            await session.commit()
            return True
