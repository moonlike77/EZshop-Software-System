from pydantic import BaseModel, Field
from typing import Optional

class CustomerDTO(BaseModel):
    id: Optional[int] = None
    name: str = Field(min_length=5)
    surname: Optional[str] = None