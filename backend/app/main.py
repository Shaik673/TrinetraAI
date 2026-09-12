"""
TrinetraAI — Autonomous SOC Investigation and Response Platform
FastAPI Application Entry Point
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.db.base import init_db, AsyncSessionLocal
from app.api import api_router
from app.services.auth_service import auth_service

# Ensure logs directory exists
os.makedirs("./logs", exist_ok=True)
setup_logging()
logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown."""
    logger.info("trinetraai_starting", version=settings.APP_VERSION)
    await init_db()
    async with AsyncSessionLocal() as db:
        await auth_service.ensure_demo_user(db)
    logger.info("database_initialized")
    yield
    logger.info("trinetraai_shutting_down")


app = FastAPI(
    title="TrinetraAI — Autonomous SOC Platform",
    description="Autonomous security investigation and response platform powered by multi-agent AI",
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# Middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all API routes
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "app": settings.APP_NAME, "version": settings.APP_VERSION}


@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "Autonomous SOC Investigation and Response Platform",
        "docs": "/api/docs",
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error("unhandled_exception", error=str(exc), path=str(request.url))
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
