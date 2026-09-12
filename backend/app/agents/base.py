"""
Base agent class for all TrinetraAI investigation agents.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
import time

from langchain_openai import ChatOpenAI
from app.core.config import settings
from app.core.logging import get_logger
from app.workflow.state import InvestigationState, AgentDecision, WorkflowEvent

logger = get_logger("agents")


class BaseAgent(ABC):
    """Base class for all investigation agents."""

    name: str = "base_agent"
    description: str = ""

    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=settings.OPENAI_TEMPERATURE,
            api_key=settings.OPENAI_API_KEY,
        )

    @abstractmethod
    async def execute(self, state: InvestigationState) -> InvestigationState:
        """Execute the agent's primary task and return updated state."""
        pass

    def _record_decision(
        self,
        state: InvestigationState,
        decision: str,
        reasoning: str,
        confidence: float = 0.0,
    ) -> AgentDecision:
        return AgentDecision(
            agent=self.name,
            timestamp=datetime.utcnow().isoformat(),
            decision=decision,
            reasoning=reasoning,
            confidence=confidence,
            cycle=state.get("cycle", 1),
        )

    def _record_event(
        self,
        state: InvestigationState,
        event_type: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> WorkflowEvent:
        return WorkflowEvent(
            timestamp=datetime.utcnow().isoformat(),
            event_type=event_type,
            agent=self.name,
            message=message,
            data=data or {},
        )

    async def _invoke_llm(self, prompt: str, system_prompt: str = "") -> str:
        """Invoke LLM with error handling and logging."""
        from langchain_core.messages import SystemMessage, HumanMessage
        messages = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=prompt))

        start = time.time()
        try:
            response = await self.llm.ainvoke(messages)
            duration = int((time.time() - start) * 1000)
            logger.info("llm_invoked", agent=self.name, duration_ms=duration)
            return response.content
        except Exception as e:
            logger.error("llm_error", agent=self.name, error=str(e))
            raise

    def _build_context_summary(self, state: InvestigationState) -> str:
        """Build a concise context string from current state for LLM prompts."""
        alert = state.get("alert", {})
        lines = [
            f"Alert: {alert.get('title', 'Unknown')}",
            f"Severity: {alert.get('severity', 'Unknown')}",
            f"Category: {alert.get('category', 'Unknown')}",
            f"Source IP: {alert.get('source_ip', 'N/A')}",
            f"Destination IP: {alert.get('destination_ip', 'N/A')}",
            f"Assets: {len(state.get('assets', []))} identified",
            f"Server Logs: {len(state.get('server_logs', []))} entries",
            f"Auth Logs: {len(state.get('auth_logs', []))} entries",
            f"Packet Metadata: {len(state.get('packet_metadata', []))} flows",
            f"Vulnerabilities: {len(state.get('vulnerabilities', []))} found",
            f"Threat Indicators: {len(state.get('threat_indicators', []))} identified",
            f"Confidence Score: {state.get('confidence_score', 0.0):.2f}",
            f"Cycle: {state.get('cycle', 1)}",
        ]
        return "\n".join(lines)
