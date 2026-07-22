from typing import List
from fastapi import APIRouter, Depends, status
from middleware.auth import get_current_user, require_roles
from models.rider_model import RiderUpdate, LocationSchema, AvailabilitySchema, RiderResponse
from models.order_model import OrderResponse
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
    rider_id: str,
    current_user: dict = Depends(get_current_user)
):
    return await rider_controller.get_rider_by_id(rider_id, current_user)

@router.put(
    "/{rider_id}",
    response_model=RiderResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Rider Profile (Rider Only)",
    description="Updates rider name or contact info."
)
async def update_rider(
    rider_id: str,
    data: RiderUpdate,
    current_user: dict = Depends(require_roles(["rider", "admin"]))
):
    return await rider_controller.update_rider(rider_id, data, current_user)

@router.patch(
    "/{rider_id}/location",
    status_code=status.HTTP_200_OK,
    summary="Update Live GPS Location (Rider Only)",
    description="Updates current latitude/longitude coordinates for live order tracking."
)
async def update_rider_location(
    rider_id: str,
    data: LocationSchema,
    current_user: dict = Depends(require_roles(["rider", "admin"]))
):
    return await rider_controller.update_rider_location(rider_id, data, current_user)

@router.patch(
    "/{rider_id}/available",
    response_model=RiderResponse,
    status_code=status.HTTP_200_OK,
    summary="Toggle Rider Availability Status (Rider Only)",
    description="Toggles rider status between available (online) and unavailable (offline)."
)
async def update_rider_availability(
    rider_id: str,
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
    rider_id: str,
    current_user: dict = Depends(require_roles(["rider", "admin"]))
):
    return await rider_controller.get_rider_deliveries(rider_id, current_user)
