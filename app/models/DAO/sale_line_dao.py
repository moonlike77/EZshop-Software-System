from sqlalchemy import Column, Integer, Float, String, Enum, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database.database import Base
from app.models.sale_status import SaleStatus

class SaleLineDAO(Base):
    __tablename__ = "sale_lines"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False)
    product_barcode = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    price_per_unit = Column(Float, nullable=False)
    discount_rate = Column(Float, nullable=False, default=0.0)

    sale = relationship("SaleDAO", back_populates="lines")