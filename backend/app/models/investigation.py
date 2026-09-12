"""
Investigation, Evidence, ThreatAssessment, Response, Verification, Reflection models.
"""
import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, Enum as SAEnum, Float, JSON, ForeignKey, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import enum

from app.db.base import Base


class InvestigationStatus(str, enum.Enum):
    PENDING = "pending"
    PLANNING = "planning"
    COLLECTING_EVIDENCE = "collecting_evidence"
    ANALYZING = "analyzing"
    ASSESSING = "assessing"
    RESPONDING = "responding"
    VERIFYING = "verifying"
    REFLECTING = "reflecting"
    REPLANNING = "replanning"
    COMPLETED = "completed"
    FAILED = "failed"


class AttackOutcome(str, enum.Enum):
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    PARTIAL = "partial"
    UNKNOWN = "unknown"
    ONGOING = "ongoing"


class EvidenceType(str, enum.Enum):
    SERVER_LOG = "server_log"
    AUTH_LOG = "auth_log"
    PACKET_METADATA = "packet_metadata"
    ASSET_INFO = "asset_info"
    VULNERABILITY = "vulnerability"
    THREAT_INTEL = "threat_intel"
    NETWORK_FLOW = "network_flow"
    ENDPOINT_TELEMETRY = "endpoint_telemetry"
    MEMORY_FORENSICS = "memory_forensics"
    FILE_SYSTEM = "file_system"


class ResponseAction(str, enum.Enum):
    BLOCK_IP = "block_ip"
    QUARANTINE_ASSET = "quarantine_asset"
    DISABLE_ACCOUNT = "disable_account"
    CLOSE_ALERT = "close_alert"
    ESCALATE_INCIDENT = "escalate_incident"
    PATCH_VULNERABILITY = "patch_vulnerability"
    RESET_PASSWORD = "reset_password"
    ISOLATE_NETWORK = "isolate_network"
    ROLLBACK = "rollback"
    NO_ACTION = "no_action"


class ResponseStatus(str, enum.Enum):
    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class VerificationStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    EFFECTIVE = "effective"
    INEFFECTIVE = "ineffective"
    PARTIAL = "partial"


class Investigation(Base):
    __tablename__ = "investigations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    investigation_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    alert_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("alerts.id"), nullable=False)
    status: Mapped[InvestigationStatus] = mapped_column(
        SAEnum(InvestigationStatus), default=InvestigationStatus.PENDING, nullable=False, index=True
    )
    attack_outcome: Mapped[AttackOutcome] = mapped_column(
        SAEnum(AttackOutcome), default=AttackOutcome.UNKNOWN, nullable=False
    )
    confidence_score: Mapped[float] = mapped_column(Float, default=0.0)
    cycle_count: Mapped[int] = mapped_column(Integer, default=0)
    max_cycles: Mapped[int] = mapped_column(Integer, default=5)
    objective: Mapped[str] = mapped_column(Text, nullable=True)
    plan: Mapped[dict] = mapped_column(JSON, default=dict)
    workflow_state: Mapped[dict] = mapped_column(JSON, default=dict)
    agent_decisions: Mapped[list] = mapped_column(JSON, default=list)
    summary: Mapped[str] = mapped_column(Text, nullable=True)
    assigned_to: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    alert: Mapped["Alert"] = relationship("Alert", back_populates="investigations")
    evidence: Mapped[list] = relationship("Evidence", back_populates="investigation", lazy="select")
    threat_assessments: Mapped[list] = relationship("ThreatAssessment", back_populates="investigation", lazy="select")
    responses: Mapped[list] = relationship("Response", back_populates="investigation", lazy="select")
    verification_reports: Mapped[list] = relationship("VerificationReport", back_populates="investigation", lazy="select")
    reflection_reports: Mapped[list] = relationship("ReflectionReport", back_populates="investigation", lazy="select")
    agent_executions: Mapped[list] = relationship("AgentExecution", back_populates="investigation", lazy="select")


class Evidence(Base):
    __tablename__ = "evidence"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    investigation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("investigations.id"), nullable=False, index=True
    )
    evidence_type: Mapped[EvidenceType] = mapped_column(SAEnum(EvidenceType), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    source: Mapped[str] = mapped_column(String(200), nullable=True)
    content: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    raw_content: Mapped[str] = mapped_column(Text, nullable=True)
    relevance_score: Mapped[float] = mapped_column(Float, default=0.0)
    threat_indicators: Mapped[list] = mapped_column(JSON, default=list)
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    investigation: Mapped["Investigation"] = relationship("Investigation", back_populates="evidence")


class ThreatAssessment(Base):
    __tablename__ = "threat_assessments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    investigation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("investigations.id"), nullable=False, index=True
    )
    attack_outcome: Mapped[AttackOutcome] = mapped_column(SAEnum(AttackOutcome), nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    threat_level: Mapped[str] = mapped_column(String(50), nullable=False)
    attack_vector: Mapped[str] = mapped_column(String(200), nullable=True)
    affected_systems: Mapped[list] = mapped_column(JSON, default=list)
    mitre_techniques: Mapped[list] = mapped_column(JSON, default=list)
    indicators_of_compromise: Mapped[list] = mapped_column(JSON, default=list)
    attack_chain: Mapped[dict] = mapped_column(JSON, default=dict)
    reasoning: Mapped[str] = mapped_column(Text, nullable=True)
    recommended_actions: Mapped[list] = mapped_column(JSON, default=list)
    cycle: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    investigation: Mapped["Investigation"] = relationship("Investigation", back_populates="threat_assessments")


class Response(Base):
    __tablename__ = "responses"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    investigation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("investigations.id"), nullable=False, index=True
    )
    action: Mapped[ResponseAction] = mapped_column(SAEnum(ResponseAction), nullable=False)
    status: Mapped[ResponseStatus] = mapped_column(
        SAEnum(ResponseStatus), default=ResponseStatus.PENDING, nullable=False
    )
    target: Mapped[str] = mapped_column(String(500), nullable=True)  # IP, asset ID, account
    target_type: Mapped[str] = mapped_column(String(100), nullable=True)
    parameters: Mapped[dict] = mapped_column(JSON, default=dict)
    reasoning: Mapped[str] = mapped_column(Text, nullable=True)
    result: Mapped[dict] = mapped_column(JSON, default=dict)
    is_simulated: Mapped[bool] = mapped_column(Boolean, default=True)
    can_rollback: Mapped[bool] = mapped_column(Boolean, default=True)
    rolled_back_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    executed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    investigation: Mapped["Investigation"] = relationship("Investigation", back_populates="responses")


class VerificationReport(Base):
    __tablename__ = "verification_reports"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    investigation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("investigations.id"), nullable=False, index=True
    )
    response_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("responses.id"), nullable=True)
    status: Mapped[VerificationStatus] = mapped_column(SAEnum(VerificationStatus), nullable=False)
    attack_neutralized: Mapped[bool] = mapped_column(Boolean, default=False)
    threat_contained: Mapped[bool] = mapped_column(Boolean, default=False)
    environment_stable: Mapped[bool] = mapped_column(Boolean, default=False)
    checks_performed: Mapped[list] = mapped_column(JSON, default=list)
    findings: Mapped[dict] = mapped_column(JSON, default=dict)
    effectiveness_score: Mapped[float] = mapped_column(Float, default=0.0)
    recommendations: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    investigation: Mapped["Investigation"] = relationship("Investigation", back_populates="verification_reports")


class ReflectionReport(Base):
    __tablename__ = "reflection_reports"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    investigation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("investigations.id"), nullable=False, index=True
    )
    cycle: Mapped[int] = mapped_column(Integer, default=1)
    quality_score: Mapped[float] = mapped_column(Float, default=0.0)
    gaps_identified: Mapped[list] = mapped_column(JSON, default=list)
    missing_evidence: Mapped[list] = mapped_column(JSON, default=list)
    weak_decisions: Mapped[list] = mapped_column(JSON, default=list)
    strengths: Mapped[list] = mapped_column(JSON, default=list)
    requires_replanning: Mapped[bool] = mapped_column(Boolean, default=False)
    replan_strategy: Mapped[dict] = mapped_column(JSON, default=dict)
    lessons_learned: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    investigation: Mapped["Investigation"] = relationship("Investigation", back_populates="reflection_reports")


class AgentExecution(Base):
    __tablename__ = "agent_executions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    investigation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("investigations.id"), nullable=False, index=True
    )
    agent_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    cycle: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(50), nullable=False)  # running, completed, failed, retrying
    input_state: Mapped[dict] = mapped_column(JSON, default=dict)
    output_state: Mapped[dict] = mapped_column(JSON, default=dict)
    decision: Mapped[str] = mapped_column(Text, nullable=True)
    reasoning: Mapped[str] = mapped_column(Text, nullable=True)
    tokens_used: Mapped[int] = mapped_column(Integer, default=0)
    duration_ms: Mapped[int] = mapped_column(Integer, default=0)
    error: Mapped[str] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    investigation: Mapped["Investigation"] = relationship("Investigation", back_populates="agent_executions")


class FirewallRule(Base):
    __tablename__ = "firewall_rules"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rule_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)  # block, allow, alert
    source_ip: Mapped[str] = mapped_column(String(45), nullable=True)
    destination_ip: Mapped[str] = mapped_column(String(45), nullable=True)
    port: Mapped[int] = mapped_column(nullable=True)
    protocol: Mapped[str] = mapped_column(String(20), nullable=True)
    direction: Mapped[str] = mapped_column(String(20), nullable=True)  # inbound, outbound
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_by_response: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("responses.id"), nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asset_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    hostname: Mapped[str] = mapped_column(String(255), nullable=True, index=True)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=True, index=True)
    asset_type: Mapped[str] = mapped_column(String(100), nullable=False)  # server, workstation, router, etc.
    os: Mapped[str] = mapped_column(String(200), nullable=True)
    os_version: Mapped[str] = mapped_column(String(100), nullable=True)
    department: Mapped[str] = mapped_column(String(200), nullable=True)
    owner: Mapped[str] = mapped_column(String(200), nullable=True)
    criticality: Mapped[str] = mapped_column(String(50), default="medium")  # critical, high, medium, low
    is_quarantined: Mapped[bool] = mapped_column(Boolean, default=False)
    vulnerabilities: Mapped[list] = mapped_column(JSON, default=list)
    open_ports: Mapped[list] = mapped_column(JSON, default=list)
    services: Mapped[list] = mapped_column(JSON, default=list)
    tags: Mapped[list] = mapped_column(JSON, default=list)
    metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    last_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class ThreatIndicator(Base):
    __tablename__ = "threat_indicators"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    indicator_type: Mapped[str] = mapped_column(String(100), nullable=False)  # ip, domain, hash, url, email
    value: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    threat_type: Mapped[str] = mapped_column(String(200), nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    source: Mapped[str] = mapped_column(String(200), nullable=True)
    tags: Mapped[list] = mapped_column(JSON, default=list)
    first_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    last_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    incident_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    severity: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="open")
    alert_ids: Mapped[list] = mapped_column(JSON, default=list)
    investigation_ids: Mapped[list] = mapped_column(JSON, default=list)
    affected_assets: Mapped[list] = mapped_column(JSON, default=list)
    timeline: Mapped[list] = mapped_column(JSON, default=list)
    attack_narrative: Mapped[str] = mapped_column(Text, nullable=True)
    mttr_minutes: Mapped[int] = mapped_column(Integer, nullable=True)
    resolved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
