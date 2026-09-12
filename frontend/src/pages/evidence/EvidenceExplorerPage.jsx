import { useQueries, useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { Database, ExternalLink } from 'lucide-react'
import { api } from '../../api/client'
import { GlassCard, LoadingSpinner, PageHeader } from '../../components/ui/GlassCard'
import { formatDate } from '../../utils/helpers'

export default function EvidenceExplorerPage() {
  const investigations = useQuery({ queryKey: ['investigations'], queryFn: () => api.getInvestigations({ limit: 100 }).then((response) => response.data) })
  const evidenceQueries = useQueries({ queries: (investigations.data || []).map((investigation) => ({ queryKey: ['investigation', investigation.investigation_id, 'evidence'], queryFn: () => api.getInvestigationEvidence(investigation.investigation_id).then((response) => response.data) })) })
  if (investigations.isLoading) return <div className="h-full flex justify-center items-center"><LoadingSpinner size="lg" /></div>
  const entries = evidenceQueries.flatMap((query, index) => (query.data || []).map((evidence) => ({ ...evidence, investigation: investigations.data[index] }))).sort((a, b) => new Date(b.collected_at) - new Date(a.collected_at))
  return <div><PageHeader title="Evidence Explorer" subtitle="Collected artifacts across completed and active investigations" icon={Database} /><div className="grid grid-cols-1 xl:grid-cols-2 gap-4">{entries.length ? entries.map((entry) => <GlassCard key={entry.id} hover={false}><div className="flex justify-between gap-3"><div><p className="font-semibold text-white">{entry.title}</p><p className="mt-1 font-mono text-xs text-neon-cyan">{entry.investigation.investigation_id}</p></div><span className="rounded border border-neon-purple/30 bg-neon-purple/10 px-2 py-1 h-fit text-xs text-neon-purple">{entry.evidence_type?.replace(/_/g, ' ')}</span></div><p className="mt-3 text-xs text-slate-500">Source: {entry.source || 'Unknown'} · collected {formatDate(entry.collected_at)} · relevance {Math.round((entry.relevance_score || 0) * 100)}%</p><pre className="mt-3 max-h-52 overflow-auto rounded-lg bg-cyber-bg p-3 text-xs text-slate-400">{JSON.stringify(entry.content, null, 2)}</pre><Link to={`/investigations/${entry.investigation.investigation_id}`} className="mt-3 inline-flex items-center gap-1 text-xs text-neon-blue">View investigation <ExternalLink className="w-3 h-3" /></Link></GlassCard>) : <GlassCard hover={false} className="col-span-full"><p className="text-slate-500 text-center py-12">Evidence will appear here after an investigation completes.</p></GlassCard>}</div></div>
}
