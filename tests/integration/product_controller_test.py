
import pytest
import pytest_asyncio

from app.controllers.product_controller import ProductController
from app.database import database
from app.models.DTO.product_dto import ProductCreateDTO, ProductUpdateDTO
from app.models.errors.bad_request import BadRequestError
from app.models.errors.conflict_error import ConflictError
from app.models.errors.notfound_error import NotFoundError


@pytest_asyncio.fixture(autouse=True)
async def _fresh_db():
    await database.reset_db()
    await database.init_db()


@pytest.mark.asyncio
async def test_product_bottom_up_crud_flow():
    controller = ProductController()

    created = await controller.create_product(
        ProductCreateDTO(
            barcode="1234567890123",
            description="Test Product",
            price_per_unit=15.99,
            quantity=10,
            note="note",
            position="1-A-1",
        )
    )

    assert created.id is not None
    assert created.barcode == "1234567890123"
    assert created.quantity == 10
    assert created.position == "1-A-1"

    by_id = await controller.get_product_by_id(created.id)
    assert by_id.id == created.id

    by_barcode = await controller.get_product_by_barcode("1234567890123")
    assert by_barcode.id == created.id

    updated = await controller.update_product(
        created.id,
        ProductUpdateDTO(description="Updated Product", barcode="9999999999999"),
    )
    assert updated.description == "Updated Product"
    assert updated.barcode == "9999999999999"

    qty_updated = await controller.update_quantity(created.id, 5)
    assert qty_updated.quantity == 15

    pos_updated = await controller.update_position(created.id, "2-B-2")
    assert pos_updated.position == "2-B-2"

    deleted = await controller.delete_product(created.id)
    assert deleted is True

    with pytest.raises(NotFoundError):
        await controller.get_product_by_id(created.id)


@pytest.mark.asyncio
async def test_product_bottom_up_not_found_paths():
    controller = ProductController()

    with pytest.raises(NotFoundError):
        await controller.get_product_by_id(999)

    with pytest.raises(NotFoundError):
        await controller.get_product_by_barcode("9999999999999")

    with pytest.raises(NotFoundError):
        await controller.update_quantity(999, 1)

    with pytest.raises(NotFoundError):
        await controller.update_position(999, "1-A-1")

    with pytest.raises(NotFoundError):
        await controller.delete_product(999)


@pytest.mark.asyncio
async def test_product_bottom_up_duplicate_barcode_conflict():
    controller = ProductController()

    await controller.create_product(
        ProductCreateDTO(
            barcode="1234567890123",
            description="P1",
            price_per_unit=10.0,
            quantity=0,
        )
    )

    with pytest.raises(ConflictError):
        await controller.create_product(
            ProductCreateDTO(
                barcode="1234567890123",
                description="P2",
                price_per_unit=11.0,
                quantity=0,
            )
        )


@pytest.mark.asyncio
async def test_product_bottom_up_update_barcode_conflict():
    controller = ProductController()

    p1 = await controller.create_product(
        ProductCreateDTO(
            barcode="1111111111111",
            description="P1",
            price_per_unit=10.0,
            quantity=0,
        )
    )
    p2 = await controller.create_product(
        ProductCreateDTO(
            barcode="2222222222222",
            description="P2",
            price_per_unit=10.0,
            quantity=0,
        )
    )

    with pytest.raises(ConflictError):
        await controller.update_product(p2.id, ProductUpdateDTO(barcode=p1.barcode))


@pytest.mark.asyncio
async def test_product_bottom_up_position_format_validation():
    controller = ProductController()

    created = await controller.create_product(
        ProductCreateDTO(
            barcode="1234567890123",
            description="P",
            price_per_unit=10.0,
            quantity=0,
        )
    )

    with pytest.raises(BadRequestError):
        await controller.update_position(created.id, "INVALID")


@pytest.mark.asyncio
async def test_product_bottom_up_position_uniqueness_conflict():
    controller = ProductController()

    p1 = await controller.create_product(
        ProductCreateDTO(
            barcode="1111111111111",
            description="P1",
            price_per_unit=10.0,
            quantity=0,
            position="1-A-1",
        )
    )
    p2 = await controller.create_product(
        ProductCreateDTO(
            barcode="2222222222222",
            description="P2",
            price_per_unit=10.0,
            quantity=0,
        )
    )

    with pytest.raises(ConflictError):
        await controller.update_position(p2.id, "1-A-1")

    assert (await controller.get_product_by_id(p1.id)).position == "1-A-1"


@pytest.mark.asyncio
async def test_product_bottom_up_update_quantity_cannot_go_negative():
    controller = ProductController()

    created = await controller.create_product(
        ProductCreateDTO(
            barcode="1234567890123",
            description="P",
            price_per_unit=10.0,
            quantity=1,
        )
    )

    with pytest.raises(BadRequestError):
        await controller.update_quantity(created.id, -2)
