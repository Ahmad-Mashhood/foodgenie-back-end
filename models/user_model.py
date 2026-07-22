from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Any
from enum import Enum

class UserRole(str, Enum):
    CUSTOMER = "customer"
    VENDOR = "vendor"
    RIDER = "rider"
    ADMIN = "admin"

class UserPreferences(BaseModel):
    diet: str = ""
    calories: int = 2000
    healthGoals: List[str] = []

class UserRegister(BaseModel):
    name: str = Field(..., example="Ahmad Mashhood")
    email: EmailStr = Field(..., example="ahmad@example.com")
    password: str = Field(..., min_length=6, example="password123")
    phone: Optional[str] = Field(None, example="+923001234567")
    role: UserRole = UserRole.CUSTOMER

class UserLogin(BaseModel):
    email: EmailStr = Field(..., example="ahmad@example.com")
    password: str = Field(..., example="password123")

class UserPreferencesUpdate(BaseModel):
    diet: Optional[str] = None
    calories: Optional[int] = None
    healthGoals: Optional[List[str]] = None

class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    preferences: Optional[UserPreferencesUpdate] = None

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str
    phone: Optional[str] = None
    preferences: Optional[UserPreferences] = None
    favorites: Optional[List[Any]] = []
    availability: Optional[bool] = True

class TokenResponse(BaseModel):
    token: str
    role: str
    user: Optional[dict] = None
    vendor: Optional[dict] = None
