from fastapi import HTTPException, status
from sqlalchemy import select
from database import AsyncSessionLocal, serialize_doc
from middleware.auth import hash_password, verify_password, create_access_token
from models.user_model import UserRegister, UserLogin
from orm_models import User, Vendor

async def register_user(data: UserRegister):
    try:
        async with AsyncSessionLocal() as session:
            email_clean = data.email.lower()
            
            res_user = await session.execute(select(User).where(User.email == email_clean))
            res_vendor = await session.execute(select(Vendor).where(Vendor.email == email_clean))
            if res_user.scalar_one_or_none() or res_vendor.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email is already registered"
                )

            hashed_pw = hash_password(data.password)
            role_str = data.role.value if hasattr(data.role, "value") else str(data.role)

            user_obj = User(
                name=data.name,
                email=email_clean,
                password=hashed_pw,
                phone=data.phone,
                role=role_str,
                is_active=True,
                preferences={"diet": "", "calories": 2000, "healthGoals": []},
                favorites=[],
                availability=True,
                location={"lat": 0.0, "lng": 0.0}
            )

            session.add(user_obj)
            await session.commit()
            await session.refresh(user_obj)

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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

async def login_user(data: UserLogin):
    try:
        email_clean = data.email.lower()
        
        async with AsyncSessionLocal() as session:
            res_u = await session.execute(select(User).where(User.email == email_clean))
            account = res_u.scalar_one_or_none()
            role = account.role if account else None
            acc_type = "user"

            if not account:
                res_v = await session.execute(select(Vendor).where(Vendor.email == email_clean))
                account = res_v.scalar_one_or_none()
                if account:
                    role = "vendor"
                    acc_type = "vendor"

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

async def get_me(current_user: dict):
    user_copy = current_user.copy()
    user_copy.pop("password", None)
    return user_copy
