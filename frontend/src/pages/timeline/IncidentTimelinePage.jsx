import { Link } from 'react-router-dom'
import { Clock3, FileSearch } from 'lucide-react'
import { useInvestigationResources } from '../../hooks/useInvestigationResources'
import { GlassCard, LoadingSpinner, PageHeader } from '../../components/ui/GlassCard'
import { formatDate } from '../../utils/helpers'

export default function IncidentTimelinePage() {
  const { items: agents, investigations, isLoading } = useInvestigationResources('agents')
  if (isLoading) return <div className="h-full flex items-center justify-center"><LoadingSpinner size="lg" /></div>
  const events = [
    ...investigations.map((investigation) => ({ id: `start-${investigation.id}`, time: investigation.started_at || investigation.created_at, type: 'Investigation started', description: investigation.investigation_id, investigation })),
    ...agents.map((agent) => ({ id: agent.id, time: agent.completed_at || agent.started_at, type: `${agent.agent_name.replace(/_/g, ' ')} completed`, description: agent.decision || 'No decision recorded.', investigation: agent.investigation })),
  ].filter((event) => event.time).sort((a, b) => new Date(b.time) - new Date(a.time))
  return <div><PageHeader title="Incident Timeline" subtitle="Chronological investigation and agent activity across the platform" icon={Clock3} /><GlassCard hover={false}>{events.length ? <div className="space-y-0">{events.map((event, index) => <div key={event.id} className="flex gap-4"><div className="flex flex-col items-center"><span className="mt-1 w-3 h-3 rounded-full bg-neon-blue border-2 border-cyber-bg" />{index < events.length - 1 && <span className="w-px flex-1 min-h-14 bg-cyber-border" />}</div><div className="pb-6"><p className="text-sm font-medium capitalize text-white">{event.type}</p><p className="mt-1 text-sm text-slate-400">{event.description}</p><div className="mt-2 flex gap-3 text-xs"><span className="text-slate-600">{formatDate(event.time)}</span><Link className="text-neon-blue" to={`/investigations/${event.investigation.investigation_id}`}>{event.investigation.investigation_id}</Link></div></div></div>)}</div> : <div className="py-14 text-center"><FileSearch className="w-8 h-8 mx-auto text-slate-600" /><p className="mt-3 text-slate-500">Events will appear as investigations progress.</p></div>}</GlassCard></div>
}
