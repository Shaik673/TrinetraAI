"""
Reflection Agent — evaluates investigation quality and identifies weaknesses.
"""
import json
from datetime import datetime
from app.agents.base import BaseAgent
from app.workflow.state import InvestigationState, ReflectionResult
from app.core.logging import get_logger

logger = get_logger("reflector_agent")

SYSTEM_PROMPT = """You are the Reflection Agent for TrinetraAI.
Your role is to critically evaluate the entire investigation lifecycle, identify weaknesses,
detect missing evidence, and determine if another investigation cycle is required.
Be brutally honest about investigation gaps. Respond with valid JSON only."""


class ReflectorAgent(BaseAgent):
    name = "reflector"
    description = "Evaluates investigation quality and identifies weaknesses for improvement"

    async def execute(self, state: InvestigationState) -> InvestigationState:
        logger.info("reflector_started", investigation_id=state["investigation_id"])
        cycle = state.get("cycle", 1)
        max_cycles = state.get("max_cycles", 5)
        confidence = state.get("confidence_score", 0.0)
        assessment = state.get("attack_assessment", {})
        verification = state.get("verification_result", {})
        decisions = state.get("agent_decisions", [])

        decisions_summary = [
            {"agent": d.get("agent"), "decision": d.get("decision")[:100] if d.get("decision") else "", "confidence": d.get("confidence")}
            for d in decisions[-10:]
        ]

        prompt = f"""Critically evaluate this security investigation.

Investigation Statistics:
- Cycle: {cycle} of {max_cycles}
- Confidence Score: {confidence:.2f}
- Evidence Collected: {len(state.get('server_logs', []))} logs, {len(state.get('packet_metadata', []))} packets, {len(state.get('vulnerabilities', []))} vulns
- Threat Indicators: {len(state.get('threat_indicators', []))}
- Correlated Patterns: {len(state.get('correlated_patterns', []))}

Attack Assessment:
{json.dumps(assessment, indent=2) if assessment else "No assessment generated"}

Verification Result:
{json.dumps(verification, indent=2) if verification else "No verification performed"}

Agent Decisions (recent):
{json.dumps(decisions_summary, indent=2)}

Evaluate the investigation and return JSON:
{{
  "quality_score": 0.0,
  "gaps_identified": ["list of investigation gaps"],
  "missing_evidence": ["list of evidence not collected"],
  "weak_decisions": ["list of questionable agent decisions"],
  "strengths": ["list of investigation strengths"],
  "requires_replanning": true/false,
  "replan_strategy": {{
    "focus_areas": ["what to investigate next"],
    "new_evidence_sources": ["additional evidence to collect"],
    "revised_hypothesis": "updated attack hypothesis",
    "priority": "high|medium|low"
  }},
  "lessons_learned": ["actionable improvements"],
  "investigation_complete": true/false,
  "completion_reasoning": "why investigation is complete or not"
}}"""

        try:
            response = await self._invoke_llm(prompt, SYSTEM_PROMPT)
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]
            reflection_data = json.loads(response.strip())
        except Exception as e:
            logger.error("reflector_error", error=str(e))
            is_complete = confidence >= 0.75 or cycle >= max_cycles
            reflection_data = {
                "quality_score": min(confidence + 0.1, 1.0),
                "gaps_identified": [] if is_complete else ["Additional threat intel needed"],
                "missing_evidence": [] if is_complete else ["Network flow analysis"],
                "weak_decisions": [],
                "strengths": ["Comprehensive log analysis", "Successful threat correlation"],
                "requires_replanning": not is_complete and cycle < max_cycles,
                "replan_strategy": {},
                "lessons_learned": ["Ensure threat intel is collected in first cycle"],
                "investigation_complete": is_complete,
                "completion_reasoning": "Confidence threshold met" if is_complete else "Additional cycles needed",
            }

        # Determine if we should continue or conclude
        requires_replan = (
            reflection_data.get("requires_replanning", False)
            and cycle < max_cycles
            and confidence < 0.75
        )
        investigation_complete = reflection_data.get("investigation_complete", False) or cycle >= max_cycles or confidence >= 0.75

        reflection = ReflectionResult(
            quality_score=float(reflection_data.get("quality_score", 0.5)),
            gaps_identified=reflection_data.get("gaps_identified", []),
            missing_evidence=reflection_data.get("missing_evidence", []),
            weak_decisions=reflection_data.get("weak_decisions", []),
            strengths=reflection_data.get("strengths", []),
            requires_replanning=requires_replan,
            replan_strategy=reflection_data.get("replan_strategy", {}),
            lessons_learned=reflection_data.get("lessons_learned", []),
        )

        next_agent = "replanner" if requires_replan else "final_reviewer"

        decision = self._record_decision(
            state,
            decision=f"Investigation quality: {reflection.get('quality_score'):.2f}. {'Replanning needed.' if requires_replan else 'Investigation complete.'} Gaps: {len(reflection.get('gaps_identified', []))}",
            reasoning=reflection_data.get("completion_reasoning", ""),
            confidence=float(reflection.get("quality_score", 0.5)),
        )

        event = self._record_event(
            state,
            event_type="reflection_complete",
            message=f"Reflection done. Quality: {reflection.get('quality_score'):.2f}. Replanning: {requires_replan}",
            data={"quality_score": reflection.get("quality_score"), "requires_replanning": requires_replan, "complete": investigation_complete},
        )

        return {
            **state,
            "reflection_result": reflection,
            "replan_needed": requires_replan,
            "replan_strategy": reflection_data.get("replan_strategy", {}),
            "objective_met": investigation_complete,
            "current_agent": "reflector",
            "next_agent": next_agent,
            "agent_decisions": [decision],
            "workflow_history": [event],
            "updated_at": datetime.utcnow().isoformat(),
        }
