from fastapi import APIRouter
from app.api.routes import auth, alerts, investigations, analytics, threat_intel, websocket

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(alerts.router)
api_router.include_router(investigations.router)
api_router.include_router(analytics.router)
api_router.include_router(threat_intel.router)
api_router.include_router(websocket.router)
