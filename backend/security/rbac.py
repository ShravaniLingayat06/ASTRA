"""Role-Based Access Control (RBAC) dependency decorators."""
from typing import List
from fastapi import Depends, HTTPException, status
from backend.security.auth import get_current_user
from backend.models.user import User

class RequireRoles:
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if current_user.role not in self.allowed_roles and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access forbidden: User role '{current_user.role}' lacks permission."
            )
        return current_user

require_citizen = RequireRoles(["citizen", "security", "authority", "admin"])
require_security = RequireRoles(["security", "authority", "admin"])
require_authority = RequireRoles(["authority", "admin"])
require_admin = RequireRoles(["admin"])
