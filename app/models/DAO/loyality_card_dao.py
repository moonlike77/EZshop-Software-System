from sqlalchemy import Column, Integer, String
from app.database.database import Base


class LoyalityCardDAO(Base):
    __tablename__ = "loyality cards"

    id = Column(Integer, primary_key=True, autoincrement=True)
    points = Column(Integer, nullable=False)