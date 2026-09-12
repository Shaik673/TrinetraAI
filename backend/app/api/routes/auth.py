from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.schemas.auth import UserCreate, UserLogin, TokenResponse, UserResponse, RefreshRequest
from app.services.auth_service import auth_service
from app.core.security import decode_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    try:
        user = await auth_service.create_user(db, user_data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    user = await auth_service.authenticate_user(db, credentials.email, credentials.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    tokens = auth_service.create_tokens(user)
    return {**tokens, "user": user}


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    payload = decode_token(body.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    user = await auth_service.get_current_user(db, body.refresh_token)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    tokens = auth_service.create_tokens(user)
    return {**tokens, "user": user}


@router.get("/me", response_model=UserResponse)
async def get_me(db: AsyncSession = Depends(get_db), token: str = Depends(lambda: None)):
    # Simplified — in production use OAuth2 dependency
    pass
