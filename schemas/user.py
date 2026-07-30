from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Any
from enum import Enum

class UserRole(str, Enum):
    CUSTOMER = "customer"
    RIDER = "rider"
    ADMIN = "admin"
    VENDOR = "vendor"

class UserRegister(BaseModel):
    name: str = Field(..., example="Ahmad Mashhood")
    email: EmailStr = Field(..., example="ahmad@example.com")
    password: str = Field(..., min_length=6, example="password123")
    phone: Optional[str] = Field(None, example="+923001234567")
    role: UserRole = Field(UserRole.CUSTOMER, example="customer")

class UserLogin(BaseModel):
    email: EmailStr = Field(..., example="ahmad@example.com")
    password: str = Field(..., example="password123")

class GoogleAuthRequest(BaseModel):
    token: str
    role: str = "customer"
    phone: Optional[str] = None
    city: Optional[str] = None
    category: Optional[str] = None
    password: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    phone: Optional[str] = None

class TokenResponse(BaseModel):
    token: str
    role: str
    user: Optional[dict] = None
    vendor: Optional[dict] = None

class ForgotPasswordRequest(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")

class VerifyOtpRequest(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")
    otp: str = Field(..., min_length=6, max_length=6, example="123456")

class ResetPasswordRequest(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")
    otp: str = Field(..., min_length=6, max_length=6, example="123456")
    new_password: str = Field(..., min_length=6, example="newpassword123")
