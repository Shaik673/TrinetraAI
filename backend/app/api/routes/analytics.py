from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.services.analytics_service import analytics_service

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/dashboard")
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    return await analytics_service.get_dashboard_stats(db)


@router.get("/severity-distribution")
async def get_severity_distribution(db: AsyncSession = Depends(get_db)):
    return await analytics_service.get_severity_distribution(db)


@router.get("/investigation-trend")
async def get_investigation_trend(
    days: int = Query(7, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
):
    return await analytics_service.get_investigation_trend(db, days=days)
