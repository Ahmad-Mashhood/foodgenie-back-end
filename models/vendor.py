from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.orm import relationship
from models import Base

class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    city = Column(String(100), default="Vehari")
    phone = Column(String(50), nullable=True)
    category = Column(String(100), default="restaurant")
    status = Column(String(50), default="open")
    rating = Column(Float, default=0.0)
    is_approved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    foods = relationship("Food", back_populates="vendor", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="vendor")
    reviews = relationship("Review", back_populates="vendor")
