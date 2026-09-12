import { Brain, CheckCircle2, Clock, Timer } from 'lucide-react'
import { Link } from 'react-router-dom'
import { useInvestigationResources } from '../../hooks/useInvestigationResources'
import { GlassCard, LoadingSpinner, PageHeader, StatusBadge } from '../../components/ui/GlassCard'
import { formatRelative } from '../../utils/helpers'

export default function AgentOperationsPage() {
  const { items: executions, isLoading } = useInvestigationResources('agents')
  if (isLoading) return <div className="h-full flex items-center justify-center"><LoadingSpinner size="lg" /></div>
  const completed = executions.filter((execution) => execution.status === 'completed').length
  const averageMs = executions.length ? Math.round(executions.reduce((total, execution) => total + (execution.duration_ms || 0), 0) / executions.length) : 0
  const grouped = executions.reduce((groups, execution) => ({ ...groups, [execution.agent_name]: [...(groups[execution.agent_name] || []), execution] }), {})
  return <div><PageHeader title="Agent Operations" subtitle="Audit the decisions and execution state of the autonomous investigation team" icon={Brain} /><div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-5"><Metric label="Agent executions" value={executions.length} icon={Brain} color="text-neon-blue" /><Metric label="Completed" value={completed} icon={CheckCircle2} color="text-neon-green" /><Metric label="Avg. duration" value={`${averageMs}ms`} icon={Timer} color="text-neon-purple" /></div><div className="grid grid-cols-1 xl:grid-cols-2 gap-4">{Object.entries(grouped).length ? Object.entries(grouped).map(([name, entries]) => <GlassCard key={name} hover={false}><div className="flex justify-between gap-3"><div><h2 className="font-semibold text-white capitalize">{name.replace(/_/g, ' ')}</h2><p className="text-xs text-slate-500 mt-1">{entries.length} executions</p></div><StatusBadge status={entries.at(-1).status} /></div><div className="mt-4 space-y-3">{entries.slice(-3).reverse().map((entry) => <Link key={entry.id} to={`/investigations/${entry.investigation.investigation_id}`} className="block rounded-lg border border-cyber-border/50 p-3 hover:border-neon-blue/40"><div className="flex justify-between gap-2"><span className="font-mono text-xs text-neon-cyan">{entry.investigation.investigation_id}</span><span className="text-xs text-slate-500">cycle {entry.cycle}</span></div><p className="mt-2 text-sm text-slate-300 line-clamp-2">{entry.decision || 'No decision was persisted.'}</p><p className="mt-2 text-xs text-slate-500">{formatRelative(entry.started_at)} · {entry.duration_ms || 0}ms</p></Link>)}</div></GlassCard>) : <Empty />}</div></div>
}

function Metric({ label, value, icon: Icon, color }) { return <GlassCard hover={false} className="p-4"><div className="flex justify-between"><div><p className="text-[10px] uppercase tracking-wider text-slate-500">{label}</p><p className={`text-2xl font-semibold mt-2 ${color}`}>{value}</p></div><Icon className={`w-5 h-5 ${color}`} /></div></GlassCard> }
function Empty() { return <GlassCard hover={false} className="col-span-full text-center"><Clock className="w-8 h-8 text-slate-600 mx-auto" /><p className="mt-3 text-slate-500">Agent execution data appears after an investigation has finished.</p></GlassCard> }
