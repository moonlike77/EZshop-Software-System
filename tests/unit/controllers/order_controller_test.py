
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime, timezone

from app.controllers.order_controller import OrderController
from app.models.DTO.order_dto import (
    OrderCreateDTO,
    OrderPayForDTO,
    OrderResponseDTO,
    ReorderWarningCreateDTO,
)
from app.models.DAO.order_dao import OrderDAO, OrderStatus
from app.models.DAO.product_dao import ProductDAO


@pytest.mark.asyncio
async def test_create_order():
    mock_order_repo = MagicMock()
    mock_product_repo = MagicMock()

    mock_order_repo.create_order = AsyncMock()
    mock_product_repo.get_product_by_barcode = AsyncMock()

    product = MagicMock(spec=ProductDAO)
    product.id = 1
    product.barcode = "1234567890123"
    mock_product_repo.get_product_by_barcode.return_value = product

    order = MagicMock(spec=OrderDAO)
    order.id = 1
    order.product_id = 1
    order.quantity = 5
    order.price_per_unit = 10.0
    order.status = OrderStatus.Issued
    order.issue_date = datetime.now(timezone.utc)
    order.product = product
    mock_order_repo.create_order.return_value = order

    with patch("app.controllers.order_controller.OrderRepository", return_value=mock_order_repo), \
         patch("app.repositories.product_repository.ProductRepository", return_value=mock_product_repo):
        controller = OrderController()
        input_dto = OrderCreateDTO(
            product_barcode="1234567890123",
            quantity=5,
            price_per_unit=10.0,
        )

        result = await controller.create_order(input_dto)

        mock_product_repo.get_product_by_barcode.assert_called_once_with("1234567890123")
        mock_order_repo.create_order.assert_called_once_with(
            product_id=1,
            quantity=5,
            price_per_unit=10.0,
        )

        assert isinstance(result, OrderResponseDTO)
        assert result.id == 1
        assert result.quantity == 5


@pytest.mark.asyncio
async def test_create_and_pay_order():
    mock_order_repo = MagicMock()
    mock_product_repo = MagicMock()

    mock_order_repo.create_order = AsyncMock()
    mock_order_repo.pay_order = AsyncMock()
    mock_product_repo.get_product_by_barcode = AsyncMock()

    product = MagicMock(spec=ProductDAO)
    product.id = 1
    product.barcode = "1234567890123"
    mock_product_repo.get_product_by_barcode.return_value = product

    created_order = MagicMock(spec=OrderDAO)
    created_order.id = 1
    mock_order_repo.create_order.return_value = created_order

    paid_order = MagicMock(spec=OrderDAO)
    paid_order.id = 1
    paid_order.status = OrderStatus.Paid
    paid_order.product = product
    mock_order_repo.pay_order.return_value = paid_order

    with patch("app.controllers.order_controller.OrderRepository", return_value=mock_order_repo), \
         patch("app.repositories.product_repository.ProductRepository", return_value=mock_product_repo):
        controller = OrderController()
        input_dto = OrderPayForDTO(
            product_barcode="1234567890123",
            quantity=5,
            price_per_unit=10.0,
        )

        result = await controller.create_and_pay_order(input_dto)

        mock_product_repo.get_product_by_barcode.assert_called_once_with("1234567890123")
        mock_order_repo.create_order.assert_called_once()
        mock_order_repo.pay_order.assert_called_once_with(1)

        assert isinstance(result, OrderResponseDTO)


@pytest.mark.asyncio
async def test_get_order_by_id():
    mock_repo = MagicMock()
    mock_repo.get_order = AsyncMock()

    product = MagicMock(spec=ProductDAO)
    product.barcode = "1234567890123"

    order = MagicMock(spec=OrderDAO)
    order.id = 1
    order.quantity = 5
    order.price_per_unit = 10.0
    order.status = "Issued"
    order.issue_date = datetime.now(timezone.utc)
    order.product = product
    mock_repo.get_order.return_value = order

    with patch("app.controllers.order_controller.OrderRepository", return_value=mock_repo):
        controller = OrderController()
        result = await controller.get_order_by_id(1)

        mock_repo.get_order.assert_called_once_with(1)
        assert isinstance(result, OrderResponseDTO)
        assert result.id == 1


@pytest.mark.asyncio
async def test_get_all_orders():
    mock_repo = MagicMock()
    mock_repo.get_all_orders = AsyncMock()

    product = MagicMock(spec=ProductDAO)
    product.barcode = "1234567890123"

    order1 = MagicMock(spec=OrderDAO)
    order1.id = 1
    order1.quantity = 5
    order1.price_per_unit = 10.0
    order1.status = "Issued"
    order1.issue_date = datetime.now(timezone.utc)
    order1.product = product

    order2 = MagicMock(spec=OrderDAO)
    order2.id = 2
    order2.quantity = 10
    order2.price_per_unit = 8.0
    order2.status = "Paid"
    order2.issue_date = datetime.now(timezone.utc)
    order2.product = product

    mock_repo.get_all_orders.return_value = [order1, order2]

    with patch("app.controllers.order_controller.OrderRepository", return_value=mock_repo):
        controller = OrderController()
        results = await controller.get_all_orders()

        mock_repo.get_all_orders.assert_called_once()
        assert len(results) == 2
        assert all(isinstance(r, OrderResponseDTO) for r in results)


@pytest.mark.asyncio
async def test_pay_order():
    mock_repo = MagicMock()
    mock_repo.pay_order = AsyncMock()

    product = MagicMock(spec=ProductDAO)
    product.barcode = "1234567890123"

    order = MagicMock(spec=OrderDAO)
    order.id = 1
    order.status = "Paid"
    order.quantity = 5
    order.price_per_unit = 10.0
    order.issue_date = datetime.now(timezone.utc)
    order.product = product
    mock_repo.pay_order.return_value = order

    with patch("app.controllers.order_controller.OrderRepository", return_value=mock_repo):
        controller = OrderController()
        result = await controller.pay_order(1)

        mock_repo.pay_order.assert_called_once_with(1)
        assert isinstance(result, OrderResponseDTO)


@pytest.mark.asyncio
async def test_record_order_arrival():
    mock_repo = MagicMock()
    mock_repo.record_order_arrival = AsyncMock()

    product = MagicMock(spec=ProductDAO)
    product.barcode = "1234567890123"

    order = MagicMock(spec=OrderDAO)
    order.id = 1
    order.status = "Completed"
    order.quantity = 5
    order.price_per_unit = 10.0
    order.issue_date = datetime.now(timezone.utc)
    order.product = product
    mock_repo.record_order_arrival.return_value = order

    with patch("app.controllers.order_controller.OrderRepository", return_value=mock_repo):
        controller = OrderController()
        result = await controller.record_order_arrival(1)

        mock_repo.record_order_arrival.assert_called_once_with(1)
        assert isinstance(result, OrderResponseDTO)


@pytest.mark.asyncio
async def test_delete_order():
    mock_repo = MagicMock()
    mock_repo.delete_order = AsyncMock()
    mock_repo.delete_order.return_value = True

    with patch("app.controllers.order_controller.OrderRepository", return_value=mock_repo):
        controller = OrderController()
        result = await controller.delete_order(1)

        mock_repo.delete_order.assert_called_once_with(1)
        assert result is True


@pytest.mark.asyncio
async def test_issue_reorder_warning():
    mock_order_repo = MagicMock()
    mock_product_repo = MagicMock()

    mock_order_repo.issue_reorder_warning = AsyncMock()
    mock_product_repo.get_product_by_barcode = AsyncMock()

    product = MagicMock(spec=ProductDAO)
    product.id = 1
    product.barcode = "1234567890123"
    mock_product_repo.get_product_by_barcode.return_value = product

    reorder = MagicMock(spec=OrderDAO)
    reorder.id = 1
    reorder.product_id = 1
    reorder.quantity = 50
    reorder.price_per_unit = 9.5
    reorder.status = OrderStatus.Issued
    reorder.is_reorder_warning = True
    reorder.issue_date = datetime.now(timezone.utc)
    reorder.product = product
    mock_order_repo.issue_reorder_warning.return_value = reorder

    with patch("app.controllers.order_controller.OrderRepository", return_value=mock_order_repo), \
         patch("app.repositories.product_repository.ProductRepository", return_value=mock_product_repo):
        controller = OrderController()
        input_dto = ReorderWarningCreateDTO(
            product_barcode="1234567890123",
            quantity=50,
            price_per_unit=9.5,
        )

        result = await controller.issue_reorder_warning(input_dto)

        mock_product_repo.get_product_by_barcode.assert_called_once_with("1234567890123")
        mock_order_repo.issue_reorder_warning.assert_called_once_with(
            product_id=1,
            quantity=50,
            price_per_unit=9.5,
        )

        assert isinstance(result, OrderResponseDTO)
        assert result.id == 1
        assert result.product_barcode == "1234567890123"
        assert result.quantity == 50
        assert result.price_per_unit == 9.5
        assert result.status == "ISSUED"
        assert result.is_reorder_warning is True


@pytest.mark.asyncio
async def test_pay_reorder_warning():
    mock_repo = MagicMock()
    mock_repo.pay_reorder_warning = AsyncMock()

    product = MagicMock(spec=ProductDAO)
    product.id = 1
    product.barcode = "1234567890123"

    reorder = MagicMock(spec=OrderDAO)
    reorder.id = 1
    reorder.product_id = 1
    reorder.quantity = 50
    reorder.price_per_unit = 9.5
    reorder.status = OrderStatus.Paid
    reorder.is_reorder_warning = True
    reorder.issue_date = datetime.now(timezone.utc)
    reorder.product = product
    mock_repo.pay_reorder_warning.return_value = reorder

    with patch("app.controllers.order_controller.OrderRepository", return_value=mock_repo):
        controller = OrderController()
        result = await controller.pay_reorder_warning(1)

        mock_repo.pay_reorder_warning.assert_called_once_with(1)

        assert isinstance(result, OrderResponseDTO)
        assert result.id == 1
        assert result.product_barcode == "1234567890123"
        assert result.quantity == 50
        assert result.price_per_unit == 9.5
        assert result.status == "PAID"
        assert result.is_reorder_warning is True
