from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.sale_status import SaleStatus

class SaleLineDTO(BaseModel):
    id: int
    sale_id: int
    product_barcode: str
    quantity: int
    price_per_unit: float
    discount_rate: float