"""
Replanning Agent — changes strategy when new evidence or gaps are identified.
"""
import json
from datetime import datetime
from app.agents.base import BaseAgent
from app.workflow.state import InvestigationState
from app.core.logging import get_logger

logger = get_logger("replanner_agent")

SYSTEM_PROMPT = """You are the Replanning Agent for TrinetraAI.
Your role is to analyze the reflection report and create a revised investigation strategy.
You identify new evidence sources, update the investigation plan, and determine the next cycle's focus.
Respond with valid JSON only."""


class ReplannerAgent(BaseAgent):
    name = "replanner"
    description = "Creates revised investigation strategy based on reflection findings"

    async def execute(self, state: InvestigationState) -> InvestigationState:
        logger.info("replanner_started", investigation_id=state["investigation_id"])
        reflection = state.get("reflection_result", {})
        current_plan = state.get("investigation_plan", {})
        cycle = state.get("cycle", 1)

        prompt = f"""Create a revised investigation strategy based on the reflection analysis.

Current Investigation Plan:
{json.dumps(current_plan, indent=2)}

Reflection Findings:
- Quality Score: {reflection.get('quality_score', 0.5):.2f}
- Gaps: {reflection.get('gaps_identified', [])}
- Missing Evidence: {reflection.get('missing_evidence', [])}
- Replan Strategy: {json.dumps(reflection.get('replan_strategy', {}), indent=2)}
- Lessons Learned: {reflection.get('lessons_learned', [])}

Current Cycle: {cycle}
Current Confidence: {state.get('confidence_score', 0.0):.2f}

Create an updated investigation plan for the next cycle:
{{
  "revised_objective": "updated investigation focus",
  "revised_hypothesis": "updated attack hypothesis",
  "new_evidence_sources": ["evidence to collect in next cycle"],
  "updated_priority": ["ordered investigation steps"],
  "focus_changes": "what changed from previous plan",
  "expected_confidence_gain": 0.0,
  "cycle_timeout_actions": "what to do if max cycles reached"
}}"""

        try:
            response = await self._invoke_llm(prompt, SYSTEM_PROMPT)
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]
            new_plan = json.loads(response.strip())
        except Exception as e:
            logger.error("replanner_error", error=str(e))
            new_plan = {
                "revised_objective": current_plan.get("objective", "Determine attack outcome"),
                "revised_hypothesis": f"Revised: {current_plan.get('hypothesis', 'Unknown')}",
                "new_evidence_sources": reflection.get("missing_evidence", ["threat_intel"]),
                "updated_priority": ["collect_additional_evidence", "reassess_threat"],
                "focus_changes": "Focused on filling evidence gaps",
                "expected_confidence_gain": 0.15,
                "cycle_timeout_actions": "Conclude with available evidence",
            }

        # Update the plan with revisions
        updated_plan = {
            **current_plan,
            "objective": new_plan.get("revised_objective", current_plan.get("objective")),
            "hypothesis": new_plan.get("revised_hypothesis", current_plan.get("hypothesis")),
            "evidence_sources_needed": new_plan.get("new_evidence_sources", []),
            "investigation_priority": new_plan.get("updated_priority", []),
            "cycle": cycle + 1,
            "replan_reason": new_plan.get("focus_changes", ""),
        }

        decision = self._record_decision(
            state,
            decision=f"Replanned for cycle {cycle + 1}. New focus: {new_plan.get('revised_objective', 'TBD')}",
            reasoning=new_plan.get("focus_changes", ""),
            confidence=0.8,
        )

        event = self._record_event(
            state,
            event_type="replanning_complete",
            message=f"Investigation replanned for cycle {cycle + 1}. Focus: {new_plan.get('focus_changes', 'Evidence gaps')}",
            data={"new_plan": updated_plan, "cycle": cycle + 1},
        )

        return {
            **state,
            "investigation_plan": updated_plan,
            "cycle": cycle + 1,
            "replan_needed": False,
            "current_agent": "replanner",
            "next_agent": "evidence_collector",  # Go back to collecting
            "agent_decisions": [decision],
            "workflow_history": [event],
            "updated_at": datetime.utcnow().isoformat(),
        }
