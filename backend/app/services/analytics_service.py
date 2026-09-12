"""
Analytics service — metrics, MTTR, agent performance, investigation statistics.
"""
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.models.alert import Alert, AlertSeverity, AlertStatus
from app.models.investigation import Investigation, InvestigationStatus, Response, AgentExecution
from app.core.logging import get_logger

logger = get_logger("analytics_service")


class AnalyticsService:
    async def get_dashboard_stats(self, db: AsyncSession) -> dict:
        now = datetime.utcnow()
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)
        last_30d = now - timedelta(days=30)

        # Alert stats
        total_alerts = (await db.execute(select(func.count(Alert.id)))).scalar()
        critical_alerts = (await db.execute(
            select(func.count(Alert.id)).where(Alert.severity == AlertSeverity.CRITICAL)
        )).scalar()
        open_alerts = (await db.execute(
            select(func.count(Alert.id)).where(Alert.status == AlertStatus.NEW)
        )).scalar()
        alerts_24h = (await db.execute(
            select(func.count(Alert.id)).where(Alert.created_at >= last_24h)
        )).scalar()

        # Investigation stats
        total_investigations = (await db.execute(select(func.count(Investigation.id)))).scalar()
        active_investigations = (await db.execute(
            select(func.count(Investigation.id)).where(
                Investigation.status.not_in([InvestigationStatus.COMPLETED, InvestigationStatus.FAILED])
            )
        )).scalar()
        completed_investigations = (await db.execute(
            select(func.count(Investigation.id)).where(Investigation.status == InvestigationStatus.COMPLETED)
        )).scalar()

        # MTTR calculation
        completed = await db.execute(
            select(Investigation).where(
                and_(
                    Investigation.status == InvestigationStatus.COMPLETED,
                    Investigation.started_at.isnot(None),
                    Investigation.completed_at.isnot(None),
                )
            )
        )
        completed_list = completed.scalars().all()
        mttr_minutes = 0
        if completed_list:
            total_minutes = sum(
                (inv.completed_at - inv.started_at).total_seconds() / 60
                for inv in completed_list
                if inv.completed_at and inv.started_at
            )
            mttr_minutes = total_minutes / len(completed_list) if completed_list else 0

        # Average confidence
        avg_confidence = (await db.execute(
            select(func.avg(Investigation.confidence_score)).where(
                Investigation.status == InvestigationStatus.COMPLETED
            )
        )).scalar() or 0.0

        # Response count
        total_responses = (await db.execute(select(func.count(Response.id)))).scalar()

        # Agent execution stats
        agent_stats_result = await db.execute(
            select(AgentExecution.agent_name, func.count(AgentExecution.id).label("count"))
            .group_by(AgentExecution.agent_name)
        )
        agent_stats = {row.agent_name: row.count for row in agent_stats_result}

        return {
            "alerts": {
                "total": total_alerts,
                "critical": critical_alerts,
                "open": open_alerts,
                "last_24h": alerts_24h,
            },
            "investigations": {
                "total": total_investigations,
                "active": active_investigations,
                "completed": completed_investigations,
                "success_rate": round((completed_investigations / max(total_investigations, 1)) * 100, 1),
            },
            "performance": {
                "mttr_minutes": round(mttr_minutes, 1),
                "avg_confidence": round(float(avg_confidence), 3),
                "total_responses": total_responses,
            },
            "agent_activity": agent_stats,
            "generated_at": now.isoformat(),
        }

    async def get_severity_distribution(self, db: AsyncSession) -> dict:
        result = await db.execute(
            select(Alert.severity, func.count(Alert.id).label("count"))
            .group_by(Alert.severity)
        )
        return {row.severity: row.count for row in result}

    async def get_investigation_trend(self, db: AsyncSession, days: int = 7) -> list:
        trend = []
        for i in range(days):
            day = datetime.utcnow() - timedelta(days=i)
            day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            count = (await db.execute(
                select(func.count(Investigation.id)).where(
                    and_(Investigation.created_at >= day_start, Investigation.created_at < day_end)
                )
            )).scalar()
            trend.append({"date": day_start.strftime("%Y-%m-%d"), "count": count})
        return list(reversed(trend))


analytics_service = AnalyticsService()
