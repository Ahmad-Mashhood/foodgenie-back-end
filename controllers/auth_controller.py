import os
import json
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
service_account_env = os.getenv('FIREBASE_SERVICE_ACCOUNT') or os.getenv('FIREBASE_CREDENTIALS')
service_account_paths = [
    'firebase-service-account.json',
    'firebase-service-account.json.json',
    os.path.join(os.path.dirname(__file__), '..', 'firebase-service-account.json'),
    os.path.join(os.path.dirname(__file__), '..', 'firebase-service-account.json.json')
]

if not firebase_admin._apps:
    initialized = False
    if service_account_env:
        try:
            cert_dict = json.loads(service_account_env) if isinstance(service_account_env, str) else service_account_env
            cred = credentials.Certificate(cert_dict)
            firebase_admin.initialize_app(cred)
            initialized = True
            print("[SUCCESS] Firebase Admin initialized with environment credentials.")
        except Exception as e:
            print(f"[WARNING] Env cert init error: {e}")

    if not initialized:
        for path in service_account_paths:
            if os.path.exists(path):
                try:
                    cred = credentials.Certificate(path)
                    firebase_admin.initialize_app(cred)
                    initialized = True
                    print(f"[SUCCESS] Firebase Admin initialized with file: {path}")
                    break
                except Exception as e:
                    print(f"[WARNING] File cert init error: {e}")

    if not initialized:
        try:
            firebase_admin.initialize_app()
            print("[NOTE] Firebase Admin initialized with default app.")
        except Exception as e:
            print(f"[NOTE] Default init warning: {e}")

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
                is_approved=False,
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

async def google_login(
    token: str,
    role: str = "customer",
    phone: str = None,
    city: str = None,
    category: str = None,
    password: str = None
):
    session = SyncSessionLocal()
    try:
        email = None
        name = "Google User"
        picture = None

        # Step 1 Verify Firebase token
        try:
            decoded = firebase_auth.verify_id_token(token)
            email = decoded.get('email')
            name = decoded.get('name', 'Google User')
            picture = decoded.get('picture')
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

        # If vendor or rider registration & account does not exist yet, prompt for onboarding details if missing
        if not account and role == "vendor":
            if not phone or not category or not password:
                return {
                    "requires_details": True,
                    "google_profile": {
                        "name": name,
                        "email": email_clean,
                        "photoURL": picture
                    },
                    "message": "Vendor registration requires additional phone, category, and password"
                }

        if not account and role == "rider":
            if not phone or not password:
                return {
                    "requires_details": True,
                    "google_profile": {
                        "name": name,
                        "email": email_clean,
                        "photoURL": picture
                    },
                    "message": "Rider registration requires additional phone and password"
                }

        # Step 3 Create user if not exists
        if not account:
            user_role = role if role in ["customer", "vendor", "rider", "admin"] else "customer"
            account_password = hash_password(password) if password else hash_password("GOOGLE_AUTH_NO_PASSWORD")

            if user_role == "vendor":
                account = Vendor(
                    name=name,
                    email=email_clean,
                    password=account_password,
                    phone=phone or "",
                    city=city or "Vehari",
                    category=category or "Fast Food",
                    status="pending",
                    rating=5.0,
                    is_approved=False
                )
            elif user_role == "rider":
                account = Rider(
                    name=name,
                    email=email_clean,
                    password=account_password,
                    phone=phone or "",
                    is_available=True,
                    is_approved=False,
                    latitude=30.0440,
                    longitude=72.3440
                )
            else:
                account = User(
                    name=name,
                    email=email_clean,
                    password=account_password,
                    phone=phone or "",
                    role=user_role
                )

            session.add(account)
            session.commit()
            session.refresh(account)

        serialized_acc = serialize_doc(account)
        serialized_acc.pop("password", None)
        if picture:
            serialized_acc["photoURL"] = picture
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
            "vendor": serialized_acc if user_role == "vendor" else None,
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

# In-memory OTP storage for Password Reset
OTP_STORE = {}

def send_otp_email(to_email: str, otp_code: str):
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    import os

    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    sender_email = os.getenv("SMTP_EMAIL", "foodgenie.official.app@gmail.com")
    sender_password = os.getenv("SMTP_PASSWORD", "")

    if sender_email and sender_password:
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"Food Genie - Password Reset OTP Code ({otp_code})"
            msg["From"] = f"Food Genie Support <{sender_email}>"
            msg["To"] = to_email

            html_body = f"""
            <div style="font-family: Arial, sans-serif; max-width: 500px; margin: 0 auto; padding: 24px; border: 1px solid #eee; border-radius: 16px; background-color: #ffffff;">
                <div style="text-align: center; margin-bottom: 20px;">
                    <h2 style="color: #ab3500; font-size: 24px; margin: 0;">Food Genie</h2>
                    <p style="color: #777; font-size: 13px; margin-top: 4px;">Password Reset Verification Code</p>
                </div>
                <p style="color: #333; font-size: 14px; line-height: 1.5;">Hello,</p>
                <p style="color: #555; font-size: 14px; line-height: 1.5;">We received a request to reset the password for your account (<strong>{to_email}</strong>).</p>
                <p style="color: #555; font-size: 14px; line-height: 1.5;">Please enter the following 6-digit verification code on the website to reset your password:</p>
                <div style="text-align: center; margin: 30px 0;">
                    <span style="font-size: 36px; font-weight: 800; letter-spacing: 8px; color: #ab3500; background-color: #fff1ed; padding: 16px 28px; border-radius: 12px; border: 2px dashed #ab3500; font-family: monospace; display: inline-block;">{otp_code}</span>
                </div>
                <p style="color: #777; font-size: 13px; text-align: center;">This code is valid for <strong>10 minutes</strong>. If you did not request a password reset, please ignore this email.</p>
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0 20px 0;" />
                <p style="color: #aaa; font-size: 11px; text-align: center;">Food Genie Team &copy; 2026</p>
            </div>
            """
            msg.attach(MIMEText(html_body, "html"))

            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, msg.as_string())
            server.quit()
            print(f"✅ OTP email successfully sent to {to_email}")
        except Exception as err:
            print(f"⚠️ SMTP email notice: {err}")

async def forgot_password(email: str):
    import random
    import time
    session = SyncSessionLocal()
    try:
        email_clean = email.lower().strip()
        account = session.query(User).filter(User.email == email_clean).first()
        if not account:
            account = session.query(Vendor).filter(Vendor.email == email_clean).first()
        if not account:
            account = session.query(Rider).filter(Rider.email == email_clean).first()

        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No account found with this email address"
            )

        otp = f"{random.randint(100000, 999999)}"
        OTP_STORE[email_clean] = {
            "otp": otp,
            "expires_at": time.time() + 600
        }

        # Attempt to send real SMTP email to recipient's Gmail inbox
        try:
            send_otp_email(email_clean, otp)
        except Exception as e:
            print("Email dispatch error:", e)

        return {
            "message": f"Verification code sent to {email_clean}. Please check your Gmail inbox.",
            "email": email_clean
        }
    finally:
        session.close()


async def verify_otp(email: str, otp: str):
    import time
    email_clean = email.lower().strip()
    record = OTP_STORE.get(email_clean)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No OTP code requested for this email or OTP expired."
        )

    if time.time() > record["expires_at"]:
        OTP_STORE.pop(email_clean, None)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification OTP code has expired. Please request a new code."
        )

    if record["otp"] != otp.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification OTP code. Please check and try again."
        )

    return {"message": "OTP verified successfully", "valid": True}

async def reset_password(email: str, otp: str, new_password: str):
    import time
    session = SyncSessionLocal()
    try:
        email_clean = email.lower().strip()
        record = OTP_STORE.get(email_clean)
        if not record or record["otp"] != otp.strip() or time.time() > record["expires_at"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired OTP code."
            )

        account = session.query(User).filter(User.email == email_clean).first()
        if not account:
            account = session.query(Vendor).filter(Vendor.email == email_clean).first()
        if not account:
            account = session.query(Rider).filter(Rider.email == email_clean).first()

        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found."
            )

        account.password = hash_password(new_password)
        session.commit()

        OTP_STORE.pop(email_clean, None)

        return {"message": "Password reset successfully! You can now log in with your new password."}
    finally:
        session.close()
