from typing import List
from fastapi import Depends, HTTPException, status
from middleware.auth_middleware import get_current_user

def require_roles(allowed_roles: List[str]):
    """
    RBAC dependency generator.
    Enforces that caller's role matches one of allowed_roles (or is 'admin').
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
