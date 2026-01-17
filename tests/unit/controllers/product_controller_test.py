
import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from app.controllers.product_controller import ProductController
from app.models.DTO.product_dto import ProductCreateDTO, ProductUpdateDTO, ProductResponseDTO
from app.models.DAO.product_dao import ProductDAO
from app.models.errors.bad_request import BadRequestError


@pytest.mark.asyncio
async def test_create_product():
    mock_repo = MagicMock()
    mock_repo.create_product = AsyncMock()

    product = MagicMock(spec=ProductDAO)
    product.id = 1
    product.barcode = "1234567890123"
    product.description = "Test Product"
    product.price_per_unit = 15.99
    product.quantity = 100
    product.note = "Test notes"
    product.position = "A1-B2-C3"
    mock_repo.create_product.return_value = product

    with patch("app.controllers.product_controller.ProductRepository", return_value=mock_repo):
        controller = ProductController()
        input_dto = ProductCreateDTO(
            barcode="1234567890123",
            description="Test Product",
            price_per_unit=15.99,
            quantity=100,
            note="Test notes",
            position="A1-B2-C3",
        )

        result = await controller.create_product(input_dto)

        mock_repo.create_product.assert_called_once_with(
            barcode="1234567890123",
            description="Test Product",
            price_per_unit=15.99,
            quantity=100,
            note="Test notes",
            position="A1-B2-C3",
        )

        assert isinstance(result, ProductResponseDTO)
        assert result.id == 1
        assert result.barcode == "1234567890123"


@pytest.mark.asyncio
async def test_get_product_by_id():
    mock_repo = MagicMock()
    mock_repo.get_product_by_id = AsyncMock()

    product = MagicMock(spec=ProductDAO)
    product.id = 1
    product.barcode = "1234567890123"
    product.description = "Test Product"
    product.price_per_unit = 15.99
    product.note = None
    product.quantity = 100
    product.position = None
    mock_repo.get_product_by_id.return_value = product

    with patch("app.controllers.product_controller.ProductRepository", return_value=mock_repo):
        controller = ProductController()
        result = await controller.get_product_by_id(1)

        mock_repo.get_product_by_id.assert_called_once_with(1)
        assert isinstance(result, ProductResponseDTO)
        assert result.id == 1


@pytest.mark.asyncio
async def test_get_product_by_barcode():
    mock_repo = MagicMock()
    mock_repo.get_product_by_barcode = AsyncMock()

    product = MagicMock(spec=ProductDAO)
    product.id = 1
    product.barcode = "1234567890123"
    product.description = "Test Product"
    product.price_per_unit = 15.99
    product.note = None
    product.quantity = 100
    product.position = None
    mock_repo.get_product_by_barcode.return_value = product

    with patch("app.controllers.product_controller.ProductRepository", return_value=mock_repo):
        controller = ProductController()
        result = await controller.get_product_by_barcode("1234567890123")

        mock_repo.get_product_by_barcode.assert_called_once_with("1234567890123")
        assert isinstance(result, ProductResponseDTO)


@pytest.mark.asyncio
async def test_get_all_products():
    mock_repo = MagicMock()
    mock_repo.get_all_products = AsyncMock()

    product1 = MagicMock(spec=ProductDAO)
    product1.id = 1
    product1.barcode = "1234567890123"
    product1.description = "Product 1"
    product1.price_per_unit = 10.0
    product1.note = None
    product1.quantity = 50
    product1.position = None

    product2 = MagicMock(spec=ProductDAO)
    product2.id = 2
    product2.barcode = "2345678901234"
    product2.description = "Product 2"
    product2.price_per_unit = 20.0
    product2.note = None
    product2.quantity = 30
    product2.position = None

    mock_repo.get_all_products.return_value = [product1, product2]

    with patch("app.controllers.product_controller.ProductRepository", return_value=mock_repo):
        controller = ProductController()
        results = await controller.get_all_products()

        mock_repo.get_all_products.assert_called_once()
        assert len(results) == 2
        assert all(isinstance(r, ProductResponseDTO) for r in results)


@pytest.mark.asyncio
async def test_search_products_by_description():
    mock_repo = MagicMock()
    mock_repo.search_products_by_description = AsyncMock()

    product = MagicMock(spec=ProductDAO)
    product.id = 1
    product.description = "Test Product"
    product.barcode = "1234567890123"
    product.price_per_unit = 15.99
    product.note = None
    product.quantity = 100
    product.position = None

    mock_repo.search_products_by_description.return_value = [product]

    with patch("app.controllers.product_controller.ProductRepository", return_value=mock_repo):
        controller = ProductController()
        results = await controller.search_products_by_description("test")

        mock_repo.search_products_by_description.assert_called_once_with("test")
        assert len(results) == 1
        assert isinstance(results[0], ProductResponseDTO)


@pytest.mark.asyncio
async def test_update_product():
    mock_repo = MagicMock()
    mock_repo.update_product = AsyncMock()

    product = MagicMock(spec=ProductDAO)
    product.id = 1
    product.barcode = "9999999999999"
    product.description = "Updated Product"
    product.price_per_unit = 25.99
    product.note = "Updated note"
    product.quantity = 150
    product.position = "Z1-Y2-X3"
    mock_repo.update_product.return_value = product

    with patch("app.controllers.product_controller.ProductRepository", return_value=mock_repo):
        controller = ProductController()
        input_dto = ProductUpdateDTO(barcode="9999999999999", description="Updated Product")

        result = await controller.update_product(1, input_dto)

        mock_repo.update_product.assert_called_once_with(
            product_id=1,
            description="Updated Product",
            barcode="9999999999999",
            price_per_unit=None,
            note=None,
            quantity=None,
            position=None,
        )
        assert isinstance(result, ProductResponseDTO)


@pytest.mark.asyncio
async def test_update_product_rejects_quantity_field():
    mock_repo = MagicMock()
    mock_repo.update_product = AsyncMock()

    with patch("app.controllers.product_controller.ProductRepository", return_value=mock_repo):
        controller = ProductController()
        input_dto = ProductUpdateDTO(quantity=10)

        with pytest.raises(BadRequestError):
            await controller.update_product(1, input_dto)

        mock_repo.update_product.assert_not_called()


@pytest.mark.asyncio
async def test_update_product_rejects_position_field():
    mock_repo = MagicMock()
    mock_repo.update_product = AsyncMock()

    with patch("app.controllers.product_controller.ProductRepository", return_value=mock_repo):
        controller = ProductController()
        input_dto = ProductUpdateDTO(position="1-A-1")

        with pytest.raises(BadRequestError):
            await controller.update_product(1, input_dto)

        mock_repo.update_product.assert_not_called()


@pytest.mark.asyncio
async def test_update_quantity():
    mock_repo = MagicMock()
    mock_repo.update_quantity = AsyncMock()

    product = MagicMock(spec=ProductDAO)
    product.id = 1
    product.quantity = 150
    product.barcode = "1234567890123"
    product.description = "Test Product"
    product.price_per_unit = 15.99
    product.note = None
    product.position = None
    mock_repo.update_quantity.return_value = product

    with patch("app.controllers.product_controller.ProductRepository", return_value=mock_repo):
        controller = ProductController()
        result = await controller.update_quantity(1, 50)

        mock_repo.update_quantity.assert_called_once_with(1, 50)
        assert isinstance(result, ProductResponseDTO)


@pytest.mark.asyncio
async def test_update_position():
    mock_repo = MagicMock()
    mock_repo.update_position = AsyncMock()

    product = MagicMock(spec=ProductDAO)
    product.id = 1
    product.position = "Z9-Y8-X7"
    product.barcode = "1234567890123"
    product.description = "Test Product"
    product.price_per_unit = 15.99
    product.note = None
    product.quantity = 100
    mock_repo.update_position.return_value = product

    with patch("app.controllers.product_controller.ProductRepository", return_value=mock_repo):
        controller = ProductController()
        result = await controller.update_position(1, "Z9-Y8-X7")

        mock_repo.update_position.assert_called_once_with(1, "Z9-Y8-X7")
        assert isinstance(result, ProductResponseDTO)


@pytest.mark.asyncio
async def test_delete_product():
    mock_repo = MagicMock()
    mock_repo.delete_product = AsyncMock()
    mock_repo.delete_product.return_value = True

    with patch("app.controllers.product_controller.ProductRepository", return_value=mock_repo):
        controller = ProductController()
        result = await controller.delete_product(1)

        mock_repo.delete_product.assert_called_once_with(1)
        assert result is True
