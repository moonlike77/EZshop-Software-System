from sqlalchemy import Column, Integer, String, Enum
from app.database.database import Base


class CustomerDAO(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    surname = Column(String, nullable=False)
