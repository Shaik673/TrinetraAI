from app.agents.planner import PlannerAgent
from app.agents.alert_analyzer import AlertAnalyzerAgent
from app.agents.evidence_collector import EvidenceCollectorAgent
from app.agents.threat_correlator import ThreatCorrelatorAgent
from app.agents.threat_assessor import ThreatAssessorAgent
from app.agents.responder import ResponderAgent
from app.agents.verifier import VerifierAgent
from app.agents.reflector import ReflectorAgent
from app.agents.replanner import ReplannerAgent
from app.agents.final_reviewer import FinalReviewerAgent

AGENT_REGISTRY = {
    "planner": PlannerAgent,
    "alert_analyzer": AlertAnalyzerAgent,
    "evidence_collector": EvidenceCollectorAgent,
    "threat_correlator": ThreatCorrelatorAgent,
    "threat_assessor": ThreatAssessorAgent,
    "responder": ResponderAgent,
    "verifier": VerifierAgent,
    "reflector": ReflectorAgent,
    "replanner": ReplannerAgent,
    "final_reviewer": FinalReviewerAgent,
}
