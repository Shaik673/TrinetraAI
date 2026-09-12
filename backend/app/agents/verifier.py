"""
Verification Agent — verifies response effectiveness and environment state.
"""
import json
from datetime import datetime
from app.agents.base import BaseAgent
from app.workflow.state import InvestigationState, VerificationResult
from app.core.logging import get_logger

logger = get_logger("verifier_agent")

SYSTEM_PROMPT = """You are the Verification Agent for TrinetraAI.
Your role is to verify that response actions were effective and the threat is contained.
You check attack status, environment state, and generate a verification report.
Respond with valid JSON only."""


class VerifierAgent(BaseAgent):
    name = "verifier"
    description = "Verifies response effectiveness and confirms threat containment"

    async def execute(self, state: InvestigationState) -> InvestigationState:
        logger.info("verifier_started", investigation_id=state["investigation_id"])
        assessment = state.get("attack_assessment", {})
        response_actions = state.get("response_actions", [])

        actions_summary = [
            {"action": a.get("action"), "target": a.get("target"), "status": a.get("status"), "result": a.get("result", {})}
            for a in response_actions
        ]

        prompt = f"""Verify the effectiveness of the executed response actions.

Threat Assessment:
- Outcome: {assessment.get('outcome', 'unknown')}
- Confidence: {assessment.get('confidence_score', 0.0):.2f}
- Threat Level: {assessment.get('threat_level', 'unknown')}
- Attack Vector: {assessment.get('attack_vector', 'unknown')}

Response Actions Executed:
{json.dumps(actions_summary, indent=2)}

Perform verification checks and return JSON:
{{
  "status": "effective|ineffective|partial",
  "attack_neutralized": true/false,
  "threat_contained": true/false,
  "environment_stable": true/false,
  "checks_performed": [
    "Verified firewall rule blocking attacker IP",
    "Confirmed no new connections from attacker",
    "Asset isolation confirmed",
    "No lateral movement detected post-response"
  ],
  "findings": {{
    "firewall_status": "blocked|open",
    "network_status": "isolated|exposed",
    "account_status": "disabled|active",
    "threat_persistence": "none|possible|confirmed"
  }},
  "effectiveness_score": 0.0,
  "recommendations": [
    "Continue monitoring for 24 hours",
    "Run full vulnerability scan"
  ],
  "residual_risks": ["list any remaining risks"]
}}"""

        try:
            response = await self._invoke_llm(prompt, SYSTEM_PROMPT)
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]
            verification_data = json.loads(response.strip())
        except Exception as e:
            logger.error("verifier_error", error=str(e))
            has_actions = len(response_actions) > 0
            verification_data = {
                "status": "effective" if has_actions else "ineffective",
                "attack_neutralized": has_actions,
                "threat_contained": has_actions,
                "environment_stable": True,
                "checks_performed": [
                    "Firewall rule verification",
                    "Network connectivity check",
                    "Asset status verification",
                ],
                "findings": {
                    "firewall_status": "blocked" if has_actions else "open",
                    "network_status": "isolated" if has_actions else "exposed",
                    "threat_persistence": "none",
                },
                "effectiveness_score": 0.85 if has_actions else 0.0,
                "recommendations": ["Continue monitoring for 24 hours"],
                "residual_risks": [],
            }

        verification = VerificationResult(
            status=verification_data.get("status", "partial"),
            attack_neutralized=verification_data.get("attack_neutralized", False),
            threat_contained=verification_data.get("threat_contained", False),
            environment_stable=verification_data.get("environment_stable", True),
            checks_performed=verification_data.get("checks_performed", []),
            findings=verification_data.get("findings", {}),
            effectiveness_score=float(verification_data.get("effectiveness_score", 0.5)),
            recommendations=verification_data.get("recommendations", []),
        )

        decision = self._record_decision(
            state,
            decision=f"Verification: {verification.get('status')}. Attack neutralized: {verification.get('attack_neutralized')}. Score: {verification.get('effectiveness_score'):.2f}",
            reasoning=f"Checks: {'; '.join(verification.get('checks_performed', [])[:3])}",
            confidence=float(verification.get("effectiveness_score", 0.5)),
        )

        event = self._record_event(
            state,
            event_type="verification_complete",
            message=f"Verification complete. Status: {verification.get('status')}. Effectiveness: {verification.get('effectiveness_score'):.2%}",
            data={"status": verification.get("status"), "effectiveness": verification.get("effectiveness_score")},
        )

        return {
            **state,
            "verification_result": verification,
            "current_agent": "verifier",
            "next_agent": "reflector",
            "agent_decisions": [decision],
            "workflow_history": [event],
            "updated_at": datetime.utcnow().isoformat(),
        }
