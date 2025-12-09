from sqlalchemy import Column, Integer, String
from app.database.database import Base
from app.models.DTO.loyality_card_dto import LoyalityCardDTO


class CustomerDAO(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    #card = Column(LoyalityCardDTO, nullable=True)