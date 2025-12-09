from pydantic import BaseModel
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

    class Config:
        from_attributes = True
