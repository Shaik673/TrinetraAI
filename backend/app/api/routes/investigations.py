from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.base import get_db
from app.services.investigation_service import investigation_service
from app.models.investigation import (
    Investigation, Evidence, ThreatAssessment, Response,
    VerificationReport, ReflectionReport, AgentExecution
)

router = APIRouter(prefix="/investigations", tags=["Investigations"])


@router.get("/")
async def list_investigations(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    investigations = await investigation_service.list_investigations(db, skip=skip, limit=limit)
    return [
        {
            "id": str(inv.id),
            "investigation_id": inv.investigation_id,
            "alert_id": str(inv.alert_id),
            "status": inv.status,
            "attack_outcome": inv.attack_outcome,
            "confidence_score": inv.confidence_score,
            "cycle_count": inv.cycle_count,
            "started_at": inv.started_at.isoformat() if inv.started_at else None,
            "completed_at": inv.completed_at.isoformat() if inv.completed_at else None,
            "created_at": inv.created_at.isoformat(),
        }
        for inv in investigations
    ]


@router.get("/{investigation_id}")
async def get_investigation(investigation_id: str, db: AsyncSession = Depends(get_db)):
    inv = await investigation_service.get_investigation(db, investigation_id)
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found")
    return {
        "id": str(inv.id),
        "investigation_id": inv.investigation_id,
        "alert_id": str(inv.alert_id),
        "status": inv.status,
        "attack_outcome": inv.attack_outcome,
        "confidence_score": inv.confidence_score,
        "cycle_count": inv.cycle_count,
        "objective": inv.objective,
        "plan": inv.plan,
        "workflow_state": inv.workflow_state,
        "agent_decisions": inv.agent_decisions,
        "summary": inv.summary,
        "started_at": inv.started_at.isoformat() if inv.started_at else None,
        "completed_at": inv.completed_at.isoformat() if inv.completed_at else None,
        "created_at": inv.created_at.isoformat(),
    }


@router.get("/{investigation_id}/evidence")
async def get_investigation_evidence(investigation_id: str, db: AsyncSession = Depends(get_db)):
    inv = await investigation_service.get_investigation(db, investigation_id)
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found")
    result = await db.execute(select(Evidence).where(Evidence.investigation_id == inv.id))
    evidence = result.scalars().all()
    return [
        {
            "id": str(e.id),
            "evidence_type": e.evidence_type,
            "title": e.title,
            "source": e.source,
            "content": e.content,
            "relevance_score": e.relevance_score,
            "threat_indicators": e.threat_indicators,
            "collected_at": e.collected_at.isoformat(),
        }
        for e in evidence
    ]


@router.get("/{investigation_id}/assessments")
async def get_threat_assessments(investigation_id: str, db: AsyncSession = Depends(get_db)):
    inv = await investigation_service.get_investigation(db, investigation_id)
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found")
    result = await db.execute(select(ThreatAssessment).where(ThreatAssessment.investigation_id == inv.id))
    assessments = result.scalars().all()
    return [
        {
            "id": str(a.id),
            "attack_outcome": a.attack_outcome,
            "confidence_score": a.confidence_score,
            "threat_level": a.threat_level,
            "attack_vector": a.attack_vector,
            "affected_systems": a.affected_systems,
            "mitre_techniques": a.mitre_techniques,
            "indicators_of_compromise": a.indicators_of_compromise,
            "attack_chain": a.attack_chain,
            "reasoning": a.reasoning,
            "recommended_actions": a.recommended_actions,
            "cycle": a.cycle,
            "created_at": a.created_at.isoformat(),
        }
        for a in assessments
    ]


@router.get("/{investigation_id}/responses")
async def get_investigation_responses(investigation_id: str, db: AsyncSession = Depends(get_db)):
    inv = await investigation_service.get_investigation(db, investigation_id)
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found")
    result = await db.execute(select(Response).where(Response.investigation_id == inv.id))
    responses = result.scalars().all()
    return [
        {
            "id": str(r.id),
            "action": r.action,
            "status": r.status,
            "target": r.target,
            "target_type": r.target_type,
            "reasoning": r.reasoning,
            "result": r.result,
            "is_simulated": r.is_simulated,
            "can_rollback": r.can_rollback,
            "executed_at": r.executed_at.isoformat() if r.executed_at else None,
        }
        for r in responses
    ]


@router.get("/{investigation_id}/verifications")
async def get_verification_reports(investigation_id: str, db: AsyncSession = Depends(get_db)):
    inv = await investigation_service.get_investigation(db, investigation_id)
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found")
    result = await db.execute(select(VerificationReport).where(VerificationReport.investigation_id == inv.id))
    reports = result.scalars().all()
    return [
        {
            "id": str(r.id),
            "status": r.status,
            "attack_neutralized": r.attack_neutralized,
            "threat_contained": r.threat_contained,
            "environment_stable": r.environment_stable,
            "checks_performed": r.checks_performed,
            "findings": r.findings,
            "effectiveness_score": r.effectiveness_score,
            "recommendations": r.recommendations,
            "created_at": r.created_at.isoformat(),
        }
        for r in reports
    ]


@router.get("/{investigation_id}/reflections")
async def get_reflection_reports(investigation_id: str, db: AsyncSession = Depends(get_db)):
    inv = await investigation_service.get_investigation(db, investigation_id)
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found")
    result = await db.execute(select(ReflectionReport).where(ReflectionReport.investigation_id == inv.id))
    reports = result.scalars().all()
    return [
        {
            "id": str(r.id),
            "cycle": r.cycle,
            "quality_score": r.quality_score,
            "gaps_identified": r.gaps_identified,
            "missing_evidence": r.missing_evidence,
            "weak_decisions": r.weak_decisions,
            "strengths": r.strengths,
            "requires_replanning": r.requires_replanning,
            "lessons_learned": r.lessons_learned,
            "created_at": r.created_at.isoformat(),
        }
        for r in reports
    ]


@router.get("/{investigation_id}/agents")
async def get_agent_executions(investigation_id: str, db: AsyncSession = Depends(get_db)):
    inv = await investigation_service.get_investigation(db, investigation_id)
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found")
    result = await db.execute(
        select(AgentExecution)
        .where(AgentExecution.investigation_id == inv.id)
        .order_by(AgentExecution.started_at.asc())
    )
    executions = result.scalars().all()
    return [
        {
            "id": str(e.id),
            "agent_name": e.agent_name,
            "cycle": e.cycle,
            "status": e.status,
            "decision": e.decision,
            "reasoning": e.reasoning,
            "tokens_used": e.tokens_used,
            "duration_ms": e.duration_ms,
            "started_at": e.started_at.isoformat(),
            "completed_at": e.completed_at.isoformat() if e.completed_at else None,
        }
        for e in executions
    ]
