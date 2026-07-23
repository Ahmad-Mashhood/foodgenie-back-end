from pydantic import BaseModel, Field
from typing import Optional

class ReviewCreate(BaseModel):
    vendor_id: int = Field(..., example=1)
    food_id: Optional[int] = Field(None, example=1)
    rating: float = Field(..., ge=1.0, le=5.0, example=4.5)
    comment: Optional[str] = Field(None, example="Delicious food and fast delivery!")

class ReviewResponse(BaseModel):
    id: int
    user_id: int
    vendor_id: int
    food_id: Optional[int] = None
    rating: float
    comment: Optional[str] = None

class RecommendationCriteria(BaseModel):
    diet_type: Optional[str] = Field("any", example="vegetarian")
    max_calories: Optional[int] = Field(2000, example=600)
    allergies: Optional[str] = Field(None, example="nuts")
    preferred_cuisine: Optional[str] = Field(None, example="Pakistani")
