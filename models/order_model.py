from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from enum import Enum

class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY_FOR_PICKUP = "ready_for_pickup"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class OrderItem(BaseModel):
    menuItemId: Optional[str] = None
    name: str = Field(..., example="Chicken Biryani")
    price: float = Field(..., example=350.0)
    quantity: int = Field(1, ge=1, example=2)

class OrderCreate(BaseModel):
    vendorId: str = Field(..., example="vendor_object_id")
    items: List[OrderItem]
    totalAmount: float = Field(..., gt=0, example=700.0)
    deliveryAddress: Dict[str, Any] = Field(..., example={"address": "House 12, Sector F-7, Vehari", "lat": 30.0440, "lng": 72.3440})
    paymentMethod: Optional[str] = Field("cash", example="cash")
    specialInstructions: Optional[str] = Field(None, example="Extra spicy")

class OrderStatusUpdate(BaseModel):
    status: OrderStatus
    riderId: Optional[str] = None

class OrderResponse(BaseModel):
    id: str
    customerId: Optional[str] = None
    vendorId: Optional[str] = None
    riderId: Optional[str] = None
    items: List[OrderItem]
    totalAmount: float
    status: str
    deliveryAddress: Optional[Dict[str, Any]] = None
    paymentMethod: Optional[str] = "cash"
    createdAt: Optional[Any] = None
    customer: Optional[Any] = None
    vendor: Optional[Any] = None
    rider: Optional[Any] = None
