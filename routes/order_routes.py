from typing import List
from fastapi import APIRouter, Depends, status
from middleware.auth import get_current_user, require_roles
from models.order_model import OrderCreate, OrderStatusUpdate, OrderResponse
from controllers import order_controller

router = APIRouter(prefix="/api/orders", tags=["Orders"])

@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Place New Order (Customer Only)",
    description="Submits a new food order from a customer to a vendor."
)
async def create_order(
    data: OrderCreate,
    current_user: dict = Depends(require_roles(["customer", "admin"]))
):
    return await order_controller.create_order(data, current_user)

@router.get(
    "/customer/{customer_id}",
    response_model=List[OrderResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Customer Order History (Customer Only)",
    description="Returns order history for a specific customer."
)
async def get_customer_orders(
    customer_id: str,
    current_user: dict = Depends(require_roles(["customer", "admin"]))
):
    return await order_controller.get_customer_orders(customer_id, current_user)

@router.get(
    "/vendor/{vendor_id}",
    response_model=List[OrderResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Vendor Orders (Vendor Only)",
    description="Returns orders received by a specific vendor."
)
async def get_vendor_orders(
    vendor_id: str,
    current_user: dict = Depends(require_roles(["vendor", "admin"]))
):
    return await order_controller.get_vendor_orders(vendor_id, current_user)

@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Order Details (Protected)",
    description="Fetches order status, items, address, and participant details by Order ID."
)
async def get_order_by_id(
    order_id: str,
    current_user: dict = Depends(get_current_user)
):
    return await order_controller.get_order_by_id(order_id, current_user)

@router.patch(
    "/{order_id}/status",
    response_model=OrderResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Order Status (Vendor/Rider Only)",
    description="Transitions order state (pending → confirmed → preparing → ready_for_pickup → out_for_delivery → delivered)."
)
async def update_order_status(
    order_id: str,
    data: OrderStatusUpdate,
    current_user: dict = Depends(require_roles(["vendor", "rider", "admin"]))
):
    return await order_controller.update_order_status(order_id, data, current_user)

@router.delete(
    "/{order_id}",
    status_code=status.HTTP_200_OK,
    summary="Cancel Order (Customer Only)",
    description="Cancels an order if it has not yet been delivered."
)
async def cancel_order(
    order_id: str,
    current_user: dict = Depends(require_roles(["customer", "admin"]))
):
    return await order_controller.cancel_order(order_id, current_user)
