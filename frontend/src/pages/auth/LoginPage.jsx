import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Shield, Mail, Lock, Eye, EyeOff, Loader2, AlertTriangle } from 'lucide-react'
import { useAuthStore } from '../../store/authStore'
import { api, getApiErrorMessage } from '../../api/client'
import toast from 'react-hot-toast'

export default function LoginPage() {
  const [form, setForm] = useState({ email: '', password: '' })
  const [showPw, setShowPw] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const { login } = useAuthStore()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const { data } = await api.login(form)
      login(data)
      toast.success('Welcome to TrinetraAI')
      navigate('/dashboard')
    } catch (err) {
      setError(getApiErrorMessage(err, 'Authentication failed'))
    } finally {
      setLoading(false)
    }
  }

  const demoLogin = async () => {
    setForm({ email: 'demo@trinetraai.io', password: 'Demo@1234' })
    setError('')
    setLoading(true)
    try {
      const { data } = await api.login({ email: 'demo@trinetraai.io', password: 'Demo@1234' })
      login(data)
      toast.success('Demo access granted')
      navigate('/dashboard')
    } catch {
      // If demo doesn't exist, register then login
      try {
        await api.register({
          email: 'demo@trinetraai.io',
          username: 'demo_analyst',
          password: 'Demo@1234',
          full_name: 'Demo Analyst',
          role: 'analyst',
        })
        const { data } = await api.login({ email: 'demo@trinetraai.io', password: 'Demo@1234' })
        login(data)
        navigate('/dashboard')
      } catch {
        setError('Demo login unavailable. Ensure the backend is running.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-hero-gradient cyber-grid-bg flex items-center justify-center p-4 relative overflow-hidden">
      {/* Ambient effects */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-neon-blue/5 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-neon-purple/5 rounded-full blur-3xl pointer-events-none" />

      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md"
      >
        {/* Logo */}
        <div className="text-center mb-8">
          <motion.div
            initial={{ scale: 0.8 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.1, type: 'spring', stiffness: 200 }}
            className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-neon-blue/10 border border-neon-blue/30 mb-4"
          >
            <Shield className="w-8 h-8 text-neon-blue" />
          </motion.div>
          <h1 className="text-2xl font-bold gradient-text">TrinetraAI</h1>
          <p className="text-slate-500 text-sm mt-1">Autonomous SOC Platform</p>
        </div>

        {/* Card */}
        <div className="glass-strong rounded-2xl p-8 border border-cyber-border">
          <h2 className="text-lg font-semibold text-white mb-1">Sign In</h2>
          <p className="text-slate-500 text-sm mb-6">Access your security operations center</p>

          {error && (
            <motion.div
              initial={{ opacity: 0, y: -5 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex items-center gap-2 p-3 rounded-lg bg-threat-critical/10 border border-threat-critical/30 text-threat-critical text-sm mb-4"
            >
              <AlertTriangle className="w-4 h-4 flex-shrink-0" />
              {error}
            </motion.div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1.5 uppercase tracking-wider">Email</label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                <input
                  type="email"
                  value={form.email}
                  onChange={(e) => setForm({ ...form, email: e.target.value })}
                  placeholder="analyst@company.com"
                  required
                  className="w-full cyber-input rounded-lg pl-9 pr-4 py-2.5 text-sm"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1.5 uppercase tracking-wider">Password</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                <input
                  type={showPw ? 'text' : 'password'}
                  value={form.password}
                  onChange={(e) => setForm({ ...form, password: e.target.value })}
                  placeholder="••••••••"
                  required
                  className="w-full cyber-input rounded-lg pl-9 pr-10 py-2.5 text-sm"
                />
                <button
                  type="button"
                  onClick={() => setShowPw(!showPw)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300"
                >
                  {showPw ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <div className="flex justify-end">
              <Link to="/forgot-password" className="text-xs text-neon-blue hover:text-neon-cyan transition-colors">
                Forgot password?
              </Link>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full btn-primary rounded-lg py-2.5 text-sm font-semibold flex items-center justify-center gap-2 disabled:opacity-50"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Shield className="w-4 h-4" />}
              {loading ? 'Authenticating...' : 'Sign In'}
            </button>
          </form>

          <div className="relative my-5">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-cyber-border" />
            </div>
            <div className="relative flex justify-center text-xs text-slate-600">
              <span className="px-2 bg-transparent">or</span>
            </div>
          </div>

          <button
            onClick={demoLogin}
            disabled={loading}
            className="w-full py-2.5 text-sm font-medium text-neon-cyan border border-neon-cyan/30 rounded-lg bg-neon-cyan/5 hover:bg-neon-cyan/10 transition-all disabled:opacity-50"
          >
            Try Demo Access
          </button>

          <p className="text-center text-sm text-slate-500 mt-6">
            No account?{' '}
            <Link to="/signup" className="text-neon-blue hover:text-neon-cyan font-medium transition-colors">
              Create one
            </Link>
          </p>
        </div>
      </motion.div>
    </div>
  )
}
