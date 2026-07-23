from pydantic import BaseModel, Field
from typing import List, Optional, Any
from enum import Enum

class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    PICKED = "picked"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class OrderItemSchema(BaseModel):
    food_id: int = Field(..., example=1)
    quantity: int = Field(1, ge=1, example=2)
    price: Optional[float] = Field(None, example=350.0)

class OrderCreate(BaseModel):
    vendor_id: int = Field(..., example=1)
    items: List[OrderItemSchema]
    total_amount: float = Field(..., gt=0, example=700.0)
    delivery_address: str = Field(..., example="House 12, Sector F-7, Vehari")

class OrderStatusUpdate(BaseModel):
    status: OrderStatus = Field(..., example="confirmed")

class OrderResponse(BaseModel):
    id: int
    customer_id: Optional[int] = None
    vendor_id: Optional[int] = None
    rider_id: Optional[int] = None
    total_amount: float
    status: str
    delivery_address: str
    items: Optional[List[Any]] = []
    customer: Optional[Any] = None
    vendor: Optional[Any] = None
    rider: Optional[Any] = None
