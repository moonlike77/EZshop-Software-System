import pytest
from app.models.errors.bad_request import BadRequestError
from app.routes.sale_route import remove_product_from_sale
from app.routes.sale_route import apply_product_discount_to_sale


@pytest.mark.asyncio
async def test_sale_route_get_sale_rejects_id_le_zero_direct_call():
    from app.routes.sale_route import get_sale
    with pytest.raises(BadRequestError):
        await get_sale(0)

@pytest.mark.asyncio
async def test_sale_route_delete_sale_rejects_id_le_zero_direct_call():
    from app.routes.sale_route import delete_sale
    with pytest.raises(BadRequestError):
        await delete_sale(0)

@pytest.mark.asyncio
async def test_sale_route_add_product_rejects_sale_id_le_zero_direct_call():
    from app.routes.sale_route import add_product_to_sale
    with pytest.raises(BadRequestError):
        await add_product_to_sale(sale_id=0, barcode="123", amount=1)

@pytest.mark.asyncio
async def test_sale_route_add_product_rejects_amount_le_zero_direct_call():
    from app.routes.sale_route import add_product_to_sale
    with pytest.raises(BadRequestError):
        await add_product_to_sale(sale_id=1, barcode="123", amount=0)

@pytest.mark.asyncio
async def test_sale_route_remove_product_rejects_amount_le_zero_direct_call():
    from app.routes.sale_route import remove_product_from_sale
    with pytest.raises(BadRequestError):
        await remove_product_from_sale(sale_id=1, barcode="123", amount=0)

@pytest.mark.asyncio
async def test_sale_route_apply_discount_rejects_invalid_rate_direct_call():
    from app.routes.sale_route import apply_discount_to_sale
    with pytest.raises(BadRequestError):
        await apply_discount_to_sale(sale_id=1, discount_rate=1.0)

@pytest.mark.asyncio
async def test_sale_route_apply_product_discount_rejects_invalid_rate_direct_call():
    from app.routes.sale_route import apply_product_discount_to_sale
    with pytest.raises(BadRequestError):
        await apply_product_discount_to_sale(sale_id=1, product_barcode="123", discount_rate=-0.1)

@pytest.mark.asyncio
async def test_sale_route_pay_sale_rejects_cash_amount_le_zero_direct_call():
    from app.routes.sale_route import pay_sale
    with pytest.raises(BadRequestError):
        await pay_sale(sale_id=1, cash_amount=0.0)

@pytest.mark.asyncio
async def test_sale_route_get_points_rejects_sale_id_le_zero_direct_call():
    from app.routes.sale_route import get_sale_points
    with pytest.raises(BadRequestError):
        await get_sale_points(0)


@pytest.mark.asyncio
async def test_sale_route_remove_product_rejects_sale_id_le_zero_direct_call():
    with pytest.raises(BadRequestError):
        await remove_product_from_sale(sale_id=0, barcode="abc", amount=1)

@pytest.mark.asyncio
async def test_sale_route_apply_product_discount_rejects_sale_id_le_zero_direct_call():
    with pytest.raises(BadRequestError):
        await apply_product_discount_to_sale(sale_id=0, product_barcode="abc", discount_rate=0.1)