import pytest

from init_db import reset, init_db
from sqlalchemy import select, delete

from app.repositories.sale_repository import SaleRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.system_repository import SystemRepository

from app.models.errors.notfound_error import NotFoundError
from app.models.errors.bad_request import BadRequestError
from app.models.errors.conflict_error import ConflictError
from app.models.errors.invalid_state_error import InvalidStateError

from app.models.sale_status import SaleStatus
from app.models.DAO.sale_dao import SaleDAO
from app.models.DAO.sale_line_dao import SaleLineDAO
from app.models.DAO.system_dao import SystemInfoDAO

@pytest.mark.asyncio
async def _create_product(barcode: str, qty: int = 100, price: float = 10.0):
    prod_repo = ProductRepository()
    return await prod_repo.create_product(
        description=f"TestProd-{barcode}",
        barcode=barcode,
        price_per_unit=price,
        quantity=qty,
        position="1-A-1"
    )

@pytest.mark.asyncio
async def _create_sale_and_add_item(repo: SaleRepository, barcode: str, amount: int):
    sale = await repo.create_sale()
    await repo.add_product_to_sale(sale.id, barcode, amount)
    return sale.id

@pytest.mark.asyncio
async def test_sale_repo_create_sale_success():
    await reset(); await init_db()
    repo = SaleRepository()

    sale = await repo.create_sale()
    assert sale.id is not None
    assert sale.status == SaleStatus.OPEN
    assert sale.discount_rate == 0.0


@pytest.mark.asyncio
async def test_sale_repo_list_sales_returns_list():
    await reset(); await init_db()
    repo = SaleRepository()

    await repo.create_sale()
    await repo.create_sale()

    sales = await repo.list_sales()
    assert isinstance(sales, list)
    assert len(sales) >= 2


@pytest.mark.asyncio
async def test_sale_repo_get_sale_not_found():
    await reset(); await init_db()
    repo = SaleRepository()

    with pytest.raises(NotFoundError):
        await repo.get_sale(99999999)


@pytest.mark.asyncio
async def test_sale_repo_get_sale_pending_no_lines_is_considered_cancelled():

    await reset(); await init_db()
    repo = SaleRepository()

    sale = await repo.create_sale()

    async with await repo._get_session() as session:
        db_sale = await session.get(SaleDAO, sale.id)
        db_sale.status = SaleStatus.PENDING
        await session.commit()

    with pytest.raises(NotFoundError):
        await repo.get_sale(sale.id)


@pytest.mark.asyncio
async def test_sale_repo_delete_sale_not_found():
    await reset(); await init_db()
    repo = SaleRepository()

    with pytest.raises(NotFoundError):
        await repo.delete_sale(99999999)


@pytest.mark.asyncio
async def test_sale_repo_delete_paid_sale_conflict():
    await reset(); await init_db()
    repo = SaleRepository()

    sale = await repo.create_sale()
    async with await repo._get_session() as session:
        db_sale = await session.get(SaleDAO, sale.id)
        db_sale.status = SaleStatus.PAID
        await session.commit()

    with pytest.raises(ConflictError):
        await repo.delete_sale(sale.id)


@pytest.mark.asyncio
async def test_sale_repo_delete_sale_restores_stock_quantities():

    await reset(); await init_db()
    repo = SaleRepository()
    prod_repo = ProductRepository()

    barcode = "sale-del-restore"
    prod = await _create_product(barcode, qty=10, price=2.0)

    sale_id = await _create_sale_and_add_item(repo, barcode, 3)

    prod_after_add = await prod_repo.get_product_by_id(prod.id)
    assert prod_after_add.quantity == 7

    ok = await repo.delete_sale(sale_id)
    assert ok is True

    prod_after_del = await prod_repo.get_product_by_id(prod.id)
    assert prod_after_del.quantity == 10


@pytest.mark.asyncio
async def test_sale_repo_add_product_bad_amount():
    await reset(); await init_db()
    repo = SaleRepository()

    sale = await repo.create_sale()
    with pytest.raises(BadRequestError):
        await repo.add_product_to_sale(sale.id, "any", 0)


@pytest.mark.asyncio
async def test_sale_repo_add_product_sale_not_found():
    await reset(); await init_db()
    repo = SaleRepository()

    with pytest.raises(NotFoundError):
        await repo.add_product_to_sale(999999, "any", 1)


@pytest.mark.asyncio
async def test_sale_repo_add_product_wrong_status():
    await reset(); await init_db()
    repo = SaleRepository()

    sale = await repo.create_sale()
    async with await repo._get_session() as session:
        db_sale = await session.get(SaleDAO, sale.id)
        db_sale.status = SaleStatus.PENDING
        await session.commit()

    with pytest.raises(InvalidStateError):
        await repo.add_product_to_sale(sale.id, "any", 1)


@pytest.mark.asyncio
async def test_sale_repo_add_product_product_not_found():
    await reset(); await init_db()
    repo = SaleRepository()

    sale = await repo.create_sale()
    with pytest.raises(NotFoundError):
        await repo.add_product_to_sale(sale.id, "nonexistent-barcode", 1)


@pytest.mark.asyncio
async def test_sale_repo_add_product_insufficient_stock_conflict():
    await reset(); await init_db()
    repo = SaleRepository()

    barcode = "sale-insuff"
    await _create_product(barcode, qty=1, price=1.0)
    sale = await repo.create_sale()

    with pytest.raises(BadRequestError):
        await repo.add_product_to_sale(sale.id, barcode, 2)


@pytest.mark.asyncio
async def test_sale_repo_add_product_success_decreases_stock_and_creates_line():
    await reset(); await init_db()
    repo = SaleRepository()
    prod_repo = ProductRepository()

    barcode = "sale-add-ok"
    prod = await _create_product(barcode, qty=10, price=3.0)

    sale = await repo.create_sale()
    ok = await repo.add_product_to_sale(sale.id, barcode, 4)
    assert ok is True

    updated_prod = await prod_repo.get_product_by_id(prod.id)
    assert updated_prod.quantity == 6

    async with await repo._get_session() as session:
        res = await session.execute(
            select(SaleLineDAO).where(
                SaleLineDAO.sale_id == sale.id,
                SaleLineDAO.product_barcode == barcode
            )
        )
        line = res.scalars().first()
        assert line is not None
        assert line.quantity == 4
        assert line.price_per_unit == 3.0


@pytest.mark.asyncio
async def test_sale_repo_remove_product_bad_amount():
    await reset(); await init_db()
    repo = SaleRepository()

    sale = await repo.create_sale()
    with pytest.raises(BadRequestError):
        await repo.remove_product_from_sale(sale.id, "any", 0)


@pytest.mark.asyncio
async def test_sale_repo_remove_product_sale_not_found():
    await reset(); await init_db()
    repo = SaleRepository()

    with pytest.raises(NotFoundError):
        await repo.remove_product_from_sale(999999, "any", 1)


@pytest.mark.asyncio
async def test_sale_repo_remove_product_wrong_status():
    await reset(); await init_db()
    repo = SaleRepository()

    barcode = "sale-rem-status"
    await _create_product(barcode, qty=10, price=1.0)
    sale_id = await _create_sale_and_add_item(repo, barcode, 1)

    async with await repo._get_session() as session:
        db_sale = await session.get(SaleDAO, sale_id)
        db_sale.status = SaleStatus.PENDING
        await session.commit()

    with pytest.raises(InvalidStateError):
        await repo.remove_product_from_sale(sale_id, barcode, 1)


@pytest.mark.asyncio
async def test_sale_repo_remove_product_line_not_found():
    await reset(); await init_db()
    repo = SaleRepository()

    barcode = "sale-rem-lnf"
    await _create_product(barcode, qty=10, price=1.0)
    sale = await repo.create_sale()

    with pytest.raises(NotFoundError):
        await repo.remove_product_from_sale(sale.id, barcode, 1)


@pytest.mark.asyncio
async def test_sale_repo_remove_product_success_partial_restores_stock_and_decreases_line_qty():
    await reset(); await init_db()
    repo = SaleRepository()
    prod_repo = ProductRepository()

    barcode = "sale-rem-partial"
    prod = await _create_product(barcode, qty=10, price=1.0)
    sale_id = await _create_sale_and_add_item(repo, barcode, 5) 

    ok = await repo.remove_product_from_sale(sale_id, barcode, 2)
    assert ok is True

    updated_prod = await prod_repo.get_product_by_id(prod.id)
    assert updated_prod.quantity == 7

    async with await repo._get_session() as session:
        from sqlalchemy import select
        res = await session.execute(
            select(SaleLineDAO).where(
                SaleLineDAO.sale_id == sale_id,
                SaleLineDAO.product_barcode == barcode
            )
        )
        line = res.scalars().first()
        assert line is not None
        assert line.quantity == 3


@pytest.mark.asyncio
async def test_sale_repo_remove_product_deletes_line_when_amount_eq_line_qty():
    await reset(); await init_db()
    repo = SaleRepository()
    prod_repo = ProductRepository()

    barcode = "sale-rem-delete"
    prod = await _create_product(barcode, qty=10, price=1.0)
    sale_id = await _create_sale_and_add_item(repo, barcode, 3)

    ok = await repo.remove_product_from_sale(sale_id, barcode, 3)
    assert ok is True

    updated_prod = await prod_repo.get_product_by_id(prod.id)
    assert updated_prod.quantity == 10

    async with await repo._get_session() as session:
        from sqlalchemy import select
        res = await session.execute(
            select(SaleLineDAO).where(
                SaleLineDAO.sale_id == sale_id,
                SaleLineDAO.product_barcode == barcode
            )
        )
        line = res.scalars().first()
        assert line is None


@pytest.mark.asyncio
async def test_sale_repo_remove_product_fails_when_amount_gt_line_qty():
    await reset(); await init_db()
    repo = SaleRepository()

    barcode = "sale-rem-too-much"
    await _create_product(barcode, qty=10, price=1.0)
    sale_id = await _create_sale_and_add_item(repo, barcode, 3)

    with pytest.raises(BadRequestError):
        await repo.remove_product_from_sale(sale_id, barcode, 10)


@pytest.mark.asyncio
async def test_sale_repo_apply_discount_invalid_rate():
    await reset(); await init_db()
    repo = SaleRepository()

    sale = await repo.create_sale()
    with pytest.raises(BadRequestError):
        await repo.apply_discount(sale.id, 1.0)


@pytest.mark.asyncio
async def test_sale_repo_apply_discount_wrong_status():
    await reset(); await init_db()
    repo = SaleRepository()

    sale = await repo.create_sale()
    async with await repo._get_session() as session:
        db_sale = await session.get(SaleDAO, sale.id)
        db_sale.status = SaleStatus.PENDING
        await session.commit()

    with pytest.raises(InvalidStateError):
        await repo.apply_discount(sale.id, 0.1)


@pytest.mark.asyncio
async def test_sale_repo_apply_product_discount_line_not_found():
    await reset(); await init_db()
    repo = SaleRepository()

    barcode = "sale-disc-line"
    await _create_product(barcode, qty=10, price=1.0)
    sale = await repo.create_sale()

    with pytest.raises(NotFoundError):
        await repo.apply_product_discount(sale.id, barcode, 0.1)


@pytest.mark.asyncio
async def test_sale_repo_close_sale_wrong_status():
    await reset(); await init_db()
    repo = SaleRepository()

    sale = await repo.create_sale()
    async with await repo._get_session() as session:
        db_sale = await session.get(SaleDAO, sale.id)
        db_sale.status = SaleStatus.PAID
        await session.commit()

    with pytest.raises(InvalidStateError):
        await repo.close_sale(sale.id)


@pytest.mark.asyncio
async def test_sale_repo_pay_sale_wrong_state():
    await reset(); await init_db()
    repo = SaleRepository()

    sale = await repo.create_sale()
    with pytest.raises(InvalidStateError):
        await repo.pay_sale(sale.id, 10.0)


@pytest.mark.asyncio
async def test_sale_repo_pay_sale_insufficient_cash():
    await reset(); await init_db()
    repo = SaleRepository()

    barcode = "sale-pay-bad"
    await _create_product(barcode, qty=10, price=10.0)
    sale_id = await _create_sale_and_add_item(repo, barcode, 1)
    await repo.close_sale(sale_id)

    with pytest.raises(BadRequestError):
        await repo.pay_sale(sale_id, 0.5)


@pytest.mark.asyncio
async def test_sale_repo_pay_sale_success_updates_status_and_balance():
    await reset(); await init_db()
    repo = SaleRepository()
    sys_repo = SystemRepository()

    await sys_repo.set_balance(0.0)

    barcode = "sale-pay-ok"
    await _create_product(barcode, qty=10, price=10.0)
    sale_id = await _create_sale_and_add_item(repo, barcode, 2)
    await repo.close_sale(sale_id)

    change = await repo.pay_sale(sale_id, 50.0)
    assert change == 30.0

    sale = await repo.get_sale(sale_id)
    assert sale.status == SaleStatus.PAID

    system = await sys_repo.get_singleton()
    assert system.balance == 20.0


@pytest.mark.asyncio
async def test_sale_repo_get_points_wrong_state():
    await reset(); await init_db()
    repo = SaleRepository()

    sale = await repo.create_sale()
    with pytest.raises(InvalidStateError):
        await repo.get_sale_points(sale.id)


@pytest.mark.asyncio
async def test_sale_repo_get_points_success_equals_floor_total():

    await reset(); await init_db()
    repo = SaleRepository()
    sys_repo = SystemRepository()
    await sys_repo.set_balance(0.0)

    barcode = "sale-points-ok"
    await _create_product(barcode, qty=10, price=12.7)
    sale_id = await _create_sale_and_add_item(repo, barcode, 1)
    await repo.close_sale(sale_id)
    await repo.pay_sale(sale_id, 20.0)

    points = await repo.get_sale_points(sale_id)
    assert points == 12


@pytest.mark.asyncio
async def test_sale_repo_apply_product_discount_invalid_rate_raises():
    await reset(); await init_db()
    repo = SaleRepository()

    with pytest.raises(BadRequestError):
        await repo.apply_product_discount(sale_id=1, product_barcode="any", discount_rate=-0.1)

    with pytest.raises(BadRequestError):
        await repo.apply_product_discount(sale_id=1, product_barcode="any", discount_rate=1.0)


@pytest.mark.asyncio
async def test_sale_repo_pay_sale_invalid_cash_amount_raises():
    await reset(); await init_db()
    repo = SaleRepository()

    with pytest.raises(BadRequestError):
        await repo.pay_sale(sale_id=1, cash_amount=0.0)

    with pytest.raises(BadRequestError):
        await repo.pay_sale(sale_id=1, cash_amount=-10.0)


@pytest.mark.asyncio
async def test_sale_repo_apply_discount_success_updates_sale():
    await reset(); await init_db()
    repo = SaleRepository()

    sale = await repo.create_sale()

    ok = await repo.apply_discount(sale.id, 0.2)
    assert ok is True

    updated = await repo.get_sale(sale.id)
    assert updated.discount_rate == 0.2


@pytest.mark.asyncio
async def test_sale_repo_apply_product_discount_success_updates_line():
    await reset(); await init_db()
    repo = SaleRepository()

    barcode = "sale-disc-ok"
    await _create_product(barcode, qty=10, price=10.0)

    sale_id = await _create_sale_and_add_item(repo, barcode, 2)

    ok = await repo.apply_product_discount(sale_id, barcode, 0.15)
    assert ok is True

    async with await repo._get_session() as session:
        res = await session.execute(
            select(SaleLineDAO).where(
                SaleLineDAO.sale_id == sale_id,
                SaleLineDAO.product_barcode == barcode
            )
        )
        line = res.scalars().first()
        assert line is not None
        assert line.discount_rate == 0.15


@pytest.mark.asyncio
async def test_sale_repo_close_empty_sale_deletes_sale():
    await reset(); await init_db()
    repo = SaleRepository()

    sale = await repo.create_sale()

    ok = await repo.close_sale(sale.id)
    assert ok is True

    with pytest.raises(NotFoundError):
        await repo.get_sale(sale.id)


@pytest.mark.asyncio
async def test_sale_repo_pay_sale_sets_closed_at_if_missing():
    await reset(); await init_db()
    repo = SaleRepository()

    barcode = "sale-pay-closedat"
    await _create_product(barcode, qty=10, price=5.0)
    sale_id = await _create_sale_and_add_item(repo, barcode, 2)

    await repo.close_sale(sale_id)

    async with await repo._get_session() as session:
        db_sale = await session.get(SaleDAO, sale_id)
        db_sale.closed_at = None
        await session.commit()

    change = await repo.pay_sale(sale_id, 50.0)
    assert change == 40.0

    sale = await repo.get_sale(sale_id)
    assert sale.status == SaleStatus.PAID
    assert sale.closed_at is not None


@pytest.mark.asyncio
async def test_sale_repo_pay_sale_creates_system_info_if_missing():
    await reset(); await init_db()
    repo = SaleRepository()

    async with await repo._get_session() as session:
        await session.execute(delete(SystemInfoDAO))
        await session.commit()

    barcode = "sale-pay-syscreate"
    await _create_product(barcode, qty=10, price=4.0)
    sale_id = await _create_sale_and_add_item(repo, barcode, 2)
    await repo.close_sale(sale_id)

    change = await repo.pay_sale(sale_id, 20.0)
    assert change == 12.0

    async with await repo._get_session() as session:
        res = await session.execute(select(SystemInfoDAO))
        system_info = res.scalars().first()
        assert system_info is not None
        assert system_info.balance == 8.0


@pytest.mark.asyncio
async def test_sale_repo_apply_product_discount_wrong_status_raises():
    await reset(); await init_db()
    repo = SaleRepository()

    barcode = "sale-disc-wrong-status"
    await _create_product(barcode, qty=10, price=1.0)

    sale_id = await _create_sale_and_add_item(repo, barcode, 1)

    await repo.close_sale(sale_id)

    with pytest.raises(InvalidStateError):
        await repo.apply_product_discount(sale_id, barcode, 0.1)
