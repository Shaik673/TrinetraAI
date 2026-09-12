"""
Alert service — ingestion, classification, and management.
"""
import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.alert import Alert, AlertSeverity, AlertStatus, AlertCategory
from app.core.logging import get_logger

logger = get_logger("alert_service")


class AlertService:
    async def ingest_alert(self, db: AsyncSession, alert_data: dict) -> Alert:
        alert_id = alert_data.get("alert_id") or f"ALT-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{str(uuid.uuid4())[:6].upper()}"

        try:
            severity = AlertSeverity(alert_data.get("severity", "medium").lower())
        except ValueError:
            severity = AlertSeverity.MEDIUM

        try:
            category = AlertCategory(alert_data.get("category", "unknown").lower())
        except ValueError:
            category = AlertCategory.UNKNOWN

        alert = Alert(
            alert_id=alert_id,
            title=alert_data.get("title", "Security Alert"),
            description=alert_data.get("description", ""),
            severity=severity,
            status=AlertStatus.NEW,
            category=category,
            source_ip=alert_data.get("source_ip"),
            destination_ip=alert_data.get("destination_ip"),
            source_port=alert_data.get("source_port"),
            destination_port=alert_data.get("destination_port"),
            protocol=alert_data.get("protocol"),
            source_system=alert_data.get("source_system", "Manual"),
            raw_data=alert_data.get("raw_data", {}),
            mitre_techniques=alert_data.get("mitre_techniques", []),
            affected_assets=alert_data.get("affected_assets", []),
            alert_time=datetime.fromisoformat(alert_data["alert_time"]) if alert_data.get("alert_time") else datetime.utcnow(),
            tags=alert_data.get("tags", []),
        )
        db.add(alert)
        await db.commit()
        await db.refresh(alert)
        logger.info("alert_ingested", alert_id=alert_id, severity=severity)
        return alert

    async def get_alert(self, db: AsyncSession, alert_id: str) -> Optional[Alert]:
        result = await db.execute(select(Alert).where(Alert.alert_id == alert_id))
        return result.scalar_one_or_none()

    async def list_alerts(
        self, db: AsyncSession, skip: int = 0, limit: int = 50,
        severity: Optional[str] = None, status: Optional[str] = None
    ) -> List[Alert]:
        query = select(Alert).order_by(Alert.created_at.desc())
        if severity:
            try:
                query = query.where(Alert.severity == AlertSeverity(severity.lower()))
            except ValueError:
                return []
        if status:
            try:
                query = query.where(Alert.status == AlertStatus(status.lower()))
            except ValueError:
                return []
        result = await db.execute(query.offset(skip).limit(limit))
        return result.scalars().all()

    async def get_alert_stats(self, db: AsyncSession) -> dict:
        total = await db.execute(select(func.count(Alert.id)))
        critical = await db.execute(select(func.count(Alert.id)).where(Alert.severity == AlertSeverity.CRITICAL))
        high = await db.execute(select(func.count(Alert.id)).where(Alert.severity == AlertSeverity.HIGH))
        open_count = await db.execute(
            select(func.count(Alert.id)).where(Alert.status.in_([AlertStatus.NEW, AlertStatus.TRIAGED]))
        )
        return {
            "total": total.scalar(),
            "critical": critical.scalar(),
            "high": high.scalar(),
            "open": open_count.scalar(),
        }

    async def seed_demo_alerts(self, db: AsyncSession) -> List[Alert]:
        """Create realistic demo alerts for the platform."""
        demo_alerts = [
            {
                "alert_id": "ALT-20260912-DEMO01",
                "title": "Brute Force SSH Attack Detected",
                "description": "Multiple failed SSH authentication attempts from external IP, followed by successful login",
                "severity": "critical",
                "category": "intrusion",
                "source_ip": "185.220.101.45",
                "destination_ip": "10.0.1.25",
                "source_port": 52341,
                "destination_port": 22,
                "protocol": "TCP",
                "source_system": "CrowdStrike Falcon",
                "mitre_techniques": ["T1110", "T1078"],
                "tags": ["brute-force", "ssh", "authentication"],
            },
            {
                "alert_id": "ALT-20260912-DEMO02",
                "title": "Ransomware Activity - File Encryption Detected",
                "description": "Mass file encryption detected on file server, shadow copies being deleted",
                "severity": "critical",
                "category": "ransomware",
                "source_ip": "10.0.2.100",
                "destination_ip": "10.0.1.50",
                "protocol": "SMB",
                "source_system": "Microsoft Sentinel",
                "mitre_techniques": ["T1486", "T1490"],
                "tags": ["ransomware", "encryption", "lateral-movement"],
            },
            {
                "alert_id": "ALT-20260912-DEMO03",
                "title": "Data Exfiltration via HTTPS",
                "description": "Large volume of data transferred to unknown external IP over encrypted channel",
                "severity": "high",
                "category": "data_exfiltration",
                "source_ip": "10.0.1.35",
                "destination_ip": "104.21.54.22",
                "destination_port": 443,
                "protocol": "HTTPS",
                "source_system": "Splunk SIEM",
                "mitre_techniques": ["T1048", "T1567"],
                "tags": ["exfiltration", "data-theft"],
            },
            {
                "alert_id": "ALT-20260912-DEMO04",
                "title": "Privilege Escalation - Admin Account Compromise",
                "description": "Service account used for lateral movement with unusual admin activity",
                "severity": "high",
                "category": "privilege_escalation",
                "source_ip": "10.0.3.20",
                "destination_ip": "10.0.1.5",
                "source_system": "IBM QRadar",
                "mitre_techniques": ["T1078", "T1548"],
                "tags": ["privilege-escalation", "admin"],
            },
            {
                "alert_id": "ALT-20260912-DEMO05",
                "title": "Command & Control Beacon Detected",
                "description": "Regular beacon traffic to known C2 infrastructure detected from internal host",
                "severity": "high",
                "category": "command_control",
                "source_ip": "10.0.2.88",
                "destination_ip": "94.102.49.190",
                "destination_port": 8080,
                "protocol": "HTTP",
                "source_system": "Palo Alto Networks",
                "mitre_techniques": ["T1071", "T1105"],
                "tags": ["c2", "beacon", "malware"],
            },
        ]

        created = []
        for a in demo_alerts:
            existing = await self.get_alert(db, a["alert_id"])
            if not existing:
                created.append(await self.ingest_alert(db, a))
        return created


alert_service = AlertService()
