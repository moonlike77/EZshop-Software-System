from pydantic import BaseModel, Field
from typing import Optional
from app.models.DTO.loyality_card_dto import LoyalityCardDTO

class CustomerDTO(BaseModel):
    id: Optional[int] = None
    name: str = Field(min_length=5)
    card: Optional[LoyalityCardDTO] = None