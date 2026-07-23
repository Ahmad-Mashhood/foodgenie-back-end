from fastapi import HTTPException, status
from sqlalchemy import select, desc
from database import AsyncSessionLocal, serialize_doc
from models.rider_model import RiderUpdate, LocationSchema, AvailabilitySchema
from orm_models import User, Order

async def get_rider_by_id(rider_id: str, current_user: dict):
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(User).where(User.id == str(rider_id), User.role == "rider"))
        rider = res.scalar_one_or_none()
        if not rider:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rider not found")

        serialized = serialize_doc(rider)
        serialized.pop("password", None)
        return serialized

async def update_rider(rider_id: str, data: RiderUpdate, current_user: dict):
    if current_user.get("role") != "admin" and str(current_user.get("id")) != str(rider_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized to update rider profile")

    async with AsyncSessionLocal() as session:
        res = await session.execute(select(User).where(User.id == str(rider_id)))
        rider = res.scalar_one_or_none()
        if not rider:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rider not found")

        update_dict = {k: v for k, v in data.dict(exclude_unset=True).items() if v is not None}
        for k, v in update_dict.items():
            if hasattr(rider, k):
                setattr(rider, k, v)

        await session.commit()
        await session.refresh(rider)

        serialized = serialize_doc(rider)
        serialized.pop("password", None)
        return serialized

async def update_rider_location(rider_id: str, data: LocationSchema, current_user: dict):
    if current_user.get("role") != "admin" and str(current_user.get("id")) != str(rider_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized to update location")

    async with AsyncSessionLocal() as session:
        res = await session.execute(select(User).where(User.id == str(rider_id)))
        rider = res.scalar_one_or_none()
        if not rider:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rider not found")

        loc = {"lat": data.lat, "lng": data.lng}
        rider.location = loc
        await session.commit()

        return {
            "message": "Location updated successfully",
            "location": loc
        }

async def update_rider_availability(rider_id: str, data: AvailabilitySchema, current_user: dict):
    if current_user.get("role") != "admin" and str(current_user.get("id")) != str(rider_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized to update availability")

    async with AsyncSessionLocal() as session:
        res = await session.execute(select(User).where(User.id == str(rider_id)))
        rider = res.scalar_one_or_none()
        if not rider:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rider not found")

        rider.availability = data.isAvailable
        await session.commit()
        await session.refresh(rider)

        serialized = serialize_doc(rider)
        serialized.pop("password", None)
        return serialized

async def get_rider_deliveries(rider_id: str, current_user: dict):
    if current_user.get("role") != "admin" and str(current_user.get("id")) != str(rider_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized to access rider deliveries")

    async with AsyncSessionLocal() as session:
        res = await session.execute(
            select(Order).where(Order.rider_id == str(rider_id)).order_by(desc(Order.created_at))
        )
        deliveries = res.scalars().all()
        serialized_list = serialize_doc(list(deliveries))
        for d in serialized_list:
            d["customerId"] = d.get("customer_id")
            d["vendorId"] = d.get("vendor_id")
            d["riderId"] = d.get("rider_id")
            d["totalAmount"] = d.get("total_amount")
            d["createdAt"] = d.get("created_at")
        return serialized_list
