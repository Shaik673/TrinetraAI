import { formatDistanceToNow, format, parseISO } from 'date-fns'

export const formatDate = (date) => {
  if (!date) return 'N/A'
  try {
    return format(typeof date === 'string' ? parseISO(date) : date, 'MMM d, yyyy HH:mm')
  } catch { return 'N/A' }
}

export const formatRelative = (date) => {
  if (!date) return 'N/A'
  try {
    return formatDistanceToNow(typeof date === 'string' ? parseISO(date) : date, { addSuffix: true })
  } catch { return 'N/A' }
}

export const severityColor = (severity) => {
  const map = {
    critical: 'text-threat-critical',
    high: 'text-threat-high',
    medium: 'text-threat-medium',
    low: 'text-threat-low',
    info: 'text-threat-info',
  }
  return map[severity?.toLowerCase()] || 'text-slate-400'
}

export const severityBg = (severity) => {
  const map = {
    critical: 'severity-critical',
    high: 'severity-high',
    medium: 'severity-medium',
    low: 'severity-low',
    info: 'severity-info',
  }
  return map[severity?.toLowerCase()] || 'bg-slate-700 text-slate-300'
}

export const statusClass = (status) => {
  const map = {
    completed: 'status-complete',
    active: 'status-active',
    investigating: 'status-active',
    pending: 'status-pending',
    failed: 'status-failed',
    new: 'status-pending',
    resolved: 'status-complete',
  }
  return map[status?.toLowerCase()] || 'bg-slate-700/30 text-slate-400 border border-slate-600'
}

export const confidenceColor = (score) => {
  if (score >= 0.8) return 'text-neon-green'
  if (score >= 0.6) return 'text-neon-cyan'
  if (score >= 0.4) return 'text-neon-orange'
  return 'text-threat-critical'
}

export const outcomeColor = (outcome) => {
  const map = {
    succeeded: 'text-threat-critical',
    failed: 'text-neon-green',
    partial: 'text-threat-medium',
    unknown: 'text-slate-400',
    ongoing: 'text-neon-blue',
  }
  return map[outcome] || 'text-slate-400'
}

export const truncate = (str, n = 60) =>
  str && str.length > n ? str.slice(0, n) + '...' : str || ''

export const formatBytes = (bytes) => {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1048576) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / 1048576).toFixed(1)} MB`
}
