from fastapi import HTTPException, status
from database import db, serialize_doc
from middleware.auth import hash_password, verify_password, create_access_token
from models.user_model import UserRegister, UserLogin

async def register_user(data: UserRegister):
    try:
        # Check if email already exists in users or vendors
        existing_user = await db.users.find_one({"email": data.email.lower()})
        existing_vendor = await db.vendors.find_one({"email": data.email.lower()})
        if existing_user or existing_vendor:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already registered"
            )

        hashed_pw = hash_password(data.password)
        user_doc = {
            "name": data.name,
            "email": data.email.lower(),
            "password": hashed_pw,
            "phone": data.phone,
            "role": data.role.value if hasattr(data.role, "value") else str(data.role),
            "isActive": True,
            "preferences": {
                "diet": "",
                "calories": 2000,
                "healthGoals": []
            },
            "favorites": [],
            "availability": True,
            "location": {"lat": 0.0, "lng": 0.0}
        }

        result = await db.users.insert_one(user_doc)
        user_doc["_id"] = result.inserted_id
        
        serialized_user = serialize_doc(user_doc)
        serialized_user.pop("password", None)

        token = create_access_token({
            "id": serialized_user["id"],
            "role": serialized_user["role"]
        })

        return {
            "token": token,
            "role": serialized_user["role"],
            "user": serialized_user
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

async def login_user(data: UserLogin):
    try:
        email_clean = data.email.lower()
        
        # 1. Check users collection
        account = await db.users.find_one({"email": email_clean})
        role = account.get("role") if account else None
        acc_type = "user"

        # 2. If not found, check vendors collection
        if not account:
            account = await db.vendors.find_one({"email": email_clean})
            if account:
                role = "vendor"
                acc_type = "vendor"

        if not account or not verify_password(data.password, account.get("password", "")):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        serialized_acc = serialize_doc(account)
        serialized_acc.pop("password", None)

        token = create_access_token({
            "id": serialized_acc["id"],
            "role": role
        })

        return {
            "token": token,
            "role": role,
            acc_type: serialized_acc
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

async def get_me(current_user: dict):
    user_copy = current_user.copy()
    user_copy.pop("password", None)
    return user_copy
