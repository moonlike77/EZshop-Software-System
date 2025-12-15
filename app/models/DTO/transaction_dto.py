from pydantic import BaseModel, ConfigDict
from app.models.transaction_type import TransactionType
from datetime import datetime

class TransactionCreateDTO(BaseModel):
    amount: float
    type: TransactionType
    description: str | None = None

class TransactionResponseDTO(BaseModel):
    id: int
    amount: float
    type: TransactionType
    description: str | None
    timestamp: datetime
    created_by: int | None

    model_config = ConfigDict(from_attributes=True)

class BalanceResponseDTO(BaseModel):
    balance: float

