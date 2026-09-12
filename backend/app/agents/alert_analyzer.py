"""
Alert Analysis Agent — deep analysis of the incoming alert.
"""
import json
from datetime import datetime
from app.agents.base import BaseAgent
from app.workflow.state import InvestigationState, ThreatIndicatorItem
from app.core.logging import get_logger

logger = get_logger("alert_analyzer_agent")

SYSTEM_PROMPT = """You are the Alert Analysis Agent for TrinetraAI.
Your role is to perform deep analysis of a security alert to extract threat indicators,
classify the attack, identify MITRE ATT&CK techniques, and determine what evidence is needed.

Respond with valid JSON only."""


class AlertAnalyzerAgent(BaseAgent):
    name = "alert_analyzer"
    description = "Performs deep analysis of the security alert to identify attack patterns and IOCs"

    async def execute(self, state: InvestigationState) -> InvestigationState:
        logger.info("alert_analyzer_started", investigation_id=state["investigation_id"])
        alert = state.get("alert", {})
        plan = state.get("investigation_plan", {})

        prompt = f"""Analyze this security alert deeply.

Alert: {json.dumps(alert, indent=2)}
Investigation Hypothesis: {plan.get('hypothesis', 'Unknown')}

Extract and return JSON:
{{
  "attack_classification": "specific attack type",
  "mitre_techniques": ["T1234", "T5678"],
  "mitre_tactics": ["initial_access", "execution"],
  "threat_indicators": [
    {{"type": "ip|domain|hash|url|email", "value": "string", "confidence": 0.0-1.0, "source": "alert", "tags": []}}
  ],
  "attack_surface": ["list of potential entry points"],
  "urgency": "critical|high|medium|low",
  "evidence_priority": ["most important evidence type first"],
  "analysis_notes": "detailed notes",
  "initial_confidence": 0.0
}}"""

        try:
            response = await self._invoke_llm(prompt, SYSTEM_PROMPT)
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]
            analysis = json.loads(response.strip())
        except Exception as e:
            logger.error("alert_analyzer_error", error=str(e))
            analysis = {
                "attack_classification": alert.get("category", "unknown"),
                "mitre_techniques": alert.get("mitre_techniques", []),
                "mitre_tactics": [],
                "threat_indicators": [
                    {"type": "ip", "value": alert.get("source_ip", "0.0.0.0"),
                     "confidence": 0.6, "source": "alert", "tags": ["source_ip"]}
                ] if alert.get("source_ip") else [],
                "attack_surface": [],
                "urgency": alert.get("severity", "medium"),
                "evidence_priority": ["server_logs", "auth_logs"],
                "analysis_notes": "Fallback analysis",
                "initial_confidence": 0.3,
            }

        # Convert to typed indicator objects
        indicators = []
        for ind in analysis.get("threat_indicators", []):
            indicators.append(ThreatIndicatorItem(
                type=ind.get("type", "unknown"),
                value=ind.get("value", ""),
                confidence=float(ind.get("confidence", 0.5)),
                source=ind.get("source", "alert_analysis"),
                tags=ind.get("tags", []),
            ))

        decision = self._record_decision(
            state,
            decision=f"Alert classified as: {analysis.get('attack_classification')}. MITRE: {analysis.get('mitre_techniques', [])}",
            reasoning=analysis.get("analysis_notes", ""),
            confidence=float(analysis.get("initial_confidence", 0.3)),
        )

        event = self._record_event(
            state,
            event_type="alert_analyzed",
            message=f"Alert analysis complete. Found {len(indicators)} threat indicators.",
            data={"attack_classification": analysis.get("attack_classification"), "urgency": analysis.get("urgency")},
        )

        return {
            **state,
            "threat_indicators": indicators,
            "confidence_score": float(analysis.get("initial_confidence", 0.3)),
            "current_agent": "alert_analyzer",
            "next_agent": "evidence_collector",
            "agent_decisions": [decision],
            "workflow_history": [event],
            "updated_at": datetime.utcnow().isoformat(),
        }
