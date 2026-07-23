from typing import List
from fastapi import APIRouter, Depends, status
from middleware.auth_middleware import require_roles
from schemas.vendor import VendorRegister, VendorUpdate, VendorStatusUpdate, VendorResponse
from schemas.food import FoodResponse
from controllers import vendor_controller

router = APIRouter(prefix="/api/vendors", tags=["Vendors & Restaurants"])

@router.get(
    "",
    response_model=List[VendorResponse],
    status_code=status.HTTP_200_OK,
    summary="Get All Approved Vendors",
    description="Returns list of active, approved local vendors and restaurants in Vehari."
)
async def get_all_vendors():
    return await vendor_controller.get_all_vendors()

@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    summary="Register a New Vendor",
    description="Registers a vendor account and returns access token."
)
async def register_vendor(data: VendorRegister):
    return await vendor_controller.register_vendor(data)

@router.get(
    "/{vendor_id}",
    response_model=VendorResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Single Vendor Details",
    description="Returns details for a vendor profile."
)
async def get_vendor_by_id(vendor_id: int):
    return await vendor_controller.get_vendor_by_id(vendor_id)

@router.put(
    "/{vendor_id}",
    response_model=VendorResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Vendor Profile (Vendor Only)",
    description="Updates vendor metadata."
)
async def update_vendor(
    vendor_id: int,
    data: VendorUpdate,
    current_user: dict = Depends(require_roles(["vendor", "admin"]))
):
    return await vendor_controller.update_vendor(vendor_id, data, current_user)

@router.get(
    "/{vendor_id}/menu",
    response_model=List[FoodResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Vendor Menu Items",
    description="Returns all food items offered by the specified vendor."
)
async def get_vendor_menu(vendor_id: int):
    return await vendor_controller.get_vendor_menu(vendor_id)

@router.patch(
    "/{vendor_id}/status",
    response_model=VendorResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Vendor Store Status (Vendor Only)",
    description="Toggles vendor operational status (open or closed)."
)
async def update_vendor_status(
    vendor_id: int,
    data: VendorStatusUpdate,
    current_user: dict = Depends(require_roles(["vendor", "admin"]))
):
    return await vendor_controller.update_vendor_status(vendor_id, data, current_user)
