"""
Security Alert model.
"""
import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, Enum as SAEnum, Float, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import enum

from app.db.base import Base


class AlertSeverity(str, enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class AlertStatus(str, enum.Enum):
    NEW = "new"
    TRIAGED = "triaged"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"
    ESCALATED = "escalated"


class AlertCategory(str, enum.Enum):
    MALWARE = "malware"
    INTRUSION = "intrusion"
    DATA_EXFILTRATION = "data_exfiltration"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    LATERAL_MOVEMENT = "lateral_movement"
    COMMAND_CONTROL = "command_control"
    DENIAL_OF_SERVICE = "denial_of_service"
    INSIDER_THREAT = "insider_threat"
    PHISHING = "phishing"
    RANSOMWARE = "ransomware"
    UNKNOWN = "unknown"


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    alert_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    severity: Mapped[AlertSeverity] = mapped_column(SAEnum(AlertSeverity), nullable=False, index=True)
    status: Mapped[AlertStatus] = mapped_column(
        SAEnum(AlertStatus), default=AlertStatus.NEW, nullable=False, index=True
    )
    category: Mapped[AlertCategory] = mapped_column(
        SAEnum(AlertCategory), default=AlertCategory.UNKNOWN, nullable=False
    )
    source_ip: Mapped[str] = mapped_column(String(45), nullable=True, index=True)
    destination_ip: Mapped[str] = mapped_column(String(45), nullable=True)
    source_port: Mapped[int] = mapped_column(nullable=True)
    destination_port: Mapped[int] = mapped_column(nullable=True)
    protocol: Mapped[str] = mapped_column(String(20), nullable=True)
    source_system: Mapped[str] = mapped_column(String(200), nullable=True)  # SIEM, EDR, etc.
    raw_data: Mapped[dict] = mapped_column(JSON, nullable=True)
    mitre_techniques: Mapped[list] = mapped_column(JSON, default=list)
    affected_assets: Mapped[list] = mapped_column(JSON, default=list)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.0)
    risk_score: Mapped[float] = mapped_column(Float, default=0.0)
    alert_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    triage_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    assigned_to: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    tags: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    investigations: Mapped[list] = relationship("Investigation", back_populates="alert", lazy="select")

    def __repr__(self):
        return f"<Alert {self.alert_id} [{self.severity}/{self.status}]>"
