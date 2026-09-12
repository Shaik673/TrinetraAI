from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from pydantic import BaseModel

from app.db.base import get_db
from app.services.alert_service import alert_service
from app.services.investigation_service import investigation_service

router = APIRouter(prefix="/alerts", tags=["Alerts"])


class AlertCreate(BaseModel):
    title: str
    description: Optional[str] = None
    severity: str = "medium"
    category: str = "unknown"
    source_ip: Optional[str] = None
    destination_ip: Optional[str] = None
    source_port: Optional[int] = None
    destination_port: Optional[int] = None
    protocol: Optional[str] = None
    source_system: Optional[str] = "Manual"
    mitre_techniques: List[str] = []
    tags: List[str] = []
    raw_data: dict = {}


@router.post("/", status_code=201)
async def create_alert(alert_data: AlertCreate, db: AsyncSession = Depends(get_db)):
    alert = await alert_service.ingest_alert(db, alert_data.dict())
    return {"id": str(alert.id), "alert_id": alert.alert_id, "status": alert.status}


@router.get("/")
async def list_alerts(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    severity: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    alerts = await alert_service.list_alerts(db, skip=skip, limit=limit, severity=severity, status=status)
    return [
        {
            "id": str(a.id),
            "alert_id": a.alert_id,
            "title": a.title,
            "severity": a.severity,
            "status": a.status,
            "category": a.category,
            "source_ip": a.source_ip,
            "destination_ip": a.destination_ip,
            "source_system": a.source_system,
            "confidence_score": a.confidence_score,
            "risk_score": a.risk_score,
            "mitre_techniques": a.mitre_techniques,
            "tags": a.tags,
            "alert_time": a.alert_time.isoformat() if a.alert_time else None,
            "created_at": a.created_at.isoformat(),
        }
        for a in alerts
    ]


@router.get("/stats")
async def get_alert_stats(db: AsyncSession = Depends(get_db)):
    return await alert_service.get_alert_stats(db)


@router.get("/{alert_id}")
async def get_alert(alert_id: str, db: AsyncSession = Depends(get_db)):
    alert = await alert_service.get_alert(db, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {
        "id": str(alert.id),
        "alert_id": alert.alert_id,
        "title": alert.title,
        "description": alert.description,
        "severity": alert.severity,
        "status": alert.status,
        "category": alert.category,
        "source_ip": alert.source_ip,
        "destination_ip": alert.destination_ip,
        "source_port": alert.source_port,
        "destination_port": alert.destination_port,
        "protocol": alert.protocol,
        "source_system": alert.source_system,
        "raw_data": alert.raw_data,
        "mitre_techniques": alert.mitre_techniques,
        "affected_assets": alert.affected_assets,
        "confidence_score": alert.confidence_score,
        "risk_score": alert.risk_score,
        "tags": alert.tags,
        "alert_time": alert.alert_time.isoformat() if alert.alert_time else None,
        "created_at": alert.created_at.isoformat(),
    }


@router.post("/{alert_id}/investigate")
async def trigger_investigation(
    alert_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Trigger an autonomous investigation for an alert."""
    alert = await alert_service.get_alert(db, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    investigation = await investigation_service.create_investigation(db, str(alert.id))

    async def run_in_background():
        from app.db.base import AsyncSessionLocal
        async with AsyncSessionLocal() as bg_db:
            try:
                await investigation_service.run_investigation(bg_db, investigation.investigation_id)
            except Exception as e:
                pass

    background_tasks.add_task(run_in_background)

    return {
        "investigation_id": investigation.investigation_id,
        "status": "investigation_started",
        "message": "Autonomous investigation launched",
    }


@router.post("/demo/seed")
async def seed_demo_alerts(db: AsyncSession = Depends(get_db)):
    """Seed the database with realistic demo alerts."""
    alerts = await alert_service.seed_demo_alerts(db)
    return {"created": len(alerts), "message": f"Created {len(alerts)} demo alerts"}
