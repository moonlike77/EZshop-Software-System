from sqlalchemy import Column, Integer, String
from app.database.database import Base


class LoyalityCardDAO(Base):
    __tablename__ = "loyality_cards"

    card_id = Column(Integer, primary_key=True, autoincrement=True)
    points = Column(Integer, nullable=False)