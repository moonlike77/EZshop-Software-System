from sqlalchemy import Column, Integer, Float, String, Enum, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database.database import Base
from app.models.sale_status import SaleStatus


class SaleDAO(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, autoincrement=True)
    status = Column(Enum(SaleStatus), nullable=False, default=SaleStatus.OPEN)
    discount_rate = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    closed_at = Column(DateTime(timezone=True), nullable=True)

    lines = relationship("SaleLineDAO", back_populates="sale", cascade="all, delete-orphan")


