"""
Planner Agent — understands the objective and creates the investigation plan.
"""
import json
from datetime import datetime
from app.agents.base import BaseAgent
from app.workflow.state import InvestigationState
from app.core.logging import get_logger

logger = get_logger("planner_agent")

SYSTEM_PROMPT = """You are the Planner Agent for TrinetraAI, an autonomous SOC investigation platform.
Your role is to analyze a security alert and create a structured investigation plan.

You must determine:
1. The investigation objective (what question needs to be answered)
2. Which evidence sources are needed (logs, packets, assets, vulns, threat intel)
3. Investigation priority order
4. Success criteria (confidence threshold)
5. Potential attack categories to investigate

Respond with a valid JSON object only. No explanations outside JSON."""

PLAN_TEMPLATE = """{
  "objective": "string — what we need to determine",
  "hypothesis": "string — initial attack hypothesis",
  "attack_categories": ["list of suspected attack types"],
  "evidence_sources_needed": ["server_logs", "auth_logs", "packet_metadata", "asset_info", "vulnerabilities", "threat_intel"],
  "investigation_priority": ["ordered list of steps"],
  "success_criteria": "string",
  "confidence_threshold": 0.75,
  "max_cycles": 5,
  "notes": "string"
}"""


class PlannerAgent(BaseAgent):
    name = "planner"
    description = "Creates the investigation plan based on alert analysis"

    async def execute(self, state: InvestigationState) -> InvestigationState:
        logger.info("planner_started", investigation_id=state["investigation_id"])
        alert = state.get("alert", {})

        prompt = f"""Analyze this security alert and create a detailed investigation plan.

Alert Details:
- Title: {alert.get('title', 'Unknown')}
- Description: {alert.get('description', 'No description')}
- Severity: {alert.get('severity', 'Unknown')}
- Category: {alert.get('category', 'Unknown')}
- Source IP: {alert.get('source_ip', 'N/A')}
- Destination IP: {alert.get('destination_ip', 'N/A')}
- Protocol: {alert.get('protocol', 'N/A')}
- MITRE Techniques: {alert.get('mitre_techniques', [])}
- Raw Data: {json.dumps(alert.get('raw_data', {}), indent=2)[:500]}

Create an investigation plan using this exact JSON format:
{PLAN_TEMPLATE}"""

        try:
            response = await self._invoke_llm(prompt, SYSTEM_PROMPT)
            # Extract JSON from response
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]
            plan = json.loads(response.strip())
        except Exception as e:
            logger.error("planner_parse_error", error=str(e))
            plan = {
                "objective": f"Determine if the {alert.get('category', 'unknown')} attack succeeded",
                "hypothesis": f"Potential {alert.get('severity', 'unknown')} severity attack from {alert.get('source_ip', 'unknown')}",
                "attack_categories": [alert.get('category', 'unknown')],
                "evidence_sources_needed": ["server_logs", "auth_logs", "asset_info", "vulnerabilities"],
                "investigation_priority": ["collect_logs", "check_assets", "correlate_evidence", "assess_threat"],
                "success_criteria": "Determine attack success/failure with >75% confidence",
                "confidence_threshold": 0.75,
                "max_cycles": 5,
                "notes": "Fallback plan due to planning error",
            }

        decision = self._record_decision(
            state,
            decision=f"Investigation plan created: {plan.get('objective', 'Unknown objective')}",
            reasoning=f"Alert {alert.get('severity', 'unknown')} severity requires {len(plan.get('evidence_sources_needed', []))} evidence sources",
            confidence=0.9,
        )

        event = self._record_event(
            state,
            event_type="plan_created",
            message=f"Investigation plan ready. Hypothesis: {plan.get('hypothesis', 'TBD')}",
            data=plan,
        )

        return {
            **state,
            "investigation_plan": plan,
            "current_agent": "planner",
            "next_agent": "alert_analyzer",
            "agent_decisions": [decision],
            "workflow_history": [event],
            "updated_at": datetime.utcnow().isoformat(),
        }
