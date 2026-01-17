import pytest

from app.controllers.sale_controller import SaleController
from app.database.database import AsyncSessionLocal, init_db, reset_db

from app.models.sale_status import SaleStatus
from app.models.DTO.sale_dto import SaleDTO

from app.models.errors.notfound_error import NotFoundError
from app.models.errors.bad_request import BadRequestError
from app.models.errors.invalid_state_error import InvalidStateError

from app.models.DAO.product_dao import ProductDAO


# ---------- helpers ----------

async def seed_product(session, barcode="614141007346", qty=100, price=2.99, desc="Test Product", position="1-A-1"):
    p = ProductDAO(
        description=desc,
        barcode=barcode,
        price_per_unit=price,
        quantity=qty,
        position=position,
    )
    session.add(p)
    await session.commit()
    await session.refresh(p)
    return p


async def create_open_sale_with_item(controller: SaleController, barcode: str, amount: int):
    sale = await controller.start_sale()
    await controller.add_product_to_sale(sale.id, barcode, amount)
    return sale.id


async def close_sale(controller: SaleController, sale_id: int):
    ok = await controller.close_sale(sale_id)
    assert ok is True
    return ok


async def pay_sale(controller: SaleController, sale_id: int, cash: float):
    change = await controller.pay_sale(sale_id, cash)
    assert isinstance(change, float)
    return change


# ---------- tests ----------

@pytest.mark.asyncio
async def test_start_sale_succes():
    await reset_db()
    await init_db()

    async with AsyncSessionLocal() as session:
        c = SaleController()
        c.repo._session = session

        sale = await c.start_sale()

        assert isinstance(sale, SaleDTO)
        assert sale.id is not None
        assert sale.status == SaleStatus.OPEN
        assert sale.discount_rate == 0.0


@pytest.mark.asyncio
async def test_list_sales_success():
    await reset_db()
    await init_db()

    async with AsyncSessionLocal() as session:
        c = SaleController()
        c.repo._session = session

        s1 = await c.start_sale()
        s2 = await c.start_sale()

        res = await c.list_sales()

        ids = [x.id for x in res]
        assert s1.id in ids
        assert s2.id in ids


@pytest.mark.asyncio
async def test_get_sale_success():
    await reset_db()
    await init_db()

    async with AsyncSessionLocal() as session:
        c = SaleController()
        c.repo._session = session

        s = await c.start_sale()
        got = await c.get_sale(s.id)

        assert got.id == s.id
        assert got.status == SaleStatus.OPEN


@pytest.mark.asyncio
async def test_get_sale_not_found():
    await reset_db()
    await init_db()

    async with AsyncSessionLocal() as session:
        c = SaleController()
        c.repo._session = session

        with pytest.raises(NotFoundError):
            await c.get_sale(999)


@pytest.mark.asyncio
async def test_delete_sale_success():
    await reset_db()
    await init_db()

    async with AsyncSessionLocal() as session:
        c = SaleController()
        c.repo._session = session

        s = await c.start_sale()
        ok = await c.delete_sale(s.id)

        assert ok is True
        with pytest.raises(NotFoundError):
            await c.get_sale(s.id)


@pytest.mark.asyncio
async def test_delete_sale_not_found():
    await reset_db()
    await init_db()

    async with AsyncSessionLocal() as session:
        c = SaleController()
        c.repo._session = session

        with pytest.raises(NotFoundError):
            await c.delete_sale(999)


@pytest.mark.asyncio
async def test_add_product_success():
    await reset_db()
    await init_db()

    async with AsyncSessionLocal() as session:
        await seed_product(session, barcode="A1", qty=10, price=2.0)

        c = SaleController()
        c.repo._session = session

        s = await c.start_sale()
        ok = await c.add_product_to_sale(s.id, "A1", 2)

        assert ok is True


@pytest.mark.asyncio
async def test_add_product_bad_amount():
    await reset_db()
    await init_db()

    async with AsyncSessionLocal() as session:
        await seed_product(session, barcode="A1", qty=10, price=2.0)

        c = SaleController()
        c.repo._session = session

        s = await c.start_sale()
        with pytest.raises(BadRequestError):
            await c.add_product_to_sale(s.id, "A1", 0)


@pytest.mark.asyncio
async def test_add_product_insufficient_stock():
    await reset_db()
    await init_db()

    async with AsyncSessionLocal() as session:
        await seed_product(session, barcode="A1", qty=1, price=2.0)

        c = SaleController()
        c.repo._session = session

        s = await c.start_sale()
        with pytest.raises(BadRequestError):
            await c.add_product_to_sale(s.id, "A1", 2)


@pytest.mark.asyncio
async def test_remove_product_success():
    await reset_db()
    await init_db()

    async with AsyncSessionLocal() as session:
        await seed_product(session, barcode="A1", qty=10, price=2.0)

        c = SaleController()
        c.repo._session = session

        sale_id = await create_open_sale_with_item(c, "A1", 5)

        ok = await c.remove_product_from_sale(sale_id, "A1", 2)
        assert ok is True


@pytest.mark.asyncio
async def test_remove_product_bad_amount():
    await reset_db()
    await init_db()

    async with AsyncSessionLocal() as session:
        await seed_product(session, barcode="A1", qty=10, price=2.0)

        c = SaleController()
        c.repo._session = session

        sale_id = await create_open_sale_with_item(c, "A1", 2)

        with pytest.raises(BadRequestError):
            await c.remove_product_from_sale(sale_id, "A1", 0)


@pytest.mark.asyncio
async def test_remove_product_too_many():
    await reset_db()
    await init_db()

    async with AsyncSessionLocal() as session:
        await seed_product(session, barcode="A1", qty=10, price=2.0)

        c = SaleController()
        c.repo._session = session

        sale_id = await create_open_sale_with_item(c, "A1", 2)

        with pytest.raises(BadRequestError):
            await c.remove_product_from_sale(sale_id, "A1", 3)


@pytest.mark.asyncio
async def test_discount_sale_success():
    await reset_db()
    await init_db()

    async with AsyncSessionLocal() as session:
        c = SaleController()
        c.repo._session = session

        s = await c.start_sale()
        ok = await c.apply_discount(s.id, 0.10)

        assert ok is True
        got = await c.get_sale(s.id)
        assert got.discount_rate == 0.10


@pytest.mark.asyncio
async def test_discount_sale_bad_rate():
    await reset_db()
    await init_db()

    async with AsyncSessionLocal() as session:
        c = SaleController()
        c.repo._session = session

        s = await c.start_sale()
        with pytest.raises(BadRequestError):
            await c.apply_discount(s.id, 1.0)


@pytest.mark.asyncio
async def test_discount_sale_not_open():
    await reset_db()
    await init_db()

    async with AsyncSessionLocal() as session:
        await seed_product(session, barcode="A1", qty=10, price=2.0)

        c = SaleController()
        c.repo._session = session

        sale_id = await create_open_sale_with_item(c, "A1", 1)
        await close_sale(c, sale_id)

        with pytest.raises(InvalidStateError):
            await c.apply_discount(sale_id, 0.10)


@pytest.mark.asyncio
async def test_discount_product_success():
    await reset_db()
    await init_db()

    async with AsyncSessionLocal() as session:
        await seed_product(session, barcode="A1", qty=10, price=2.0)

        c = SaleController()
        c.repo._session = session

        sale_id = await create_open_sale_with_item(c, "A1", 2)

        ok = await c.apply_product_discount(sale_id, "A1", 0.25)
        assert ok is True


@pytest.mark.asyncio
async def test_discount_product_bad_rate():
    await reset_db()
    await init_db()

    async with AsyncSessionLocal() as session:
        await seed_product(session, barcode="A1", qty=10, price=2.0)

        c = SaleController()
        c.repo._session = session

        sale_id = await create_open_sale_with_item(c, "A1", 2)

        with pytest.raises(BadRequestError):
            await c.apply_product_discount(sale_id, "A1", -0.1)


@pytest.mark.asyncio
async def test_close_success_sets_pending_and_closed_at():
    await reset_db()
    await init_db()

    async with AsyncSessionLocal() as session:
        await seed_product(session, barcode="A1", qty=10, price=2.0)

        c = SaleController()
        c.repo._session = session

        sale_id = await create_open_sale_with_item(c, "A1", 1)
        ok = await c.close_sale(sale_id)
        assert ok is True

        got = await c.get_sale(sale_id)
        assert got.status == SaleStatus.PENDING
        assert got.closed_at is not None


@pytest.mark.asyncio
async def test_close_empty_sale_deletes_it():
    await reset_db()
    await init_db()

    async with AsyncSessionLocal() as session:
        c = SaleController()
        c.repo._session = session

        s = await c.start_sale()
        ok = await c.close_sale(s.id)
        assert ok is True

        with pytest.raises(NotFoundError):
            await c.get_sale(s.id)


@pytest.mark.asyncio
async def test_pay_success():
    await reset_db()
    await init_db()

    async with AsyncSessionLocal() as session:
        await seed_product(session, barcode="A1", qty=10, price=2.0)

        c = SaleController()
        c.repo._session = session

        sale_id = await create_open_sale_with_item(c, "A1", 2)
        await close_sale(c, sale_id)

        change = await c.pay_sale(sale_id, 10.0)
        assert change == 6.0

        got = await c.get_sale(sale_id)
        assert got.status == SaleStatus.PAID
        assert got.closed_at is not None


@pytest.mark.asyncio
async def test_pay_bad_cash_amount():
    await reset_db()
    await init_db()

    async with AsyncSessionLocal() as session:
        c = SaleController()
        c.repo._session = session

        s = await c.start_sale()
        with pytest.raises(BadRequestError):
            await c.pay_sale(s.id, 0.0)


@pytest.mark.asyncio
async def test_pay_not_pending():
    await reset_db()
    await init_db()

    async with AsyncSessionLocal() as session:
        await seed_product(session, barcode="A1", qty=10, price=2.0)

        c = SaleController()
        c.repo._session = session

        sale_id = await create_open_sale_with_item(c, "A1", 1)
        with pytest.raises(InvalidStateError):
            await c.pay_sale(sale_id, 10.0)


@pytest.mark.asyncio
async def test_points_success():
    await reset_db()
    await init_db()

    async with AsyncSessionLocal() as session:
        await seed_product(session, barcode="A1", qty=10, price=2.0)

        c = SaleController()
        c.repo._session = session

        sale_id = await create_open_sale_with_item(c, "A1", 2)
        await close_sale(c, sale_id)
        await pay_sale(c, sale_id, 10.0)

        pts = await c.get_sale_points(sale_id)
        assert pts == 4


@pytest.mark.asyncio
async def test_points_not_paid():
    await reset_db()
    await init_db()

    async with AsyncSessionLocal() as session:
        await seed_product(session, barcode="A1", qty=10, price=2.0)

        c = SaleController()
        c.repo._session = session

        sale_id = await create_open_sale_with_item(c, "A1", 1)
        await close_sale(c, sale_id)

        with pytest.raises(InvalidStateError):
            await c.get_sale_points(sale_id)
