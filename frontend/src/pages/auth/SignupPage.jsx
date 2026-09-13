import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Loader2, Mail, Shield, User, Lock, Eye, EyeOff, AlertTriangle, CheckCircle2 } from 'lucide-react'
import toast from 'react-hot-toast'
import { api, getApiErrorMessage } from '../../api/client'
import { useAuthStore } from '../../store/authStore'

// ── Social provider icons ──────────────────────────────────────────────────
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

// ── Field component ────────────────────────────────────────────────────────
function Field({ id, label, type = 'text', value, onChange, icon: Icon, placeholder, required, minLength, extra }) {
  const [show, setShow] = useState(false)
  const isPassword = type === 'password'
  return (
    <div>
      <label htmlFor={id} className="block text-xs font-medium text-slate-400 mb-1.5 uppercase tracking-wider">
        {label}
      </label>
      <div className="relative">
        <Icon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
        <input
          id={id}
          type={isPassword && show ? 'text' : type}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          required={required}
          minLength={minLength}
          className="w-full cyber-input rounded-lg pl-9 pr-10 py-2.5 text-sm"
        />
        {isPassword && (
          <button
            type="button"
            onClick={() => setShow((s) => !s)}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300"
          >
            {show ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
          </button>
        )}
      </div>
      {extra && <p className="text-xs text-slate-600 mt-1">{extra}</p>}
    </div>
  )
}

// ── Password strength indicator ────────────────────────────────────────────
function PasswordStrength({ password }) {
  const checks = [
    { label: '8+ characters', pass: password.length >= 8 },
    { label: 'Uppercase', pass: /[A-Z]/.test(password) },
    { label: 'Number', pass: /\d/.test(password) },
    { label: 'Special char', pass: /[^a-zA-Z0-9]/.test(password) },
  ]
  const score = checks.filter((c) => c.pass).length
  const colors = ['bg-slate-700', 'bg-threat-critical', 'bg-threat-high', 'bg-neon-blue', 'bg-neon-green']
  if (!password) return null
  return (
    <div className="mt-2">
      <div className="flex gap-1 mb-1.5">
        {[0, 1, 2, 3].map((i) => (
          <div
            key={i}
            className={`h-1 flex-1 rounded-full transition-all duration-300 ${i < score ? colors[score] : 'bg-cyber-border'}`}
          />
        ))}
      </div>
      <div className="flex flex-wrap gap-x-3 gap-y-1">
        {checks.map((c) => (
          <span key={c.label} className={`flex items-center gap-1 text-xs ${c.pass ? 'text-neon-green' : 'text-slate-600'}`}>
            <CheckCircle2 className="w-3 h-3" />
            {c.label}
          </span>
        ))}
      </div>
    </div>
  )
}

// ── Main component ─────────────────────────────────────────────────────────
export default function SignupPage() {
  const navigate = useNavigate()
  const { login } = useAuthStore()
  const [form, setForm] = useState({ full_name: '', username: '', email: '', password: '' })
  const [loading, setLoading] = useState(false)
  const [socialLoading, setSocialLoading] = useState(null)
  const [error, setError] = useState('')

  const update = (name) => (e) => setForm({ ...form, [name]: e.target.value })

  const handleSocialLogin = (provider) => {
    setSocialLoading(provider)
    toast.loading(`Redirecting to ${provider}…`, { id: 'oauth' })
    api.initiateOAuth(provider)
  }

  const submit = async (e) => {
    e.preventDefault()
    if (form.password.length < 8) {
      setError('Password must be at least 8 characters.')
      return
    }
    setError('')
    setLoading(true)
    try {
      await api.register(form)
      const { data } = await api.login({ email: form.email, password: form.password })
      login(data)
      toast.success('Account created — welcome to TrinetraAI!')
      navigate('/dashboard')
    } catch (err) {
      setError(getApiErrorMessage(err, 'Could not create the account'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-hero-gradient cyber-grid-bg flex items-center justify-center p-4 relative overflow-hidden">
      <div className="absolute top-1/4 right-1/4 w-96 h-96 bg-neon-purple/5 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-1/4 left-1/4 w-96 h-96 bg-neon-blue/5 rounded-full blur-3xl pointer-events-none" />

      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md"
      >
        {/* Logo */}
        <div className="text-center mb-7">
          <motion.div
            initial={{ scale: 0.8 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.1, type: 'spring', stiffness: 200 }}
            className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-neon-blue/10 border border-neon-blue/30 mb-4"
          >
            <Shield className="w-7 h-7 text-neon-blue" />
          </motion.div>
          <h1 className="text-2xl font-bold gradient-text">Create your account</h1>
          <p className="text-sm text-slate-500 mt-1">Access the TrinetraAI security operations workspace</p>
        </div>

        <div className="glass-strong rounded-2xl p-7 border border-cyber-border">
          {/* Social signup buttons */}
          <p className="text-xs text-slate-500 uppercase tracking-wider mb-3">Sign up with</p>
          <div className="flex gap-2 mb-5">
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

          <div className="relative my-5">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-cyber-border" />
            </div>
            <div className="relative flex justify-center text-xs text-slate-600">
              <span className="px-2 bg-transparent">or register with email</span>
            </div>
          </div>

          {error && (
            <motion.div
              initial={{ opacity: 0, y: -5 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex items-center gap-2 p-3 rounded-lg border border-threat-critical/30 bg-threat-critical/10 text-threat-critical text-sm mb-4"
            >
              <AlertTriangle className="w-4 h-4 flex-shrink-0" />
              {error}
            </motion.div>
          )}

          <form onSubmit={submit} className="space-y-4">
            <Field
              id="signup-fullname"
              label="Full name"
              value={form.full_name}
              onChange={update('full_name')}
              icon={User}
              placeholder="Jane Analyst"
            />
            <Field
              id="signup-username"
              label="Username"
              value={form.username}
              onChange={update('username')}
              icon={User}
              placeholder="j_analyst"
              required
              extra="Used to identify you across investigations"
            />
            <Field
              id="signup-email"
              label="Email"
              type="email"
              value={form.email}
              onChange={update('email')}
              icon={Mail}
              placeholder="analyst@company.com"
              required
            />
            <div>
              <Field
                id="signup-password"
                label="Password"
                type="password"
                value={form.password}
                onChange={update('password')}
                icon={Lock}
                placeholder="Min. 8 characters"
                required
                minLength={8}
              />
              <PasswordStrength password={form.password} />
            </div>

            <button
              id="signup-submit"
              type="submit"
              disabled={loading}
              className="btn-primary w-full rounded-lg py-2.5 flex justify-center items-center gap-2 text-sm font-semibold mt-2"
            >
              {loading && <Loader2 className="w-4 h-4 animate-spin" />}
              {loading ? 'Creating account…' : 'Create account'}
            </button>
          </form>

          <p className="mt-5 text-center text-sm text-slate-500">
            Already registered?{' '}
            <Link to="/login" className="text-neon-blue hover:text-neon-cyan font-medium transition-colors">
              Sign in
            </Link>
          </p>
        </div>
      </motion.div>
    </div>
  )
}
