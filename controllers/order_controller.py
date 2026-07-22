from datetime import datetime
from fastapi import HTTPException, status
from database import db, parse_object_id, serialize_doc
from models.order_model import OrderCreate, OrderStatusUpdate

async def create_order(data: OrderCreate, current_user: dict):
    try:
        cust_id = current_user["id"]
        v_obj_id = parse_object_id(data.vendorId)

        order_doc = {
            "customer": parse_object_id(cust_id) or cust_id,
            "customerId": cust_id,
            "vendor": v_obj_id or data.vendorId,
            "vendorId": data.vendorId,
            "rider": None,
            "riderId": None,
            "items": [item.dict() for item in data.items],
            "totalAmount": data.totalAmount,
            "status": "pending",
            "deliveryAddress": data.deliveryAddress,
            "paymentMethod": data.paymentMethod or "cash",
            "isPaid": False,
            "specialInstructions": data.specialInstructions or "",
            "createdAt": datetime.utcnow().isoformat()
        }

        result = await db.orders.insert_one(order_doc)
        order_doc["_id"] = result.inserted_id
        return serialize_doc(order_doc)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Order creation failed: {str(e)}"
        )

async def get_order_by_id(order_id: str, current_user: dict):
    obj_id = parse_object_id(order_id)
    if not obj_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Order ID")

    order = await db.orders.find_one({"_id": obj_id})
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    serialized = serialize_doc(order)
    
    # Populate customer, vendor, rider
    if serialized.get("customerId"):
        c_obj = parse_object_id(serialized["customerId"])
        if c_obj:
            c_doc = await db.users.find_one({"_id": c_obj})
            if c_doc:
                c_clean = serialize_doc(c_doc)
                c_clean.pop("password", None)
                serialized["customer"] = c_clean

    if serialized.get("vendorId"):
        v_obj = parse_object_id(serialized["vendorId"])
        if v_obj:
            v_doc = await db.vendors.find_one({"_id": v_obj})
            if v_doc:
                v_clean = serialize_doc(v_doc)
                v_clean.pop("password", None)
                serialized["vendor"] = v_clean

    if serialized.get("riderId"):
        r_obj = parse_object_id(serialized["riderId"])
        if r_obj:
            r_doc = await db.users.find_one({"_id": r_obj})
            if r_doc:
                r_clean = serialize_doc(r_doc)
                r_clean.pop("password", None)
                serialized["rider"] = r_clean

    return serialized

async def update_order_status(order_id: str, data: OrderStatusUpdate, current_user: dict):
    obj_id = parse_object_id(order_id)
    if not obj_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Order ID")

    order = await db.orders.find_one({"_id": obj_id})
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    status_val = data.status.value if hasattr(data.status, "value") else str(data.status)
    update_fields = {"status": status_val}

    if data.riderId:
        r_obj = parse_object_id(data.riderId)
        update_fields["rider"] = r_obj or data.riderId
        update_fields["riderId"] = data.riderId
    elif current_user.get("role") == "rider":
        r_id = current_user["id"]
        r_obj = parse_object_id(r_id)
        update_fields["rider"] = r_obj or r_id
        update_fields["riderId"] = r_id

    await db.orders.update_one({"_id": obj_id}, {"$set": update_fields})
    updated_order = await db.orders.find_one({"_id": obj_id})
    return serialize_doc(updated_order)

async def cancel_order(order_id: str, current_user: dict):
    obj_id = parse_object_id(order_id)
    if not obj_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Order ID")

    order = await db.orders.find_one({"_id": obj_id})
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    serialized = serialize_doc(order)
    cust_id_str = str(serialized.get("customerId") or serialized.get("customer") or "")

    if current_user.get("role") != "admin" and cust_id_str != current_user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized to cancel this order")

    if serialized.get("status") == "delivered":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Delivered orders cannot be cancelled")

    await db.orders.update_one({"_id": obj_id}, {"$set": {"status": "cancelled"}})
    updated_order = await db.orders.find_one({"_id": obj_id})
    return serialize_doc(updated_order)

async def get_customer_orders(customer_id: str, current_user: dict):
    if current_user.get("role") != "admin" and current_user.get("id") != customer_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized access to customer orders")

    c_obj = parse_object_id(customer_id)
    query = {"$or": [{"customer": c_obj}, {"customer": customer_id}, {"customerId": customer_id}]}
    cursor = db.orders.find(query).sort("createdAt", -1)
    orders = await cursor.to_list(length=200)
    return serialize_doc(orders)

async def get_vendor_orders(vendor_id: str, current_user: dict):
    if current_user.get("role") != "admin" and current_user.get("id") != vendor_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized access to vendor orders")

    v_obj = parse_object_id(vendor_id)
    query = {"$or": [{"vendor": v_obj}, {"vendor": vendor_id}, {"vendorId": vendor_id}]}
    cursor = db.orders.find(query).sort("createdAt", -1)
    orders = await cursor.to_list(length=200)
    return serialize_doc(orders)
