from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.database import Base
from app.models.return_status import ReturnStatus

class ReturnDAO(Base):
    __tablename__ = "returns"

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # تغییر موقت: حذف ForeignKey برای اینکه بدون جدول Sales کار کنه
    sale_id = Column(Integer, nullable=False) 
    # sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False) # نسخه اصلی
    
    status = Column(Enum(ReturnStatus), default=ReturnStatus.OPEN, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)
    
    # ارتباط با خطوط مرجوعی (این مشکلی نداره چون ReturnLineDAO همینجاست)
    lines = relationship("ReturnLineDAO", back_populates="return_transaction", cascade="all, delete-orphan")
    
    # تغییر موقت: کامنت کردن ارتباط با SaleDAO
    # sale = relationship("SaleDAO") 

class ReturnLineDAO(Base):
    __tablename__ = "return_lines"

    id = Column(Integer, primary_key=True, autoincrement=True)
    return_id = Column(Integer, ForeignKey("returns.id"), nullable=False)
    product_barcode = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    price_per_unit = Column(Float, nullable=False)

    return_transaction = relationship("ReturnDAO", back_populates="lines")