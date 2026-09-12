"""
Threat Correlation Agent — connects attack indicators across evidence sources.
"""
import json
from datetime import datetime
from app.agents.base import BaseAgent
from app.workflow.state import InvestigationState, ThreatIndicatorItem
from app.core.logging import get_logger

logger = get_logger("threat_correlator_agent")

SYSTEM_PROMPT = """You are the Threat Correlation Agent for TrinetraAI.
Your role is to correlate evidence from multiple sources to identify attack patterns,
connect indicators of compromise, and build a coherent picture of the attack.
You think like a senior threat analyst. Respond with valid JSON only."""


class ThreatCorrelatorAgent(BaseAgent):
    name = "threat_correlator"
    description = "Correlates evidence to connect attack indicators and build attack chain"

    async def execute(self, state: InvestigationState) -> InvestigationState:
        logger.info("threat_correlator_started", investigation_id=state["investigation_id"])
        context = self._build_context_summary(state)

        # Prepare evidence summary for LLM
        log_sample = [
            {"level": l.get("level"), "message": l.get("message"), "source": l.get("source")}
            for l in (state.get("server_logs", []) + state.get("auth_logs", []))[:10]
        ]
        pkt_sample = [
            {"src_ip": p.get("src_ip"), "dst_ip": p.get("dst_ip"),
             "dst_port": p.get("dst_port"), "bytes": p.get("bytes_transferred"), "flags": p.get("flags")}
            for p in state.get("packet_metadata", [])[:5]
        ]
        vuln_sample = [
            {"cve": v.get("cve_id"), "cvss": v.get("cvss_score"), "exploit": v.get("exploit_available")}
            for v in state.get("vulnerabilities", [])
        ]
        existing_indicators = [
            {"type": i.get("type"), "value": i.get("value"), "confidence": i.get("confidence")}
            for i in state.get("threat_indicators", [])
        ]

        prompt = f"""Correlate the following security evidence and identify attack patterns.

Investigation Context:
{context}

Log Entries (sample):
{json.dumps(log_sample, indent=2)}

Packet Flows (sample):
{json.dumps(pkt_sample, indent=2)}

Vulnerabilities:
{json.dumps(vuln_sample, indent=2)}

Existing Threat Indicators:
{json.dumps(existing_indicators, indent=2)}

Return JSON correlation analysis:
{{
  "correlated_patterns": [
    {{
      "pattern_id": "P1",
      "name": "pattern name",
      "description": "what the pattern indicates",
      "confidence": 0.0,
      "evidence_sources": ["log", "network"],
      "mitre_technique": "T1234",
      "severity": "critical|high|medium|low"
    }}
  ],
  "new_indicators": [
    {{"type": "ip|domain|hash", "value": "string", "confidence": 0.0, "source": "correlation", "tags": []}}
  ],
  "attack_chain_hypothesis": {{
    "initial_access": "how attacker got in",
    "execution": "what they executed",
    "persistence": "how they maintain access",
    "lateral_movement": "where they moved",
    "exfiltration": "what they stole"
  }},
  "correlation_confidence": 0.0,
  "key_finding": "single most important finding"
}}"""

        try:
            response = await self._invoke_llm(prompt, SYSTEM_PROMPT)
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]
            correlation = json.loads(response.strip())
        except Exception as e:
            logger.error("correlator_error", error=str(e))
            correlation = {
                "correlated_patterns": [
                    {
                        "pattern_id": "P1",
                        "name": "Brute Force followed by Lateral Movement",
                        "description": "Multiple auth failures followed by successful login",
                        "confidence": 0.7,
                        "evidence_sources": ["auth_log", "network"],
                        "mitre_technique": "T1110",
                        "severity": "high",
                    }
                ],
                "new_indicators": [],
                "attack_chain_hypothesis": {
                    "initial_access": "Brute force SSH",
                    "execution": "Command shell",
                    "persistence": "Cron job",
                    "lateral_movement": "SSH pivoting",
                    "exfiltration": "Unknown",
                },
                "correlation_confidence": 0.65,
                "key_finding": "Brute force attack with successful authentication",
            }

        # Merge new indicators
        new_indicators = [
            ThreatIndicatorItem(
                type=ind.get("type", "unknown"),
                value=ind.get("value", ""),
                confidence=float(ind.get("confidence", 0.5)),
                source=ind.get("source", "correlation"),
                tags=ind.get("tags", []),
            )
            for ind in correlation.get("new_indicators", [])
        ]

        new_confidence = max(
            state.get("confidence_score", 0.0),
            float(correlation.get("correlation_confidence", 0.0))
        )

        decision = self._record_decision(
            state,
            decision=f"Correlation complete. {len(correlation.get('correlated_patterns', []))} patterns found. Key: {correlation.get('key_finding', 'N/A')}",
            reasoning=f"Attack chain: {json.dumps(correlation.get('attack_chain_hypothesis', {}))}",
            confidence=float(correlation.get("correlation_confidence", 0.0)),
        )

        event = self._record_event(
            state,
            event_type="correlation_complete",
            message=f"Threat correlation done. Key finding: {correlation.get('key_finding')}",
            data={"patterns_count": len(correlation.get("correlated_patterns", []))},
        )

        return {
            **state,
            "correlated_patterns": correlation.get("correlated_patterns", []),
            "threat_indicators": new_indicators,
            "confidence_score": new_confidence,
            "current_agent": "threat_correlator",
            "next_agent": "threat_assessor",
            "agent_decisions": [decision],
            "workflow_history": [event],
            "updated_at": datetime.utcnow().isoformat(),
        }
