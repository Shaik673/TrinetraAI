"""
Authentication service — registration, login, token management.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token, decode_token
from app.schemas.auth import UserCreate
from app.core.logging import get_logger

logger = get_logger("auth_service")


class AuthService:
    async def create_user(self, db: AsyncSession, user_data: UserCreate) -> User:
        result = await db.execute(select(User).where(User.email == user_data.email))
        if result.scalar_one_or_none():
            raise ValueError("Email already registered")

        result = await db.execute(select(User).where(User.username == user_data.username))
        if result.scalar_one_or_none():
            raise ValueError("Username already taken")

        user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=get_password_hash(user_data.password),
            full_name=user_data.full_name,
            role=user_data.role,
            is_active=True,
            is_verified=True,  # Auto-verify in dev
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        logger.info("user_created", email=user.email, role=user.role)
        return user

    async def authenticate_user(self, db: AsyncSession, email: str, password: str) -> Optional[User]:
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if not user or not verify_password(password, user.hashed_password):
            return None
        if not user.is_active:
            return None
        user.last_login = datetime.utcnow()
        await db.commit()
        return user

    def create_tokens(self, user: User) -> dict:
        payload = {"sub": str(user.id), "email": user.email, "role": user.role}
        return {
            "access_token": create_access_token(payload),
            "refresh_token": create_refresh_token(payload),
            "token_type": "bearer",
        }

    async def get_current_user(self, db: AsyncSession, token: str) -> Optional[User]:
        payload = decode_token(token)
        if not payload:
            return None
        user_id = payload.get("sub")
        if not user_id:
            return None
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()


auth_service = AuthService()
