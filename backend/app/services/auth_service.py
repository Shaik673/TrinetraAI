"""
Authentication service — registration, login, token management, social OAuth.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User, UserRole, OAuthProvider
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token, decode_token
from app.schemas.auth import UserCreate
from app.core.logging import get_logger

logger = get_logger("auth_service")


class AuthService:
    async def ensure_demo_user(self, db: AsyncSession) -> User:
        demo_email = "demo@trinetraai.io"
        user = await self.get_user_by_email(db, demo_email)
        if user:
            return user

        user = User(
            email=demo_email,
            username="demo_analyst",
            hashed_password=get_password_hash("Demo@1234"),
            full_name="Demo Analyst",
            role=UserRole.ANALYST,
            is_active=True,
            is_verified=True,
            oauth_provider=OAuthProvider.LOCAL,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        logger.info("demo_user_created", email=user.email)
        return user

    async def get_user_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        result = await db.execute(select(User).where(User.email == email.strip().lower()))
        return result.scalar_one_or_none()

    async def get_user_by_oauth(self, db: AsyncSession, provider: str, provider_id: str) -> Optional[User]:
        """Look up a user by their OAuth provider + provider_id pair."""
        result = await db.execute(
            select(User).where(
                User.oauth_provider == provider,
                User.oauth_provider_id == provider_id,
            )
        )
        return result.scalar_one_or_none()

    async def find_or_create_oauth_user(
        self,
        db: AsyncSession,
        provider: str,
        provider_id: str,
        email: str,
        full_name: Optional[str] = None,
        avatar_url: Optional[str] = None,
    ) -> User:
        """Find an existing user by OAuth identity, or create a new one.

        Handles three scenarios:
        1. User already authenticated with this provider before — return existing.
        2. User exists with same email (local or other provider) — link provider.
        3. Brand-new user — create account.
        """
        # 1. Exact provider match
        user = await self.get_user_by_oauth(db, provider, provider_id)
        if user:
            user.last_login = datetime.utcnow()
            if avatar_url and not user.avatar_url:
                user.avatar_url = avatar_url
            await db.commit()
            await db.refresh(user)
            return user

        # 2. Email already registered under a different provider
        clean_email = email.strip().lower()
        user = await self.get_user_by_email(db, clean_email)
        if user:
            # Link this provider to existing account
            user.oauth_provider = OAuthProvider(provider)
            user.oauth_provider_id = provider_id
            user.is_verified = True
            user.last_login = datetime.utcnow()
            if avatar_url and not user.avatar_url:
                user.avatar_url = avatar_url
            await db.commit()
            await db.refresh(user)
            logger.info("oauth_linked_existing_account", email=clean_email, provider=provider)
            return user

        # 3. New user
        base_username = clean_email.split("@")[0].replace(".", "_").replace("+", "_")
        username = base_username
        suffix = 1
        while True:
            result = await db.execute(select(User).where(User.username == username))
            if not result.scalar_one_or_none():
                break
            username = f"{base_username}{suffix}"
            suffix += 1

        user = User(
            email=clean_email,
            username=username,
            hashed_password=None,  # social-only account
            full_name=full_name or username,
            role=UserRole.ANALYST,
            is_active=True,
            is_verified=True,
            avatar_url=avatar_url,
            oauth_provider=OAuthProvider(provider),
            oauth_provider_id=provider_id,
            last_login=datetime.utcnow(),
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        logger.info("oauth_user_created", email=clean_email, provider=provider)
        return user

    async def create_user(self, db: AsyncSession, user_data: UserCreate) -> User:
        if await self.get_user_by_email(db, user_data.email):
            raise ValueError("Email already registered")

        result = await db.execute(select(User).where(User.username == user_data.username))
        if result.scalar_one_or_none():
            raise ValueError("Username already taken")

        user = User(
            email=str(user_data.email).strip().lower(),
            username=user_data.username.strip(),
            hashed_password=get_password_hash(user_data.password),
            full_name=user_data.full_name,
            role=UserRole.ANALYST,
            is_active=True,
            is_verified=True,  # Auto-verify in dev
            oauth_provider=OAuthProvider.LOCAL,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        logger.info("user_created", email=user.email, role=user.role)
        return user

    async def authenticate_user(self, db: AsyncSession, email: str, password: str) -> Optional[User]:
        user = await self.get_user_by_email(db, email)
        if not user or not user.hashed_password or not verify_password(password, user.hashed_password):
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
        try:
            user_uuid = UUID(str(user_id))
        except ValueError:
            return None
        result = await db.execute(select(User).where(User.id == user_uuid))
        return result.scalar_one_or_none()

    async def update_user(self, db: AsyncSession, user: User, **fields) -> User:
        """Update only profile fields that are safe for a user to change."""
        for name, value in fields.items():
            if value is not None:
                setattr(user, name, value)
        await db.commit()
        await db.refresh(user)
        return user


auth_service = AuthService()



class AuthService:
    async def ensure_demo_user(self, db: AsyncSession) -> User:
        demo_email = "demo@trinetraai.io"
        user = await self.get_user_by_email(db, demo_email)
        if user:
            return user

        user = User(
            email=demo_email,
            username="demo_analyst",
            hashed_password=get_password_hash("Demo@1234"),
            full_name="Demo Analyst",
            role=UserRole.ANALYST,
            is_active=True,
            is_verified=True,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        logger.info("demo_user_created", email=user.email)
        return user

    async def get_user_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        result = await db.execute(select(User).where(User.email == email.strip().lower()))
        return result.scalar_one_or_none()

    async def create_user(self, db: AsyncSession, user_data: UserCreate) -> User:
        if await self.get_user_by_email(db, user_data.email):
            raise ValueError("Email already registered")

        result = await db.execute(select(User).where(User.username == user_data.username))
        if result.scalar_one_or_none():
            raise ValueError("Username already taken")

        user = User(
            email=str(user_data.email).strip().lower(),
            username=user_data.username.strip(),
            hashed_password=get_password_hash(user_data.password),
            full_name=user_data.full_name,
            role=UserRole.ANALYST,
            is_active=True,
            is_verified=True,  # Auto-verify in dev
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        logger.info("user_created", email=user.email, role=user.role)
        return user

    async def authenticate_user(self, db: AsyncSession, email: str, password: str) -> Optional[User]:
        user = await self.get_user_by_email(db, email)
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
        try:
            user_uuid = UUID(str(user_id))
        except ValueError:
            return None
        result = await db.execute(select(User).where(User.id == user_uuid))
        return result.scalar_one_or_none()

    async def update_user(self, db: AsyncSession, user: User, **fields) -> User:
        """Update only profile fields that are safe for a user to change."""
        for name, value in fields.items():
            if value is not None:
                setattr(user, name, value)
        await db.commit()
        await db.refresh(user)
        return user


auth_service = AuthService()
