from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from enum import Enum

class VendorStatus(str, Enum):
    OPEN = "open"
    CLOSED = "closed"

class VendorRegister(BaseModel):
    name: str = Field(..., example="Savour Foods Vehari")
    email: EmailStr = Field(..., example="vendor@savour.com")
    password: str = Field(..., min_length=6, example="password123")
    city: str = Field("Vehari", example="Vehari")
    phone: Optional[str] = Field(None, example="+923001234567")
    category: Optional[str] = Field("Pakistani", example="Pakistani")
    cuisine: Optional[str] = Field("Biryani & Pulao", example="Biryani & Pulao")
    address: Optional[str] = Field(None, example="Jinnah Shaheed Road, Vehari")

class VendorUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    category: Optional[str] = None
    cuisine: Optional[str] = None
    address: Optional[str] = None
    openingTime: Optional[str] = None
    closingTime: Optional[str] = None

class VendorStatusUpdate(BaseModel):
    status: VendorStatus

class VendorResponse(BaseModel):
    id: str
    name: str
    email: str
    city: Optional[str] = "Vehari"
    phone: Optional[str] = None
    category: Optional[str] = None
    cuisine: Optional[str] = None
    status: Optional[str] = "open"
    rating: Optional[float] = 0.0
    isApproved: Optional[bool] = False
    isActive: Optional[bool] = True
    address: Optional[str] = None
    logo: Optional[str] = None
    coverImage: Optional[str] = None
