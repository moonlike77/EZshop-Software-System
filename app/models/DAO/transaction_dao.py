from sqlalchemy import Column, Integer, Float, String, Enum, DateTime, ForeignKey
from app.models.transaction_type import TransactionType
from app.database.database import Base
from datetime import datetime, timezone

class TransactionDAO(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    amount = Column(Float, nullable=False)
    type = Column(Enum(TransactionType), nullable=False)
    description = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.now(timezone.utc))
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
