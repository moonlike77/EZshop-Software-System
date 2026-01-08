from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from app.database.database import Base


class ProductDAO(Base):
    __tablename__ = "product_types"

    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(String, nullable=False)
    barcode = Column(String, nullable=False, unique=True)
    price_per_unit = Column(Float, nullable=False)
    note = Column(String, nullable=True)
    quantity = Column(Integer, nullable=False, default=0)
    position = Column(String, nullable=True)

    orders = relationship(
        "OrderDAO",
        back_populates="product",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
