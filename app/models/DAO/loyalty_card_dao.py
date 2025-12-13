from sqlalchemy import Column, Integer
from app.database.database import Base


class LoyaltyCardDAO(Base):
    __tablename__ = "loyalty_cards"

    card_id = Column(Integer, primary_key=True, autoincrement=True)
    points = Column(Integer, nullable=False)