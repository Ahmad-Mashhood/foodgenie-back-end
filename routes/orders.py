from typing import List
from fastapi import APIRouter, Depends, status
from middleware.auth_middleware import get_current_user, require_roles
from schemas.order import OrderCreate, OrderStatusUpdate, OrderResponse
from controllers import order_controller

router = APIRouter(prefix="/api/orders", tags=["Orders"])

@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Place a New Order (Customer Only)",
    description="Submits a food order with list of items, quantities, and delivery address."
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
    description="Returns all orders placed by the specified customer."
)
async def get_customer_orders(
    customer_id: int,
    current_user: dict = Depends(require_roles(["customer", "admin"]))
):
    return await order_controller.get_customer_orders(customer_id, current_user)

@router.get(
    "/vendor/{vendor_id}",
    response_model=List[OrderResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Vendor Incoming Orders (Vendor Only)",
    description="Returns all orders submitted to the specified vendor."
)
async def get_vendor_orders(
    vendor_id: int,
    current_user: dict = Depends(require_roles(["vendor", "admin"]))
):
    return await order_controller.get_vendor_orders(vendor_id, current_user)

@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Order Details (Protected)",
    description="Returns details for a specific order."
)
async def get_order_by_id(
    order_id: int,
    current_user: dict = Depends(get_current_user)
):
    return await order_controller.get_order_by_id(order_id, current_user)

@router.patch(
    "/{order_id}/status",
    response_model=OrderResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Order Status (Vendor & Rider Only)",
    description="Updates order lifecycle status (e.g. confirmed, preparing, picked, delivered)."
)
async def update_order_status(
    order_id: int,
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
    order_id: int,
    current_user: dict = Depends(require_roles(["customer", "admin"]))
):
    return await order_controller.cancel_order(order_id, current_user)
