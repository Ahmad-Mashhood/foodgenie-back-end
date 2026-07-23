from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy import select, or_, desc
from database import AsyncSessionLocal, serialize_doc
from models.order_model import OrderCreate, OrderStatusUpdate
from orm_models import Order, User, Vendor

async def create_order(data: OrderCreate, current_user: dict):
    try:
        cust_id = current_user["id"]

        async with AsyncSessionLocal() as session:
            order_obj = Order(
                customer_id=str(cust_id),
                vendor_id=str(data.vendorId),
                rider_id=None,
                items=[item.dict() for item in data.items],
                total_amount=data.totalAmount,
                status="pending",
                delivery_address=data.deliveryAddress,
                payment_method=data.paymentMethod or "cash",
                special_instructions=data.specialInstructions or "",
                created_at=datetime.utcnow()
            )

            session.add(order_obj)
            await session.commit()
            await session.refresh(order_obj)

            res_dict = serialize_doc(order_obj)
            res_dict["customerId"] = res_dict.get("customer_id")
            res_dict["vendorId"] = res_dict.get("vendor_id")
            res_dict["riderId"] = res_dict.get("rider_id")
            res_dict["totalAmount"] = res_dict.get("total_amount")
            res_dict["createdAt"] = res_dict.get("created_at")
            return res_dict
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Order creation failed: {str(e)}"
        )

async def get_order_by_id(order_id: str, current_user: dict):
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(Order).where(Order.id == str(order_id)))
        order = res.scalar_one_or_none()
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

        serialized = serialize_doc(order)
        serialized["customerId"] = serialized.get("customer_id")
        serialized["vendorId"] = serialized.get("vendor_id")
        serialized["riderId"] = serialized.get("rider_id")
        serialized["totalAmount"] = serialized.get("total_amount")
        serialized["createdAt"] = serialized.get("created_at")

        if serialized.get("customer_id"):
            c_res = await session.execute(select(User).where(User.id == str(serialized["customer_id"])))
            c_doc = c_res.scalar_one_or_none()
            if c_doc:
                c_clean = serialize_doc(c_doc)
                c_clean.pop("password", None)
                serialized["customer"] = c_clean

        if serialized.get("vendor_id"):
            v_res = await session.execute(select(Vendor).where(Vendor.id == str(serialized["vendor_id"])))
            v_doc = v_res.scalar_one_or_none()
            if v_doc:
                v_clean = serialize_doc(v_doc)
                v_clean.pop("password", None)
                serialized["vendor"] = v_clean

        if serialized.get("rider_id"):
            r_res = await session.execute(select(User).where(User.id == str(serialized["rider_id"])))
            r_doc = r_res.scalar_one_or_none()
            if r_doc:
                r_clean = serialize_doc(r_doc)
                r_clean.pop("password", None)
                serialized["rider"] = r_clean

        return serialized

async def update_order_status(order_id: str, data: OrderStatusUpdate, current_user: dict):
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(Order).where(Order.id == str(order_id)))
        order = res.scalar_one_or_none()
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

        status_val = data.status.value if hasattr(data.status, "value") else str(data.status)
        order.status = status_val

        if data.riderId:
            order.rider_id = str(data.riderId)
        elif current_user.get("role") == "rider":
            order.rider_id = str(current_user["id"])

        await session.commit()
        await session.refresh(order)

        serialized = serialize_doc(order)
        serialized["customerId"] = serialized.get("customer_id")
        serialized["vendorId"] = serialized.get("vendor_id")
        serialized["riderId"] = serialized.get("rider_id")
        serialized["totalAmount"] = serialized.get("total_amount")
        serialized["createdAt"] = serialized.get("created_at")
        return serialized

async def cancel_order(order_id: str, current_user: dict):
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(Order).where(Order.id == str(order_id)))
        order = res.scalar_one_or_none()
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

        if current_user.get("role") != "admin" and str(order.customer_id) != str(current_user["id"]):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized to cancel this order")

        if order.status == "delivered":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Delivered orders cannot be cancelled")

        order.status = "cancelled"
        await session.commit()
        await session.refresh(order)

        serialized = serialize_doc(order)
        serialized["customerId"] = serialized.get("customer_id")
        serialized["vendorId"] = serialized.get("vendor_id")
        serialized["riderId"] = serialized.get("rider_id")
        serialized["totalAmount"] = serialized.get("total_amount")
        serialized["createdAt"] = serialized.get("created_at")
        return serialized

async def get_customer_orders(customer_id: str, current_user: dict):
    if current_user.get("role") != "admin" and str(current_user.get("id")) != str(customer_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized access to customer orders")

    async with AsyncSessionLocal() as session:
        res = await session.execute(
            select(Order).where(Order.customer_id == str(customer_id)).order_by(desc(Order.created_at))
        )
        orders = res.scalars().all()
        serialized_list = serialize_doc(list(orders))
        for o in serialized_list:
            o["customerId"] = o.get("customer_id")
            o["vendorId"] = o.get("vendor_id")
            o["riderId"] = o.get("rider_id")
            o["totalAmount"] = o.get("total_amount")
            o["createdAt"] = o.get("created_at")
        return serialized_list

async def get_vendor_orders(vendor_id: str, current_user: dict):
    if current_user.get("role") != "admin" and str(current_user.get("id")) != str(vendor_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized access to vendor orders")

    async with AsyncSessionLocal() as session:
        res = await session.execute(
            select(Order).where(Order.vendor_id == str(vendor_id)).order_by(desc(Order.created_at))
        )
        orders = res.scalars().all()
        serialized_list = serialize_doc(list(orders))
        for o in serialized_list:
            o["customerId"] = o.get("customer_id")
            o["vendorId"] = o.get("vendor_id")
            o["riderId"] = o.get("rider_id")
            o["totalAmount"] = o.get("total_amount")
            o["createdAt"] = o.get("created_at")
        return serialized_list
