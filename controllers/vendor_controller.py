from fastapi import HTTPException, status
from sqlalchemy import select, update
from database import AsyncSessionLocal, serialize_doc
from middleware.auth import hash_password, create_access_token
from models.vendor_model import VendorRegister, VendorUpdate, VendorStatusUpdate
from orm_models import Vendor, User, Food

async def get_all_vendors():
    try:
        async with AsyncSessionLocal() as session:
            res = await session.execute(select(Vendor).where(Vendor.is_active == True))
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

async def get_vendor_by_id(vendor_id: str):
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(Vendor).where(Vendor.id == str(vendor_id)))
        vendor = res.scalar_one_or_none()
        if not vendor:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found")

        serialized = serialize_doc(vendor)
        serialized.pop("password", None)
        return serialized

async def register_vendor(data: VendorRegister):
    try:
        email_clean = data.email.lower()
        async with AsyncSessionLocal() as session:
            res_v = await session.execute(select(Vendor).where(Vendor.email == email_clean))
            res_u = await session.execute(select(User).where(User.email == email_clean))
            if res_v.scalar_one_or_none() or res_u.scalar_one_or_none():
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is already in use")

            hashed_pw = hash_password(data.password)
            vendor_obj = Vendor(
                name=data.name,
                email=email_clean,
                password=hashed_pw,
                city=data.city or "Vehari",
                phone=data.phone,
                category=data.category or "Pakistani",
                cuisine=data.cuisine or "General",
                address=data.address or "Vehari, Pakistan",
                status="open",
                rating=4.5,
                is_active=True,
                is_approved=True,
                logo="",
                cover_image=""
            )

            session.add(vendor_obj)
            await session.commit()
            await session.refresh(vendor_obj)

            serialized = serialize_doc(vendor_obj)
            serialized.pop("password", None)

            token = create_access_token({"id": serialized["id"], "role": "vendor"})

            return {
                "token": token,
                "role": "vendor",
                "vendor": serialized
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Vendor registration failed: {str(e)}"
        )

async def update_vendor(vendor_id: str, data: VendorUpdate, current_user: dict):
    if current_user.get("role") != "admin" and current_user.get("id") != str(vendor_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized to update vendor profile")

    async with AsyncSessionLocal() as session:
        res = await session.execute(select(Vendor).where(Vendor.id == str(vendor_id)))
        vendor = res.scalar_one_or_none()
        if not vendor:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found")

        update_dict = {k: v for k, v in data.dict(exclude_unset=True).items() if v is not None}
        for k, v in update_dict.items():
            if hasattr(vendor, k):
                setattr(vendor, k, v)

        await session.commit()
        await session.refresh(vendor)

        serialized = serialize_doc(vendor)
        serialized.pop("password", None)
        return serialized

async def get_vendor_menu(vendor_id: str):
    try:
        async with AsyncSessionLocal() as session:
            res = await session.execute(select(Food).where(Food.vendor_id == str(vendor_id)))
            foods = res.scalars().all()
            return serialize_doc(list(foods))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch vendor menu: {str(e)}"
        )

async def update_vendor_status(vendor_id: str, data: VendorStatusUpdate, current_user: dict):
    if current_user.get("role") != "admin" and current_user.get("id") != str(vendor_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized to update vendor status")

    status_val = data.status.value if hasattr(data.status, "value") else str(data.status)
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(Vendor).where(Vendor.id == str(vendor_id)))
        vendor = res.scalar_one_or_none()
        if not vendor:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found")

        vendor.status = status_val
        await session.commit()
        await session.refresh(vendor)

        serialized = serialize_doc(vendor)
        serialized.pop("password", None)
        return serialized
