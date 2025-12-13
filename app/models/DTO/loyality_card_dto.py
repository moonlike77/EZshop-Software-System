from pydantic import BaseModel, Field
from typing import Optional

class LoyalityCardDTO(BaseModel):
    card_id: str = Field(min_length=10, max_length=10)
    points: Optional[int] = None