import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { Activity, AlertTriangle, Brain, Clock, ShieldCheck, Database } from 'lucide-react'
import toast from 'react-hot-toast'
import { api } from '../../api/client'
import { CyberAreaChart } from '../../components/charts/AreaChart'
import { SeverityDonut } from '../../components/charts/DonutChart'
import { DataTable } from '../../components/ui/DataTable'
import { GlassCard, LoadingSpinner, PageHeader, SeverityBadge, StatCard, StatusBadge } from '../../components/ui/GlassCard'
import { formatRelative } from '../../utils/helpers'

const responseData = (request) => request.then((response) => response.data)

export default function DashboardPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const dashboard = useQuery({ queryKey: ['dashboard'], queryFn: () => responseData(api.getDashboardStats()), refetchInterval: 30_000 })
  const severity = useQuery({ queryKey: ['severity-distribution'], queryFn: () => responseData(api.getSeverityDistribution()) })
  const trend = useQuery({ queryKey: ['investigation-trend'], queryFn: () => responseData(api.getInvestigationTrend(7)) })
  const alerts = useQuery({ queryKey: ['alerts', 'recent'], queryFn: () => responseData(api.getAlerts({ limit: 6 })), refetchInterval: 30_000 })
  const investigations = useQuery({ queryKey: ['investigations', 'recent'], queryFn: () => responseData(api.getInvestigations({ limit: 5 })), refetchInterval: 30_000 })
  const seed = useMutation({
    mutationFn: () => responseData(api.seedDemoAlerts()),
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard'] })
      queryClient.invalidateQueries({ queryKey: ['severity-distribution'] })
      toast.success(result.created ? `Added ${result.created} demo alerts` : 'Demo alerts are already available')
    },
    onError: () => toast.error('Could not seed demo alerts. Is the API running?'),
  })

  if (dashboard.isLoading) return <div className="h-full flex items-center justify-center"><LoadingSpinner size="lg" /></div>
  if (dashboard.isError) return <DashboardUnavailable onSeed={() => seed.mutate()} loading={seed.isPending} />

  const stats = dashboard.data || {}
  const alertStats = stats.alerts || {}
  const investigationStats = stats.investigations || {}
  const performance = stats.performance || {}
  const columns = [
    { key: 'severity', label: 'Severity', render: (value) => <SeverityBadge severity={value} /> },
    { key: 'title', label: 'Alert' },
    { key: 'source_ip', label: 'Source' },
    { key: 'status', label: 'Status', render: (value) => <StatusBadge status={value} /> },
    { key: 'created_at', label: 'Detected', render: (value) => formatRelative(value) },
  ]

  return <div>
    <PageHeader
      title="Security Operations Dashboard"
      subtitle="Live visibility across alerts, investigations, and AI response activity"
      icon={Activity}
      actions={<button onClick={() => seed.mutate()} disabled={seed.isPending} className="btn-primary rounded-lg px-3 py-2 text-xs font-semibold disabled:opacity-50">{seed.isPending ? 'Seeding…' : 'Load demo data'}</button>}
    />

    <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4 mb-6">
      <StatCard title="Open alerts" value={alertStats.open ?? 0} subtitle={`${alertStats.critical ?? 0} critical`} icon={AlertTriangle} color="red" />
      <StatCard title="Active investigations" value={investigationStats.active ?? 0} subtitle={`${investigationStats.completed ?? 0} completed`} icon={Brain} color="blue" />
      <StatCard title="Avg. response time" value={`${performance.mttr_minutes ?? 0}m`} subtitle="Completed investigations" icon={Clock} color="cyan" />
      <StatCard title="AI confidence" value={`${Math.round((performance.avg_confidence ?? 0) * 100)}%`} subtitle={`${performance.total_responses ?? 0} response actions`} icon={ShieldCheck} color="green" />
    </div>

    <div className="grid grid-cols-1 xl:grid-cols-3 gap-5 mb-5">
      <GlassCard className="xl:col-span-2" hover={false}>
        <div className="flex items-center justify-between mb-4"><div><h2 className="font-semibold text-white">Investigation activity</h2><p className="text-xs text-slate-500 mt-1">Investigations started each day</p></div><Database className="w-4 h-4 text-neon-blue" /></div>
        <CyberAreaChart data={trend.data || []} dataKey="count" name="Investigations" height={230} />
      </GlassCard>
      <GlassCard hover={false}>
        <h2 className="font-semibold text-white">Alert severity</h2><p className="text-xs text-slate-500 mt-1">Current alert distribution</p>
        <SeverityDonut data={severity.data || {}} height={230} />
      </GlassCard>
    </div>

    <div className="grid grid-cols-1 xl:grid-cols-3 gap-5">
      <GlassCard className="xl:col-span-2 p-0 overflow-hidden" hover={false}>
        <div className="flex items-center justify-between p-5 pb-2"><div><h2 className="font-semibold text-white">Recent alerts</h2><p className="text-xs text-slate-500 mt-1">Prioritized by latest detection time</p></div><button onClick={() => navigate('/alerts')} className="text-xs text-neon-blue hover:text-neon-cyan">View all</button></div>
        <DataTable columns={columns} data={alerts.data || []} loading={alerts.isLoading} onRowClick={(alert) => navigate(`/alerts/${alert.alert_id}`)} emptyMessage="No alerts yet — load the demo data to begin." />
      </GlassCard>
      <GlassCard hover={false}>
        <h2 className="font-semibold text-white">Recent investigations</h2><div className="mt-4 space-y-3">
          {(investigations.data || []).length === 0 ? <p className="text-sm text-slate-500">No investigations running.</p> : investigations.data.map((item) => <button key={item.id} onClick={() => navigate(`/investigations/${item.investigation_id}`)} className="w-full text-left rounded-lg border border-cyber-border/60 p-3 hover:border-neon-blue/40 hover:bg-neon-blue/5"><div className="flex justify-between gap-2"><span className="font-mono text-xs text-neon-cyan">{item.investigation_id}</span><StatusBadge status={item.status} /></div><p className="text-xs text-slate-500 mt-2">Confidence: {Math.round((item.confidence_score || 0) * 100)}% · cycle {item.cycle_count}</p></button>)}
        </div>
      </GlassCard>
    </div>
  </div>
}

function DashboardUnavailable({ onSeed, loading }) {
  return <div><PageHeader title="Security Operations Dashboard" subtitle="The API connection is unavailable" icon={Activity} /><GlassCard hover={false} className="max-w-2xl"><h2 className="text-lg font-semibold text-white">Start the backend to load live operations data</h2><p className="text-sm text-slate-400 mt-2">Run <code className="text-neon-cyan">uvicorn app.main:app --reload</code> from the backend directory, then reload this page.</p><button onClick={onSeed} disabled={loading} className="btn-primary rounded-lg px-4 py-2 mt-5 text-sm">Retry connection</button></GlassCard></div>
}
