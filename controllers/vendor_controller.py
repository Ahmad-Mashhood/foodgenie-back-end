from fastapi import HTTPException, status
from database import db, parse_object_id, serialize_doc
from middleware.auth import hash_password, create_access_token
from models.vendor_model import VendorRegister, VendorUpdate, VendorStatusUpdate

async def get_all_vendors():
    try:
        cursor = db.vendors.find({"isActive": True})
        vendors = await cursor.to_list(length=200)
        serialized = serialize_doc(vendors)
        for v in serialized:
            v.pop("password", None)
        return serialized
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch vendors: {str(e)}"
        )

async def get_vendor_by_id(vendor_id: str):
    obj_id = parse_object_id(vendor_id)
    if not obj_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Vendor ID")

    vendor = await db.vendors.find_one({"_id": obj_id})
    if not vendor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found")

    serialized = serialize_doc(vendor)
    serialized.pop("password", None)
    return serialized

async def register_vendor(data: VendorRegister):
    try:
        email_clean = data.email.lower()
        existing_vendor = await db.vendors.find_one({"email": email_clean})
        existing_user = await db.users.find_one({"email": email_clean})
        if existing_vendor or existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is already in use")

        hashed_pw = hash_password(data.password)
        vendor_doc = {
            "name": data.name,
            "email": email_clean,
            "password": hashed_pw,
            "city": data.city or "Vehari",
            "phone": data.phone,
            "category": data.category or "Pakistani",
            "cuisine": data.cuisine or "General",
            "address": data.address or "Vehari, Pakistan",
            "status": "open",
            "rating": 4.5,
            "totalReviews": 0,
            "isActive": True,
            "isApproved": True,  # Auto-approve for seamless onboarding or approval by admin
            "logo": "",
            "coverImage": ""
        }

        result = await db.vendors.insert_one(vendor_doc)
        vendor_doc["_id"] = result.inserted_id

        serialized = serialize_doc(vendor_doc)
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
    obj_id = parse_object_id(vendor_id)
    if not obj_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Vendor ID")

    if current_user.get("role") != "admin" and current_user.get("id") != vendor_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized to update vendor profile")

    update_dict = {k: v for k, v in data.dict(exclude_unset=True).items() if v is not None}
    if update_dict:
        await db.vendors.update_one({"_id": obj_id}, {"$set": update_dict})

    updated_vendor = await db.vendors.find_one({"_id": obj_id})
    if not updated_vendor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found")

    serialized = serialize_doc(updated_vendor)
    serialized.pop("password", None)
    return serialized

async def get_vendor_menu(vendor_id: str):
    try:
        obj_id = parse_object_id(vendor_id)
        query = {"$or": [{"vendor": obj_id}, {"vendor": vendor_id}, {"vendorId": vendor_id}]}
        cursor = db.menuitems.find(query)
        menu_items = await cursor.to_list(length=200)
        return serialize_doc(menu_items)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch vendor menu: {str(e)}"
        )

async def update_vendor_status(vendor_id: str, data: VendorStatusUpdate, current_user: dict):
    obj_id = parse_object_id(vendor_id)
    if not obj_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Vendor ID")

    if current_user.get("role") != "admin" and current_user.get("id") != vendor_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized to update vendor status")

    status_val = data.status.value if hasattr(data.status, "value") else str(data.status)
    await db.vendors.update_one({"_id": obj_id}, {"$set": {"status": status_val}})
    
    updated_vendor = await db.vendors.find_one({"_id": obj_id})
    if not updated_vendor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found")

    serialized = serialize_doc(updated_vendor)
    serialized.pop("password", None)
    return serialized
