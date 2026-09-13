import { useRef } from 'react'
import { Link } from 'react-router-dom'
import { motion, useInView } from 'framer-motion'
import {
  Shield, Brain, Search, Network, Target, Zap, CheckCircle2,
  RotateCcw, ChevronRight, AlertTriangle, Activity, Eye,
  Database, Cpu, Globe, Lock, TrendingUp, Users, Clock,
  ArrowRight, Github, Twitter, Linkedin, Star
} from 'lucide-react'

// ── Animation helpers ────────────────────────────────────────────────────────
const fadeUp = {
  hidden: { opacity: 0, y: 30 },
  visible: (delay = 0) => ({ opacity: 1, y: 0, transition: { duration: 0.6, delay } }),
}

function InViewSection({ children, className = '', delay = 0 }) {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin: '-80px' })
  return (
    <motion.div
      ref={ref}
      variants={fadeUp}
      initial="hidden"
      animate={inView ? 'visible' : 'hidden'}
      custom={delay}
      className={className}
    >
      {children}
    </motion.div>
  )
}

// ── Agent pipeline data ──────────────────────────────────────────────────────
const AGENTS = [
  { icon: Brain, name: 'Planner', desc: 'Understands objective and plans the investigation strategy', color: 'text-neon-blue', bg: 'bg-neon-blue/10', border: 'border-neon-blue/30' },
  { icon: Search, name: 'Alert Analyzer', desc: 'Identifies attack categories from incoming alert data', color: 'text-neon-purple', bg: 'bg-neon-purple/10', border: 'border-neon-purple/30' },
  { icon: Database, name: 'Evidence Collector', desc: 'Gathers logs, assets, vulnerabilities and packet metadata', color: 'text-neon-cyan', bg: 'bg-neon-cyan/10', border: 'border-neon-cyan/30' },
  { icon: Network, name: 'Threat Correlator', desc: 'Connects attack indicators across evidence sources', color: 'text-neon-blue', bg: 'bg-neon-blue/10', border: 'border-neon-blue/30' },
  { icon: Target, name: 'Threat Assessor', desc: 'Determines attack success and generates confidence scores', color: 'text-threat-high', bg: 'bg-threat-high/10', border: 'border-threat-high/30' },
  { icon: Zap, name: 'Responder', desc: 'Selects and executes simulated firewall and quarantine actions', color: 'text-neon-purple', bg: 'bg-neon-purple/10', border: 'border-neon-purple/30' },
  { icon: CheckCircle2, name: 'Verifier', desc: 'Validates response effectiveness and environment stability', color: 'text-neon-green', bg: 'bg-neon-green/10', border: 'border-neon-green/30' },
  { icon: Eye, name: 'Reflector', desc: 'Evaluates investigation quality and detects weaknesses', color: 'text-neon-cyan', bg: 'bg-neon-cyan/10', border: 'border-neon-cyan/30' },
  { icon: RotateCcw, name: 'Replanner', desc: 'Changes strategy when new evidence demands a fresh approach', color: 'text-neon-blue', bg: 'bg-neon-blue/10', border: 'border-neon-blue/30' },
  { icon: Shield, name: 'Final Reviewer', desc: 'Approves the final assessment before case closure', color: 'text-neon-green', bg: 'bg-neon-green/10', border: 'border-neon-green/30' },
]

// ── Features ─────────────────────────────────────────────────────────────────
const FEATURES = [
  {
    icon: Brain,
    title: 'Multi-Agent Orchestration',
    desc: '10 specialized AI agents coordinate autonomously through a LangGraph workflow — no human intervention required.',
    color: 'text-neon-blue',
    bg: 'bg-neon-blue/10',
    border: 'border-neon-blue/20',
  },
  {
    icon: Activity,
    title: 'Real-Time Investigation Engine',
    desc: 'Continuously evaluates evidence sufficiency and decides the next collection step — exactly like an expert analyst.',
    color: 'text-neon-cyan',
    bg: 'bg-neon-cyan/10',
    border: 'border-neon-cyan/20',
  },
  {
    icon: Network,
    title: 'Threat Correlation Graph',
    desc: 'Visually maps connections between alerts, evidence, assets, and CVEs to expose lateral movement and attack chains.',
    color: 'text-neon-purple',
    bg: 'bg-neon-purple/10',
    border: 'border-neon-purple/20',
  },
  {
    icon: Zap,
    title: 'Autonomous Response Actions',
    desc: 'Block IPs, quarantine hosts, disable accounts, escalate incidents — all with full reasoning and rollback support.',
    color: 'text-threat-high',
    bg: 'bg-threat-high/10',
    border: 'border-threat-high/20',
  },
  {
    icon: Globe,
    title: 'Threat Intelligence Layer',
    desc: 'MITRE ATT&CK, CVE database, live threat feeds, and similar-incident retrieval via ChromaDB vector search.',
    color: 'text-neon-green',
    bg: 'bg-neon-green/10',
    border: 'border-neon-green/20',
  },
  {
    icon: Lock,
    title: 'Enterprise-Grade Security',
    desc: 'JWT authentication, role-based access (Admin, SOC Lead, Analyst, Viewer), full audit trails and structured logs.',
    color: 'text-neon-blue',
    bg: 'bg-neon-blue/10',
    border: 'border-neon-blue/20',
  },
  {
    icon: RotateCcw,
    title: 'Reflection & Replanning',
    desc: 'After every response cycle, the Reflector identifies gaps. The Replanner triggers a new investigation if needed.',
    color: 'text-neon-cyan',
    bg: 'bg-neon-cyan/10',
    border: 'border-neon-cyan/20',
  },
  {
    icon: TrendingUp,
    title: 'Analytics & MTTR Metrics',
    desc: 'Track mean time to respond, investigation success rates, agent performance, and severity distributions.',
    color: 'text-neon-purple',
    bg: 'bg-neon-purple/10',
    border: 'border-neon-purple/20',
  },
]

// ── Stats ─────────────────────────────────────────────────────────────────────
const STATS = [
  { value: '10', label: 'Autonomous Agents', icon: Brain, color: 'text-neon-blue' },
  { value: '9', label: 'SOC Dashboard Views', icon: Activity, color: 'text-neon-cyan' },
  { value: '<2m', label: 'Avg Investigation Time', icon: Clock, color: 'text-neon-purple' },
  { value: '100%', label: 'Evidence-Backed Decisions', icon: CheckCircle2, color: 'text-neon-green' },
]

// ── Workflow steps ────────────────────────────────────────────────────────────
const WORKFLOW = [
  { step: '01', title: 'Alert Ingested', desc: 'Security alert arrives — classified by severity, type, and source.' },
  { step: '02', title: 'Investigation Planned', desc: 'Planner agent determines strategy and orders evidence collection.' },
  { step: '03', title: 'Evidence Collected', desc: 'Logs, packets, asset data, vulnerabilities gathered autonomously.' },
  { step: '04', title: 'Threat Assessed', desc: 'Correlator + Assessor determine attack success and confidence score.' },
  { step: '05', title: 'Response Executed', desc: 'Block, quarantine, escalate — with full reasoning and audit trail.' },
  { step: '06', title: 'Verified & Reflected', desc: 'Effectiveness confirmed. Reflector triggers replanning if gaps found.' },
]

// ── FAQ ───────────────────────────────────────────────────────────────────────
const FAQ = [
  {
    q: 'Does TrinetraAI replace human analysts?',
    a: 'No. It acts as a force multiplier — handling routine investigations autonomously so analysts can focus on complex cases that require human judgment.',
  },
  {
    q: 'What does "simulated environment" mean?',
    a: 'Response actions like IP blocks and account disables are executed against a sandbox environment. No production systems are touched until an analyst approves a verified action.',
  },
  {
    q: 'Which AI model powers the agents?',
    a: 'Agents use OpenAI GPT-4o by default. You can swap the model by setting OPENAI_MODEL in your .env file.',
  },
  {
    q: 'Can I add my own alert sources?',
    a: 'Yes. The Alert Ingestion API accepts JSON payloads. You can connect SIEMs, EDRs, or any webhook-capable tool.',
  },
  {
    q: 'Is there social login support?',
    a: 'Yes — Google, GitHub, and Facebook OAuth are built in. Add your provider credentials to .env and the buttons appear immediately.',
  },
]

// ── NAV ───────────────────────────────────────────────────────────────────────
function Navbar() {
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 border-b border-cyber-border/50 bg-cyber-bg/80 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-neon-blue/10 border border-neon-blue/30 flex items-center justify-center">
            <Shield className="w-4 h-4 text-neon-blue" />
          </div>
          <span className="font-bold text-white text-lg">TrinetraAI</span>
          <span className="hidden sm:inline text-xs text-slate-600 border border-cyber-border/50 rounded px-1.5 py-0.5 ml-1">SOC</span>
        </div>

        <div className="hidden md:flex items-center gap-6 text-sm text-slate-400">
          <a href="#features" className="hover:text-white transition-colors">Features</a>
          <a href="#agents" className="hover:text-white transition-colors">Agents</a>
          <a href="#workflow" className="hover:text-white transition-colors">How it works</a>
          <a href="#faq" className="hover:text-white transition-colors">FAQ</a>
        </div>

        <div className="flex items-center gap-3">
          <Link
            to="/login"
            className="text-sm text-slate-400 hover:text-white transition-colors px-3 py-1.5"
          >
            Sign in
          </Link>
          <Link
            to="/signup"
            className="btn-primary rounded-lg px-4 py-2 text-sm font-semibold"
          >
            Get started
          </Link>
        </div>
      </div>
    </nav>
  )
}

// ── HERO ─────────────────────────────────────────────────────────────────────
function Hero() {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden pt-16">
      {/* Background layers */}
      <div className="absolute inset-0 bg-hero-gradient" />
      <div className="absolute inset-0 cyber-grid-bg opacity-40" />
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[800px] h-[500px] bg-neon-blue/5 rounded-full blur-3xl" />
      <div className="absolute top-1/3 left-1/4 w-72 h-72 bg-neon-purple/8 rounded-full blur-3xl" />
      <div className="absolute top-1/3 right-1/4 w-72 h-72 bg-neon-cyan/8 rounded-full blur-3xl" />

      {/* Animated pulse rings */}
      {[1, 2, 3].map((i) => (
        <motion.div
          key={i}
          className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 rounded-full border border-neon-blue/10"
          style={{ width: i * 300 + 200, height: i * 300 + 200 }}
          animate={{ opacity: [0.3, 0.05, 0.3], scale: [1, 1.05, 1] }}
          transition={{ duration: 4 + i, repeat: Infinity, ease: 'easeInOut', delay: i * 0.8 }}
        />
      ))}

      <div className="relative max-w-5xl mx-auto px-6 text-center">
        {/* Badge */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-neon-blue/30 bg-neon-blue/10 text-neon-blue text-xs font-medium mb-6"
        >
          <span className="w-1.5 h-1.5 rounded-full bg-neon-green animate-pulse" />
          Autonomous AI · 10 Specialized Agents · Real-Time SOC
        </motion.div>

        {/* Headline */}
        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.1 }}
          className="text-5xl sm:text-6xl lg:text-7xl font-black leading-tight tracking-tight"
        >
          <span className="text-white">The SOC that</span>
          <br />
          <span className="gradient-text">investigates itself.</span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.2 }}
          className="mt-6 text-lg sm:text-xl text-slate-400 max-w-2xl mx-auto leading-relaxed"
        >
          TrinetraAI autonomously investigates security alerts, collects evidence,
          correlates threats, executes response actions, and verifies effectiveness —
          all without waiting for a human to click.
        </motion.p>

        {/* CTA */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.35 }}
          className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4"
        >
          <Link
            to="/signup"
            className="btn-primary rounded-xl px-7 py-3.5 text-base font-semibold flex items-center gap-2 group"
          >
            Start free
            <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </Link>
          <Link
            to="/login"
            className="flex items-center gap-2 px-7 py-3.5 text-base font-medium text-slate-300 border border-cyber-border rounded-xl hover:border-neon-blue/40 hover:text-white transition-all"
          >
            Try demo
          </Link>
        </motion.div>

        {/* Social proof */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.7, delay: 0.55 }}
          className="mt-10 flex items-center justify-center gap-6 text-xs text-slate-600"
        >
          <span className="flex items-center gap-1.5"><CheckCircle2 className="w-3.5 h-3.5 text-neon-green" /> No credit card required</span>
          <span className="flex items-center gap-1.5"><CheckCircle2 className="w-3.5 h-3.5 text-neon-green" /> Demo data pre-loaded</span>
          <span className="flex items-center gap-1.5"><CheckCircle2 className="w-3.5 h-3.5 text-neon-green" /> Open source core</span>
        </motion.div>

        {/* Dashboard preview mockup */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.9, delay: 0.5 }}
          className="mt-16 relative mx-auto max-w-4xl"
        >
          <div className="rounded-2xl border border-cyber-border overflow-hidden shadow-2xl shadow-black/50">
            {/* Fake browser chrome */}
            <div className="bg-cyber-card border-b border-cyber-border px-4 py-3 flex items-center gap-2">
              <div className="flex gap-1.5">
                <div className="w-3 h-3 rounded-full bg-threat-critical/60" />
                <div className="w-3 h-3 rounded-full bg-threat-high/60" />
                <div className="w-3 h-3 rounded-full bg-neon-green/60" />
              </div>
              <div className="flex-1 mx-4 bg-cyber-surface rounded px-3 py-1 text-xs text-slate-500">
                https://trinetraai.io/dashboard
              </div>
            </div>
            {/* Fake dashboard content */}
            <div className="bg-cyber-bg p-6 min-h-[260px]">
              <div className="grid grid-cols-4 gap-3 mb-4">
                {['14 Active Alerts', '7 Investigating', '3 Critical', '98% Success'].map((label, i) => (
                  <div key={label} className="glass rounded-lg p-3 border border-cyber-border/50">
                    <p className="text-[10px] text-slate-500 uppercase tracking-wider">
                      {label.split(' ').slice(1).join(' ')}
                    </p>
                    <p className={`text-xl font-bold mt-1 ${['text-neon-blue', 'text-neon-cyan', 'text-threat-critical', 'text-neon-green'][i]}`}>
                      {label.split(' ')[0]}
                    </p>
                  </div>
                ))}
              </div>
              <div className="grid grid-cols-3 gap-3">
                <div className="col-span-2 glass rounded-lg p-3 border border-cyber-border/50 h-28">
                  <p className="text-xs text-slate-500 mb-2">Investigation Activity</p>
                  <div className="flex items-end gap-1 h-16">
                    {[40, 65, 45, 80, 55, 90, 70, 85, 60, 95, 75, 88].map((h, i) => (
                      <motion.div
                        key={i}
                        className="flex-1 bg-neon-blue/30 rounded-sm"
                        style={{ height: `${h}%` }}
                        initial={{ scaleY: 0 }}
                        animate={{ scaleY: 1 }}
                        transition={{ delay: 0.8 + i * 0.05, duration: 0.4 }}
                      />
                    ))}
                  </div>
                </div>
                <div className="glass rounded-lg p-3 border border-cyber-border/50 h-28">
                  <p className="text-xs text-slate-500 mb-2">Agent Status</p>
                  {['Planner', 'Collector', 'Assessor'].map((a, i) => (
                    <div key={a} className="flex items-center justify-between mt-2">
                      <span className="text-xs text-slate-400">{a}</span>
                      <span className="w-2 h-2 rounded-full bg-neon-green animate-pulse" />
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
          {/* Glow under the card */}
          <div className="absolute -bottom-6 left-1/2 -translate-x-1/2 w-3/4 h-12 bg-neon-blue/20 blur-2xl rounded-full" />
        </motion.div>
      </div>
    </section>
  )
}

// ── STATS ─────────────────────────────────────────────────────────────────────
function StatsSection() {
  return (
    <section className="py-16 border-y border-cyber-border/50 bg-cyber-card/30">
      <div className="max-w-5xl mx-auto px-6 grid grid-cols-2 md:grid-cols-4 gap-8">
        {STATS.map((s, i) => (
          <InViewSection key={s.label} delay={i * 0.1} className="text-center">
            <s.icon className={`w-7 h-7 mx-auto mb-2 ${s.color}`} />
            <p className={`text-4xl font-black ${s.color}`}>{s.value}</p>
            <p className="text-sm text-slate-500 mt-1">{s.label}</p>
          </InViewSection>
        ))}
      </div>
    </section>
  )
}

// ── FEATURES ──────────────────────────────────────────────────────────────────
function FeaturesSection() {
  return (
    <section id="features" className="py-24 max-w-7xl mx-auto px-6">
      <InViewSection className="text-center mb-14">
        <span className="text-xs font-semibold uppercase tracking-widest text-neon-blue">Platform capabilities</span>
        <h2 className="text-4xl font-black text-white mt-3">Everything a SOC needs, automated.</h2>
        <p className="text-slate-500 mt-4 max-w-xl mx-auto">
          From ingestion to verified response — TrinetraAI handles the entire investigation lifecycle autonomously.
        </p>
      </InViewSection>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-5">
        {FEATURES.map((f, i) => (
          <InViewSection key={f.title} delay={i * 0.07}>
            <div className={`glass rounded-xl p-5 border ${f.border} h-full glass-hover`}>
              <div className={`w-10 h-10 rounded-lg ${f.bg} border ${f.border} flex items-center justify-center mb-4`}>
                <f.icon className={`w-5 h-5 ${f.color}`} />
              </div>
              <h3 className="text-sm font-semibold text-white mb-2">{f.title}</h3>
              <p className="text-xs text-slate-500 leading-relaxed">{f.desc}</p>
            </div>
          </InViewSection>
        ))}
      </div>
    </section>
  )
}

// ── AGENTS ────────────────────────────────────────────────────────────────────
function AgentsSection() {
  return (
    <section id="agents" className="py-24 bg-cyber-card/20 border-y border-cyber-border/50">
      <div className="max-w-7xl mx-auto px-6">
        <InViewSection className="text-center mb-14">
          <span className="text-xs font-semibold uppercase tracking-widest text-neon-purple">Multi-agent system</span>
          <h2 className="text-4xl font-black text-white mt-3">10 agents. One mission.</h2>
          <p className="text-slate-500 mt-4 max-w-xl mx-auto">
            Each agent is a specialist. Together they form a fully autonomous investigation and response team
            orchestrated by LangGraph.
          </p>
        </InViewSection>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          {AGENTS.map((agent, i) => (
            <InViewSection key={agent.name} delay={i * 0.06}>
              <motion.div
                whileHover={{ y: -4 }}
                className={`glass rounded-xl p-4 border ${agent.border} h-full`}
              >
                <div className={`w-9 h-9 rounded-lg ${agent.bg} border ${agent.border} flex items-center justify-center mb-3`}>
                  <agent.icon className={`w-4 h-4 ${agent.color}`} />
                </div>
                <p className={`text-xs font-semibold uppercase tracking-wider ${agent.color} mb-1`}>{agent.name}</p>
                <p className="text-xs text-slate-500 leading-relaxed">{agent.desc}</p>
              </motion.div>
            </InViewSection>
          ))}
        </div>

        {/* Pipeline flow diagram */}
        <InViewSection delay={0.3} className="mt-12">
          <div className="glass rounded-xl p-6 border border-cyber-border">
            <p className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-5 text-center">
              Autonomous investigation lifecycle
            </p>
            <div className="flex flex-wrap items-center justify-center gap-2 text-xs">
              {['Alert', 'Investigation', 'Evidence', 'Analysis', 'Response', 'Verification', 'Reflection', 'Replanning'].map(
                (stage, i, arr) => (
                  <div key={stage} className="flex items-center gap-2">
                    <span className="px-3 py-1.5 rounded-lg bg-neon-blue/10 border border-neon-blue/20 text-neon-blue font-medium">
                      {stage}
                    </span>
                    {i < arr.length - 1 && (
                      <ChevronRight className="w-3 h-3 text-slate-600 flex-shrink-0" />
                    )}
                  </div>
                )
              )}
            </div>
          </div>
        </InViewSection>
      </div>
    </section>
  )
}

// ── WORKFLOW ──────────────────────────────────────────────────────────────────
function WorkflowSection() {
  return (
    <section id="workflow" className="py-24 max-w-7xl mx-auto px-6">
      <InViewSection className="text-center mb-14">
        <span className="text-xs font-semibold uppercase tracking-widest text-neon-cyan">How it works</span>
        <h2 className="text-4xl font-black text-white mt-3">From alert to verified response in minutes.</h2>
        <p className="text-slate-500 mt-4 max-w-xl mx-auto">
          Six stages. Fully autonomous. Every step logged and auditable.
        </p>
      </InViewSection>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {WORKFLOW.map((w, i) => (
          <InViewSection key={w.step} delay={i * 0.1}>
            <div className="glass rounded-xl p-6 border border-cyber-border glass-hover h-full relative overflow-hidden">
              <span className="absolute top-4 right-4 text-4xl font-black text-cyber-border/60 select-none">
                {w.step}
              </span>
              <h3 className="text-base font-semibold text-white mb-2 pr-10">{w.title}</h3>
              <p className="text-sm text-slate-500 leading-relaxed">{w.desc}</p>
              <div className="mt-4 h-0.5 bg-gradient-to-r from-neon-blue/40 to-transparent rounded-full" />
            </div>
          </InViewSection>
        ))}
      </div>
    </section>
  )
}

// ── FAQ ───────────────────────────────────────────────────────────────────────
function FaqSection() {
  return (
    <section id="faq" className="py-24 bg-cyber-card/20 border-t border-cyber-border/50">
      <div className="max-w-3xl mx-auto px-6">
        <InViewSection className="text-center mb-12">
          <span className="text-xs font-semibold uppercase tracking-widest text-neon-purple">FAQ</span>
          <h2 className="text-4xl font-black text-white mt-3">Common questions</h2>
        </InViewSection>

        <div className="space-y-4">
          {FAQ.map((item, i) => (
            <InViewSection key={i} delay={i * 0.08}>
              <div className="glass rounded-xl p-5 border border-cyber-border">
                <p className="text-sm font-semibold text-white mb-2">{item.q}</p>
                <p className="text-sm text-slate-500 leading-relaxed">{item.a}</p>
              </div>
            </InViewSection>
          ))}
        </div>
      </div>
    </section>
  )
}

// ── CTA ───────────────────────────────────────────────────────────────────────
function CtaSection() {
  return (
    <section className="py-24 relative overflow-hidden">
      <div className="absolute inset-0 bg-hero-gradient" />
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[300px] bg-neon-blue/8 rounded-full blur-3xl" />

      <div className="relative max-w-3xl mx-auto px-6 text-center">
        <InViewSection>
          <motion.div
            className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-neon-blue/10 border border-neon-blue/30 mb-6"
          >
            <Shield className="w-8 h-8 text-neon-blue" />
          </motion.div>
          <h2 className="text-4xl font-black text-white">
            Ready to automate your SOC?
          </h2>
          <p className="text-slate-400 mt-4 text-lg max-w-xl mx-auto">
            Start investigating threats autonomously in minutes. No setup required — demo data is pre-loaded.
          </p>
          <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              to="/signup"
              className="btn-primary rounded-xl px-8 py-3.5 text-base font-semibold flex items-center gap-2 group"
            >
              Create free account
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </Link>
            <Link
              to="/login"
              className="text-slate-400 hover:text-white transition-colors text-base font-medium"
            >
              Sign in with demo →
            </Link>
          </div>
        </InViewSection>
      </div>
    </section>
  )
}

// ── FOOTER ────────────────────────────────────────────────────────────────────
function Footer() {
  return (
    <footer className="border-t border-cyber-border/50 bg-cyber-bg">
      <div className="max-w-7xl mx-auto px-6 py-10 flex flex-col md:flex-row items-center justify-between gap-6">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-neon-blue/10 border border-neon-blue/30 flex items-center justify-center">
            <Shield className="w-3.5 h-3.5 text-neon-blue" />
          </div>
          <span className="font-bold text-white">TrinetraAI</span>
          <span className="text-slate-600 text-sm ml-2">· Autonomous SOC Platform</span>
        </div>

        <div className="flex items-center gap-4 text-sm text-slate-600">
          <Link to="/login" className="hover:text-slate-300 transition-colors">Platform</Link>
          <Link to="/signup" className="hover:text-slate-300 transition-colors">Sign up</Link>
          <a href="#features" className="hover:text-slate-300 transition-colors">Features</a>
          <a href="#faq" className="hover:text-slate-300 transition-colors">FAQ</a>
        </div>

        <p className="text-xs text-slate-700">
          © {new Date().getFullYear()} TrinetraAI. Built with React + FastAPI + LangGraph.
        </p>
      </div>
    </footer>
  )
}

// ── Main export ───────────────────────────────────────────────────────────────
export default function LandingPage() {
  return (
    <div className="bg-cyber-bg text-slate-100 font-sans antialiased">
      <Navbar />
      <Hero />
      <StatsSection />
      <FeaturesSection />
      <AgentsSection />
      <WorkflowSection />
      <FaqSection />
      <CtaSection />
      <Footer />
    </div>
  )
}
