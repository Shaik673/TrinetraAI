"""
LangGraph Investigation Workflow — the autonomous investigation pipeline.
"""
from langgraph.graph import StateGraph, END
from app.workflow.state import InvestigationState
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
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("workflow")

# Instantiate agents (singletons per workflow build)
_planner = PlannerAgent()
_alert_analyzer = AlertAnalyzerAgent()
_evidence_collector = EvidenceCollectorAgent()
_threat_correlator = ThreatCorrelatorAgent()
_threat_assessor = ThreatAssessorAgent()
_responder = ResponderAgent()
_verifier = VerifierAgent()
_reflector = ReflectorAgent()
_replanner = ReplannerAgent()
_final_reviewer = FinalReviewerAgent()


# --- Node functions (wrap async agents for LangGraph) ---

async def planner_node(state: InvestigationState) -> InvestigationState:
    return await _planner.execute(state)


async def alert_analyzer_node(state: InvestigationState) -> InvestigationState:
    return await _alert_analyzer.execute(state)


async def evidence_collector_node(state: InvestigationState) -> InvestigationState:
    return await _evidence_collector.execute(state)


async def threat_correlator_node(state: InvestigationState) -> InvestigationState:
    return await _threat_correlator.execute(state)


async def threat_assessor_node(state: InvestigationState) -> InvestigationState:
    return await _threat_assessor.execute(state)


async def responder_node(state: InvestigationState) -> InvestigationState:
    return await _responder.execute(state)


async def verifier_node(state: InvestigationState) -> InvestigationState:
    return await _verifier.execute(state)


async def reflector_node(state: InvestigationState) -> InvestigationState:
    return await _reflector.execute(state)


async def replanner_node(state: InvestigationState) -> InvestigationState:
    return await _replanner.execute(state)


async def final_reviewer_node(state: InvestigationState) -> InvestigationState:
    return await _final_reviewer.execute(state)


# --- Routing functions ---

def route_after_assessor(state: InvestigationState) -> str:
    """After threat assessment: respond if confident, collect more if not."""
    confidence = state.get("confidence_score", 0.0)
    next_agent = state.get("next_agent", "responder")
    if next_agent == "evidence_collector":
        return "evidence_collector"
    return "responder"


def route_after_reflector(state: InvestigationState) -> str:
    """After reflection: replan or finalize."""
    replan_needed = state.get("replan_needed", False)
    objective_met = state.get("objective_met", False)
    cycle = state.get("cycle", 1)
    max_cycles = state.get("max_cycles", settings.MAX_INVESTIGATION_CYCLES)

    if objective_met or cycle >= max_cycles:
        return "final_reviewer"
    if replan_needed:
        return "replanner"
    return "final_reviewer"


def route_after_replanner(state: InvestigationState) -> str:
    """After replanning: go back to evidence collection."""
    return "evidence_collector"


def build_investigation_graph() -> StateGraph:
    """Build and compile the investigation workflow graph."""
    workflow = StateGraph(InvestigationState)

    # Add all agent nodes
    workflow.add_node("planner", planner_node)
    workflow.add_node("alert_analyzer", alert_analyzer_node)
    workflow.add_node("evidence_collector", evidence_collector_node)
    workflow.add_node("threat_correlator", threat_correlator_node)
    workflow.add_node("threat_assessor", threat_assessor_node)
    workflow.add_node("responder", responder_node)
    workflow.add_node("verifier", verifier_node)
    workflow.add_node("reflector", reflector_node)
    workflow.add_node("replanner", replanner_node)
    workflow.add_node("final_reviewer", final_reviewer_node)

    # Entry point
    workflow.set_entry_point("planner")

    # Linear flow: planner → alert_analyzer → evidence_collector
    workflow.add_edge("planner", "alert_analyzer")
    workflow.add_edge("alert_analyzer", "evidence_collector")
    workflow.add_edge("evidence_collector", "threat_correlator")
    workflow.add_edge("threat_correlator", "threat_assessor")

    # Conditional routing after threat assessment
    workflow.add_conditional_edges(
        "threat_assessor",
        route_after_assessor,
        {
            "responder": "responder",
            "evidence_collector": "evidence_collector",
        },
    )

    # Linear: responder → verifier → reflector
    workflow.add_edge("responder", "verifier")
    workflow.add_edge("verifier", "reflector")

    # Conditional routing after reflection
    workflow.add_conditional_edges(
        "reflector",
        route_after_reflector,
        {
            "final_reviewer": "final_reviewer",
            "replanner": "replanner",
        },
    )

    # Replanner loops back to evidence collection
    workflow.add_conditional_edges(
        "replanner",
        route_after_replanner,
        {"evidence_collector": "evidence_collector"},
    )

    # Final reviewer ends the workflow
    workflow.add_edge("final_reviewer", END)

    return workflow.compile()


# Compile the graph once at module load
investigation_graph = build_investigation_graph()
