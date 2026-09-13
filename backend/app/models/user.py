"""
User model with role-based access control and social OAuth support.
"""
import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Enum as SAEnum, Uuid as UUID
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional
import enum

from app.db.base import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"
    SOC_LEAD = "soc_lead"


class OAuthProvider(str, enum.Enum):
    LOCAL = "local"
    GOOGLE = "google"
    GITHUB = "github"
    FACEBOOK = "facebook"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    # Nullable so social-only users don't need a local password
    hashed_password: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    full_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole), default=UserRole.ANALYST, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    # Social OAuth fields
    oauth_provider: Mapped[OAuthProvider] = mapped_column(
        SAEnum(OAuthProvider), default=OAuthProvider.LOCAL, nullable=False
    )
    oauth_provider_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)

    def __repr__(self):
        return f"<User {self.email} [{self.role}] via {self.oauth_provider}>"

