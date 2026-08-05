from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from models import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="customer")
    reset_token = Column(String(500), nullable=True, default=None)
    reset_token_expires_at = Column(DateTime, nullable=True, default=None)
    created_at = Column(DateTime, default=datetime.utcnow)


    # Relationships
    orders = relationship("Order", foreign_keys="Order.customer_id", back_populates="customer")
    reviews = relationship("Review", back_populates="user")
    preferences = relationship("UserPreferences", back_populates="user", uselist=False)
