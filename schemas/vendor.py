from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from enum import Enum

class VendorCategory(str, Enum):
    RESTAURANT = "restaurant"
    HOTEL = "hotel"
    HOME_BASED = "home_based"

class VendorStatus(str, Enum):
    OPEN = "open"
    CLOSED = "closed"

class VendorRegister(BaseModel):
    name: str = Field(..., example="Vehari Spice Grill")
    email: EmailStr = Field(..., example="vendor@vehari.com")
    password: str = Field(..., min_length=6, example="password123")
    city: Optional[str] = Field("Vehari", example="Vehari")
    phone: Optional[str] = Field(None, example="+923007778888")
    category: Optional[VendorCategory] = Field(VendorCategory.RESTAURANT, example="restaurant")

class VendorUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    category: Optional[VendorCategory] = None
    address: Optional[str] = None

class VendorStatusUpdate(BaseModel):
    status: VendorStatus = Field(..., example="open")

class VendorResponse(BaseModel):
    id: int
    name: str
    email: str
    city: Optional[str] = "Vehari"
    phone: Optional[str] = None
    category: Optional[str] = "restaurant"
    status: Optional[str] = "open"
    rating: Optional[float] = 0.0
    is_approved: Optional[bool] = False
