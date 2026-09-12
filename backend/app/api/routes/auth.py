from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.schemas.auth import UserCreate, UserLogin, TokenResponse, UserResponse, RefreshRequest, UserUpdate, PasswordResetRequest
from app.core.logging import get_logger
from app.services.auth_service import auth_service
from app.core.security import decode_token, oauth2_scheme

router = APIRouter(prefix="/auth", tags=["Authentication"])
logger = get_logger("auth_routes")


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


@router.post("/request-password-reset")
async def request_password_reset(body: PasswordResetRequest, db: AsyncSession = Depends(get_db)):
    """Accept password-reset requests without revealing whether an account exists.

    Email delivery is intentionally an infrastructure concern and can be added
    behind this endpoint without changing the browser contract.
    """
    user = await auth_service.get_user_by_email(db, body.email)
    if user:
        logger.info("password_reset_requested", user_id=str(user.id))
    return {"message": "If an account matches that email, reset instructions will be sent."}


async def get_authenticated_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    """Return the user represented by a valid access token."""
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")

    user = await auth_service.get_current_user(db, token)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")
    return user


@router.get("/me", response_model=UserResponse)
async def get_me(user=Depends(get_authenticated_user)):
    return user


@router.put("/me", response_model=UserResponse)
async def update_me(profile: UserUpdate, db: AsyncSession = Depends(get_db), user=Depends(get_authenticated_user)):
    return await auth_service.update_user(db, user, **profile.model_dump(exclude_unset=True))
