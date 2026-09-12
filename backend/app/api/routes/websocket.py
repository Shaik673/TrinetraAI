"""
WebSocket endpoint for real-time investigation updates.
"""
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Set
from app.core.logging import get_logger

router = APIRouter(tags=["WebSocket"])
logger = get_logger("websocket")


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, channel: str):
        await websocket.accept()
        if channel not in self.active_connections:
            self.active_connections[channel] = set()
        self.active_connections[channel].add(websocket)
        logger.info("ws_connected", channel=channel, total=len(self.active_connections.get(channel, set())))

    def disconnect(self, websocket: WebSocket, channel: str):
        if channel in self.active_connections:
            self.active_connections[channel].discard(websocket)

    async def broadcast(self, channel: str, message: dict):
        if channel not in self.active_connections:
            return
        dead = set()
        for ws in self.active_connections[channel]:
            try:
                await ws.send_text(json.dumps(message))
            except Exception:
                dead.add(ws)
        for ws in dead:
            self.active_connections[channel].discard(ws)

    async def broadcast_all(self, message: dict):
        for channel in list(self.active_connections.keys()):
            await self.broadcast(channel, message)


manager = ConnectionManager()


@router.websocket("/ws/investigations/{investigation_id}")
async def investigation_websocket(websocket: WebSocket, investigation_id: str):
    """Real-time updates for a specific investigation."""
    channel = f"investigation:{investigation_id}"
    await manager.connect(websocket, channel)
    try:
        while True:
            data = await websocket.receive_text()
            # Ping/pong keepalive
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket, channel)


@router.websocket("/ws/dashboard")
async def dashboard_websocket(websocket: WebSocket):
    """Real-time dashboard updates."""
    await manager.connect(websocket, "dashboard")
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket, "dashboard")
