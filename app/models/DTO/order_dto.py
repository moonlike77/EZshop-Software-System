from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class OrderCreateDTO(BaseModel):
    product_barcode: str = Field(..., min_length=1)
    quantity: int = Field(..., gt=0)
    price_per_unit: float = Field(..., gt=0)


class OrderPayForDTO(BaseModel):
    product_barcode: str = Field(..., min_length=1)
    quantity: int = Field(..., gt=0)
    price_per_unit: float = Field(..., gt=0)


class OrderResponseDTO(BaseModel):
    id: int
    product_barcode: str
    quantity: int
    price_per_unit: float
    status: str
    issue_date: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)