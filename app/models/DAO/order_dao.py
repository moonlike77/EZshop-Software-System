from __future__ import annotations
import enum
from datetime import datetime, timezone
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Float, ForeignKey, DateTime, Enum 
from app.database.database import Base


class OrderStatusEnum(str, enum.Enum):
    ISSUED = "ISSUED"
    PAID = "PAID"
    COMPLETED = "COMPLETED"


class OrderDAO(Base):
    __tablename__= "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    product_barcode: Mapped[str] = mapped_column(String, ForeignKey("product_types.barcode", ondelete= "CASCADE"), nullable=False)

    quantity: Mapped[int] = mapped_column(Integer, nullable = False)

    price_per_unit: Mapped[float] = mapped_column(Float, nullable=False)

    status: Mapped[OrderStatusEnum] = mapped_column(Enum(OrderStatusEnum), nullable=False, default=OrderStatusEnum.ISSUED) # FR4.7: List all orders (issued, payed, completed)

    issue_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default= lambda: datetime.now(timezone.utc),)

    product: Mapped["ProductTypeDAO"] = relationship(
        "ProductTypeDAO",
        back_populates ="orders",
        lazy="joined",
   )