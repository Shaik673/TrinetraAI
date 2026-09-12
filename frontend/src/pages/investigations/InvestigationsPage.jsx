import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { FileSearch } from 'lucide-react'
import { api } from '../../api/client'
import { DataTable } from '../../components/ui/DataTable'
import { GlassCard, PageHeader, StatusBadge } from '../../components/ui/GlassCard'
import { formatDate, outcomeColor } from '../../utils/helpers'

export default function InvestigationsPage() {
  const navigate = useNavigate()
  const investigations = useQuery({ queryKey: ['investigations'], queryFn: () => api.getInvestigations({ limit: 100 }).then((response) => response.data), refetchInterval: 15_000 })
  const columns = [
    { key: 'investigation_id', label: 'Investigation', render: (value) => <span className="font-mono text-xs text-neon-cyan">{value}</span> },
    { key: 'status', label: 'Status', render: (value) => <StatusBadge status={value} /> },
    { key: 'attack_outcome', label: 'Outcome', render: (value) => <span className={`capitalize text-xs font-medium ${outcomeColor(value)}`}>{value || 'unknown'}</span> },
    { key: 'confidence_score', label: 'Confidence', render: (value) => `${Math.round((value || 0) * 100)}%` },
    { key: 'cycle_count', label: 'Cycles' },
    { key: 'started_at', label: 'Started', render: (value) => formatDate(value) },
  ]
  return <div><PageHeader title="Investigations" subtitle="Autonomous AI investigations, updated every 15 seconds" icon={FileSearch} /><GlassCard hover={false} className="p-0 overflow-hidden"><DataTable columns={columns} data={investigations.data || []} loading={investigations.isLoading} onRowClick={(investigation) => navigate(`/investigations/${investigation.investigation_id}`)} emptyMessage="No investigations have been launched. Open an alert to begin one." /></GlassCard></div>
}
