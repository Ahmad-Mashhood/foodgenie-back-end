from typing import List
from fastapi import APIRouter, Depends, status
from middleware.auth_middleware import get_current_user, require_roles
from schemas.rider import RiderUpdate, LocationSchema, AvailabilitySchema, RiderResponse
from schemas.order import OrderResponse
from controllers import rider_controller

router = APIRouter(prefix="/api/riders", tags=["Riders & Delivery"])

@router.get(
    "/{rider_id}",
    response_model=RiderResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Rider Profile (Protected)",
    description="Returns profile details for a rider."
)
async def get_rider_by_id(
    rider_id: int,
    current_user: dict = Depends(get_current_user)
):
    return await rider_controller.get_rider_by_id(rider_id, current_user)

@router.put(
    "/{rider_id}",
    response_model=RiderResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Rider Profile (Rider Only)",
    description="Updates rider contact information."
)
async def update_rider(
    rider_id: int,
    data: RiderUpdate,
    current_user: dict = Depends(require_roles(["rider", "admin"]))
):
    return await rider_controller.update_rider(rider_id, data, current_user)

@router.patch(
    "/{rider_id}/location",
    status_code=status.HTTP_200_OK,
    summary="Update Live GPS Location (Rider Only)",
    description="Updates current latitude and longitude coordinates for live delivery tracking."
)
async def update_rider_location(
    rider_id: int,
    data: LocationSchema,
    current_user: dict = Depends(require_roles(["rider", "admin"]))
):
    return await rider_controller.update_rider_location(rider_id, data, current_user)

@router.patch(
    "/{rider_id}/available",
    response_model=RiderResponse,
    status_code=status.HTTP_200_OK,
    summary="Toggle Rider Availability Status (Rider Only)",
    description="Toggles rider status between available (true) and unavailable (false)."
)
async def update_rider_availability(
    rider_id: int,
    data: AvailabilitySchema,
    current_user: dict = Depends(require_roles(["rider", "admin"]))
):
    return await rider_controller.update_rider_availability(rider_id, data, current_user)

@router.get(
    "/{rider_id}/deliveries",
    response_model=List[OrderResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Rider Assigned Deliveries (Rider Only)",
    description="Returns all orders assigned to the specified rider."
)
async def get_rider_deliveries(
    rider_id: int,
    current_user: dict = Depends(require_roles(["rider", "admin"]))
):
    return await rider_controller.get_rider_deliveries(rider_id, current_user)
