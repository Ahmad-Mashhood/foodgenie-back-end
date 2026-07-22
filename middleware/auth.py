import os
import bcrypt
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from dotenv import load_dotenv

from database import db, parse_object_id, serialize_doc

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
    Decodes JWT token, checks DB for active user/vendor, and attaches identity to request.
    Raises HTTP 401 if invalid or missing token.
    """
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("id")
        role: str = payload.get("role")
        if user_id is None or role is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    obj_id = parse_object_id(user_id)
    if not obj_id:
        raise credentials_exception

    # Check users collection (customer, rider, admin)
    account = None
    if role == "vendor":
        account = await db.vendors.find_one({"_id": obj_id})
    else:
        account = await db.users.find_one({"_id": obj_id})

    if not account:
        # Fallback check
        account = await db.users.find_one({"_id": obj_id})
        if not account:
            account = await db.vendors.find_one({"_id": obj_id})

    if not account:
        raise credentials_exception

    account_data = serialize_doc(account)
    account_data["role"] = account_data.get("role", role)
    return account_data

def require_roles(allowed_roles: List[str]):
    """
    RBAC dependency generator.
    Enforces that caller's role matches one of allowed_roles (or is 'admin').
    Raises HTTP 403 Forbidden if not authorized.
    """
    async def role_checker(current_user: dict = Depends(get_current_user)) -> dict:
        user_role = current_user.get("role")
        
        # Admin has master access to all routes
        if user_role == "admin":
            return current_user
        
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: Requires one of roles {allowed_roles}, but caller is '{user_role}'"
            )
        return current_user

    return role_checker
