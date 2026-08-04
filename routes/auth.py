from fastapi import APIRouter, Depends, status
from middleware.auth_middleware import get_current_user
from schemas.user import (
    UserRegister, UserLogin, TokenResponse, UserResponse, GoogleAuthRequest,
    ForgotPasswordRequest, VerifyOtpRequest, ResetPasswordRequest
)
from controllers import auth_controller

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new User",
    description="Registers a user account (customer, rider, admin) with hashed password and returns signed JWT token."
)
async def register(data: UserRegister):
    return await auth_controller.register_user(data)

@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="User & Vendor Login",
    description="Authenticates credentials against User, Vendor, and Rider accounts and returns signed JWT token."
)
async def login(data: UserLogin):
    return await auth_controller.login_user(data)

@router.post(
    "/google",
    status_code=status.HTTP_200_OK,
    summary="Google Auth Login / Register",
    description="Verifies Firebase Google ID token, logs in or registers user automatically with role, and returns JWT token."
)
async def google_auth(data: GoogleAuthRequest):
    return await auth_controller.google_login(
        token=data.token,
        role=data.role,
        phone=data.phone,
        city=data.city,
        category=data.category,
        password=data.password
    )

@router.post(
    "/forgot-password",
    status_code=status.HTTP_200_OK,
    summary="Send Password Reset Verification Code to Email",
    description="Generates a 6-digit verification code for password recovery."
)
async def forgot_password(data: ForgotPasswordRequest):
    return await auth_controller.forgot_password(data.email)

@router.post(
    "/verify-otp",
    status_code=status.HTTP_200_OK,
    summary="Verify Password Reset OTP Code",
    description="Validates 6-digit verification code."
)
async def verify_otp(data: VerifyOtpRequest):
    return await auth_controller.verify_otp(data.email, data.otp)

@router.post(
    "/reset-password",
    status_code=status.HTTP_200_OK,
    summary="Reset Password with OTP",
    description="Updates user, vendor, or rider password after verifying OTP."
)
async def reset_password(data: ResetPasswordRequest):
    return await auth_controller.reset_password(data.email, data.otp, data.new_password)

@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    summary="Get Current Logged in User Profile",
    description="Returns identity payload for the currently authenticated Bearer token owner."
)
async def get_me(current_user: dict = Depends(get_current_user)):
    return await auth_controller.get_me(current_user)

@router.put(
    "/profile",
    status_code=status.HTTP_200_OK,
    summary="Update Logged In User Profile & Credentials",
    description="Updates email, name, phone, or password in database for current account."
)
async def update_profile(
    data: dict,
    current_user: dict = Depends(get_current_user)
):
    return await auth_controller.update_profile(current_user, data)

