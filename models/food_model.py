from pydantic import BaseModel, Field
from typing import List, Optional, Any

class FoodCreate(BaseModel):
    name: str = Field(..., example="Chicken Biryani Special")
    price: float = Field(..., gt=0, example=350.0)
    category: str = Field(..., example="biryani")
    description: Optional[str] = Field(None, example="Traditional Pakistani Spiced Biryani")
    vendorId: Optional[str] = Field(None, example="vendor_id_string")
    calories: Optional[int] = Field(500, example=500)
    isAvailable: bool = Field(True, example=True)
    tags: List[str] = Field([], example=["spicy", "rice", "biryani"])
    image: Optional[str] = Field(None, example="https://example.com/image.jpg")

class FoodUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    description: Optional[str] = None
    calories: Optional[int] = None
    isAvailable: Optional[bool] = None
    tags: Optional[List[str]] = None
    image: Optional[str] = None

class FoodResponse(BaseModel):
    id: str
    name: str
    price: float
    category: Optional[str] = None
    description: Optional[str] = None
    vendorId: Optional[str] = None
    vendor: Optional[Any] = None
    calories: Optional[int] = 0
    isAvailable: bool = True
    tags: List[str] = []
    image: Optional[str] = None
