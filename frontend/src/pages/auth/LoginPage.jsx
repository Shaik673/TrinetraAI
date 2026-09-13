import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Shield, Mail, Lock, Eye, EyeOff, Loader2, AlertTriangle } from 'lucide-react'
import { useAuthStore } from '../../store/authStore'
import { api, getApiErrorMessage } from '../../api/client'
import toast from 'react-hot-toast'

// Social provider icons as inline SVG
function GoogleIcon() {
  return (
    <svg viewBox="0 0 24 24" className="w-4 h-4" fill="none">
      <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
      <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
      <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z" fill="#FBBC05"/>
      <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
    </svg>
  )
}

function GithubIcon() {
  return (
    <svg viewBox="0 0 24 24" className="w-4 h-4" fill="currentColor">
      <path d="M12 2C6.477 2 2 6.477 2 12c0 4.418 2.865 8.166 6.839 9.489.5.092.682-.217.682-.482 0-.237-.008-.866-.013-1.7-2.782.604-3.369-1.341-3.369-1.341-.454-1.154-1.11-1.462-1.11-1.462-.908-.62.069-.608.069-.608 1.003.07 1.531 1.03 1.531 1.03.892 1.529 2.341 1.087 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.11-4.555-4.943 0-1.091.39-1.984 1.029-2.683-.103-.253-.446-1.27.098-2.647 0 0 .84-.269 2.75 1.025A9.578 9.578 0 0 1 12 6.836c.85.004 1.705.114 2.504.337 1.909-1.294 2.747-1.025 2.747-1.025.546 1.377.202 2.394.1 2.647.64.699 1.028 1.592 1.028 2.683 0 3.842-2.339 4.687-4.566 4.935.359.309.678.919.678 1.852 0 1.336-.012 2.415-.012 2.743 0 .267.18.578.688.48C19.138 20.163 22 16.418 22 12c0-5.523-4.477-10-10-10z"/>
    </svg>
  )
}

function FacebookIcon() {
  return (
    <svg viewBox="0 0 24 24" className="w-4 h-4" fill="#1877F2">
      <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
    </svg>
  )
}

function SocialButton({ icon: Icon, label, provider, onClick, disabled }) {
  return (
    <button
      type="button"
      onClick={() => onClick(provider)}
      disabled={disabled}
      className="flex-1 flex items-center justify-center gap-2 py-2.5 px-3 rounded-lg border border-cyber-border bg-cyber-surface/50 text-slate-300 text-sm font-medium hover:bg-cyber-card hover:border-slate-600 transition-all duration-200 disabled:opacity-40 disabled:cursor-not-allowed"
    >
      <Icon />
      <span className="hidden sm:inline">{label}</span>
    </button>
  )
}

export default function LoginPage() {
  const [form, setForm] = useState({ email: '', password: '' })
  const [showPw, setShowPw] = useState(false)
  const [loading, setLoading] = useState(false)
  const [socialLoading, setSocialLoading] = useState(null)
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

  const handleSocialLogin = (provider) => {
    setSocialLoading(provider)
    toast.loading(`Redirecting to ${provider}…`, { id: 'oauth' })
    api.initiateOAuth(provider)
  }

  const demoLogin = async () => {
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
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-neon-cyan/3 rounded-full blur-3xl pointer-events-none" />

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
            className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-neon-blue/10 border border-neon-blue/30 mb-4 relative"
          >
            <Shield className="w-8 h-8 text-neon-blue" />
            <span className="absolute -top-1 -right-1 w-3 h-3 bg-neon-green rounded-full animate-pulse" />
          </motion.div>
          <h1 className="text-2xl font-bold gradient-text">TrinetraAI</h1>
          <p className="text-slate-500 text-sm mt-1">Autonomous SOC Platform</p>
        </div>

        {/* Card */}
        <div className="glass-strong rounded-2xl p-8 border border-cyber-border">
          <h2 className="text-lg font-semibold text-white mb-1">Sign In</h2>
          <p className="text-slate-500 text-sm mb-6">Access your security operations center</p>

          {/* Social Login Buttons */}
          <div className="mb-5">
            <p className="text-xs text-slate-500 uppercase tracking-wider mb-3">Continue with</p>
            <div className="flex gap-2">
              <SocialButton
                icon={GoogleIcon}
                label="Google"
                provider="google"
                onClick={handleSocialLogin}
                disabled={!!socialLoading || loading}
              />
              <SocialButton
                icon={GithubIcon}
                label="GitHub"
                provider="github"
                onClick={handleSocialLogin}
                disabled={!!socialLoading || loading}
              />
              <SocialButton
                icon={FacebookIcon}
                label="Facebook"
                provider="facebook"
                onClick={handleSocialLogin}
                disabled={!!socialLoading || loading}
              />
            </div>
          </div>

          <div className="relative my-5">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-cyber-border" />
            </div>
            <div className="relative flex justify-center text-xs text-slate-600">
              <span className="px-2 bg-transparent">or sign in with email</span>
            </div>
          </div>

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
                  id="login-email"
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
                  id="login-password"
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
              id="login-submit"
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
            id="demo-login"
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
