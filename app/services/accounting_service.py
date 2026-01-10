from datetime import datetime
from app.repositories.transaction_repository import TransactionRepository
from app.models.DTO.transaction_dto import TransactionCreateDTO, TransactionResponseDTO
from app.models.user_type import UserType
from app.models.DAO.transaction_dao import TransactionDAO

class AccountingService:
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

    async def get_history(self, start_date: datetime | None, end_date: datetime | None) -> list[TransactionResponseDTO]:
        transactions = await self.repository.get_transactions(start_date, end_date)
        return [TransactionResponseDTO.model_validate(t) for t in transactions]

    async def get_current_balance(self) -> float:
        return await self.repository.get_balance()
