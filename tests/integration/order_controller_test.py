
import pytest
import pytest_asyncio

from app.controllers.order_controller import OrderController
from app.controllers.product_controller import ProductController
from app.database import database
from app.models.DTO.order_dto import OrderCreateDTO, ReorderWarningCreateDTO
from app.models.DTO.product_dto import ProductCreateDTO
from app.models.errors.app_error import AppError
from app.models.errors.bad_request import BadRequestError
from app.models.errors.internal_server_error import InternalServerError
from app.models.errors.invalid_state_error import InvalidStateError
from app.models.errors.notfound_error import NotFoundError
from app.repositories.system_repository import SystemRepository


@pytest_asyncio.fixture(autouse=True)
async def _fresh_db():
    await database.reset_db()
    await database.init_db()


@pytest.mark.asyncio
async def test_order_bottom_up_create_pay_arrive_flow():
    product_controller = ProductController()
    order_controller = OrderController()

    await product_controller.create_product(
        ProductCreateDTO(
            barcode="1234567890123",
            description="Orderable Product",
            price_per_unit=10.0,
            quantity=0,
            position="1-A-1",
        )
    )

    created_order = await order_controller.create_order(
        OrderCreateDTO(product_barcode="1234567890123", quantity=5, price_per_unit=10.0)
    )
    assert created_order.id is not None
    assert created_order.status == "ISSUED"

    await SystemRepository().set_balance(1000.0)

    paid = await order_controller.pay_order(created_order.id)
    assert paid.status == "PAID"

    completed = await order_controller.record_order_arrival(created_order.id)
    assert completed.status == "COMPLETED"

    product_after = await product_controller.get_product_by_barcode("1234567890123")
    assert product_after.quantity == 5


@pytest.mark.asyncio
async def test_order_bottom_up_delete_then_not_found():
    product_controller = ProductController()
    order_controller = OrderController()

    await product_controller.create_product(
        ProductCreateDTO(
            barcode="1234567890123",
            description="Orderable Product",
            price_per_unit=10.0,
            quantity=0,
            position="1-A-1",
        )
    )

    created_order = await order_controller.create_order(
        OrderCreateDTO(product_barcode="1234567890123", quantity=1, price_per_unit=10.0)
    )

    assert await order_controller.delete_order(created_order.id) is True

    with pytest.raises(NotFoundError):
        await order_controller.get_order_by_id(created_order.id)


@pytest.mark.asyncio
async def test_order_bottom_up_not_found_paths():
    order_controller = OrderController()

    with pytest.raises(NotFoundError):
        await order_controller.get_order_by_id(999)

    with pytest.raises(NotFoundError):
        await order_controller.pay_order(999)

    with pytest.raises(NotFoundError):
        await order_controller.record_order_arrival(999)

    with pytest.raises(NotFoundError):
        await order_controller.delete_order(999)


@pytest.mark.asyncio
async def test_order_bottom_up_create_order_missing_product():
    order_controller = OrderController()

    with pytest.raises(NotFoundError):
        await order_controller.create_order(
            OrderCreateDTO(product_barcode="1234567890123", quantity=1, price_per_unit=10.0)
        )


@pytest.mark.asyncio
async def test_order_bottom_up_pay_requires_sufficient_balance():
    product_controller = ProductController()
    order_controller = OrderController()

    await product_controller.create_product(
        ProductCreateDTO(
            barcode="1234567890123",
            description="Orderable Product",
            price_per_unit=10.0,
            quantity=0,
            position="1-A-1",
        )
    )

    created_order = await order_controller.create_order(
        OrderCreateDTO(product_barcode="1234567890123", quantity=5, price_per_unit=10.0)
    )

    await SystemRepository().set_balance(0.0)

    with pytest.raises(AppError) as excinfo:
        await order_controller.pay_order(created_order.id)

    assert excinfo.value.status == 421


@pytest.mark.asyncio
async def test_order_bottom_up_pay_invalid_state_cannot_pay_twice():
    product_controller = ProductController()
    order_controller = OrderController()

    await product_controller.create_product(
        ProductCreateDTO(
            barcode="1234567890123",
            description="Orderable Product",
            price_per_unit=10.0,
            quantity=0,
            position="1-A-1",
        )
    )

    created_order = await order_controller.create_order(
        OrderCreateDTO(product_barcode="1234567890123", quantity=1, price_per_unit=10.0)
    )

    await SystemRepository().set_balance(1000.0)
    await order_controller.pay_order(created_order.id)

    with pytest.raises(InvalidStateError):
        await order_controller.pay_order(created_order.id)


@pytest.mark.asyncio
async def test_order_bottom_up_arrival_invalid_state_requires_paid():
    product_controller = ProductController()
    order_controller = OrderController()

    await product_controller.create_product(
        ProductCreateDTO(
            barcode="1234567890123",
            description="Orderable Product",
            price_per_unit=10.0,
            quantity=0,
            position="1-A-1",
        )
    )

    created_order = await order_controller.create_order(
        OrderCreateDTO(product_barcode="1234567890123", quantity=1, price_per_unit=10.0)
    )

    with pytest.raises(InvalidStateError):
        await order_controller.record_order_arrival(created_order.id)


@pytest.mark.asyncio
async def test_order_bottom_up_arrival_requires_product_position():
    product_controller = ProductController()
    order_controller = OrderController()

    await product_controller.create_product(
        ProductCreateDTO(
            barcode="1234567890123",
            description="No Position",
            price_per_unit=10.0,
            quantity=0,
            position=None,
        )
    )

    created_order = await order_controller.create_order(
        OrderCreateDTO(product_barcode="1234567890123", quantity=1, price_per_unit=10.0)
    )

    await SystemRepository().set_balance(1000.0)
    await order_controller.pay_order(created_order.id)

    with pytest.raises(InternalServerError):
        await order_controller.record_order_arrival(created_order.id)


@pytest.mark.asyncio
async def test_order_bottom_up_reorder_warning_flow_and_integrity():
    product_controller = ProductController()
    order_controller = OrderController()

    await product_controller.create_product(
        ProductCreateDTO(
            barcode="1234567890123",
            description="Low Stock",
            price_per_unit=10.0,
            quantity=1,
            position="1-A-1",
        )
    )

    warning = await order_controller.issue_reorder_warning(
        ReorderWarningCreateDTO(product_barcode="1234567890123", quantity=10, price_per_unit=9.5)
    )
    assert warning.is_reorder_warning is True
    assert warning.status == "ISSUED"

    await SystemRepository().set_balance(1000.0)
    paid_warning = await order_controller.pay_reorder_warning(warning.id)
    assert paid_warning.is_reorder_warning is True
    assert paid_warning.status == "PAID"

    regular_order = await order_controller.create_order(
        OrderCreateDTO(product_barcode="1234567890123", quantity=1, price_per_unit=10.0)
    )

    with pytest.raises(BadRequestError):
        await order_controller.pay_reorder_warning(regular_order.id)
