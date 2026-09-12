import { Link } from 'react-router-dom'

export default function PlaceholderPage({ title = 'TrinetraAI' }) {
  return <section className="glass rounded-xl border border-cyber-border p-8 text-slate-200"><h1 className="text-2xl font-bold">{title}</h1><p className="text-slate-400 mt-2">This workspace view is ready for its API integration.</p><Link to="/dashboard" className="inline-block mt-5 text-neon-cyan">Return to dashboard</Link></section>
}
