from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.models.sale_status import SaleStatus
from app.models.DTO.sale_line_dto import SaleLineDTO


class SaleDTO(BaseModel):
    id: int
    status: SaleStatus
    discount_rate: float
    created_at: datetime
    closed_at: Optional[datetime] = None
    lines: List[SaleLineDTO] = []