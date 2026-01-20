# app/controllers/return_controller.py
from typing import List, Optional
from app.repositories.return_repository import ReturnRepository
from app.models.DTO.return_dto import ReturnDTO, ReturnLineDTO
from app.models.return_status import ReturnStatus
from app.models.errors.notfound_error import NotFoundError
from app.models.errors.bad_request import BadRequestError
from app.models.errors.conflict_error import ConflictError 
from app.models.errors.invalid_state_error import InvalidStateError

# چون فایل‌های بقیه رو نداری، اینجا فرض میکنیم ایمپورت میشن. 
# اگر زیرش خط قرمز کشید نگران نباش، وقتی مرج بشه درست میشه.
# اما اگر میخوای تست کنی، باید این فایل‌ها باشه.
#try:
#    from app.repositories.product_repository import ProductRepository
#    from app.repositories.sale_repository import SaleRepository
#    from app.repositories.system_repository import SystemRepository
#except ImportError:
    # فقط برای اینکه کد بدون بقیه فایل‌ها کرش نکنه (ماک)
#    pass

class ReturnController:
    def __init__(self):
        self.repo = ReturnRepository()
        # مخازن مربوط به بقیه اعضا
        # self.product_repo = ProductRepository()
        # self.sale_repo = SaleRepository()
        # self.system_repo = SystemRepository()

    # Helper برای تبدیل DAO به DTO
    def _dao_to_dto(self, dao) -> ReturnDTO:
        lines_dto = [
            ReturnLineDTO(
                id=line.id,
                return_id=line.return_id,
                product_barcode=line.product_barcode,
                quantity=line.quantity,
                price_per_unit=line.price_per_unit
            ) for line in dao.lines
        ]
        return ReturnDTO(
            id=dao.id,
            sale_id=dao.sale_id,
            status=dao.status,
            created_at=dao.created_at,
            closed_at=dao.closed_at,
            lines=lines_dto
        )

    async def start_return(self, sale_id: int) -> ReturnDTO:
        # 1. چک کنیم که فروش وجود دارد و وضعیتش PAID است
        # sale = await self.sale_repo.get_sale(sale_id)
        # if not sale: raise NotFoundError("Sale not found")
        # if sale.status != "PAID": raise AppError("Return allowed only on paid sales", 420)
        
        # فعلا بدون چک کردن فروش (چون کدش رو نداری) می‌سازیم:
        new_return = await self.repo.create_return(sale_id)
        return self._dao_to_dto(new_return)

    async def list_returns(self) -> List[ReturnDTO]:
        daos = await self.repo.list_returns()
        return [self._dao_to_dto(d) for d in daos]

    async def get_return(self, return_id: int) -> ReturnDTO:
        dao = await self.repo.get_return(return_id)
        if not dao:
            raise NotFoundError("Return not found")
        return self._dao_to_dto(dao)

    async def get_returns_by_sale(self, sale_id: int) -> List[ReturnDTO]:
        daos = await self.repo.get_returns_by_sale(sale_id)
        return [self._dao_to_dto(d) for d in daos]

    async def add_item(self, return_id: int, barcode: str, amount: int) -> bool:
        # 1. پیدا کردن مرجوعی
        return_dao = await self.repo.get_return(return_id)
        if not return_dao:
            raise NotFoundError("Return not found")
        
        # 2. چک کردن وضعیت (فقط OPEN میشه تغییر داد)
        if return_dao.status != ReturnStatus.OPEN:
            raise InvalidStateError("Cannot modify a closed return")

        # 3. چک کردن اینکه کالا توی اون فروش بوده یا نه و قیمت چنده
        # اینجا باید از SaleRepository استفاده کنی تا قیمت رو پیدا کنی
        # sale = await self.sale_repo.get_sale(return_dao.sale_id)
        # item_in_sale = next((x for x in sale.lines if x.product_barcode == barcode), None)
        # if not item_in_sale: raise NotFoundError("Product not in sale")
        
        # مقدار بازگشتی نباید از مقدار فروخته شده بیشتر باشه (لاجیک پیچیده)
        
        # فعلا قیمت رو ثابت میگیریم (چون کد Sale رو نداریم):
        
        return await self.repo.add_line(return_dao, barcode, amount)

    async def remove_item(self, return_id: int, barcode: str, amount: int) -> bool:
        return_dao = await self.repo.get_return(return_id)
        if not return_dao:
            raise NotFoundError("Return not found")
            
        if return_dao.status != ReturnStatus.OPEN:
            raise InvalidStateError("Cannot remove items from a closed return")
            
        success = await self.repo.remove_line_quantity(return_dao, barcode, amount)
        # طبق Swagger اگر موفق بود True برمیگردونه اما اگر آیتم نبود یا... باید هندل شه
        return success # در Route این رو دیکشنری میکنیم

    async def close_return(self, return_id: int) -> bool:
        return_dao = await self.repo.get_return(return_id)
        if not return_dao:
            raise NotFoundError("Return not found")
        
        if return_dao.status != ReturnStatus.OPEN:
             raise InvalidStateError("Invalid Return state to be closed")

        # 1. اگر مرجوعی خالی بود، حذفش کن
        if not return_dao.lines:
            await self.repo.delete_return(return_id)
            return True # یا شاید فالس، ولی طبق داکیومنت دیلیت میشه

        # 2. برگرداندن کالاها به انبار (Inventory)
        # for line in return_dao.lines:
        #     await self.product_repo.increase_quantity(line.product_barcode, line.quantity)

        await self.repo.update_status(return_id, ReturnStatus.CLOSED, None)
        return True

    async def reimburse_return(self, return_id: int) -> dict:
        return_dao = await self.repo.get_return(return_id)
        if not return_dao:
            raise NotFoundError("Return not found")
        
        if return_dao.status != ReturnStatus.CLOSED:
             raise InvalidStateError("Return must be closed before reimbursement")

        # محاسبه مبلغ کل
        total_refund = round(sum(line.quantity * line.price_per_unit for line in return_dao.lines))

        # آپدیت بالانس سیستم
        # await self.system_repo.update_balance(-total_refund)
        
        await self.repo.update_status(return_id, ReturnStatus.REIMBURSED, total_refund)
        return {"refund_amount": total_refund}

    async def delete_return(self, return_id: int):
        return_dao = await self.repo.get_return(return_id)
        if not return_dao:
            raise NotFoundError("Return not found")
            
        if return_dao.status == ReturnStatus.REIMBURSED:
             raise InvalidStateError("Cannot delete a reimbursed return")
             
        await self.repo.delete_return(return_id)