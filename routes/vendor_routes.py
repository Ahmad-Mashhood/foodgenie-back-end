from typing import List
from fastapi import APIRouter, Depends, status
from middleware.auth import require_roles
from models.vendor_model import VendorRegister, VendorUpdate, VendorStatusUpdate, VendorResponse
from controllers import vendor_controller

router = APIRouter(prefix="/api/vendors", tags=["Vendors & Restaurants"])

@router.get(
    "",
    response_model=List[VendorResponse],
    status_code=status.HTTP_200_OK,
    summary="Get All Vendors",
    description="Public endpoint to list active local vendors and restaurants in Vehari."
)
async def get_all_vendors():
    return await vendor_controller.get_all_vendors()

@router.get(
    "/{vendor_id}",
    response_model=VendorResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Single Vendor Details",
    description="Fetches profile details for a single vendor by ID."
)
async def get_vendor_by_id(vendor_id: str):
    return await vendor_controller.get_vendor_by_id(vendor_id)

@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    summary="Vendor Registration",
    description="Registers a new local restaurant or food vendor."
)
async def register_vendor(data: VendorRegister):
    return await vendor_controller.register_vendor(data)

@router.put(
    "/{vendor_id}",
    response_model=VendorResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Vendor Profile (Vendor Only)",
    description="Updates information of a vendor account."
)
async def update_vendor(
    vendor_id: str,
    data: VendorUpdate,
    current_user: dict = Depends(require_roles(["vendor", "admin"]))
):
    return await vendor_controller.update_vendor(vendor_id, data, current_user)

@router.get(
    "/{vendor_id}/menu",
    status_code=status.HTTP_200_OK,
    summary="Get Vendor Menu Items",
    description="Fetches all menu items associated with a specific vendor ID."
)
async def get_vendor_menu(vendor_id: str):
    return await vendor_controller.get_vendor_menu(vendor_id)

@router.patch(
    "/{vendor_id}/status",
    response_model=VendorResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Vendor Open/Closed Status (Vendor Only)",
    description="Toggles vendor shop status between 'open' and 'closed'."
)
async def update_vendor_status(
    vendor_id: str,
    data: VendorStatusUpdate,
    current_user: dict = Depends(require_roles(["vendor", "admin"]))
):
    return await vendor_controller.update_vendor_status(vendor_id, data, current_user)
