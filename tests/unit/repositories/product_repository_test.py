import pytest
import pytest_asyncio
from init_db import reset, init_db
from app.repositories.product_repository import ProductRepository
from app.models.errors.notfound_error import NotFoundError
from app.models.errors.conflict_error import ConflictError
from app.models.errors.bad_request import BadRequestError


@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    await reset()
    await init_db()


@pytest.fixture()
def product_repository():
    return ProductRepository()


@pytest.mark.asyncio
async def test_create_product_success(product_repository):
    product = await product_repository.create_product(
        description="Test Product",
        barcode="1234567890123",
        price_per_unit=10.0,
        note="Test note",
        quantity=50,
        position="1-A-1"
    )
    
    assert product.id is not None
    assert product.description == "Test Product"
    assert product.barcode == "1234567890123"
    assert product.price_per_unit == 10.0
    assert product.note == "Test note"
    assert product.quantity == 50
    assert product.position == "1-A-1"


@pytest.mark.asyncio
async def test_create_product_minimal(product_repository):
    product = await product_repository.create_product(
        description="Minimal Product",
        barcode="1111111111111",
        price_per_unit=5.0
    )
    
    assert product.id is not None
    assert product.quantity == 0
    assert product.note is None
    assert product.position is None


@pytest.mark.asyncio
async def test_create_product_duplicate_barcode(product_repository):
    await product_repository.create_product(
        description="First Product",
        barcode="1234567890123",
        price_per_unit=10.0
    )
    
    with pytest.raises(ConflictError, match="already exists"):
        await product_repository.create_product(
            description="Second Product",
            barcode="1234567890123",
            price_per_unit=15.0
        )


@pytest.mark.asyncio
async def test_get_product_by_id_success(product_repository):
    created = await product_repository.create_product(
        description="Test Product",
        barcode="1234567890123",
        price_per_unit=10.0
    )
    
    retrieved = await product_repository.get_product_by_id(created.id)
    assert retrieved.id == created.id
    assert retrieved.description == "Test Product"


@pytest.mark.asyncio
async def test_get_product_by_id_not_found(product_repository):
    with pytest.raises(NotFoundError):
        await product_repository.get_product_by_id(999)


@pytest.mark.asyncio
async def test_get_product_by_barcode_success(product_repository):
    await product_repository.create_product(
        description="Test Product",
        barcode="1234567890123",
        price_per_unit=10.0
    )
    
    retrieved = await product_repository.get_product_by_barcode("1234567890123")
    assert retrieved.barcode == "1234567890123"


@pytest.mark.asyncio
async def test_get_product_by_barcode_not_found(product_repository):
    with pytest.raises(NotFoundError):
        await product_repository.get_product_by_barcode("9999999999999")


@pytest.mark.asyncio
async def test_get_all_products_empty(product_repository):
    products = await product_repository.get_all_products()
    assert len(products) == 0


@pytest.mark.asyncio
async def test_get_all_products_success(product_repository):
    await product_repository.create_product("Product 1", "1111111111111", 10.0)
    await product_repository.create_product("Product 2", "2222222222222", 20.0)
    await product_repository.create_product("Product 3", "3333333333333", 30.0)
    
    products = await product_repository.get_all_products()
    assert len(products) == 3


@pytest.mark.asyncio
async def test_search_products_by_description_found(product_repository):
    await product_repository.create_product("Red Widget", "1111111111111", 10.0)
    await product_repository.create_product("Blue Widget", "2222222222222", 20.0)
    await product_repository.create_product("Green Gadget", "3333333333333", 30.0)
    
    results = await product_repository.search_products_by_description("Widget")
    assert len(results) == 2


@pytest.mark.asyncio
async def test_search_products_by_description_not_found(product_repository):
    await product_repository.create_product("Red Widget", "1111111111111", 10.0)
    
    results = await product_repository.search_products_by_description("Nonexistent")
    assert len(results) == 0


@pytest.mark.asyncio
async def test_search_products_case_insensitive(product_repository):
    await product_repository.create_product("Test Product", "1111111111111", 10.0)
    
    results = await product_repository.search_products_by_description("test")
    assert len(results) == 1


@pytest.mark.asyncio
async def test_update_product_all_fields(product_repository):
    product = await product_repository.create_product(
        description="Original",
        barcode="1111111111111",
        price_per_unit=10.0,
        quantity=100
    )
    
    updated = await product_repository.update_product(
        product_id=product.id,
        description="Updated",
        barcode="2222222222222",
        price_per_unit=20.0,
        note="New note",
        quantity=200,
        position="2-B-2"
    )
    
    assert updated.description == "Updated"
    assert updated.barcode == "2222222222222"
    assert updated.price_per_unit == 20.0
    assert updated.note == "New note"
    assert updated.quantity == 200
    assert updated.position == "2-B-2"


@pytest.mark.asyncio
async def test_update_product_partial(product_repository):
    product = await product_repository.create_product(
        description="Original",
        barcode="1111111111111",
        price_per_unit=10.0
    )
    
    updated = await product_repository.update_product(
        product_id=product.id,
        description="Updated Description"
    )
    
    assert updated.description == "Updated Description"
    assert updated.barcode == "1111111111111"  # Unchanged


@pytest.mark.asyncio
async def test_update_product_not_found(product_repository):
    with pytest.raises(NotFoundError):
        await product_repository.update_product(999, description="Test")


@pytest.mark.asyncio
async def test_update_product_barcode_conflict(product_repository):
    await product_repository.create_product("Product 1", "1111111111111", 10.0)
    product2 = await product_repository.create_product("Product 2", "2222222222222", 20.0)
    
    with pytest.raises(ConflictError, match="already exists"):
        await product_repository.update_product(
            product_id=product2.id,
            barcode="1111111111111"  # Conflicts with Product 1
        )


@pytest.mark.asyncio
async def test_update_product_same_barcode(product_repository):
    product = await product_repository.create_product("Product", "1111111111111", 10.0)
    
    # Update with same barcode should work
    updated = await product_repository.update_product(
        product_id=product.id,
        barcode="1111111111111",
        description="Updated"
    )
    
    assert updated.description == "Updated"
    assert updated.barcode == "1111111111111"


@pytest.mark.asyncio
async def test_update_quantity_increase(product_repository):
    product = await product_repository.create_product(
        description="Test",
        barcode="1111111111111",
        price_per_unit=10.0,
        quantity=100
    )
    
    updated = await product_repository.update_quantity(product.id, 50)
    assert updated.quantity == 150


@pytest.mark.asyncio
async def test_update_quantity_decrease(product_repository):
    product = await product_repository.create_product(
        description="Test",
        barcode="1111111111111",
        price_per_unit=10.0,
        quantity=100
    )
    
    updated = await product_repository.update_quantity(product.id, -30)
    assert updated.quantity == 70


@pytest.mark.asyncio
async def test_update_quantity_to_zero(product_repository):
    product = await product_repository.create_product(
        description="Test",
        barcode="1111111111111",
        price_per_unit=10.0,
        quantity=50
    )
    
    updated = await product_repository.update_quantity(product.id, -50)
    assert updated.quantity == 0


@pytest.mark.asyncio
async def test_update_quantity_negative_result(product_repository):
    product = await product_repository.create_product(
        description="Test",
        barcode="1111111111111",
        price_per_unit=10.0,
        quantity=10
    )
    
    with pytest.raises(BadRequestError, match="cannot be negative"):
        await product_repository.update_quantity(product.id, -20)


@pytest.mark.asyncio
async def test_update_quantity_not_found(product_repository):
    with pytest.raises(NotFoundError):
        await product_repository.update_quantity(999, 10)


@pytest.mark.asyncio
async def test_update_position_valid_format(product_repository):
    product = await product_repository.create_product(
        description="Test",
        barcode="1111111111111",
        price_per_unit=10.0
    )
    
    updated = await product_repository.update_position(product.id, "1-A-1")
    assert updated.position == "1-A-1"


@pytest.mark.asyncio
async def test_update_position_various_formats(product_repository):
    product = await product_repository.create_product(
        description="Test",
        barcode="1111111111111",
        price_per_unit=10.0
    )
    
    # Test different valid formats
    for position in ["1-A-1", "99-ZZZ-999", "10-ABC-20"]:
        updated = await product_repository.update_position(product.id, position)
        assert updated.position == position


@pytest.mark.asyncio
async def test_update_position_invalid_format(product_repository):
    product = await product_repository.create_product(
        description="Test",
        barcode="1111111111111",
        price_per_unit=10.0
    )
    
    with pytest.raises(BadRequestError, match="must match pattern"):
        await product_repository.update_position(product.id, "INVALID")


@pytest.mark.asyncio
async def test_update_position_clear(product_repository):
    product = await product_repository.create_product(
        description="Test",
        barcode="1111111111111",
        price_per_unit=10.0,
        position="1-A-1"
    )
    
    updated = await product_repository.update_position(product.id, "")
    assert updated.position is None


@pytest.mark.asyncio
async def test_update_position_not_found(product_repository):
    with pytest.raises(NotFoundError):
        await product_repository.update_position(999, "1-A-1")


@pytest.mark.asyncio
async def test_delete_product_success(product_repository):
    product = await product_repository.create_product(
        description="Test",
        barcode="1111111111111",
        price_per_unit=10.0
    )
    
    result = await product_repository.delete_product(product.id)
    assert result is True
    
    # Verify product is deleted
    with pytest.raises(NotFoundError):
        await product_repository.get_product_by_id(product.id)


@pytest.mark.asyncio
async def test_delete_product_not_found(product_repository):
    with pytest.raises(NotFoundError):
        await product_repository.delete_product(999)


@pytest.mark.asyncio
async def test_validate_position_format_internal(product_repository):
    # Valid formats
    assert product_repository._validate_position_format("1-A-1") is True
    assert product_repository._validate_position_format("99-ZZZ-999") is True
    assert product_repository._validate_position_format("5-ABC-10") is True
    
    # Invalid formats
    assert product_repository._validate_position_format("INVALID") is False
    assert product_repository._validate_position_format("1-1-1") is False
    assert product_repository._validate_position_format("A-B-C") is False
    assert product_repository._validate_position_format("1--1") is False
