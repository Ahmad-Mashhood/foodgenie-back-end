from pydantic import BaseModel, Field
from typing import Optional

class RiderUpdate(BaseModel):
    name: Optional[str] = Field(None, example="FastAPI Test Rider")
    phone: Optional[str] = Field(None, example="+923003334444")

class LocationSchema(BaseModel):
    latitude: float = Field(..., example=30.0440)
    longitude: float = Field(..., example=72.3440)

class AvailabilitySchema(BaseModel):
    is_available: bool = Field(..., example=True)

class RiderResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[str] = None
    is_available: bool = True
    latitude: Optional[float] = None
    longitude: Optional[float] = None
