from datetime import datetime
from fastapi import HTTPException, status
from database import SyncSessionLocal, serialize_doc
from schemas.order import OrderCreate, OrderStatusUpdate
from models.order import Order, OrderItem
from models.user import User
from models.vendor import Vendor
from models.rider import Rider
from models.food import Food

async def create_order(data: OrderCreate, current_user: dict):
    session = SyncSessionLocal()
    try:
        cust_id = current_user["id"]

        order_obj = Order(
            customer_id=cust_id,
            vendor_id=data.vendor_id,
            rider_id=None,
            total_amount=data.total_amount,
            status="pending",
            delivery_address=data.delivery_address,
            created_at=datetime.utcnow()
        )

        session.add(order_obj)
        session.commit()
        session.refresh(order_obj)

        # Create OrderItems
        item_dicts = []
        for item in data.items:
            food_item = session.query(Food).filter(Food.id == item.food_id).first()
            item_price = item.price if item.price is not None else (food_item.price if food_item else 0.0)
            
            order_item = OrderItem(
                order_id=order_obj.id,
                food_id=item.food_id,
                quantity=item.quantity,
                price=item_price
            )
            session.add(order_item)
            item_dicts.append({
                "food_id": item.food_id,
                "name": food_item.name if food_item else "Food Item",
                "quantity": item.quantity,
                "price": item_price
            })

        session.commit()
        session.refresh(order_obj)

        res_dict = serialize_doc(order_obj)
        res_dict["items"] = item_dicts
        return res_dict
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Order creation failed: {str(e)}"
        )
    finally:
        session.close()

async def get_order_by_id(order_id: int, current_user: dict):
    session = SyncSessionLocal()
    try:
        order = session.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

        serialized = serialize_doc(order)
        items = session.query(OrderItem).filter(OrderItem.order_id == order_id).all()
        serialized["items"] = serialize_doc(items)

        if serialized.get("customer_id"):
            c_doc = session.query(User).filter(User.id == serialized["customer_id"]).first()
            if c_doc:
                c_clean = serialize_doc(c_doc)
                c_clean.pop("password", None)
                serialized["customer"] = c_clean

        if serialized.get("vendor_id"):
            v_doc = session.query(Vendor).filter(Vendor.id == serialized["vendor_id"]).first()
            if v_doc:
                v_clean = serialize_doc(v_doc)
                v_clean.pop("password", None)
                serialized["vendor"] = v_clean

        if serialized.get("rider_id"):
            r_doc = session.query(Rider).filter(Rider.id == serialized["rider_id"]).first()
            if r_doc:
                r_clean = serialize_doc(r_doc)
                r_clean.pop("password", None)
                serialized["rider"] = r_clean

        return serialized
    finally:
        session.close()

async def update_order_status(order_id: int, data: OrderStatusUpdate, current_user: dict):
    session = SyncSessionLocal()
    try:
        order = session.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

        status_val = data.status.value if hasattr(data.status, "value") else str(data.status)
        order.status = status_val

        if current_user.get("role") == "rider":
            order.rider_id = current_user["id"]

        session.commit()
        session.refresh(order)

        serialized = serialize_doc(order)
        items = session.query(OrderItem).filter(OrderItem.order_id == order_id).all()
        serialized["items"] = serialize_doc(items)
        return serialized
    finally:
        session.close()

async def cancel_order(order_id: int, current_user: dict):
    session = SyncSessionLocal()
    try:
        order = session.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

        if current_user.get("role") != "admin" and order.customer_id != current_user["id"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized to cancel this order")

        if order.status == "delivered":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Delivered orders cannot be cancelled")

        order.status = "cancelled"
        session.commit()
        session.refresh(order)

        serialized = serialize_doc(order)
        items = session.query(OrderItem).filter(OrderItem.order_id == order_id).all()
        serialized["items"] = serialize_doc(items)
        return serialized
    finally:
        session.close()

async def get_customer_orders(customer_id: int, current_user: dict):
    if current_user.get("role") != "admin" and current_user.get("id") != customer_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized access to customer orders")

    session = SyncSessionLocal()
    try:
        orders = session.query(Order).filter(Order.customer_id == customer_id).order_by(Order.created_at.desc()).all()
        serialized_list = serialize_doc(orders)
        for o in serialized_list:
            items = session.query(OrderItem).filter(OrderItem.order_id == o["id"]).all()
            o["items"] = serialize_doc(items)
        return serialized_list
    finally:
        session.close()

async def get_vendor_orders(vendor_id: int, current_user: dict):
    if current_user.get("role") != "admin" and current_user.get("id") != vendor_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized access to vendor orders")

    session = SyncSessionLocal()
    try:
        orders = session.query(Order).filter(Order.vendor_id == vendor_id).order_by(Order.created_at.desc()).all()
        serialized_list = serialize_doc(orders)
        for o in serialized_list:
            items = session.query(OrderItem).filter(OrderItem.order_id == o["id"]).all()
            o["items"] = serialize_doc(items)
        return serialized_list
    finally:
        session.close()
