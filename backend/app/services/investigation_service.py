"""
Investigation service — manages investigation lifecycle and LangGraph execution.
"""
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.investigation import (
    Investigation, Evidence, ThreatAssessment, Response,
    VerificationReport, ReflectionReport, AgentExecution,
    InvestigationStatus, AttackOutcome, EvidenceType,
    ResponseAction, ResponseStatus, VerificationStatus
)
from app.models.alert import Alert, AlertStatus
from app.workflow.state import create_initial_state, InvestigationState
from app.core.logging import get_logger

logger = get_logger("investigation_service")


class InvestigationService:

    async def create_investigation(self, db: AsyncSession, alert_id: str, user_id: Optional[str] = None) -> Investigation:
        """Create and start an investigation for an alert."""
        # Fetch the alert
        result = await db.execute(select(Alert).where(Alert.id == alert_id))
        alert = result.scalar_one_or_none()
        if not alert:
            raise ValueError(f"Alert {alert_id} not found")

        investigation_id = f"INV-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"

        investigation = Investigation(
            investigation_id=investigation_id,
            alert_id=alert.id,
            status=InvestigationStatus.PLANNING,
            assigned_to=uuid.UUID(user_id) if user_id else None,
            started_at=datetime.utcnow(),
            cycle_count=0,
        )
        db.add(investigation)

        # Update alert status
        alert.status = AlertStatus.INVESTIGATING
        await db.commit()
        await db.refresh(investigation)
        logger.info("investigation_created", investigation_id=investigation_id, alert_id=str(alert.id))
        return investigation

    async def run_investigation(self, db: AsyncSession, investigation_id: str) -> InvestigationState:
        """Execute the full LangGraph investigation workflow."""
        result = await db.execute(
            select(Investigation).where(Investigation.investigation_id == investigation_id)
        )
        investigation = result.scalar_one_or_none()
        if not investigation:
            raise ValueError(f"Investigation {investigation_id} not found")

        alert_result = await db.execute(select(Alert).where(Alert.id == investigation.alert_id))
        alert = alert_result.scalar_one_or_none()

        # Build initial state
        alert_data = {
            "alert_id": alert.alert_id,
            "title": alert.title,
            "description": alert.description or "",
            "severity": alert.severity.value,
            "category": alert.category.value,
            "source_ip": alert.source_ip,
            "destination_ip": alert.destination_ip,
            "source_port": alert.source_port,
            "destination_port": alert.destination_port,
            "protocol": alert.protocol,
            "source_system": alert.source_system,
            "raw_data": alert.raw_data or {},
            "mitre_techniques": alert.mitre_techniques or [],
            "alert_time": alert.alert_time.isoformat(),
        }

        initial_state = create_initial_state(investigation_id, alert_data)
        initial_state["max_cycles"] = investigation.max_cycles

        # Update investigation status
        investigation.status = InvestigationStatus.COLLECTING_EVIDENCE
        await db.commit()

        try:
            # Run the LangGraph workflow
            # Import lazily: dashboard and alert APIs do not require optional
            # AI-workflow dependencies to be initialized at server startup.
            from app.workflow.graph import investigation_graph
            logger.info("investigation_workflow_started", investigation_id=investigation_id)
            final_state = await investigation_graph.ainvoke(initial_state)

            # Persist results
            await self._persist_investigation_results(db, investigation, final_state)
            logger.info("investigation_workflow_completed", investigation_id=investigation_id)
            return final_state

        except Exception as e:
            logger.error("investigation_workflow_failed", investigation_id=investigation_id, error=str(e))
            investigation.status = InvestigationStatus.FAILED
            await db.commit()
            raise

    async def _persist_investigation_results(
        self, db: AsyncSession, investigation: Investigation, state: InvestigationState
    ):
        """Save all investigation results to the database."""
        # Update investigation record
        assessment = state.get("attack_assessment")
        verification = state.get("verification_result")
        reflection = state.get("reflection_result")

        investigation.status = InvestigationStatus.COMPLETED
        investigation.attack_outcome = AttackOutcome(assessment.get("outcome", "unknown")) if assessment else AttackOutcome.UNKNOWN
        investigation.confidence_score = state.get("confidence_score", 0.0)
        investigation.cycle_count = state.get("cycle", 1)
        investigation.workflow_state = {
            "agents_executed": state.get("agents_executed", []),
            "final_confidence": state.get("confidence_score", 0.0),
        }
        investigation.agent_decisions = state.get("agent_decisions", [])
        investigation.completed_at = datetime.utcnow()

        # Save evidence entries
        all_evidence = (
            [(e, EvidenceType.SERVER_LOG) for e in state.get("server_logs", [])] +
            [(e, EvidenceType.AUTH_LOG) for e in state.get("auth_logs", [])] +
            [(e, EvidenceType.PACKET_METADATA) for e in state.get("packet_metadata", [])] +
            [(e, EvidenceType.VULNERABILITY) for e in state.get("vulnerabilities", [])]
        )

        for ev_data, ev_type in all_evidence[:50]:  # Cap at 50 entries for DB
            evidence = Evidence(
                investigation_id=investigation.id,
                evidence_type=ev_type,
                title=f"{ev_type.value} - {ev_data.get('timestamp', datetime.utcnow().isoformat())}",
                source=ev_data.get("source", "simulation"),
                content=ev_data if isinstance(ev_data, dict) else dict(ev_data),
                relevance_score=0.7,
            )
            db.add(evidence)

        # Save threat assessment
        if assessment:
            ta = ThreatAssessment(
                investigation_id=investigation.id,
                attack_outcome=AttackOutcome(assessment.get("outcome", "unknown")),
                confidence_score=assessment.get("confidence_score", 0.0),
                threat_level=assessment.get("threat_level", "medium"),
                attack_vector=assessment.get("attack_vector"),
                affected_systems=assessment.get("affected_systems", []),
                mitre_techniques=assessment.get("mitre_techniques", []),
                indicators_of_compromise=assessment.get("ioc_list", []),
                attack_chain=assessment.get("attack_chain", {}),
                reasoning=assessment.get("reasoning", ""),
                recommended_actions=assessment.get("recommended_actions", []),
                cycle=state.get("cycle", 1),
            )
            db.add(ta)

        # Save responses
        for r_data in state.get("response_actions", []):
            try:
                action_val = ResponseAction(r_data.get("action", "no_action"))
            except ValueError:
                action_val = ResponseAction.NO_ACTION

            resp = Response(
                investigation_id=investigation.id,
                action=action_val,
                status=ResponseStatus.COMPLETED,
                target=r_data.get("target", ""),
                reasoning=r_data.get("reasoning", ""),
                result=r_data.get("result", {}),
                is_simulated=True,
                can_rollback=r_data.get("can_rollback", True),
                executed_at=datetime.utcnow(),
            )
            db.add(resp)

        # Save verification
        if verification:
            try:
                ver_status = VerificationStatus(verification.get("status", "partial"))
            except ValueError:
                ver_status = VerificationStatus.PARTIAL

            vr = VerificationReport(
                investigation_id=investigation.id,
                status=ver_status,
                attack_neutralized=verification.get("attack_neutralized", False),
                threat_contained=verification.get("threat_contained", False),
                environment_stable=verification.get("environment_stable", True),
                checks_performed=verification.get("checks_performed", []),
                findings=verification.get("findings", {}),
                effectiveness_score=verification.get("effectiveness_score", 0.0),
                recommendations=verification.get("recommendations", []),
            )
            db.add(vr)

        # Save reflection
        if reflection:
            rr = ReflectionReport(
                investigation_id=investigation.id,
                cycle=state.get("cycle", 1),
                quality_score=reflection.get("quality_score", 0.0),
                gaps_identified=reflection.get("gaps_identified", []),
                missing_evidence=reflection.get("missing_evidence", []),
                weak_decisions=reflection.get("weak_decisions", []),
                strengths=reflection.get("strengths", []),
                requires_replanning=reflection.get("requires_replanning", False),
                replan_strategy=reflection.get("replan_strategy", {}),
                lessons_learned=reflection.get("lessons_learned", []),
            )
            db.add(rr)

        # Save agent executions
        for decision in state.get("agent_decisions", [])[:20]:
            ae = AgentExecution(
                investigation_id=investigation.id,
                agent_name=decision.get("agent", "unknown"),
                cycle=decision.get("cycle", 1),
                status="completed",
                output_state={"decision": decision.get("decision"), "confidence": decision.get("confidence")},
                decision=decision.get("decision", ""),
                reasoning=decision.get("reasoning", ""),
            )
            db.add(ae)

        await db.commit()

    async def get_investigation(self, db: AsyncSession, investigation_id: str) -> Optional[Investigation]:
        result = await db.execute(
            select(Investigation).where(Investigation.investigation_id == investigation_id)
        )
        return result.scalar_one_or_none()

    async def list_investigations(self, db: AsyncSession, skip: int = 0, limit: int = 50) -> list:
        result = await db.execute(
            select(Investigation).order_by(Investigation.created_at.desc()).offset(skip).limit(limit)
        )
        return result.scalars().all()


investigation_service = InvestigationService()
