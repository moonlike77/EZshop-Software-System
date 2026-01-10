from datetime import datetime
from typing import List
from app.repositories.transaction_repository import TransactionRepository
from app.models.DTO.transaction_dto import TransactionCreateDTO, TransactionResponseDTO
from app.models.DAO.transaction_dao import TransactionDAO

class AccountingController:
    """
    Controller for managing accounting operations including transaction recording,
    history retrieval, and balance management.
    """

    def __init__(self):
        """
        Initialize the AccountingController with a TransactionRepository.
        """
        self.repository = TransactionRepository()

    async def record_transaction(self, transaction_dto: TransactionCreateDTO, user_id: int) -> TransactionResponseDTO:
        """
        Record a new transaction for a user.

        Args:
            transaction_dto (TransactionCreateDTO): Data transfer object containing transaction details.
            user_id (int): The ID of the user performing the transaction.

        Returns:
            TransactionResponseDTO: The created transaction data.
        """
        transaction = await self.repository.create_transaction(
            amount=transaction_dto.amount,
            type=transaction_dto.type,
            description=transaction_dto.description,
            user_id=user_id
        )
        return TransactionResponseDTO.model_validate(transaction)

    async def get_history(self, start_date: datetime | None, end_date: datetime | None) -> List[TransactionResponseDTO]:
        """
        Retrieve transaction history, optionally filtered by date range.

        Args:
            start_date (datetime | None): The start date for filtering transactions.
            end_date (datetime | None): The end date for filtering transactions.

        Returns:
            List[TransactionResponseDTO]: A list of transactions matching the criteria.
        
        Raises:
            ValueError: If start_date is after end_date.
        """
        if start_date and end_date and start_date > end_date:
            raise ValueError("Start date cannot be after end date")

        transactions = await self.repository.get_transactions(start_date, end_date)
        return [TransactionResponseDTO.model_validate(t) for t in transactions]

    async def get_current_balance(self) -> float:
        """
        Retrieve the current system balance.

        Returns:
            float: The current balance amount.
        """
        return await self.repository.get_balance()

    async def set_balance(self, amount: float, user_id: int) -> float:
        """
        Set the balance to a specific amount.

        Args:
            amount (float): The target balance amount.
            user_id (int): The ID of the user setting the balance.

        Returns:
            float: The new balance amount.

        Raises:
            ValueError: If the provided amount is negative.
        """
        if amount < 0:
            raise ValueError("Balance cannot be negative")
        await self.repository.set_balance(amount, user_id)
        return amount

    async def reset_balance(self, user_id: int) -> float:
        """
        Reset the balance to zero.

        Args:
            user_id (int): The ID of the user resetting the balance.

        Returns:
            float: The new balance (0.0).
        """
        await self.repository.reset_balance(user_id)
        return 0.0
