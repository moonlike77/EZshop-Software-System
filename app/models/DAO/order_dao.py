from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum
from app.database.database import Base
from app.models.order_status import OrderStatus

class OrderDAO(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("product_types.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price_per_unit = Column(Float, nullable=False)
    status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.Issued)
    issue_date = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    product = relationship(
        "ProductTypeDAO",
        back_populates="orders",
        lazy="joined"
    )