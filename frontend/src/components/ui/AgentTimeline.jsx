import { motion } from 'framer-motion'
import clsx from 'clsx'
import { Brain, CheckCircle, Loader2, AlertTriangle, Clock } from 'lucide-react'

const AGENT_COLORS = {
  planner: 'blue',
  alert_analyzer: 'cyan',
  evidence_collector: 'purple',
  threat_correlator: 'orange',
  threat_assessor: 'red',
  responder: 'red',
  verifier: 'green',
  reflector: 'blue',
  replanner: 'orange',
  final_reviewer: 'cyan',
}

const AGENT_LABELS = {
  planner: 'Planner',
  alert_analyzer: 'Alert Analyzer',
  evidence_collector: 'Evidence Collector',
  threat_correlator: 'Threat Correlator',
  threat_assessor: 'Threat Assessor',
  responder: 'Responder',
  verifier: 'Verifier',
  reflector: 'Reflector',
  replanner: 'Replanner',
  final_reviewer: 'Final Reviewer',
}

const colorClasses = {
  blue: { text: 'text-neon-blue', bg: 'bg-neon-blue/10', border: 'border-neon-blue/30', dot: 'bg-neon-blue' },
  cyan: { text: 'text-neon-cyan', bg: 'bg-neon-cyan/10', border: 'border-neon-cyan/30', dot: 'bg-neon-cyan' },
  purple: { text: 'text-neon-purple', bg: 'bg-neon-purple/10', border: 'border-neon-purple/30', dot: 'bg-neon-purple' },
  orange: { text: 'text-threat-high', bg: 'bg-threat-high/10', border: 'border-threat-high/30', dot: 'bg-threat-high' },
  red: { text: 'text-threat-critical', bg: 'bg-threat-critical/10', border: 'border-threat-critical/30', dot: 'bg-threat-critical' },
  green: { text: 'text-neon-green', bg: 'bg-neon-green/10', border: 'border-neon-green/30', dot: 'bg-neon-green' },
}

export function AgentTimeline({ decisions = [], currentAgent = null }) {
  return (
    <div className="space-y-3">
      {decisions.map((d, i) => {
        const color = colorClasses[AGENT_COLORS[d.agent] || 'blue']
        const isLast = i === decisions.length - 1
        const isCurrent = d.agent === currentAgent
        return (
          <motion.div
            key={i}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.05 }}
            className="flex gap-3"
          >
            {/* Timeline connector */}
            <div className="flex flex-col items-center">
              <div className={clsx(
                'w-8 h-8 rounded-lg flex items-center justify-center border flex-shrink-0',
                color.bg, color.border
              )}>
                {isCurrent ? (
                  <Loader2 className={clsx('w-4 h-4 animate-spin', color.text)} />
                ) : (
                  <Brain className={clsx('w-4 h-4', color.text)} />
                )}
              </div>
              {!isLast && <div className="w-px flex-1 bg-cyber-border/50 mt-1 mb-1 min-h-4" />}
            </div>

            {/* Content */}
            <div className={clsx('flex-1 glass rounded-lg p-3 border mb-3', color.border)}>
              <div className="flex items-center justify-between mb-1">
                <span className={clsx('text-xs font-semibold uppercase tracking-wide', color.text)}>
                  {AGENT_LABELS[d.agent] || d.agent}
                </span>
                <div className="flex items-center gap-2">
                  {d.confidence > 0 && (
                    <span className="text-xs text-slate-500 font-mono">
                      {(d.confidence * 100).toFixed(0)}% conf
                    </span>
                  )}
                  <span className="text-xs text-slate-600">Cycle {d.cycle}</span>
                </div>
              </div>
              <p className="text-sm text-slate-300 leading-relaxed">{d.decision}</p>
              {d.reasoning && (
                <p className="text-xs text-slate-500 mt-1 line-clamp-2">{d.reasoning}</p>
              )}
            </div>
          </motion.div>
        )
      })}
    </div>
  )
}

export function AgentWorkflowDiagram({ currentAgent, completedAgents = [] }) {
  const agents = [
    'planner', 'alert_analyzer', 'evidence_collector',
    'threat_correlator', 'threat_assessor', 'responder',
    'verifier', 'reflector', 'replanner', 'final_reviewer'
  ]

  return (
    <div className="flex flex-wrap gap-2 items-center">
      {agents.map((agent, i) => {
        const isDone = completedAgents.includes(agent)
        const isCurrent = agent === currentAgent
        const color = colorClasses[AGENT_COLORS[agent] || 'blue']
        return (
          <div key={agent} className="flex items-center gap-1">
            <div className={clsx(
              'flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border transition-all',
              isCurrent ? clsx(color.bg, color.border, color.text, 'shadow-neon-blue') :
                isDone ? 'bg-neon-green/10 border-neon-green/30 text-neon-green' :
                  'bg-cyber-card border-cyber-border text-slate-600'
            )}>
              {isCurrent ? (
                <Loader2 className="w-3 h-3 animate-spin" />
              ) : isDone ? (
                <CheckCircle className="w-3 h-3" />
              ) : (
                <Clock className="w-3 h-3" />
              )}
              {AGENT_LABELS[agent] || agent}
            </div>
            {i < agents.length - 1 && (
              <span className="text-slate-700 text-xs">→</span>
            )}
          </div>
        )
      })}
    </div>
  )
}
