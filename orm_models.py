import uuid
from datetime import datetime
from typing import Any, Dict, List
from sqlalchemy import Column, String, Float, Boolean, Integer, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

def generate_uuid() -> str:
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"

    id = Column(String(50), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True)
    role = Column(String(50), nullable=False, default="customer")
    is_active = Column(Boolean, default=True)
    preferences = Column(JSON, nullable=True, default=lambda: {"diet": "", "calories": 2000, "healthGoals": []})
    favorites = Column(JSON, nullable=True, default=list)
    availability = Column(Boolean, default=True)
    location = Column(JSON, nullable=True, default=lambda: {"lat": 0.0, "lng": 0.0})
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    rider_profile = relationship("Rider", back_populates="user", uselist=False, cascade="all, delete-orphan")

class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(String(50), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    city = Column(String(100), default="Vehari")
    phone = Column(String(50), nullable=True)
    category = Column(String(100), nullable=True)
    cuisine = Column(String(100), nullable=True)
    address = Column(String(500), nullable=True)
    status = Column(String(50), default="open")
    rating = Column(Float, default=0.0)
    is_approved = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    logo = Column(String(500), nullable=True)
    cover_image = Column(String(500), nullable=True)
    opening_time = Column(String(50), nullable=True)
    closing_time = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    foods = relationship("Food", back_populates="vendor", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="vendor")

class Food(Base):
    __tablename__ = "foods"

    id = Column(String(50), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)
    category = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    vendor_id = Column(String(50), ForeignKey("vendors.id", ondelete="CASCADE"), nullable=True, index=True)
    calories = Column(Integer, default=0)
    is_available = Column(Boolean, default=True)
    tags = Column(JSON, nullable=True, default=list)
    image = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    vendor = relationship("Vendor", back_populates="foods")

class Order(Base):
    __tablename__ = "orders"

    id = Column(String(50), primary_key=True, default=generate_uuid)
    customer_id = Column(String(50), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    vendor_id = Column(String(50), ForeignKey("vendors.id", ondelete="SET NULL"), nullable=True, index=True)
    rider_id = Column(String(50), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    items = Column(JSON, nullable=False, default=list)
    total_amount = Column(Float, nullable=False)
    status = Column(String(50), default="pending")
    delivery_address = Column(JSON, nullable=True)
    payment_method = Column(String(50), default="cash")
    special_instructions = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    customer = relationship("User", foreign_keys=[customer_id])
    vendor = relationship("Vendor", back_populates="orders")
    rider = relationship("User", foreign_keys=[rider_id])

class Rider(Base):
    __tablename__ = "riders"

    id = Column(String(50), primary_key=True, default=generate_uuid)
    user_id = Column(String(50), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    is_available = Column(Boolean, default=True)
    current_location = Column(JSON, nullable=True, default=lambda: {"lat": 30.0440, "lng": 72.3440})
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="rider_profile")
