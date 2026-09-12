import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { Bell, Filter, Plus, RefreshCw } from 'lucide-react'
import toast from 'react-hot-toast'
import { api } from '../../api/client'
import { DataTable } from '../../components/ui/DataTable'
import { GlassCard, PageHeader, SeverityBadge, StatusBadge } from '../../components/ui/GlassCard'
import { formatRelative } from '../../utils/helpers'

const responseData = (request) => request.then((response) => response.data)
const EMPTY_ALERT = { title: '', description: '', severity: 'medium', category: 'unknown', source_ip: '', destination_ip: '' }

export default function AlertsPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [severity, setSeverity] = useState('')
  const [status, setStatus] = useState('')
  const [showCreate, setShowCreate] = useState(false)
  const [form, setForm] = useState(EMPTY_ALERT)
  const alerts = useQuery({ queryKey: ['alerts', { severity, status }], queryFn: () => responseData(api.getAlerts({ limit: 100, ...(severity && { severity }), ...(status && { status }) })) })
  const seed = useMutation({ mutationFn: () => responseData(api.seedDemoAlerts()), onSuccess: (data) => { queryClient.invalidateQueries({ queryKey: ['alerts'] }); queryClient.invalidateQueries({ queryKey: ['dashboard'] }); toast.success(data.created ? `${data.created} alerts added` : 'Demo alerts already exist') }, onError: () => toast.error('Demo seed failed') })
  const create = useMutation({ mutationFn: () => responseData(api.createAlert(form)), onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['alerts'] }); setForm(EMPTY_ALERT); setShowCreate(false); toast.success('Alert created') }, onError: (error) => toast.error(error.response?.data?.detail || 'Could not create alert') })
  const columns = [
    { key: 'alert_id', label: 'Alert ID', render: (value) => <span className="font-mono text-xs text-neon-cyan">{value}</span> },
    { key: 'severity', label: 'Severity', render: (value) => <SeverityBadge severity={value} /> },
    { key: 'title', label: 'Title' },
    { key: 'category', label: 'Category', render: (value) => <span className="capitalize">{value?.replace(/_/g, ' ')}</span> },
    { key: 'source_ip', label: 'Source' },
    { key: 'status', label: 'Status', render: (value) => <StatusBadge status={value} /> },
    { key: 'created_at', label: 'Detected', render: (value) => formatRelative(value) },
  ]
  return <div>
    <PageHeader title="Alert Center" subtitle="Triage incoming security signals and launch investigations" icon={Bell} actions={<><button onClick={() => setShowCreate((value) => !value)} className="btn-primary rounded-lg px-3 py-2 text-xs font-semibold flex gap-1.5 items-center"><Plus className="w-3.5 h-3.5" /> New alert</button><button onClick={() => seed.mutate()} disabled={seed.isPending} className="rounded-lg border border-cyber-border px-3 py-2 text-xs text-slate-300 hover:text-white"><RefreshCw className="w-3.5 h-3.5 inline mr-1" /> Demo data</button></>} />
    {showCreate && <GlassCard hover={false} className="mb-5"><form onSubmit={(event) => { event.preventDefault(); create.mutate() }} className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3"><FormField label="Title" value={form.title} onChange={(title) => setForm({ ...form, title })} required /><FormField label="Source IP" value={form.source_ip} onChange={(source_ip) => setForm({ ...form, source_ip })} /><FormField label="Destination IP" value={form.destination_ip} onChange={(destination_ip) => setForm({ ...form, destination_ip })} /><label className="text-xs text-slate-400">Severity<select value={form.severity} onChange={(event) => setForm({ ...form, severity: event.target.value })} className="cyber-input w-full mt-1 rounded-lg px-3 py-2"><option value="critical">Critical</option><option value="high">High</option><option value="medium">Medium</option><option value="low">Low</option><option value="info">Info</option></select></label><FormField label="Category" value={form.category} onChange={(category) => setForm({ ...form, category })} /><label className="text-xs text-slate-400 md:col-span-2 xl:col-span-1">Description<textarea value={form.description} onChange={(event) => setForm({ ...form, description: event.target.value })} className="cyber-input w-full mt-1 rounded-lg px-3 py-2 min-h-10" /></label><div className="md:col-span-2 xl:col-span-3 flex justify-end gap-2"><button type="button" onClick={() => setShowCreate(false)} className="px-3 py-2 text-xs text-slate-400">Cancel</button><button disabled={create.isPending} className="btn-primary rounded-lg px-4 py-2 text-xs font-semibold">{create.isPending ? 'Creating…' : 'Create alert'}</button></div></form></GlassCard>}
    <GlassCard hover={false} className="p-0 overflow-hidden"><div className="flex flex-wrap gap-3 p-4 border-b border-cyber-border/50 items-center"><Filter className="w-4 h-4 text-slate-500" /><select value={severity} onChange={(event) => setSeverity(event.target.value)} className="cyber-input rounded-lg px-3 py-2 text-xs"><option value="">All severities</option>{['critical', 'high', 'medium', 'low', 'info'].map((value) => <option key={value}>{value}</option>)}</select><select value={status} onChange={(event) => setStatus(event.target.value)} className="cyber-input rounded-lg px-3 py-2 text-xs"><option value="">All statuses</option>{['new', 'triaged', 'investigating', 'resolved', 'false_positive'].map((value) => <option key={value}>{value}</option>)}</select><span className="ml-auto text-xs text-slate-500">{(alerts.data || []).length} alerts</span></div><DataTable columns={columns} data={alerts.data || []} loading={alerts.isLoading} onRowClick={(alert) => navigate(`/alerts/${alert.alert_id}`)} emptyMessage="No alerts match these filters." /></GlassCard>
  </div>
}

function FormField({ label, value, onChange, required = false }) { return <label className="text-xs text-slate-400">{label}<input value={value || ''} onChange={(event) => onChange(event.target.value)} required={required} className="cyber-input w-full mt-1 rounded-lg px-3 py-2" /></label> }
