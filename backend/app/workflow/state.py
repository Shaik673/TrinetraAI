"""
LangGraph Workflow State — the central nervous system of the investigation.
All agents read from and write to this state.
"""
from typing import TypedDict, Optional, List, Dict, Any, Annotated
from datetime import datetime
import operator


class AlertInfo(TypedDict):
    alert_id: str
    title: str
    description: str
    severity: str
    category: str
    source_ip: Optional[str]
    destination_ip: Optional[str]
    source_port: Optional[int]
    destination_port: Optional[int]
    protocol: Optional[str]
    source_system: Optional[str]
    raw_data: Dict[str, Any]
    mitre_techniques: List[str]
    alert_time: str


class AssetInfo(TypedDict):
    asset_id: str
    hostname: Optional[str]
    ip_address: Optional[str]
    asset_type: str
    os: Optional[str]
    criticality: str
    is_quarantined: bool
    vulnerabilities: List[Dict]
    open_ports: List[int]
    services: List[str]


class LogEntry(TypedDict):
    timestamp: str
    source: str
    level: str
    message: str
    raw: Dict[str, Any]


class PacketMetadata(TypedDict):
    timestamp: str
    src_ip: str
    dst_ip: str
    src_port: int
    dst_port: int
    protocol: str
    bytes_transferred: int
    flags: List[str]
    payload_summary: Optional[str]


class VulnerabilityInfo(TypedDict):
    cve_id: str
    description: str
    cvss_score: float
    cvss_vector: str
    affected_systems: List[str]
    exploit_available: bool
    patch_available: bool


class ThreatIndicatorItem(TypedDict):
    type: str  # ip, domain, hash, url
    value: str
    confidence: float
    source: str
    tags: List[str]


class AgentDecision(TypedDict):
    agent: str
    timestamp: str
    decision: str
    reasoning: str
    confidence: float
    cycle: int


class AttackAssessment(TypedDict):
    outcome: str  # succeeded, failed, partial, unknown, ongoing
    confidence_score: float
    threat_level: str
    attack_vector: Optional[str]
    affected_systems: List[str]
    mitre_techniques: List[str]
    ioc_list: List[Dict]
    attack_chain: Dict[str, Any]
    reasoning: str
    recommended_actions: List[str]


class ResponseResult(TypedDict):
    action: str
    target: str
    status: str
    reasoning: str
    executed_at: str
    result: Dict[str, Any]
    can_rollback: bool


class VerificationResult(TypedDict):
    status: str  # effective, ineffective, partial
    attack_neutralized: bool
    threat_contained: bool
    environment_stable: bool
    checks_performed: List[str]
    findings: Dict[str, Any]
    effectiveness_score: float
    recommendations: List[str]


class ReflectionResult(TypedDict):
    quality_score: float
    gaps_identified: List[str]
    missing_evidence: List[str]
    weak_decisions: List[str]
    strengths: List[str]
    requires_replanning: bool
    replan_strategy: Dict[str, Any]
    lessons_learned: List[str]


class WorkflowEvent(TypedDict):
    timestamp: str
    event_type: str
    agent: Optional[str]
    message: str
    data: Optional[Dict[str, Any]]


class InvestigationState(TypedDict):
    """
    Central state for the entire investigation workflow.
    Passed between all agents in the LangGraph pipeline.
    """
    # Identity
    investigation_id: str
    alert_id: str
    cycle: int

    # Alert context
    alert: AlertInfo

    # Assets involved
    assets: List[AssetInfo]

    # Evidence collected
    server_logs: Annotated[List[LogEntry], operator.add]
    auth_logs: Annotated[List[LogEntry], operator.add]
    packet_metadata: Annotated[List[PacketMetadata], operator.add]
    vulnerabilities: Annotated[List[VulnerabilityInfo], operator.add]
    threat_intel: Annotated[List[Dict[str, Any]], operator.add]
    raw_evidence: Annotated[List[Dict[str, Any]], operator.add]

    # Analysis outputs
    threat_indicators: Annotated[List[ThreatIndicatorItem], operator.add]
    correlated_patterns: List[Dict[str, Any]]

    # Assessment
    attack_assessment: Optional[AttackAssessment]
    confidence_score: float
    investigation_plan: Dict[str, Any]

    # Response
    response_actions: Annotated[List[ResponseResult], operator.add]
    active_firewall_rules: List[str]

    # Verification
    verification_result: Optional[VerificationResult]

    # Reflection & Replanning
    reflection_result: Optional[ReflectionResult]
    replan_needed: bool
    replan_strategy: Dict[str, Any]

    # Agent tracking
    agent_decisions: Annotated[List[AgentDecision], operator.add]
    current_agent: str
    next_agent: Optional[str]
    agents_executed: List[str]

    # History
    workflow_history: Annotated[List[WorkflowEvent], operator.add]

    # Control
    objective_met: bool
    error_message: Optional[str]
    retry_count: int
    max_cycles: int

    # Metadata
    started_at: str
    updated_at: str


def create_initial_state(investigation_id: str, alert_data: Dict[str, Any]) -> InvestigationState:
    """Create a fresh investigation state from an alert."""
    now = datetime.utcnow().isoformat()
    return InvestigationState(
        investigation_id=investigation_id,
        alert_id=alert_data.get("alert_id", ""),
        cycle=1,
        alert=AlertInfo(**{k: alert_data.get(k) for k in AlertInfo.__annotations__ if k in alert_data}),
        assets=[],
        server_logs=[],
        auth_logs=[],
        packet_metadata=[],
        vulnerabilities=[],
        threat_intel=[],
        raw_evidence=[],
        threat_indicators=[],
        correlated_patterns=[],
        attack_assessment=None,
        confidence_score=0.0,
        investigation_plan={},
        response_actions=[],
        active_firewall_rules=[],
        verification_result=None,
        reflection_result=None,
        replan_needed=False,
        replan_strategy={},
        agent_decisions=[],
        current_agent="planner",
        next_agent=None,
        agents_executed=[],
        workflow_history=[WorkflowEvent(
            timestamp=now,
            event_type="investigation_started",
            agent=None,
            message=f"Investigation {investigation_id} initiated",
            data={"alert_id": alert_data.get("alert_id")},
        )],
        objective_met=False,
        error_message=None,
        retry_count=0,
        max_cycles=5,
        started_at=now,
        updated_at=now,
    )
