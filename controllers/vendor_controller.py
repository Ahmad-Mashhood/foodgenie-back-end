from fastapi import HTTPException, status
from database import SyncSessionLocal, serialize_doc
from middleware.auth_middleware import hash_password, create_access_token
from schemas.vendor import VendorRegister, VendorUpdate, VendorStatusUpdate
from models.vendor import Vendor
from models.user import User
from models.food import Food

async def get_all_vendors():
    session = SyncSessionLocal()
    try:
        vendors = session.query(Vendor).filter(Vendor.is_approved == True).all()
        serialized = serialize_doc(vendors)
        for v in serialized:
            v.pop("password", None)
        return serialized
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch vendors: {str(e)}"
        )
    finally:
        session.close()

async def get_vendor_by_id(vendor_id: int):
    session = SyncSessionLocal()
    try:
        vendor = session.query(Vendor).filter(Vendor.id == vendor_id).first()
        if not vendor:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found")

        serialized = serialize_doc(vendor)
        serialized.pop("password", None)
        return serialized
    finally:
        session.close()

async def register_vendor(data: VendorRegister):
    session = SyncSessionLocal()
    try:
        email_clean = data.email.lower()
        if session.query(Vendor).filter(Vendor.email == email_clean).first() or \
           session.query(User).filter(User.email == email_clean).first():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is already in use")

        hashed_pw = hash_password(data.password)
        cat_str = data.category.value if hasattr(data.category, "value") else str(data.category or "restaurant")

        vendor_obj = Vendor(
            name=data.name,
            email=email_clean,
            password=hashed_pw,
            city=data.city or "Vehari",
            phone=data.phone,
            category=cat_str,
            status="open",
            rating=4.5,
            is_approved=True
        )

        session.add(vendor_obj)
        session.commit()
        session.refresh(vendor_obj)

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
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Vendor registration failed: {str(e)}"
        )
    finally:
        session.close()

async def update_vendor(vendor_id: int, data: VendorUpdate, current_user: dict):
    if current_user.get("role") != "admin" and current_user.get("id") != vendor_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized to update vendor profile")

    session = SyncSessionLocal()
    try:
        vendor = session.query(Vendor).filter(Vendor.id == vendor_id).first()
        if not vendor:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found")

        update_dict = {k: v for k, v in data.dict(exclude_unset=True).items() if v is not None}
        for k, v in update_dict.items():
            if k == "category" and hasattr(v, "value"):
                v = v.value
            if hasattr(vendor, k):
                setattr(vendor, k, v)

        session.commit()
        session.refresh(vendor)

        serialized = serialize_doc(vendor)
        serialized.pop("password", None)
        return serialized
    finally:
        session.close()

async def get_vendor_menu(vendor_id: int):
    session = SyncSessionLocal()
    try:
        foods = session.query(Food).filter(Food.vendor_id == vendor_id).all()
        return serialize_doc(foods)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch vendor menu: {str(e)}"
        )
    finally:
        session.close()

async def update_vendor_status(vendor_id: int, data: VendorStatusUpdate, current_user: dict):
    if current_user.get("role") != "admin" and current_user.get("id") != vendor_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized to update vendor status")

    status_val = data.status.value if hasattr(data.status, "value") else str(data.status)
    session = SyncSessionLocal()
    try:
        vendor = session.query(Vendor).filter(Vendor.id == vendor_id).first()
        if not vendor:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found")

        vendor.status = status_val
        session.commit()
        session.refresh(vendor)

        serialized = serialize_doc(vendor)
        serialized.pop("password", None)
        return serialized
    finally:
        session.close()
