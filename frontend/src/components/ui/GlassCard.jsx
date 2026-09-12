import { motion } from 'framer-motion'
import clsx from 'clsx'

export function GlassCard({ children, className, hover = true, glow = false, onClick, delay = 0 }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay }}
      onClick={onClick}
      className={clsx(
        'glass rounded-xl p-5',
        hover && 'glass-hover cursor-pointer',
        glow && 'shadow-neon-blue',
        onClick && 'cursor-pointer',
        className
      )}
    >
      {children}
    </motion.div>
  )
}

export function StatCard({ title, value, subtitle, icon: Icon, trend, color = 'blue', delay = 0 }) {
  const colorMap = {
    blue: { text: 'text-neon-blue', bg: 'bg-neon-blue/10', border: 'border-neon-blue/20' },
    cyan: { text: 'text-neon-cyan', bg: 'bg-neon-cyan/10', border: 'border-neon-cyan/20' },
    purple: { text: 'text-neon-purple', bg: 'bg-neon-purple/10', border: 'border-neon-purple/20' },
    red: { text: 'text-threat-critical', bg: 'bg-threat-critical/10', border: 'border-threat-critical/20' },
    orange: { text: 'text-threat-high', bg: 'bg-threat-high/10', border: 'border-threat-high/20' },
    green: { text: 'text-neon-green', bg: 'bg-neon-green/10', border: 'border-neon-green/20' },
  }
  const c = colorMap[color] || colorMap.blue

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay }}
      className={clsx('glass rounded-xl p-5 glass-hover border', c.border)}
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">{title}</p>
          <p className={clsx('text-3xl font-bold mt-2', c.text)}>{value}</p>
          {subtitle && <p className="text-xs text-slate-500 mt-1">{subtitle}</p>}
        </div>
        {Icon && (
          <div className={clsx('w-10 h-10 rounded-lg flex items-center justify-center', c.bg, 'border', c.border)}>
            <Icon className={clsx('w-5 h-5', c.text)} />
          </div>
        )}
      </div>
      {trend !== undefined && (
        <div className="mt-3 pt-3 border-t border-cyber-border/50">
          <span className={clsx('text-xs font-medium', trend >= 0 ? 'text-threat-critical' : 'text-neon-green')}>
            {trend >= 0 ? '↑' : '↓'} {Math.abs(trend)}%
          </span>
          <span className="text-xs text-slate-600 ml-1">vs last 24h</span>
        </div>
      )}
    </motion.div>
  )
}

export function SeverityBadge({ severity }) {
  return (
    <span className={clsx('inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold uppercase tracking-wide',
      `severity-${severity?.toLowerCase()}` || 'bg-slate-700 text-slate-300'
    )}>
      {severity}
    </span>
  )
}

export function StatusBadge({ status }) {
  const map = {
    completed: 'status-complete',
    active: 'status-active',
    investigating: 'status-active',
    pending: 'status-pending',
    failed: 'status-failed',
    new: 'status-pending',
    resolved: 'status-complete',
    planning: 'status-active',
    collecting_evidence: 'status-active',
    analyzing: 'status-active',
    false_positive: 'bg-slate-700/30 text-slate-400 border border-slate-600',
    escalated: 'severity-high',
  }
  return (
    <span className={clsx('inline-flex items-center px-2 py-0.5 rounded text-xs font-medium capitalize',
      map[status?.toLowerCase()] || 'bg-slate-700/30 text-slate-400 border border-slate-600'
    )}>
      {status?.replace(/_/g, ' ')}
    </span>
  )
}

export function LoadingSpinner({ size = 'md', className }) {
  const sizes = { sm: 'w-4 h-4', md: 'w-6 h-6', lg: 'w-10 h-10' }
  return (
    <div className={clsx('relative flex items-center justify-center', className)}>
      <div className={clsx(sizes[size], 'border-2 border-cyber-border border-t-neon-blue rounded-full animate-spin')} />
    </div>
  )
}

export function PageHeader({ title, subtitle, actions, icon: Icon }) {
  return (
    <div className="flex items-center justify-between mb-6">
      <div className="flex items-center gap-3">
        {Icon && (
          <div className="w-10 h-10 rounded-xl bg-neon-blue/10 border border-neon-blue/20 flex items-center justify-center">
            <Icon className="w-5 h-5 text-neon-blue" />
          </div>
        )}
        <div>
          <h1 className="text-xl font-bold text-white">{title}</h1>
          {subtitle && <p className="text-sm text-slate-500 mt-0.5">{subtitle}</p>}
        </div>
      </div>
      {actions && <div className="flex items-center gap-2">{actions}</div>}
    </div>
  )
}

export function EmptyState({ icon: Icon, title, description, action }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      {Icon && (
        <div className="w-16 h-16 rounded-2xl bg-cyber-card border border-cyber-border flex items-center justify-center mb-4">
          <Icon className="w-8 h-8 text-slate-600" />
        </div>
      )}
      <h3 className="text-lg font-semibold text-slate-300 mb-2">{title}</h3>
      <p className="text-sm text-slate-500 max-w-sm mb-4">{description}</p>
      {action}
    </div>
  )
}
