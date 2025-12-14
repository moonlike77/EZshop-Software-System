from __future__ import annotations
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Float, ForeignKey, UniqueConstraint
from app.database.database import Base



class ProductTypeDAO(Base):

    __tablename__ ="product_types"
    __table_args__ = (
        UniqueConstraint("barcode", name="uq_product_types_barcode"),
        UniqueConstraint("position", name="uq_product_types_position"),
    )


    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    description: Mapped[str] = mapped_column(String, nullable=False)

    barcode: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    
    price_per_unit: Mapped[float] = mapped_column(Float, nullable=False)

    note: Mapped[str|None] = mapped_column(String, nullable=True)

    quantity: Mapped[int]= mapped_column(Integer, nullable=False, default=0)

    position: Mapped[str|None] = mapped_column(String, nullable=True)

    orders: Mapped[list["OrderDAO"]] = relationship(
        "OrderDAO", 
        back_populates="product", 
        cascade= "all, delete-orphan",
        passive_deletes=True) # This sets up a bidirectional relationship.