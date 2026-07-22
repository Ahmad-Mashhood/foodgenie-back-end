from fastapi import HTTPException, status
from database import db, parse_object_id, serialize_doc
from models.rider_model import RiderUpdate, LocationSchema, AvailabilitySchema

async def get_rider_by_id(rider_id: str, current_user: dict):
    obj_id = parse_object_id(rider_id)
    if not obj_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Rider ID")

    rider = await db.users.find_one({"_id": obj_id, "role": "rider"})
    if not rider:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rider not found")

    serialized = serialize_doc(rider)
    serialized.pop("password", None)
    return serialized

async def update_rider(rider_id: str, data: RiderUpdate, current_user: dict):
    obj_id = parse_object_id(rider_id)
    if not obj_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Rider ID")

    if current_user.get("role") != "admin" and current_user.get("id") != rider_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized to update rider profile")

    update_dict = {k: v for k, v in data.dict(exclude_unset=True).items() if v is not None}
    if update_dict:
        await db.users.update_one({"_id": obj_id}, {"$set": update_dict})

    updated_rider = await db.users.find_one({"_id": obj_id})
    if not updated_rider:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rider not found")

    serialized = serialize_doc(updated_rider)
    serialized.pop("password", None)
    return serialized

async def update_rider_location(rider_id: str, data: LocationSchema, current_user: dict):
    obj_id = parse_object_id(rider_id)
    if not obj_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Rider ID")

    if current_user.get("role") != "admin" and current_user.get("id") != rider_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized to update location")

    await db.users.update_one(
        {"_id": obj_id},
        {"$set": {"location": {"lat": data.lat, "lng": data.lng}}}
    )

    return {
        "message": "Location updated successfully",
        "location": {"lat": data.lat, "lng": data.lng}
    }

async def update_rider_availability(rider_id: str, data: AvailabilitySchema, current_user: dict):
    obj_id = parse_object_id(rider_id)
    if not obj_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Rider ID")

    if current_user.get("role") != "admin" and current_user.get("id") != rider_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized to update availability")

    await db.users.update_one({"_id": obj_id}, {"$set": {"availability": data.isAvailable}})
    
    updated_rider = await db.users.find_one({"_id": obj_id})
    serialized = serialize_doc(updated_rider)
    serialized.pop("password", None)
    return serialized

async def get_rider_deliveries(rider_id: str, current_user: dict):
    if current_user.get("role") != "admin" and current_user.get("id") != rider_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized to access rider deliveries")

    r_obj = parse_object_id(rider_id)
    query = {"$or": [{"rider": r_obj}, {"rider": rider_id}, {"riderId": rider_id}]}
    cursor = db.orders.find(query).sort("createdAt", -1)
    deliveries = await cursor.to_list(length=200)
    return serialize_doc(deliveries)
