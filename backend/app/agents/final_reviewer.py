"""
Final Review Agent — approves the final assessment and produces the investigation summary.
"""
import json
from datetime import datetime
from app.agents.base import BaseAgent
from app.workflow.state import InvestigationState
from app.core.logging import get_logger

logger = get_logger("final_reviewer_agent")

SYSTEM_PROMPT = """You are the Final Review Agent for TrinetraAI.
Your role is to produce the definitive investigation summary, approve the final assessment,
and generate a comprehensive incident report.

You are the last line of quality control. Be thorough, objective, and evidence-based.
Respond with valid JSON only."""


class FinalReviewerAgent(BaseAgent):
    name = "final_reviewer"
    description = "Approves final assessment and produces comprehensive investigation summary"

    async def execute(self, state: InvestigationState) -> InvestigationState:
        logger.info("final_reviewer_started", investigation_id=state["investigation_id"])
        assessment = state.get("attack_assessment", {})
        verification = state.get("verification_result", {})
        reflection = state.get("reflection_result", {})
        response_actions = state.get("response_actions", [])

        prompt = f"""Produce the final investigation summary and approve the security assessment.

Investigation ID: {state.get('investigation_id')}
Total Cycles: {state.get('cycle', 1)}
Final Confidence: {state.get('confidence_score', 0.0):.2f}

Final Threat Assessment:
{json.dumps(assessment, indent=2) if assessment else "No assessment"}

Response Actions Taken:
{json.dumps([{{'action': a.get('action'), 'target': a.get('target'), 'status': a.get('status')}} for a in response_actions], indent=2)}

Verification:
- Status: {verification.get('status') if verification else 'Not performed'}
- Effectiveness: {verification.get('effectiveness_score', 0.0) if verification else 0.0:.2f}
- Attack Neutralized: {verification.get('attack_neutralized', False) if verification else False}

Reflection Quality: {reflection.get('quality_score', 0.0) if reflection else 0.0:.2f}

Evidence Collected:
- Server Logs: {len(state.get('server_logs', []))}
- Auth Logs: {len(state.get('auth_logs', []))}
- Packet Flows: {len(state.get('packet_metadata', []))}
- Vulnerabilities: {len(state.get('vulnerabilities', []))}
- Threat Indicators: {len(state.get('threat_indicators', []))}

Produce final summary JSON:
{{
  "final_verdict": "attack_succeeded|attack_failed|attack_partial|false_positive",
  "approved": true/false,
  "final_confidence": 0.0,
  "executive_summary": "2-3 sentence summary for management",
  "technical_summary": "detailed technical narrative",
  "attack_timeline": [
    {{"time": "relative_time", "event": "what happened"}}
  ],
  "impact_assessment": {{
    "data_compromised": true/false,
    "systems_affected": 0,
    "business_impact": "high|medium|low",
    "estimated_dwell_time": "duration"
  }},
  "response_effectiveness": "string",
  "outstanding_risks": ["list"],
  "next_steps": ["list of follow-up actions"],
  "lessons_learned": ["list"]
}}"""

        try:
            response = await self._invoke_llm(prompt, SYSTEM_PROMPT)
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]
            final_report = json.loads(response.strip())
        except Exception as e:
            logger.error("final_reviewer_error", error=str(e))
            outcome = assessment.get("outcome", "unknown") if assessment else "unknown"
            final_report = {
                "final_verdict": f"attack_{outcome}" if outcome != "unknown" else "unknown",
                "approved": True,
                "final_confidence": state.get("confidence_score", 0.5),
                "executive_summary": f"Investigation complete. Attack outcome: {outcome}. Confidence: {state.get('confidence_score', 0.5):.2%}",
                "technical_summary": f"Multi-agent investigation completed {state.get('cycle', 1)} cycle(s).",
                "attack_timeline": [],
                "impact_assessment": {
                    "data_compromised": outcome == "succeeded",
                    "systems_affected": len(assessment.get("affected_systems", [])) if assessment else 0,
                    "business_impact": "high" if outcome == "succeeded" else "low",
                    "estimated_dwell_time": "Unknown",
                },
                "response_effectiveness": verification.get("status", "unknown") if verification else "not_assessed",
                "outstanding_risks": [],
                "next_steps": ["Continue monitoring", "Review firewall rules"],
                "lessons_learned": [],
            }

        decision = self._record_decision(
            state,
            decision=f"FINAL VERDICT: {final_report.get('final_verdict')} (Approved: {final_report.get('approved')}). Confidence: {final_report.get('final_confidence', 0.0):.2f}",
            reasoning=final_report.get("executive_summary", ""),
            confidence=float(final_report.get("final_confidence", 0.5)),
        )

        event = self._record_event(
            state,
            event_type="investigation_complete",
            message=f"Investigation concluded. Verdict: {final_report.get('final_verdict')}. {final_report.get('executive_summary', '')}",
            data=final_report,
        )

        return {
            **state,
            "objective_met": True,
            "current_agent": "final_reviewer",
            "next_agent": None,
            "agent_decisions": [decision],
            "workflow_history": [event],
            "raw_evidence": [{"type": "final_report", "data": final_report}],
            "updated_at": datetime.utcnow().isoformat(),
        }
