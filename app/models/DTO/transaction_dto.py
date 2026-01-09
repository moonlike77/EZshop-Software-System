from pydantic import BaseModel, ConfigDict, field_validator
from app.models.transaction_type import TransactionType
from datetime import datetime

class TransactionCreateDTO(BaseModel):
    amount: float
    type: TransactionType
    description: str | None = None

    @field_validator('amount')
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Amount must be positive')
        return v

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

