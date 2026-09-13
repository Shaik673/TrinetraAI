import { useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Shield, Lock, Eye, EyeOff, Loader2, AlertTriangle, CheckCircle2 } from 'lucide-react'
import { api, getApiErrorMessage } from '../../api/client'
import toast from 'react-hot-toast'

/**
 * ResetPasswordPage — /reset-password?token=...
 *
 * Provides a form for the user to set a new password using a reset token
 * that was delivered to their email. On success, redirects to /login.
 */
export default function ResetPasswordPage() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const token = searchParams.get('token') || ''

  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [showPw, setShowPw] = useState(false)
  const [showConfirm, setShowConfirm] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [done, setDone] = useState(false)

  const strength = (() => {
    const checks = [
      password.length >= 8,
      /[A-Z]/.test(password),
      /\d/.test(password),
      /[^a-zA-Z0-9]/.test(password),
    ]
    return checks.filter(Boolean).length
  })()

  const strengthColors = ['bg-slate-700', 'bg-threat-critical', 'bg-threat-high', 'bg-neon-blue', 'bg-neon-green']

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    if (password.length < 8) {
      setError('Password must be at least 8 characters.')
      return
    }
    if (password !== confirm) {
      setError('Passwords do not match.')
      return
    }
    if (!token) {
      setError('Reset token is missing. Please use the link from your email.')
      return
    }

    setLoading(true)
    try {
      // POST /auth/reset-password with token + new password
      await api.apiClient.post('/auth/reset-password', { token, new_password: password })
      setDone(true)
      toast.success('Password updated successfully!')
      setTimeout(() => navigate('/login', { replace: true }), 2500)
    } catch (err) {
      setError(getApiErrorMessage(err, 'Could not reset password. The link may have expired.'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-hero-gradient cyber-grid-bg flex items-center justify-center p-4 relative overflow-hidden">
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

        <div className="glass-strong rounded-2xl p-8 border border-cyber-border">
          {done ? (
            /* ── Success state ── */
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="text-center py-4"
            >
              <div className="flex justify-center mb-5">
                <div className="w-14 h-14 rounded-2xl bg-neon-green/10 border border-neon-green/30 flex items-center justify-center">
                  <CheckCircle2 className="w-7 h-7 text-neon-green" />
                </div>
              </div>
              <h2 className="text-lg font-semibold text-white">Password Updated!</h2>
              <p className="text-sm text-slate-400 mt-2">
                Your password has been reset. Redirecting to sign in…
              </p>
              <Link
                to="/login"
                className="inline-block mt-5 btn-primary rounded-lg px-6 py-2.5 text-sm font-semibold"
              >
                Go to Sign In
              </Link>
            </motion.div>
          ) : (
            /* ── Form state ── */
            <>
              <h2 className="text-lg font-semibold text-white mb-1">Set New Password</h2>
              <p className="text-slate-500 text-sm mb-6">
                Enter a strong new password for your account.
              </p>

              {!token && (
                <div className="flex items-start gap-2 p-3 rounded-lg bg-threat-high/10 border border-threat-high/30 text-threat-high text-sm mb-4">
                  <AlertTriangle className="w-4 h-4 flex-shrink-0 mt-0.5" />
                  <span>
                    No reset token found in this URL. Please use the link sent to your email, or{' '}
                    <Link to="/forgot-password" className="underline">request a new one</Link>.
                  </span>
                </div>
              )}

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
                {/* New password */}
                <div>
                  <label htmlFor="new-password" className="block text-xs font-medium text-slate-400 mb-1.5 uppercase tracking-wider">
                    New Password
                  </label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                    <input
                      id="new-password"
                      type={showPw ? 'text' : 'password'}
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="Min. 8 characters"
                      required
                      minLength={8}
                      className="w-full cyber-input rounded-lg pl-9 pr-10 py-2.5 text-sm"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPw((s) => !s)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300"
                    >
                      {showPw ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  </div>
                  {/* Strength bar */}
                  {password && (
                    <div className="mt-2 flex gap-1">
                      {[0, 1, 2, 3].map((i) => (
                        <div
                          key={i}
                          className={`h-1 flex-1 rounded-full transition-all duration-300 ${
                            i < strength ? strengthColors[strength] : 'bg-cyber-border'
                          }`}
                        />
                      ))}
                    </div>
                  )}
                </div>

                {/* Confirm password */}
                <div>
                  <label htmlFor="confirm-password" className="block text-xs font-medium text-slate-400 mb-1.5 uppercase tracking-wider">
                    Confirm Password
                  </label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                    <input
                      id="confirm-password"
                      type={showConfirm ? 'text' : 'password'}
                      value={confirm}
                      onChange={(e) => setConfirm(e.target.value)}
                      placeholder="Repeat your password"
                      required
                      className="w-full cyber-input rounded-lg pl-9 pr-10 py-2.5 text-sm"
                    />
                    <button
                      type="button"
                      onClick={() => setShowConfirm((s) => !s)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300"
                    >
                      {showConfirm ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  </div>
                  {confirm && password !== confirm && (
                    <p className="text-xs text-threat-critical mt-1">Passwords do not match</p>
                  )}
                  {confirm && password === confirm && password.length >= 8 && (
                    <p className="text-xs text-neon-green mt-1 flex items-center gap-1">
                      <CheckCircle2 className="w-3 h-3" /> Passwords match
                    </p>
                  )}
                </div>

                <button
                  id="reset-password-submit"
                  type="submit"
                  disabled={loading || !token}
                  className="w-full btn-primary rounded-lg py-2.5 text-sm font-semibold flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Lock className="w-4 h-4" />}
                  {loading ? 'Updating password…' : 'Update Password'}
                </button>
              </form>

              <p className="text-center text-sm text-slate-500 mt-6">
                Remember it?{' '}
                <Link to="/login" className="text-neon-blue hover:text-neon-cyan font-medium transition-colors">
                  Back to Sign In
                </Link>
              </p>
            </>
          )}
        </div>
      </motion.div>
    </div>
  )
}
