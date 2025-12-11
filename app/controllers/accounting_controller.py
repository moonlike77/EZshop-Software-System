from datetime import datetime
from typing import List
from app.repositories.transaction_repository import TransactionRepository
from app.models.DTO.transaction_dto import TransactionCreateDTO, TransactionResponseDTO
from app.models.DAO.transaction_dao import TransactionDAO

class AccountingController:
    def __init__(self):
        self.repository = TransactionRepository()

    async def record_transaction(self, transaction_dto: TransactionCreateDTO, user_id: int) -> TransactionResponseDTO:
        transaction = await self.repository.create_transaction(
            amount=transaction_dto.amount,
            type=transaction_dto.type,
            description=transaction_dto.description,
            user_id=user_id
        )
        return TransactionResponseDTO.model_validate(transaction)

    async def get_history(self, start_date: datetime | None, end_date: datetime | None) -> List[TransactionResponseDTO]:
        transactions = await self.repository.get_transactions(start_date, end_date)
        return [TransactionResponseDTO.model_validate(t) for t in transactions]

    async def get_current_balance(self) -> float:
        return await self.repository.get_balance()

    async def set_balance(self, amount: float, user_id: int) -> float:
        if amount < 0:
            raise ValueError("Balance cannot be negative")
        await self.repository.set_balance(amount, user_id)
        return amount

    async def reset_balance(self, user_id: int) -> float:
        await self.repository.reset_balance(user_id)
        return 0.0
