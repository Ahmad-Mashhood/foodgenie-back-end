from typing import List
from fastapi import APIRouter, Depends, status
from middleware.auth import require_roles
from models.user_model import UserResponse
from models.vendor_model import VendorResponse
from models.order_model import OrderResponse
from controllers import admin_controller

router = APIRouter(prefix="/api/admin", tags=["Admin Administration"])

@router.get(
    "/users",
    response_model=List[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="Get All Platform Users (Admin Only)",
    description="Returns list of all customers, riders, and users on the platform."
)
async def get_all_users(
    current_user: dict = Depends(require_roles(["admin"]))
):
    return await admin_controller.get_all_users()

@router.get(
    "/vendors",
    response_model=List[VendorResponse],
    status_code=status.HTTP_200_OK,
    summary="Get All Platform Vendors (Admin Only)",
    description="Returns list of all registered vendors regardless of approval status."
)
async def get_all_vendors(
    current_user: dict = Depends(require_roles(["admin"]))
):
    return await admin_controller.get_all_vendors()

@router.patch(
    "/vendors/{vendor_id}/approve",
    response_model=VendorResponse,
    status_code=status.HTTP_200_OK,
    summary="Approve Vendor Account (Admin Only)",
    description="Approves a pending vendor registration, allowing them to list foods."
)
async def approve_vendor(
    vendor_id: str,
    current_user: dict = Depends(require_roles(["admin"]))
):
    return await admin_controller.approve_vendor(vendor_id)

@router.get(
    "/orders",
    response_model=List[OrderResponse],
    status_code=status.HTTP_200_OK,
    summary="Get All Platform Orders (Admin Only)",
    description="Returns complete platform order audit log."
)
async def get_all_orders(
    current_user: dict = Depends(require_roles(["admin"]))
):
    return await admin_controller.get_all_orders()

@router.get(
    "/analytics",
    status_code=status.HTTP_200_OK,
    summary="Get Platform Analytics (Admin Only)",
    description="Returns high-level platform statistics (users count, orders count, total revenue, status breakdown)."
)
async def get_analytics(
    current_user: dict = Depends(require_roles(["admin"]))
):
    return await admin_controller.get_analytics()
