from fastapi import HTTPException, status
from database import SyncSessionLocal, serialize_doc
from schemas.rider import RiderUpdate, LocationSchema, AvailabilitySchema
from models.rider import Rider
from models.order import Order, OrderItem

async def get_rider_by_id(rider_id: int, current_user: dict):
    session = SyncSessionLocal()
    try:
        rider = session.query(Rider).filter(Rider.id == rider_id).first()
        if not rider:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rider not found")

        serialized = serialize_doc(rider)
        serialized.pop("password", None)
        return serialized
    finally:
        session.close()

async def update_rider(rider_id: int, data: RiderUpdate, current_user: dict):
    if current_user.get("role") != "admin" and current_user.get("id") != rider_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized to update rider profile")

    session = SyncSessionLocal()
    try:
        rider = session.query(Rider).filter(Rider.id == rider_id).first()
        if not rider:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rider not found")

        update_dict = {k: v for k, v in data.dict(exclude_unset=True).items() if v is not None}
        for k, v in update_dict.items():
            if hasattr(rider, k):
                setattr(rider, k, v)

        session.commit()
        session.refresh(rider)

        serialized = serialize_doc(rider)
        serialized.pop("password", None)
        return serialized
    finally:
        session.close()

async def update_rider_location(rider_id: int, data: LocationSchema, current_user: dict):
    if current_user.get("role") != "admin" and current_user.get("id") != rider_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized to update location")

    session = SyncSessionLocal()
    try:
        rider = session.query(Rider).filter(Rider.id == rider_id).first()
        if not rider:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rider not found")

        rider.latitude = data.latitude
        rider.longitude = data.longitude
        session.commit()

        return {
            "message": "Location updated successfully",
            "latitude": data.latitude,
            "longitude": data.longitude
        }
    finally:
        session.close()

async def update_rider_availability(rider_id: int, data: AvailabilitySchema, current_user: dict):
    if current_user.get("role") != "admin" and current_user.get("id") != rider_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized to update availability")

    session = SyncSessionLocal()
    try:
        rider = session.query(Rider).filter(Rider.id == rider_id).first()
        if not rider:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rider not found")

        rider.is_available = data.is_available
        session.commit()
        session.refresh(rider)

        serialized = serialize_doc(rider)
        serialized.pop("password", None)
        return serialized
    finally:
        session.close()

async def get_rider_deliveries(rider_id: int, current_user: dict):
    if current_user.get("role") != "admin" and current_user.get("id") != rider_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized to access rider deliveries")

    session = SyncSessionLocal()
    try:
        deliveries = session.query(Order).filter(Order.rider_id == rider_id).order_by(Order.created_at.desc()).all()
        serialized_list = serialize_doc(deliveries)
        for d in serialized_list:
            items = session.query(OrderItem).filter(OrderItem.order_id == d["id"]).all()
            d["items"] = serialize_doc(items)
        return serialized_list
    finally:
        session.close()
