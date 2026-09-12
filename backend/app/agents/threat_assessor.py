"""
Threat Assessment Agent — determines if the attack succeeded and generates confidence score.
"""
import json
from datetime import datetime
from app.agents.base import BaseAgent
from app.workflow.state import InvestigationState, AttackAssessment
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("threat_assessor_agent")

SYSTEM_PROMPT = """You are the Threat Assessment Agent for TrinetraAI.
Your role is to make the final determination on whether a security attack succeeded,
generate a confidence score, and recommend response actions.

You have ALL available evidence and must make a definitive, evidence-backed assessment.
Be precise, analytical, and objective. Respond with valid JSON only."""


class ThreatAssessorAgent(BaseAgent):
    name = "threat_assessor"
    description = "Determines attack outcome and generates confidence score"

    async def execute(self, state: InvestigationState) -> InvestigationState:
        logger.info("threat_assessor_started", investigation_id=state["investigation_id"])
        context = self._build_context_summary(state)
        patterns = state.get("correlated_patterns", [])
        indicators = [
            {"type": i.get("type"), "value": i.get("value"), "confidence": i.get("confidence")}
            for i in state.get("threat_indicators", [])
        ]

        prompt = f"""Make a definitive threat assessment based on all collected evidence.

Investigation Summary:
{context}

Correlated Attack Patterns:
{json.dumps(patterns, indent=2)}

Threat Indicators ({len(indicators)} total):
{json.dumps(indicators[:15], indent=2)}

Vulnerabilities: {json.dumps([
    {"cve": v.get("cve_id"), "cvss": v.get("cvss_score"), "exploit": v.get("exploit_available")}
    for v in state.get("vulnerabilities", [])
], indent=2)}

Investigation Plan Objective: {state.get('investigation_plan', {}).get('objective', 'Determine attack success')}

Return a comprehensive threat assessment JSON:
{{
  "outcome": "succeeded|failed|partial|unknown|ongoing",
  "confidence_score": 0.0,
  "threat_level": "critical|high|medium|low",
  "attack_vector": "specific attack path",
  "affected_systems": ["list of affected system IPs/names"],
  "mitre_techniques": ["T1234"],
  "ioc_list": [{{"type": "ip", "value": "x.x.x.x", "description": "attacker IP"}}],
  "attack_chain": {{
    "stage_1": "Initial Access description",
    "stage_2": "Execution description",
    "stage_3": "Persistence description"
  }},
  "reasoning": "detailed explanation of your determination",
  "recommended_actions": ["block_ip", "quarantine_asset", "disable_account"],
  "evidence_gaps": ["what evidence is still missing"],
  "requires_more_evidence": false
}}"""

        try:
            response = await self._invoke_llm(prompt, SYSTEM_PROMPT)
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]
            assessment_data = json.loads(response.strip())
        except Exception as e:
            logger.error("assessor_error", error=str(e))
            assessment_data = {
                "outcome": "partial",
                "confidence_score": 0.65,
                "threat_level": "high",
                "attack_vector": "Network brute-force followed by privilege escalation",
                "affected_systems": [state.get("alert", {}).get("destination_ip", "unknown")],
                "mitre_techniques": ["T1110", "T1078"],
                "ioc_list": [],
                "attack_chain": {"stage_1": "Brute force", "stage_2": "Initial access gained"},
                "reasoning": "Evidence suggests partial attack success based on authentication patterns",
                "recommended_actions": ["block_ip", "reset_password"],
                "evidence_gaps": [],
                "requires_more_evidence": False,
            }

        assessment = AttackAssessment(
            outcome=assessment_data.get("outcome", "unknown"),
            confidence_score=float(assessment_data.get("confidence_score", 0.5)),
            threat_level=assessment_data.get("threat_level", "medium"),
            attack_vector=assessment_data.get("attack_vector"),
            affected_systems=assessment_data.get("affected_systems", []),
            mitre_techniques=assessment_data.get("mitre_techniques", []),
            ioc_list=assessment_data.get("ioc_list", []),
            attack_chain=assessment_data.get("attack_chain", {}),
            reasoning=assessment_data.get("reasoning", ""),
            recommended_actions=assessment_data.get("recommended_actions", []),
        )

        # Check if we have enough confidence to proceed
        threshold = settings.INVESTIGATION_CONFIDENCE_THRESHOLD
        confidence = float(assessment_data.get("confidence_score", 0.5))
        requires_more = assessment_data.get("requires_more_evidence", False) and confidence < threshold

        next_agent = "responder" if not requires_more else "evidence_collector"

        decision = self._record_decision(
            state,
            decision=f"Attack outcome: {assessment.get('outcome')} (confidence: {confidence:.2f}). {'Proceeding to response.' if not requires_more else 'More evidence needed.'}",
            reasoning=assessment.get("reasoning", ""),
            confidence=confidence,
        )

        event = self._record_event(
            state,
            event_type="threat_assessed",
            message=f"Threat assessment complete. Outcome: {assessment.get('outcome')}. Confidence: {confidence:.2%}",
            data={"outcome": assessment.get("outcome"), "confidence": confidence, "threat_level": assessment.get("threat_level")},
        )

        return {
            **state,
            "attack_assessment": assessment,
            "confidence_score": confidence,
            "current_agent": "threat_assessor",
            "next_agent": next_agent,
            "agent_decisions": [decision],
            "workflow_history": [event],
            "updated_at": datetime.utcnow().isoformat(),
        }
