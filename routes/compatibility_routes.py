from typing import List
from fastapi import APIRouter, Depends, status
from middleware.auth_middleware import get_current_user, require_roles
from schemas.user import UserRegister, UserLogin, TokenResponse
from schemas.rider import LocationSchema, AvailabilitySchema, RiderResponse
from schemas.order import OrderResponse
from controllers import auth_controller, rider_controller

router = APIRouter(tags=["Compatibility Routes"])

# Rider Auth & Compatibility Endpoints
@router.post("/api/rider/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
@router.post("/api/riders/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def rider_register(data: UserRegister):
    data.role = "rider"
    return await auth_controller.register_user(data)

@router.post("/api/rider/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
@router.post("/api/riders/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def rider_login(data: UserLogin):
    return await auth_controller.login_user(data)

# Customer Auth Compatibility Endpoints
@router.post("/api/customer/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
@router.post("/api/customers/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def customer_register(data: UserRegister):
    data.role = "customer"
    return await auth_controller.register_user(data)

@router.post("/api/customer/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
@router.post("/api/customers/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def customer_login(data: UserLogin):
    return await auth_controller.login_user(data)

# Rider Operations Compatibility
@router.get("/api/rider/{rider_id}", response_model=RiderResponse, status_code=status.HTTP_200_OK)
async def get_rider_alias(rider_id: int, current_user: dict = Depends(get_current_user)):
    return await rider_controller.get_rider_by_id(rider_id, current_user)

@router.patch("/api/rider/{rider_id}/location", status_code=status.HTTP_200_OK)
async def update_rider_location_alias(rider_id: int, data: LocationSchema, current_user: dict = Depends(require_roles(["rider", "admin"]))):
    return await rider_controller.update_rider_location(rider_id, data, current_user)

@router.patch("/api/rider/{rider_id}/available", response_model=RiderResponse, status_code=status.HTTP_200_OK)
async def update_rider_availability_alias(rider_id: int, data: AvailabilitySchema, current_user: dict = Depends(require_roles(["rider", "admin"]))):
    return await rider_controller.update_rider_availability(rider_id, data, current_user)

@router.get("/api/rider/{rider_id}/deliveries", response_model=List[OrderResponse], status_code=status.HTTP_200_OK)
async def get_rider_deliveries_alias(rider_id: int, current_user: dict = Depends(require_roles(["rider", "admin"]))):
    return await rider_controller.get_rider_deliveries(rider_id, current_user)
