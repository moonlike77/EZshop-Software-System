from sqlalchemy import Column, Integer, String, ForeignKey
from app.database.database import Base
from sqlalchemy.orm import relationship


class CustomerDAO(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    card_id = Column(Integer, ForeignKey("loyalty_cards.card_id"), nullable=True)
    card = relationship("LoyaltyCardDAO", backref="customer", uselist=False, lazy="joined")