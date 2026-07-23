from fastapi import HTTPException, status
from sqlalchemy import select, func, desc
from database import AsyncSessionLocal, serialize_doc
from orm_models import User, Vendor, Order

async def get_all_users():
    try:
        async with AsyncSessionLocal() as session:
            res = await session.execute(
                select(User).where(User.role != "admin").order_by(desc(User.created_at))
            )
            users = res.scalars().all()
            serialized = serialize_doc(list(users))
            for u in serialized:
                u.pop("password", None)
            return serialized
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch users: {str(e)}"
        )

async def get_all_vendors():
    try:
        async with AsyncSessionLocal() as session:
            res = await session.execute(select(Vendor).order_by(desc(Vendor.created_at)))
            vendors = res.scalars().all()
            serialized = serialize_doc(list(vendors))
            for v in serialized:
                v.pop("password", None)
            return serialized
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch vendors: {str(e)}"
        )

async def approve_vendor(vendor_id: str):
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(Vendor).where(Vendor.id == str(vendor_id)))
        vendor = res.scalar_one_or_none()
        if not vendor:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found")

        vendor.is_approved = True
        await session.commit()
        await session.refresh(vendor)

        serialized = serialize_doc(vendor)
        serialized.pop("password", None)
        return serialized

async def get_all_orders():
    try:
        async with AsyncSessionLocal() as session:
            res = await session.execute(select(Order).order_by(desc(Order.created_at)))
            orders = res.scalars().all()
            serialized = serialize_doc(list(orders))

            for order in serialized:
                order["customerId"] = order.get("customer_id")
                order["vendorId"] = order.get("vendor_id")
                order["riderId"] = order.get("rider_id")
                order["totalAmount"] = order.get("total_amount")
                order["createdAt"] = order.get("created_at")

                if order.get("customer_id"):
                    c_res = await session.execute(select(User).where(User.id == str(order["customer_id"])))
                    c_doc = c_res.scalar_one_or_none()
                    if c_doc:
                        c_clean = serialize_doc(c_doc)
                        c_clean.pop("password", None)
                        order["customer"] = c_clean

                if order.get("vendor_id"):
                    v_res = await session.execute(select(Vendor).where(Vendor.id == str(order["vendor_id"])))
                    v_doc = v_res.scalar_one_or_none()
                    if v_doc:
                        v_clean = serialize_doc(v_doc)
                        v_clean.pop("password", None)
                        order["vendor"] = v_clean

                if order.get("rider_id"):
                    r_res = await session.execute(select(User).where(User.id == str(order["rider_id"])))
                    r_doc = r_res.scalar_one_or_none()
                    if r_doc:
                        r_clean = serialize_doc(r_doc)
                        r_clean.pop("password", None)
                        order["rider"] = r_clean

            return serialized
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch orders: {str(e)}"
        )

async def get_analytics():
    try:
        async with AsyncSessionLocal() as session:
            c_res = await session.execute(select(func.count(User.id)).where(User.role == "customer"))
            customers_count = c_res.scalar_one() or 0

            r_res = await session.execute(select(func.count(User.id)).where(User.role == "rider"))
            riders_count = r_res.scalar_one() or 0

            v_res = await session.execute(select(func.count(Vendor.id)))
            vendors_count = v_res.scalar_one() or 0

            o_res = await session.execute(select(func.count(Order.id)))
            orders_count = o_res.scalar_one() or 0

            rev_res = await session.execute(
                select(func.sum(Order.total_amount)).where(Order.status == "delivered")
            )
            total_revenue = rev_res.scalar_one() or 0.0

            st_res = await session.execute(
                select(Order.status, func.count(Order.id)).group_by(Order.status)
            )
            orders_by_status = {row[0]: row[1] for row in st_res.all() if row[0]}

            return {
                "users": {
                    "customers": customers_count,
                    "riders": riders_count
                },
                "vendorsCount": vendors_count,
                "ordersCount": orders_count,
                "totalRevenue": float(total_revenue),
                "ordersByStatus": orders_by_status
            }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analytics calculation failed: {str(e)}"
        )
