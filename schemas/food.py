from pydantic import BaseModel, Field
from typing import Optional, Any

class FoodCreate(BaseModel):
    name: str = Field(..., example="Chicken Biryani Special")
    price: float = Field(..., gt=0, example=350.0)
    category: str = Field(..., example="biryani")
    description: Optional[str] = Field(None, example="Authentic Pakistani Spiced Chicken Biryani")
    calories: Optional[int] = Field(500, example=500)
    is_available: bool = Field(True, example=True)
    vendor_id: Optional[int] = Field(None, example=1)

class FoodUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    description: Optional[str] = None
    calories: Optional[int] = None
    is_available: Optional[bool] = None

class FoodResponse(BaseModel):
    id: int
    name: str
    price: float
    category: str
    description: Optional[str] = None
    calories: Optional[int] = 0
    is_available: bool = True
    vendor_id: Optional[int] = None
    vendor: Optional[Any] = None
