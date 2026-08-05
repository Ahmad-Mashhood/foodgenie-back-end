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
    email: str
    frontend_url: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "email": "ahmad@gmail.com"
            }
        }

class VerifyOtpRequest(BaseModel):
    email: Optional[str] = None
    otp: Optional[str] = None

class ResetPasswordRequest(BaseModel):
    token: Optional[str] = None
    email: Optional[str] = None
    otp: Optional[str] = None
    new_password: str

    class Config:
        json_schema_extra = {
            "example": {
                "token": "abc123defxyz...",
                "new_password": "mynewpassword123"
            }
        }

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

    class Config:
        json_schema_extra = {
            "example": {
                "old_password": "oldpass123",
                "new_password": "newpass123"
            }
        }
