from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.DAO.product_type_dao import ProductTypeDAO
from app.models.DTO.product_dto import (
    ProductTypeCreateDTO, 
    ProductTypeUpdateDTO, 
    ProductTypeResponseDTO
)
from app.utils import throw_conflict_if_found, find_or_throw_not_found
from app.database.database import AsyncSessionLocal
from typing import Optional
import re


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

    # Service layer methods (validation + DTO conversion)
    
    async def create_product_from_dto(self, product_dto: ProductTypeCreateDTO) -> ProductTypeResponseDTO:
        """Create product with validation"""
        if product_dto.price_per_unit <= 0:
            from app.models.errors.bad_request import BadRequestError
            raise BadRequestError("Price per unit must be greater than 0")

        if product_dto.quantity and product_dto.quantity < 0:
            from app.models.errors.bad_request import BadRequestError
            raise BadRequestError("Quantity cannot be negative")

        if product_dto.position:
            if not self._validate_position_format(product_dto.position):
                from app.models.errors.bad_request import BadRequestError
                raise BadRequestError("Position must match pattern <digits>-<letters>-<digits> (e.g., 1-A-3)")

        product_dao = await self.create_product(
            description=product_dto.description,
            barcode=product_dto.barcode,
            price_per_unit=product_dto.price_per_unit,
            note=product_dto.note,
            quantity=product_dto.quantity or 0,
            position=product_dto.position
        )

        return self._dao_to_response_dto(product_dao)

    async def get_product_by_id_dto(self, product_id: int) -> ProductTypeResponseDTO:
        """Get product by ID and convert to DTO"""
        product_dao = await self.get_product_by_id(product_id)
        return self._dao_to_response_dto(product_dao)

    async def get_product_by_barcode_dto(self, barcode: str) -> ProductTypeResponseDTO:
        """Get product by barcode and convert to DTO"""
        product_dao = await self.get_product_by_barcode(barcode)
        return self._dao_to_response_dto(product_dao)

    async def get_all_products_dto(self) -> list[ProductTypeResponseDTO]:
        """Get all products and convert to DTOs"""
        products_dao = await self.get_all_products()
        return [self._dao_to_response_dto(p) for p in products_dao]

    async def search_products_by_description_dto(self, query: str) -> list[ProductTypeResponseDTO]:
        """Search products and convert to DTOs"""
        products_dao = await self.search_products_by_description(query)
        return [self._dao_to_response_dto(p) for p in products_dao]

    async def update_product_from_dto(
        self, 
        product_id: int, 
        product_dto: ProductTypeUpdateDTO
    ) -> ProductTypeResponseDTO:
        """Update product with validation"""
        if product_dto.price_per_unit is not None and product_dto.price_per_unit <= 0:
            from app.models.errors.bad_request import BadRequestError
            raise BadRequestError("Price per unit must be greater than 0")

        if product_dto.quantity is not None and product_dto.quantity < 0:
            from app.models.errors.bad_request import BadRequestError
            raise BadRequestError("Quantity cannot be negative")

        if product_dto.position and product_dto.position != "":
            if not self._validate_position_format(product_dto.position):
                from app.models.errors.bad_request import BadRequestError
                raise BadRequestError("Position must match pattern <digits>-<letters>-<digits> (e.g., 1-A-3)")

        product_dao = await self.update_product(
            product_id=product_id,
            description=product_dto.description,
            barcode=product_dto.barcode,
            price_per_unit=product_dto.price_per_unit,
            note=product_dto.note,
            quantity=product_dto.quantity,
            position=product_dto.position if product_dto.position is not None else None
        )

        return self._dao_to_response_dto(product_dao)

    async def update_quantity_dto(self, product_id: int, quantity_change: int) -> ProductTypeResponseDTO:
        """Update quantity with validation"""
        product_dao = await self.get_product_by_id(product_id)
        final_quantity = product_dao.quantity + quantity_change

        if final_quantity < 0:
            from app.models.errors.bad_request import BadRequestError
            raise BadRequestError(f"Quantity cannot be negative. Current: {product_dao.quantity}, Change: {quantity_change}")

        product_dao = await self.update_quantity(product_id, quantity_change)
        return self._dao_to_response_dto(product_dao)

    async def update_position_dto(self, product_id: int, position: str) -> ProductTypeResponseDTO:
        """Update position with validation"""
        if position and position != "":
            if not self._validate_position_format(position):
                from app.models.errors.bad_request import BadRequestError
                raise BadRequestError("Position must match pattern <digits>-<letters>-<digits> (e.g., 1-A-3)")

        product_dao = await self.update_position(product_id, position)
        return self._dao_to_response_dto(product_dao)

    def _validate_position_format(self, position: str) -> bool:
        """Validate position format: <digits>-<letters>-<digits>"""
        pattern = r"^\d+-[A-Za-z]+-\d+$"
        return bool(re.match(pattern, position))

    def _dao_to_response_dto(self, product_dao: ProductTypeDAO) -> ProductTypeResponseDTO:
        """Convert ProductTypeDAO to ProductTypeResponseDTO"""
        return ProductTypeResponseDTO(
            id=product_dao.id,
            description=product_dao.description,
            barcode=product_dao.barcode,
            price_per_unit=product_dao.price_per_unit,
            note=product_dao.note,
            quantity=product_dao.quantity,
            position=product_dao.position
        )