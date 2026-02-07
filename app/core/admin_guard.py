from fastapi import Depends, HTTPException, status
from app.core.dependencies import get_current_user
from app.core.roles import UserRole
from app.models.user import User

def require_admin(user: User = Depends(get_current_user)):
    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return user
