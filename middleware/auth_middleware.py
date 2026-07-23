import os
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from dotenv import load_dotenv

from database import SyncSessionLocal, serialize_doc
from models.user import User
from models.vendor import Vendor
from models.rider import Rider

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET", "your_super_secret_jwt_key_change_me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7

security = HTTPBearer()

def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    pw_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pw_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against hashed password."""
    try:
        pw_bytes = plain_password.encode('utf-8')[:72]
        hash_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(pw_bytes, hash_bytes)
    except Exception:
        return False

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Generate a signed JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Decodes JWT token, queries PostgreSQL for active User/Vendor/Rider, and returns user dict.
    """
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("id")
        role: str = payload.get("role")
        if user_id is None or role is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    session = SyncSessionLocal()
    account = None
    try:
        try:
            uid_int = int(user_id)
        except (ValueError, TypeError):
            uid_int = None

        if role == "vendor":
            if uid_int:
                account = session.query(Vendor).filter(Vendor.id == uid_int).first()
            if not account:
                account = session.query(Vendor).filter(Vendor.email == str(user_id)).first()
        elif role == "rider":
            if uid_int:
                account = session.query(Rider).filter(Rider.id == uid_int).first()
            if not account:
                account = session.query(Rider).filter(Rider.email == str(user_id)).first()
            if not account and uid_int:
                account = session.query(User).filter(User.id == uid_int).first()
        else:
            if uid_int:
                account = session.query(User).filter(User.id == uid_int).first()
            if not account:
                account = session.query(User).filter(User.email == str(user_id)).first()

        if not account:
            if uid_int:
                account = session.query(User).filter(User.id == uid_int).first() or \
                          session.query(Vendor).filter(Vendor.id == uid_int).first() or \
                          session.query(Rider).filter(Rider.id == uid_int).first()

        if not account:
            raise credentials_exception

        account_data = serialize_doc(account)
        account_data["role"] = account_data.get("role", role)
        return account_data
    finally:
        session.close()

def require_roles(allowed_roles: List[str]):
    """
    RBAC dependency generator.
    Enforces that caller's role matches one of allowed_roles (or is 'admin').
    """
    async def role_checker(current_user: dict = Depends(get_current_user)) -> dict:
        user_role = current_user.get("role")
        if user_role == "admin":
            return current_user
        
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: Requires one of roles {allowed_roles}, but caller is '{user_role}'"
            )
        return current_user

    return role_checker
