from app.repositories.product_repository import ProductRepository
from app.models.DTO.product_dto import (
    ProductTypeCreateDTO, 
    ProductTypeUpdateDTO, 
    ProductTypeResponseDTO
)
from app.models.DAO.product_type_dao import ProductTypeDAO
from typing import Optional
import re


class ProductService:

    def __init__(self, repository: Optional[ProductRepository] = None):
        self.repository = repository or ProductRepository()

    async def create_product(self, product_dto: ProductTypeCreateDTO) -> ProductTypeResponseDTO:
        # Validate price
        if product_dto.price_per_unit <= 0:
            from app.models.errors.bad_request import BadRequestError
            raise BadRequestError("Price per unit must be greater than 0")

        # Validate quantity
        if product_dto.quantity and product_dto.quantity < 0:
            from app.models.errors.bad_request import BadRequestError
            raise BadRequestError("Quantity cannot be negative")

        # Validate position format if provided (pattern: <digits>-<letters>-<digits>)
        if product_dto.position:
            if not self._validate_position_format(product_dto.position):
                from app.models.errors.bad_request import BadRequestError
                raise BadRequestError("Position must match pattern <digits>-<letters>-<digits> (e.g., 1-A-3)")

        product_dao = await self.repository.create_product(
            description=product_dto.description,
            barcode=product_dto.barcode,
            price_per_unit=product_dto.price_per_unit,
            note=product_dto.note,
            quantity=product_dto.quantity or 0,
            position=product_dto.position
        )

        return self._dao_to_response_dto(product_dao)

    async def get_product_by_id(self, product_id: int) -> ProductTypeResponseDTO:
        product_dao = await self.repository.get_product_by_id(product_id)
        return self._dao_to_response_dto(product_dao)

    async def get_product_by_barcode(self, barcode: str) -> ProductTypeResponseDTO:
        product_dao = await self.repository.get_product_by_barcode(barcode)
        return self._dao_to_response_dto(product_dao)

    async def get_all_products(self) -> list[ProductTypeResponseDTO]:
        products_dao = await self.repository.get_all_products()
        return [self._dao_to_response_dto(p) for p in products_dao]

    async def search_products_by_description(self, query: str) -> list[ProductTypeResponseDTO]:
        products_dao = await self.repository.search_products_by_description(query)
        return [self._dao_to_response_dto(p) for p in products_dao]

    async def update_product(
        self, 
        product_id: int, 
        product_dto: ProductTypeUpdateDTO
    ) -> ProductTypeResponseDTO:
        # Validate price if provided
        if product_dto.price_per_unit is not None and product_dto.price_per_unit <= 0:
            from app.models.errors.bad_request import BadRequestError
            raise BadRequestError("Price per unit must be greater than 0")

        # Validate quantity if provided
        if product_dto.quantity is not None and product_dto.quantity < 0:
            from app.models.errors.bad_request import BadRequestError
            raise BadRequestError("Quantity cannot be negative")

        # Validate position format if provided
        if product_dto.position and product_dto.position != "":
            if not self._validate_position_format(product_dto.position):
                from app.models.errors.bad_request import BadRequestError
                raise BadRequestError("Position must match pattern <digits>-<letters>-<digits> (e.g., 1-A-3)")

        product_dao = await self.repository.update_product(
            product_id=product_id,
            description=product_dto.description,
            barcode=product_dto.barcode,
            price_per_unit=product_dto.price_per_unit,
            note=product_dto.note,
            quantity=product_dto.quantity,
            position=product_dto.position if product_dto.position is not None else None
        )

        return self._dao_to_response_dto(product_dao)

    async def update_quantity(self, product_id: int, quantity_change: int) -> ProductTypeResponseDTO:
        # Get current product to validate final quantity
        product_dao = await self.repository.get_product_by_id(product_id)
        final_quantity = product_dao.quantity + quantity_change

        if final_quantity < 0:
            from app.models.errors.bad_request import BadRequestError
            raise BadRequestError(f"Quantity cannot be negative. Current: {product_dao.quantity}, Change: {quantity_change}")

        product_dao = await self.repository.update_quantity(product_id, quantity_change)
        return self._dao_to_response_dto(product_dao)

    async def update_position(self, product_id: int, position: str) -> ProductTypeResponseDTO:
        # Validate position format if provided and not empty
        if position and position != "":
            if not self._validate_position_format(position):
                from app.models.errors.bad_request import BadRequestError
                raise BadRequestError("Position must match pattern <digits>-<letters>-<digits> (e.g., 1-A-3)")

        product_dao = await self.repository.update_position(product_id, position)
        return self._dao_to_response_dto(product_dao)

    async def delete_product(self, product_id: int) -> bool:
        return await self.repository.delete_product(product_id)

    def _validate_position_format(self, position: str) -> bool:
        pattern = r"^\d+-[A-Za-z]+-\d+$"
        return bool(re.match(pattern, position))

    def _dao_to_response_dto(self, product_dao: ProductTypeDAO) -> ProductTypeResponseDTO:
        return ProductTypeResponseDTO(
            id=product_dao.id,
            description=product_dao.description,
            barcode=product_dao.barcode,
            price_per_unit=product_dao.price_per_unit,
            note=product_dao.note,
            quantity=product_dao.quantity,
            position=product_dao.position
        )
