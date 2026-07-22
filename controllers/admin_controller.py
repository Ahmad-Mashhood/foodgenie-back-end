from fastapi import HTTPException, status
from database import db, parse_object_id, serialize_doc

async def get_all_users():
    try:
        cursor = db.users.find({"role": {"$ne": "admin"}}).sort("_id", -1)
        users = await cursor.to_list(length=500)
        serialized = serialize_doc(users)
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
        cursor = db.vendors.find().sort("_id", -1)
        vendors = await cursor.to_list(length=500)
        serialized = serialize_doc(vendors)
        for v in serialized:
            v.pop("password", None)
        return serialized
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch vendors: {str(e)}"
        )

async def approve_vendor(vendor_id: str):
    obj_id = parse_object_id(vendor_id)
    if not obj_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Vendor ID")

    result = await db.vendors.update_one({"_id": obj_id}, {"$set": {"isApproved": True}})
    if result.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found")

    updated_vendor = await db.vendors.find_one({"_id": obj_id})
    serialized = serialize_doc(updated_vendor)
    serialized.pop("password", None)
    return serialized

async def get_all_orders():
    try:
        cursor = db.orders.find().sort("createdAt", -1)
        orders = await cursor.to_list(length=500)
        serialized = serialize_doc(orders)
        
        for order in serialized:
            if order.get("customerId"):
                c_obj = parse_object_id(order["customerId"])
                if c_obj:
                    c_doc = await db.users.find_one({"_id": c_obj})
                    if c_doc:
                        c_clean = serialize_doc(c_doc)
                        c_clean.pop("password", None)
                        order["customer"] = c_clean

            if order.get("vendorId"):
                v_obj = parse_object_id(order["vendorId"])
                if v_obj:
                    v_doc = await db.vendors.find_one({"_id": v_obj})
                    if v_doc:
                        v_clean = serialize_doc(v_doc)
                        v_clean.pop("password", None)
                        order["vendor"] = v_clean

            if order.get("riderId"):
                r_obj = parse_object_id(order["riderId"])
                if r_obj:
                    r_doc = await db.users.find_one({"_id": r_obj})
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
        customers_count = await db.users.count_documents({"role": "customer"})
        riders_count = await db.users.count_documents({"role": "rider"})
        vendors_count = await db.vendors.count_documents({})
        orders_count = await db.orders.count_documents({})

        # Calculate Total Revenue for Delivered orders
        pipeline_revenue = [
            {"$match": {"status": "delivered"}},
            {"$group": {"_id": None, "total": {"$sum": "$totalAmount"}}}
        ]
        revenue_res = await db.orders.aggregate(pipeline_revenue).to_list(length=1)
        total_revenue = revenue_res[0]["total"] if revenue_res else 0.0

        # Group orders by status
        pipeline_status = [
            {"$group": {"_id": "$status", "count": {"$sum": 1}}}
        ]
        status_res = await db.orders.aggregate(pipeline_status).to_list(length=20)
        orders_by_status = {item["_id"]: item["count"] for item in status_res if item["_id"]}

        return {
            "users": {
                "customers": customers_count,
                "riders": riders_count
            },
            "vendorsCount": vendors_count,
            "ordersCount": orders_count,
            "totalRevenue": total_revenue,
            "ordersByStatus": orders_by_status
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analytics calculation failed: {str(e)}"
        )
