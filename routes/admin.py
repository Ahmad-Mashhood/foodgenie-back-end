from typing import List
from fastapi import APIRouter, Depends, status
from middleware.auth_middleware import require_roles
from schemas.user import UserResponse
from schemas.vendor import VendorResponse
from schemas.order import OrderResponse
from controllers import admin_controller

router = APIRouter(prefix="/api/admin", tags=["Admin Administration"])

@router.get(
    "/users",
    response_model=List[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="Get All Platform Users (Admin Only)",
    description="Returns list of all registered platform users."
)
async def get_all_users(current_user: dict = Depends(require_roles(["admin"]))):
    return await admin_controller.get_all_users()

@router.get(
    "/vendors",
    response_model=List[VendorResponse],
    status_code=status.HTTP_200_OK,
    summary="Get All Vendors Including Unapproved (Admin Only)",
    description="Returns all vendor profiles."
)
async def get_all_vendors(current_user: dict = Depends(require_roles(["admin"]))):
    return await admin_controller.get_all_vendors()

@router.patch(
    "/vendors/{vendor_id}/approve",
    response_model=VendorResponse,
    status_code=status.HTTP_200_OK,
    summary="Approve Vendor Account (Admin Only)",
    description="Sets vendor approval status to True."
)
async def approve_vendor(
    vendor_id: int,
    current_user: dict = Depends(require_roles(["admin"]))
):
    return await admin_controller.approve_vendor(vendor_id)

@router.get(
    "/orders",
    response_model=List[OrderResponse],
    status_code=status.HTTP_200_OK,
    summary="Get All Platform Orders (Admin Only)",
    description="Returns all orders across the platform."
)
async def get_all_orders(current_user: dict = Depends(require_roles(["admin"]))):
    return await admin_controller.get_all_orders()

@router.get(
    "/analytics",
    status_code=status.HTTP_200_OK,
    summary="Get System Analytics Summary (Admin Only)",
    description="Returns system metrics: total users, total vendors, total orders, total revenue, most ordered foods, top rated vendors."
)
async def get_analytics(current_user: dict = Depends(require_roles(["admin"]))):
    return await admin_controller.get_analytics()
