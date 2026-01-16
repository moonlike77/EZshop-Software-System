import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime, timezone

from app.controllers.sale_controller import SaleController
from app.models.sale_status import SaleStatus
from app.models.DTO.sale_dto import SaleDTO

from app.models.DAO.sale_dao import SaleDAO


def _make_sale_dao(
    sale_id: int = 1,
    status: SaleStatus = SaleStatus.OPEN,
    discount_rate: float = 0.0
) -> SaleDAO:
    # Usiamo il vero SaleDAO (niente FakeSaleDAO)
    sale = SaleDAO(
        status=status,
        discount_rate=discount_rate,
    )
    # di solito id/created_at arrivano dal DB, ma per il controller basta averli
    sale.id = sale_id
    sale.created_at = datetime.now(timezone.utc)
    sale.closed_at = None
    return sale


@pytest.mark.asyncio
async def test_start_sale_returns_dto():
    mock_repo_inst = MagicMock()
    mock_repo_inst.create_sale = AsyncMock()

    sale_dao = _make_sale_dao(sale_id=10, status=SaleStatus.OPEN, discount_rate=0.0)
    mock_repo_inst.create_sale.return_value = sale_dao

    with patch("app.controllers.sale_controller.SaleRepository", return_value=mock_repo_inst):
        controller = SaleController()

        result = await controller.start_sale()

        mock_repo_inst.create_sale.assert_called_once()
        assert isinstance(result, SaleDTO)
        assert result.id == 10
        assert result.status == SaleStatus.OPEN
        assert result.discount_rate == 0.0


@pytest.mark.asyncio
async def test_list_sales_returns_list_of_dtos():
    mock_repo_inst = MagicMock()
    mock_repo_inst.list_sales = AsyncMock()

    mock_repo_inst.list_sales.return_value = [
        _make_sale_dao(sale_id=1, status=SaleStatus.OPEN),
        _make_sale_dao(sale_id=2, status=SaleStatus.PENDING),
    ]

    with patch("app.controllers.sale_controller.SaleRepository", return_value=mock_repo_inst):
        controller = SaleController()

        result = await controller.list_sales()

        mock_repo_inst.list_sales.assert_called_once()
        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(x, SaleDTO) for x in result)
        assert result[0].id == 1
        assert result[1].id == 2
        assert result[1].status == SaleStatus.PENDING


@pytest.mark.asyncio
async def test_get_sale_returns_dto():
    mock_repo_inst = MagicMock()
    mock_repo_inst.get_sale = AsyncMock()

    mock_repo_inst.get_sale.return_value = _make_sale_dao(sale_id=7, status=SaleStatus.OPEN, discount_rate=0.2)

    with patch("app.controllers.sale_controller.SaleRepository", return_value=mock_repo_inst):
        controller = SaleController()

        result = await controller.get_sale(7)

        mock_repo_inst.get_sale.assert_called_once_with(7)
        assert isinstance(result, SaleDTO)
        assert result.id == 7
        assert result.discount_rate == 0.2


@pytest.mark.asyncio
async def test_delete_sale_calls_repo_and_returns_bool():
    mock_repo_inst = MagicMock()
    mock_repo_inst.delete_sale = AsyncMock(return_value=True)

    with patch("app.controllers.sale_controller.SaleRepository", return_value=mock_repo_inst):
        controller = SaleController()

        result = await controller.delete_sale(5)

        mock_repo_inst.delete_sale.assert_called_once_with(5)
        assert result is True


@pytest.mark.asyncio
async def test_add_product_to_sale_calls_repo():
    mock_repo_inst = MagicMock()
    mock_repo_inst.add_product_to_sale = AsyncMock(return_value=True)

    with patch("app.controllers.sale_controller.SaleRepository", return_value=mock_repo_inst):
        controller = SaleController()

        result = await controller.add_product_to_sale(3, "ABC", 2)

        mock_repo_inst.add_product_to_sale.assert_called_once_with(3, "ABC", 2)
        assert result is True


@pytest.mark.asyncio
async def test_remove_product_from_sale_calls_repo():
    mock_repo_inst = MagicMock()
    mock_repo_inst.remove_product_from_sale = AsyncMock(return_value=True)

    with patch("app.controllers.sale_controller.SaleRepository", return_value=mock_repo_inst):
        controller = SaleController()

        result = await controller.remove_product_from_sale(3, "ABC", 1)

        mock_repo_inst.remove_product_from_sale.assert_called_once_with(3, "ABC", 1)
        assert result is True


@pytest.mark.asyncio
async def test_apply_discount_calls_repo():
    mock_repo_inst = MagicMock()
    mock_repo_inst.apply_discount = AsyncMock(return_value=True)

    with patch("app.controllers.sale_controller.SaleRepository", return_value=mock_repo_inst):
        controller = SaleController()

        result = await controller.apply_discount(9, 0.15)

        mock_repo_inst.apply_discount.assert_called_once_with(9, 0.15)
        assert result is True


@pytest.mark.asyncio
async def test_apply_product_discount_calls_repo():
    mock_repo_inst = MagicMock()
    mock_repo_inst.apply_product_discount = AsyncMock(return_value=True)

    with patch("app.controllers.sale_controller.SaleRepository", return_value=mock_repo_inst):
        controller = SaleController()

        result = await controller.apply_product_discount(9, "ABC", 0.3)

        mock_repo_inst.apply_product_discount.assert_called_once_with(9, "ABC", 0.3)
        assert result is True


@pytest.mark.asyncio
async def test_close_sale_calls_repo():
    mock_repo_inst = MagicMock()
    mock_repo_inst.close_sale = AsyncMock(return_value=True)

    with patch("app.controllers.sale_controller.SaleRepository", return_value=mock_repo_inst):
        controller = SaleController()

        result = await controller.close_sale(11)

        mock_repo_inst.close_sale.assert_called_once_with(11)
        assert result is True


@pytest.mark.asyncio
async def test_pay_sale_returns_change():
    mock_repo_inst = MagicMock()
    mock_repo_inst.pay_sale = AsyncMock(return_value=12.5)

    with patch("app.controllers.sale_controller.SaleRepository", return_value=mock_repo_inst):
        controller = SaleController()

        change = await controller.pay_sale(4, 100.0)

        mock_repo_inst.pay_sale.assert_called_once_with(4, 100.0)
        assert change == 12.5


@pytest.mark.asyncio
async def test_get_sale_points_returns_int():
    mock_repo_inst = MagicMock()
    mock_repo_inst.get_sale_points = AsyncMock(return_value=42)

    with patch("app.controllers.sale_controller.SaleRepository", return_value=mock_repo_inst):
        controller = SaleController()

        points = await controller.get_sale_points(4)

        mock_repo_inst.get_sale_points.assert_called_once_with(4)
        assert points == 42
        assert isinstance(points, int)
