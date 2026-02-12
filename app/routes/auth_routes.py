
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from app.database import get_db
from app.schemas.user_schema import UserCreate, TokenResponse
from app.services.auth_service import create_user, authenticate_user
from app.core.security import create_access_token
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register")
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    return create_user(db, user_data.username, user_data.password)


@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
        
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}


@router.get('/me')
def me(current_user: User = Depends(get_current_user)):
    # expose minimal user info to frontend
    return {
        'id': current_user.id,
        'username': current_user.username,
        'role': current_user.role
    }
