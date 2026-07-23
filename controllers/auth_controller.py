from fastapi import HTTPException, status
from database import SyncSessionLocal, serialize_doc
from middleware.auth_middleware import hash_password, verify_password, create_access_token
from schemas.user import UserRegister, UserLogin
from models.user import User
from models.vendor import Vendor
from models.rider import Rider

async def register_user(data: UserRegister):
    session = SyncSessionLocal()
    try:
        email_clean = data.email.lower()
        
        # Check if email exists in User, Vendor, or Rider
        if session.query(User).filter(User.email == email_clean).first() or \
           session.query(Vendor).filter(Vendor.email == email_clean).first() or \
           session.query(Rider).filter(Rider.email == email_clean).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already registered"
            )

        hashed_pw = hash_password(data.password)
        role_str = data.role.value if hasattr(data.role, "value") else str(data.role)

        if role_str == "rider":
            rider_obj = Rider(
                name=data.name,
                email=email_clean,
                password=hashed_pw,
                phone=data.phone,
                is_available=True,
                latitude=30.0440,
                longitude=72.3440
            )
            session.add(rider_obj)
            session.commit()
            session.refresh(rider_obj)

            serialized_acc = serialize_doc(rider_obj)
            serialized_acc.pop("password", None)
            serialized_acc["role"] = "rider"

            token = create_access_token({"id": serialized_acc["id"], "role": "rider"})
            return {"token": token, "role": "rider", "user": serialized_acc}

        user_obj = User(
            name=data.name,
            email=email_clean,
            password=hashed_pw,
            phone=data.phone,
            role=role_str
        )

        session.add(user_obj)
        session.commit()
        session.refresh(user_obj)

        serialized_user = serialize_doc(user_obj)
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
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )
    finally:
        session.close()

async def login_user(data: UserLogin):
    session = SyncSessionLocal()
    try:
        email_clean = data.email.lower()
        
        # 1. Check users
        account = session.query(User).filter(User.email == email_clean).first()
        role = account.role if account else None
        acc_type = "user"

        # 2. Check vendors
        if not account:
            account = session.query(Vendor).filter(Vendor.email == email_clean).first()
            if account:
                role = "vendor"
                acc_type = "vendor"

        # 3. Check riders
        if not account:
            account = session.query(Rider).filter(Rider.email == email_clean).first()
            if account:
                role = "rider"
                acc_type = "user"

        if not account or not verify_password(data.password, account.password):
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
    finally:
        session.close()

async def get_me(current_user: dict):
    user_copy = current_user.copy()
    user_copy.pop("password", None)
    return user_copy
