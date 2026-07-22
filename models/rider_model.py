from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class LocationSchema(BaseModel):
    lat: float = Field(..., example=30.0440)
    lng: float = Field(..., example=72.3440)
    orderId: Optional[str] = Field(None, example="order_id_string")

class AvailabilitySchema(BaseModel):
    isAvailable: bool = Field(..., example=True)

class RiderUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None

class RiderResponse(BaseModel):
    id: str
    name: str
    email: str
    phone: Optional[str] = None
    role: str = "rider"
    isAvailable: bool = True
    location: Optional[Dict[str, float]] = None
