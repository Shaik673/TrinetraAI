"""
Response Agent — selects and executes appropriate response actions.
"""
import json
from datetime import datetime
from app.agents.base import BaseAgent
from app.workflow.state import InvestigationState, ResponseResult
from app.core.logging import get_logger

logger = get_logger("responder_agent")

SYSTEM_PROMPT = """You are the Response Agent for TrinetraAI.
Your role is to select the most appropriate response actions based on the threat assessment.
You execute simulated security responses: blocking IPs, quarantining assets, disabling accounts, escalating incidents.

Always explain WHY each action was chosen. Prioritize least-disruptive effective responses.
Respond with valid JSON only."""

ACTION_TEMPLATES = {
    "block_ip": {
        "description": "Block the attacker IP at the firewall level",
        "can_rollback": True,
        "simulated": True,
    },
    "quarantine_asset": {
        "description": "Isolate the compromised asset from the network",
        "can_rollback": True,
        "simulated": True,
    },
    "disable_account": {
        "description": "Disable the compromised user account",
        "can_rollback": True,
        "simulated": True,
    },
    "close_alert": {
        "description": "Mark alert as false positive and close",
        "can_rollback": False,
        "simulated": True,
    },
    "escalate_incident": {
        "description": "Escalate to security leadership and IR team",
        "can_rollback": False,
        "simulated": True,
    },
    "reset_password": {
        "description": "Force password reset for affected accounts",
        "can_rollback": False,
        "simulated": True,
    },
    "patch_vulnerability": {
        "description": "Trigger emergency patch deployment",
        "can_rollback": True,
        "simulated": True,
    },
    "no_action": {
        "description": "No response needed - false positive or contained threat",
        "can_rollback": False,
        "simulated": True,
    },
}


class ResponderAgent(BaseAgent):
    name = "responder"
    description = "Selects and executes appropriate response actions based on threat assessment"

    async def execute(self, state: InvestigationState) -> InvestigationState:
        logger.info("responder_started", investigation_id=state["investigation_id"])
        assessment = state.get("attack_assessment", {})
        alert = state.get("alert", {})

        if not assessment:
            logger.warning("no_assessment_for_response", investigation_id=state["investigation_id"])
            return {
                **state,
                "current_agent": "responder",
                "next_agent": "verifier",
                "agent_decisions": [self._record_decision(state, "No action — no assessment available", "", 0.0)],
                "workflow_history": [self._record_event(state, "response_skipped", "No assessment available")],
                "updated_at": datetime.utcnow().isoformat(),
            }

        prompt = f"""Based on this threat assessment, select and execute the appropriate response actions.

Threat Assessment:
- Outcome: {assessment.get('outcome', 'unknown')}
- Confidence: {assessment.get('confidence_score', 0.0):.2f}
- Threat Level: {assessment.get('threat_level', 'unknown')}
- Attack Vector: {assessment.get('attack_vector', 'unknown')}
- Affected Systems: {assessment.get('affected_systems', [])}
- Recommended Actions: {assessment.get('recommended_actions', [])}
- Reasoning: {assessment.get('reasoning', '')[:300]}

Alert Details:
- Source IP: {alert.get('source_ip', 'N/A')}
- Destination IP: {alert.get('destination_ip', 'N/A')}
- Severity: {alert.get('severity', 'unknown')}

Available Actions: {list(ACTION_TEMPLATES.keys())}

Select the best 1-3 response actions and return JSON:
{{
  "selected_actions": [
    {{
      "action": "action_name",
      "target": "IP/hostname/username",
      "target_type": "ip|asset|account|alert",
      "reasoning": "why this action was chosen",
      "priority": 1,
      "parameters": {{}},
      "expected_impact": "what this will achieve"
    }}
  ],
  "overall_reasoning": "explanation of response strategy",
  "escalation_required": false,
  "response_confidence": 0.0
}}"""

        try:
            response = await self._invoke_llm(prompt, SYSTEM_PROMPT)
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]
            response_plan = json.loads(response.strip())
        except Exception as e:
            logger.error("responder_error", error=str(e))
            response_plan = {
                "selected_actions": [
                    {
                        "action": "block_ip",
                        "target": alert.get("source_ip", "0.0.0.0"),
                        "target_type": "ip",
                        "reasoning": "Block attacker's source IP as immediate containment",
                        "priority": 1,
                        "parameters": {"duration": "24h"},
                        "expected_impact": "Stop ongoing attack from this source",
                    }
                ],
                "overall_reasoning": "Immediate containment required based on threat level",
                "escalation_required": False,
                "response_confidence": 0.8,
            }

        # Execute simulated actions
        executed_actions = []
        now = datetime.utcnow().isoformat()
        for action_item in response_plan.get("selected_actions", []):
            action_name = action_item.get("action", "no_action")
            template = ACTION_TEMPLATES.get(action_name, ACTION_TEMPLATES["no_action"])
            executed = ResponseResult(
                action=action_name,
                target=action_item.get("target", "unknown"),
                status="completed",
                reasoning=action_item.get("reasoning", ""),
                executed_at=now,
                result={
                    "simulated": True,
                    "success": True,
                    "message": f"[SIMULATED] {template['description']} — Target: {action_item.get('target')}",
                    "expected_impact": action_item.get("expected_impact", ""),
                    "parameters": action_item.get("parameters", {}),
                },
                can_rollback=template["can_rollback"],
            )
            executed_actions.append(executed)
            logger.info("response_action_executed", action=action_name, target=action_item.get("target"))

        decision = self._record_decision(
            state,
            decision=f"Executed {len(executed_actions)} response action(s): {[a.get('action') for a in executed_actions]}",
            reasoning=response_plan.get("overall_reasoning", ""),
            confidence=float(response_plan.get("response_confidence", 0.8)),
        )

        event = self._record_event(
            state,
            event_type="response_executed",
            message=f"Response actions executed: {[a.get('action') for a in executed_actions]}",
            data={"actions": [a.get("action") for a in executed_actions], "escalation": response_plan.get("escalation_required")},
        )

        return {
            **state,
            "response_actions": executed_actions,
            "current_agent": "responder",
            "next_agent": "verifier",
            "agent_decisions": [decision],
            "workflow_history": [event],
            "updated_at": datetime.utcnow().isoformat(),
        }
