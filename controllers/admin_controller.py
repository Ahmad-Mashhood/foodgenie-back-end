from fastapi import HTTPException, status
from sqlalchemy import func, desc
from database import SyncSessionLocal, serialize_doc
from models.user import User
from models.vendor import Vendor
from models.order import Order, OrderItem
from models.rider import Rider
from models.food import Food

async def get_all_users():
    session = SyncSessionLocal()
    try:
        users = session.query(User).filter(User.role != "admin").order_by(User.created_at.desc()).all()
        serialized = serialize_doc(users)
        for u in serialized:
            u.pop("password", None)
        return serialized
    finally:
        session.close()

async def get_all_vendors():
    session = SyncSessionLocal()
    try:
        vendors = session.query(Vendor).order_by(Vendor.created_at.desc()).all()
        serialized = serialize_doc(vendors)
        for v in serialized:
            v.pop("password", None)
        return serialized
    finally:
        session.close()

async def approve_vendor(vendor_id: int):
    session = SyncSessionLocal()
    try:
        vendor = session.query(Vendor).filter(Vendor.id == vendor_id).first()
        if not vendor:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found")

        vendor.is_approved = True
        session.commit()
        session.refresh(vendor)

        serialized = serialize_doc(vendor)
        serialized.pop("password", None)
        return serialized
    finally:
        session.close()

async def get_all_orders():
    session = SyncSessionLocal()
    try:
        orders = session.query(Order).order_by(Order.created_at.desc()).all()
        serialized = serialize_doc(orders)

        for order in serialized:
            items = session.query(OrderItem).filter(OrderItem.order_id == order["id"]).all()
            order["items"] = serialize_doc(items)

            if order.get("customer_id"):
                c_doc = session.query(User).filter(User.id == order["customer_id"]).first()
                if c_doc:
                    c_clean = serialize_doc(c_doc)
                    c_clean.pop("password", None)
                    order["customer"] = c_clean

            if order.get("vendor_id"):
                v_doc = session.query(Vendor).filter(Vendor.id == order["vendor_id"]).first()
                if v_doc:
                    v_clean = serialize_doc(v_doc)
                    v_clean.pop("password", None)
                    order["vendor"] = v_clean

            if order.get("rider_id"):
                r_doc = session.query(Rider).filter(Rider.id == order["rider_id"]).first()
                if r_doc:
                    r_clean = serialize_doc(r_doc)
                    r_clean.pop("password", None)
                    order["rider"] = r_clean

        return serialized
    finally:
        session.close()

async def get_analytics():
    session = SyncSessionLocal()
    try:
        users_count = session.query(func.count(User.id)).scalar() or 0
        vendors_count = session.query(func.count(Vendor.id)).scalar() or 0
        orders_count = session.query(func.count(Order.id)).scalar() or 0

        # Total Revenue for delivered orders
        total_revenue = session.query(func.sum(Order.total_amount)).filter(Order.status == "delivered").scalar() or 0.0

        # Pending & Delivered counts
        pending_orders_count = session.query(func.count(Order.id)).filter(Order.status == "pending").scalar() or 0
        delivered_orders_count = session.query(func.count(Order.id)).filter(Order.status == "delivered").scalar() or 0

        # Most ordered food items
        most_ordered_query = session.query(
            Food.name, func.sum(OrderItem.quantity).label("total_quantity")
        ).join(OrderItem, Food.id == OrderItem.food_id).group_by(Food.name).order_by(desc("total_quantity")).limit(5).all()

        most_ordered_items = [{"food_name": row[0], "total_ordered": row[1]} for row in most_ordered_query]

        # Top rated vendors
        top_vendors = session.query(Vendor).order_by(Vendor.rating.desc()).limit(5).all()
        top_rated_vendors = serialize_doc(top_vendors)
        for v in top_rated_vendors:
            v.pop("password", None)

        return {
            "total_users": users_count,
            "total_vendors": vendors_count,
            "total_orders": orders_count,
            "total_revenue": float(total_revenue),
            "pending_orders_count": pending_orders_count,
            "delivered_orders_count": delivered_orders_count,
            "most_ordered_food_items": most_ordered_items,
            "top_rated_vendors": top_rated_vendors
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analytics calculation failed: {str(e)}"
        )
    finally:
        session.close()
