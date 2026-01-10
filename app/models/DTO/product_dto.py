from pydantic import BaseModel, Field
from typing import Optional


class ProductCreateDTO(BaseModel):
    description: str = Field(..., min_length=1)
    barcode: str = Field(..., min_length=1)
    price_per_unit: float = Field(..., gt=0)
    note: Optional[str] = Field(None, min_length=1)
    quantity: Optional[int] = Field(0, ge=0)
    position: Optional[str] = None


class ProductUpdateDTO(BaseModel):
    description: Optional[str] = Field(None, min_length=1)
    barcode: Optional[str] = Field(None, min_length=1)
    price_per_unit: Optional[float] = Field(None, gt=0)
    note: Optional[str] = Field(None, min_length=1)
    quantity: Optional[int] = Field(None, ge=0)
    position: Optional[str] = None


class ProductResponseDTO(BaseModel):
    id: int
    description: str
    barcode: str
    price_per_unit: float
    note: Optional[str] = None
    quantity: int
    position: Optional[str] = None

    class Config:
        from_attributes = True
