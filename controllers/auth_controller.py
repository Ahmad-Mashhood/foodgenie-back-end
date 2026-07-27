import os
import firebase_admin
from firebase_admin import credentials, auth as firebase_auth
from fastapi import HTTPException, status
from database import SyncSessionLocal, serialize_doc
from middleware.auth_middleware import hash_password, verify_password, create_access_token
from schemas.user import UserRegister, UserLogin
from models.user import User
from models.vendor import Vendor
from models.rider import Rider

# Initialize Firebase Admin SDK once
service_account_paths = [
    'firebase-service-account.json',
    'firebase-service-account.json.json',
    os.path.join(os.path.dirname(__file__), '..', 'firebase-service-account.json'),
    os.path.join(os.path.dirname(__file__), '..', 'firebase-service-account.json.json')
]

service_account_found = None
for path in service_account_paths:
    if os.path.exists(path):
        service_account_found = path
        break

if not firebase_admin._apps:
    if service_account_found:
        try:
            cred = credentials.Certificate(service_account_found)
            firebase_admin.initialize_app(cred)
            print(f"[SUCCESS] Firebase Admin initialized with certificate: {service_account_found}")
        except Exception as e:
            print(f"[WARNING] Firebase Admin cert init warning: {e}")
    else:
        try:
            firebase_admin.initialize_app()
            print("[NOTE] Firebase Admin initialized without service account certificate.")
        except Exception as e:
            print(f"[NOTE] Firebase Admin init note: {e}")

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

async def google_login(token: str, role: str):
    session = SyncSessionLocal()
    try:
        email = None
        name = "Google User"

        # Step 1 Verify Firebase token
        try:
            decoded = firebase_auth.verify_id_token(token)
            email = decoded.get('email')
            name = decoded.get('name', 'Google User')
        except Exception as ver_err:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid Google token: {str(ver_err)}"
            )

        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email not found in Google token"
            )

        email_clean = email.lower()

        # Step 2 Check if user exists in User, Vendor, or Rider
        account = session.query(User).filter(User.email == email_clean).first()
        user_role = account.role if account else None

        if not account:
            account = session.query(Vendor).filter(Vendor.email == email_clean).first()
            if account:
                user_role = "vendor"

        if not account:
            account = session.query(Rider).filter(Rider.email == email_clean).first()
            if account:
                user_role = "rider"

        # Step 3 Create user if not exists
        if not account:
            user_role = role if role in ["customer", "vendor", "rider", "admin"] else "customer"
            dummy_password = hash_password("GOOGLE_AUTH_NO_PASSWORD")

            if user_role == "vendor":
                account = Vendor(
                    name=name,
                    email=email_clean,
                    password=dummy_password,
                    city="Vehari",
                    category="restaurant",
                    status="open",
                    rating=5.0,
                    is_approved=True
                )
            elif user_role == "rider":
                account = Rider(
                    name=name,
                    email=email_clean,
                    password=dummy_password,
                    phone="",
                    is_available=True,
                    latitude=30.0440,
                    longitude=72.3440
                )
            else:
                account = User(
                    name=name,
                    email=email_clean,
                    password=dummy_password,
                    role=user_role
                )

            session.add(account)
            session.commit()
            session.refresh(account)

        serialized_acc = serialize_doc(account)
        serialized_acc.pop("password", None)
        serialized_acc["role"] = user_role

        # Step 4 Generate JWT token
        jwt_token = create_access_token({
            "id": serialized_acc["id"],
            "role": user_role
        })

        # Step 5 Return response
        return {
            "token": jwt_token,
            "role": user_role,
            "user": serialized_acc,
            "message": "Google login successful"
        }

    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Google login failed: {str(e)}"
        )
    finally:
        session.close()

async def get_me(current_user: dict):
    user_copy = current_user.copy()
    user_copy.pop("password", None)
    return user_copy
