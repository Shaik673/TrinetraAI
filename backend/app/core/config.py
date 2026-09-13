"""
Core configuration for TrinetraAI SOC Platform.
"""
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl
from typing import List, Optional
import os


class Settings(BaseSettings):
    # App
    APP_NAME: str = "TrinetraAI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # Security
    SECRET_KEY: str = "changethis-in-production-use-strong-random-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database
    # SQLite makes local development self-contained. Override in .env for PostgreSQL.
    DATABASE_URL: str = "sqlite+aiosqlite:///./trinetraai.db"
    SYNC_DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/trinetraai"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PASSWORD: Optional[str] = None

    # OpenAI
    OPENAI_API_KEY: str = "sk-placeholder"
    OPENAI_MODEL: str = "gpt-4o"
    OPENAI_TEMPERATURE: float = 0.1

    # ChromaDB
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8001
    CHROMA_PERSIST_DIR: str = "./chroma_data"

    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
    ]

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/trinetraai.log"

    # Investigation
    INVESTIGATION_CONFIDENCE_THRESHOLD: float = 0.75
    MAX_INVESTIGATION_CYCLES: int = 5

    # Frontend URL (used for OAuth redirects)
    FRONTEND_URL: str = "http://localhost:5173"

    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""

    # GitHub OAuth
    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""

    # Facebook OAuth
    FACEBOOK_CLIENT_ID: str = ""
    FACEBOOK_CLIENT_SECRET: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

