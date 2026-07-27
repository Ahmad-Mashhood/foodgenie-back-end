from fastapi import APIRouter, Depends, status
from middleware.auth_middleware import get_current_user
from schemas.user import UserRegister, UserLogin, TokenResponse, UserResponse, GoogleAuthRequest
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
    return await auth_controller.google_login(data.token, data.role)

@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    summary="Get Current Logged in User Profile",
    description="Returns identity payload for the currently authenticated Bearer token owner."
)
async def get_me(current_user: dict = Depends(get_current_user)):
    return await auth_controller.get_me(current_user)
