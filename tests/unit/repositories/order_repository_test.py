"""
Unit tests for OrderRepository
Tests the repository layer in isolation with real database operations
"""
import pytest
import pytest_asyncio
from init_db import reset, init_db
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.system_repository import SystemRepository
from app.models.DAO.order_dao import OrderStatus
from app.models.errors.notfound_error import NotFoundError
from app.models.errors.app_error import AppError
from app.models.errors.invalid_state_error import InvalidStateError
from app.models.errors.internal_server_error import InternalServerError
from app.models.DAO.order_dao import OrderDAO
from app.models.DAO.product_dao import ProductDAO
from unittest.mock import AsyncMock, MagicMock


@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    """Reset and initialize database before each test"""
    await reset()
    await init_db()


@pytest.fixture()
def order_repository():
    return OrderRepository()


@pytest.fixture()
def product_repository():
    return ProductRepository()


@pytest.fixture()
def system_repository():
    return SystemRepository()


@pytest.mark.asyncio
async def test_create_order_success(order_repository, product_repository):
    """Test creating an order successfully"""
    # Create a product first
    product = await product_repository.create_product(
        description="Test Product",
        barcode="1234567890123",
        price_per_unit=10.0,
        quantity=100
    )
    
    # Create order
    order = await order_repository.create_order(
        product_id=product.id,
        quantity=5,
        price_per_unit=10.0
    )
    
    assert order.id is not None
    assert order.product_id == product.id
    assert order.quantity == 5
    assert order.price_per_unit == 10.0
    assert order.status == OrderStatus.Issued


@pytest.mark.asyncio
async def test_get_order_success(order_repository, product_repository):
    """Test retrieving an order by ID"""
    product = await product_repository.create_product(
        description="Test Product",
        barcode="1234567890123",
        price_per_unit=10.0
    )
    
    created_order = await order_repository.create_order(
        product_id=product.id,
        quantity=3,
        price_per_unit=10.0
    )
    
    retrieved_order = await order_repository.get_order(created_order.id)
    assert retrieved_order.id == created_order.id
    assert retrieved_order.quantity == 3


@pytest.mark.asyncio
async def test_get_order_not_found(order_repository):
    """Test getting non-existent order raises NotFoundError"""
    with pytest.raises(NotFoundError):
        await order_repository.get_order(999)


@pytest.mark.asyncio
async def test_get_all_orders_empty(order_repository):
    """Test getting all orders when none exist"""
    orders = await order_repository.get_all_orders()
    assert len(orders) == 0


@pytest.mark.asyncio
async def test_get_all_orders_success(order_repository, product_repository):
    """Test retrieving all orders"""
    product = await product_repository.create_product(
        description="Test Product",
        barcode="1234567890123",
        price_per_unit=10.0
    )
    
    await order_repository.create_order(product.id, 5, 10.0)
    await order_repository.create_order(product.id, 3, 10.0)
    
    orders = await order_repository.get_all_orders()
    assert len(orders) == 2

@pytest.mark.asyncio
async def test_pay_order_success(order_repository, product_repository, system_repository):
    """Test paying for an issued order"""
    # Set system balance
    await system_repository.set_balance(1000.0)
    
    product = await product_repository.create_product(
        description="Test Product",
        barcode="1234567890123",
        price_per_unit=10.0
    )
    
    order = await order_repository.create_order(product.id, 5, 10.0)
    
    paid_order = await order_repository.pay_order(order.id)
    assert paid_order.status == OrderStatus.Paid
    
    # Check balance was deducted
    system_info = await system_repository.get_singleton()
    assert system_info.balance == 950.0  # 1000 - (5 * 10)


@pytest.mark.asyncio
async def test_pay_order_not_found(order_repository):
    """Test paying for non-existent order"""
    with pytest.raises(NotFoundError):
        await order_repository.pay_order(999)


@pytest.mark.asyncio
async def test_pay_order_wrong_status(order_repository, product_repository, system_repository):
    """Test paying for order that's not in ISSUED state"""
    await system_repository.set_balance(1000.0)
    
    product = await product_repository.create_product(
        description="Test Product",
        barcode="1234567890123",
        price_per_unit=10.0
    )
    
    order = await order_repository.create_order(product.id, 5, 10.0)
    await order_repository.pay_order(order.id)  # Pay once
    
    # Try to pay again (now in PAID state)
    with pytest.raises(InvalidStateError):
        await order_repository.pay_order(order.id)


@pytest.mark.asyncio
async def test_pay_order_insufficient_balance(order_repository, product_repository, system_repository):
    """Test paying for order with insufficient balance"""
    await system_repository.set_balance(10.0)  # Low balance
    
    product = await product_repository.create_product(
        description="Test Product",
        barcode="1234567890123",
        price_per_unit=100.0
    )
    
    order = await order_repository.create_order(product.id, 5, 100.0)  # Cost: 500
    
    with pytest.raises(AppError) as excinfo:
        await order_repository.pay_order(order.id)
    assert excinfo.value.status == 421


@pytest.mark.asyncio
async def test_record_order_arrival_success(order_repository, product_repository, system_repository):
    """Test recording arrival for a paid order"""
    await system_repository.set_balance(1000.0)
    
    product = await product_repository.create_product(
        description="Test Product",
        barcode="1234567890123",
        price_per_unit=10.0,
        quantity=100,
        position="1-A-1"
    )
    
    order = await order_repository.create_order(product.id, 5, 10.0)
    await order_repository.pay_order(order.id)
    
    completed_order = await order_repository.record_order_arrival(order.id)
    assert completed_order.status == OrderStatus.Completed
    
    # Check product quantity increased
    updated_product = await product_repository.get_product_by_id(product.id)
    assert updated_product.quantity == 105  # 100 + 5


@pytest.mark.asyncio
async def test_record_arrival_not_found(order_repository):
    """Test recording arrival for non-existent order"""
    with pytest.raises(NotFoundError):
        await order_repository.record_order_arrival(999)


@pytest.mark.asyncio
async def test_record_arrival_wrong_status(order_repository, product_repository):
    """Test recording arrival for order not in PAID state"""
    product = await product_repository.create_product(
        description="Test Product",
        barcode="1234567890123",
        price_per_unit=10.0,
        position="1-A-1"
    )
    
    order = await order_repository.create_order(product.id, 5, 10.0)  # ISSUED state
    
    with pytest.raises(InvalidStateError):
        await order_repository.record_order_arrival(order.id)


@pytest.mark.asyncio
async def test_record_arrival_no_position(order_repository, product_repository, system_repository):
    """Test recording arrival when product has no position"""
    await system_repository.set_balance(1000.0)
    
    product = await product_repository.create_product(
        description="Test Product",
        barcode="1234567890123",
        price_per_unit=10.0,
        position=None  # No position
    )
    
    order = await order_repository.create_order(product.id, 5, 10.0)
    await order_repository.pay_order(order.id)
    
    with pytest.raises(InternalServerError):
        await order_repository.record_order_arrival(order.id)


@pytest.mark.asyncio
async def test_delete_order_success(order_repository, product_repository):
    """Test deleting an order"""
    product = await product_repository.create_product(
        description="Test Product",
        barcode="1234567890123",
        price_per_unit=10.0
    )
    
    order = await order_repository.create_order(product.id, 5, 10.0)
    
    result = await order_repository.delete_order(order.id)
    assert result is True
    
    # Verify order is deleted
    with pytest.raises(NotFoundError):
        await order_repository.get_order(order.id)


@pytest.mark.asyncio
async def test_delete_order_not_found(order_repository):
    """Test deleting non-existent order"""
    with pytest.raises(NotFoundError):
        await order_repository.delete_order(999)


@pytest.mark.asyncio
async def test_get_system_info_creates_if_missing(order_repository):
    """Test that _get_system_info creates system info if missing"""
    # This tests the internal helper method indirectly
    from app.database.database import AsyncSessionLocal
    from sqlalchemy import text
    
    async with AsyncSessionLocal() as session:
        # Delete all system info
        await session.execute(text("DELETE FROM system_info"))
        await session.commit()
    
    # Create system info through repository method
    async with AsyncSessionLocal() as session:
        system_info = await order_repository._get_system_info(session)
        assert system_info.balance == 0.0


@pytest.mark.asyncio
async def test_record_arrival_orphaned_order(order_repository):
    """Test record arrival when order exists but product does not (orphaned)"""
    mock_session = AsyncMock()
    # Need to simulate context manager behavior
    mock_session.__aenter__.return_value = mock_session
    mock_session.__aexit__.return_value = None
    
    # Mock data
    mock_order = MagicMock(spec=OrderDAO)
    mock_order.status = OrderStatus.Paid
    mock_order.product_id = 999
    
    async def get_side_effect(entity_cls, entity_id):
        if entity_cls == OrderDAO:
            return mock_order
        # Return None for ProductDAO
        return None
        
    mock_session.get.side_effect = get_side_effect
    
    # Needs to return an AWAITABLE that returns the mocked session object
    async def mock_get_session():
        return mock_session
        
    # Monkeypatch the _get_session method on the instance
    order_repository._get_session = mock_get_session
    
    with pytest.raises(NotFoundError) as excinfo:
        await order_repository.record_order_arrival(123)
    
    assert "Product with id '999' not found" in str(excinfo.value)


@pytest.mark.asyncio
async def test_issue_reorder_warning_success(order_repository, product_repository, system_repository):
    """FR4.3: Test issuing a reorder warning successfully"""
    # Create a product first
    product = await product_repository.create_product(
        description="Low Stock Product",
        barcode="1234567890123",
        price_per_unit=10.0,
        quantity=5,
        position="1-A-1"
    )
    
    # Issue reorder warning
    reorder = await order_repository.issue_reorder_warning(
        product_id=product.id,
        quantity=50,
        price_per_unit=9.5
    )
    
    # Assertions
    assert reorder.id is not None
    assert reorder.product_id == product.id
    assert reorder.quantity == 50
    assert reorder.price_per_unit == 9.5
    assert reorder.status == OrderStatus.Issued
    assert reorder.is_reorder_warning is True
    assert reorder.issue_date is not None


@pytest.mark.asyncio
async def test_pay_reorder_warning_success(order_repository, product_repository, system_repository):
    """FR4.5: Test paying for a reorder warning successfully"""
    # Create a product
    product = await product_repository.create_product(
        description="Low Stock Product",
        barcode="1234567890123",
        price_per_unit=10.0,
        quantity=5,
        position="1-A-1"
    )
    
    # Set sufficient balance
    await system_repository.set_balance(1000.0)
    
    # Issue reorder warning
    reorder = await order_repository.issue_reorder_warning(
        product_id=product.id,
        quantity=50,
        price_per_unit=9.5
    )
    
    initial_system = await system_repository.get_singleton()
    initial_balance = initial_system.balance
    
    # Pay for reorder warning
    paid_reorder = await order_repository.pay_reorder_warning(reorder.id)
    
    # Assertions
    assert paid_reorder.id == reorder.id
    assert paid_reorder.status == OrderStatus.Paid
    assert paid_reorder.is_reorder_warning is True
    
    # Check balance was updated
    final_system = await system_repository.get_singleton()
    final_balance = final_system.balance
    expected_cost = 50 * 9.5
    assert final_balance == initial_balance - expected_cost


@pytest.mark.asyncio
async def test_pay_reorder_warning_not_found(order_repository):
    """FR4.5: Test paying for non-existent reorder warning"""
    with pytest.raises(NotFoundError) as excinfo:
        await order_repository.pay_reorder_warning(999)
    
    assert "Order with id '999' not found" in str(excinfo.value)


@pytest.mark.asyncio
async def test_pay_reorder_warning_not_a_reorder(order_repository, product_repository, system_repository):
    """FR4.5: Test paying for regular order (not a reorder warning) should fail"""
    # Create a product
    product = await product_repository.create_product(
        description="Product",
        barcode="1234567890123",
        price_per_unit=10.0,
        quantity=10,
        position="1-A-1"
    )
    
    # Create regular order (not reorder warning)
    order = await order_repository.create_order(
        product_id=product.id,
        quantity=10,
        price_per_unit=10.0
    )
    
    # Try to pay as reorder warning - should fail
    from app.models.errors.bad_request import BadRequestError
    with pytest.raises(BadRequestError) as excinfo:
        await order_repository.pay_reorder_warning(order.id)
    
    assert "not a reorder warning" in str(excinfo.value)


@pytest.mark.asyncio
async def test_pay_reorder_warning_already_paid(order_repository, product_repository, system_repository):
    """FR4.5: Test paying for already paid reorder warning"""
    # Create a product
    product = await product_repository.create_product(
        description="Product",
        barcode="1234567890123",
        price_per_unit=10.0,
        quantity=5,
        position="1-A-1"
    )
    
    # Set sufficient balance
    await system_repository.set_balance(1000.0)
    
    # Issue and pay reorder warning
    reorder = await order_repository.issue_reorder_warning(
        product_id=product.id,
        quantity=10,
        price_per_unit=10.0
    )
    await order_repository.pay_reorder_warning(reorder.id)
    
    # Try to pay again - should fail
    with pytest.raises(InvalidStateError) as excinfo:
        await order_repository.pay_reorder_warning(reorder.id)
    
    assert "not in ISSUED state" in str(excinfo.value)


@pytest.mark.asyncio
async def test_pay_reorder_warning_insufficient_balance(order_repository, product_repository, system_repository):
    """FR4.5: Test paying for reorder warning with insufficient balance"""
    # Create a product
    product = await product_repository.create_product(
        description="Product",
        barcode="1234567890123",
        price_per_unit=10.0,
        quantity=5,
        position="1-A-1"
    )
    
    # Set low balance
    await system_repository.set_balance(10.0)
    
    # Issue reorder warning
    reorder = await order_repository.issue_reorder_warning(
        product_id=product.id,
        quantity=100,
        price_per_unit=10.0
    )
    
    # Try to pay - should fail due to insufficient balance
    with pytest.raises(AppError) as excinfo:
        await order_repository.pay_reorder_warning(reorder.id)
    
    assert "Insufficient balance" in str(excinfo.value)
