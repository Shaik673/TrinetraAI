import { useMutation, useQuery } from '@tanstack/react-query'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { AlertTriangle, ArrowLeft, Play, Server } from 'lucide-react'
import toast from 'react-hot-toast'
import { api } from '../../api/client'
import { GlassCard, LoadingSpinner, PageHeader, SeverityBadge, StatusBadge } from '../../components/ui/GlassCard'
import { formatDate } from '../../utils/helpers'

export default function AlertDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const alertQuery = useQuery({ queryKey: ['alert', id], queryFn: () => api.getAlert(id).then((response) => response.data) })
  const investigate = useMutation({ mutationFn: () => api.triggerInvestigation(id).then((response) => response.data), onSuccess: (data) => { toast.success('Investigation launched'); navigate(`/investigations/${data.investigation_id}`) }, onError: (error) => toast.error(error.response?.data?.detail || 'Could not launch investigation') })
  if (alertQuery.isLoading) return <div className="h-full flex justify-center items-center"><LoadingSpinner size="lg" /></div>
  if (alertQuery.isError) return <NotFound />
  const alert = alertQuery.data
  return <div><PageHeader title={alert.title} subtitle={`${alert.alert_id} · detected ${formatDate(alert.alert_time || alert.created_at)}`} icon={AlertTriangle} actions={<button onClick={() => investigate.mutate()} disabled={investigate.isPending || alert.status === 'investigating'} className="btn-primary rounded-lg px-4 py-2 text-xs font-semibold flex items-center gap-2"><Play className="w-3.5 h-3.5" />{investigate.isPending ? 'Launching…' : alert.status === 'investigating' ? 'Investigation active' : 'Investigate with AI'}</button>} />
    <div className="grid grid-cols-1 xl:grid-cols-3 gap-5"><GlassCard hover={false} className="xl:col-span-2"><div className="flex gap-2 mb-5"><SeverityBadge severity={alert.severity} /><StatusBadge status={alert.status} /></div><h2 className="font-semibold text-white">Alert context</h2><p className="text-sm text-slate-300 mt-3 leading-6">{alert.description || 'No description was provided.'}</p><div className="grid grid-cols-2 md:grid-cols-3 gap-3 mt-6">{[['Source IP', alert.source_ip], ['Destination IP', alert.destination_ip], ['Protocol', alert.protocol], ['Source system', alert.source_system], ['Risk score', alert.risk_score], ['Confidence', alert.confidence_score != null ? `${Math.round(alert.confidence_score * 100)}%` : null]].map(([label, value]) => <div key={label} className="rounded-lg bg-cyber-surface/60 border border-cyber-border/50 p-3"><p className="text-[10px] uppercase tracking-wider text-slate-500">{label}</p><p className="mt-1 text-sm text-slate-200 break-words">{value ?? '—'}</p></div>)}</div></GlassCard><GlassCard hover={false}><div className="flex items-center gap-2"><Server className="w-4 h-4 text-neon-blue" /><h2 className="font-semibold text-white">MITRE techniques</h2></div><div className="mt-4 flex flex-wrap gap-2">{(alert.mitre_techniques || []).length ? alert.mitre_techniques.map((technique) => <Link key={technique} to={`/threat-intel?search=${technique}`} className="rounded border border-neon-purple/30 bg-neon-purple/10 px-2 py-1 font-mono text-xs text-neon-purple hover:bg-neon-purple/20">{technique}</Link>) : <p className="text-sm text-slate-500">No techniques mapped.</p>}</div><h3 className="font-semibold text-white text-sm mt-6">Tags</h3><div className="mt-3 flex flex-wrap gap-2">{(alert.tags || []).map((tag) => <span key={tag} className="rounded bg-cyber-card px-2 py-1 text-xs text-slate-400">#{tag}</span>)}</div></GlassCard></div><GlassCard hover={false} className="mt-5"><h2 className="font-semibold text-white">Raw event data</h2><pre className="mt-3 max-h-96 overflow-auto rounded-lg bg-cyber-bg p-4 text-xs leading-5 text-slate-400">{JSON.stringify(alert.raw_data || {}, null, 2)}</pre></GlassCard></div>
}

function NotFound() { return <div><PageHeader title="Alert not found" icon={AlertTriangle} /><Link to="/alerts" className="inline-flex items-center gap-2 text-sm text-neon-blue"><ArrowLeft className="w-4 h-4" />Back to alerts</Link></div> }
