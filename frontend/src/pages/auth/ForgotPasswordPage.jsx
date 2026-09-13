import { useState } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { CheckCircle2, Mail, Shield, Loader2, AlertTriangle, ArrowLeft } from 'lucide-react'
import { api } from '../../api/client'

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('')
  const [sent, setSent] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const submit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      await api.requestPasswordReset({ email })
      setSent(true)
    } catch {
      setError('Could not submit your request. Check the API connection and try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-hero-gradient cyber-grid-bg flex items-center justify-center p-4 relative overflow-hidden">
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-neon-blue/5 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-72 h-72 bg-neon-purple/5 rounded-full blur-3xl pointer-events-none" />

      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md"
      >
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-neon-blue/10 border border-neon-blue/30 mb-4">
            <Shield className="w-7 h-7 text-neon-blue" />
          </div>
          <h1 className="text-2xl font-bold gradient-text">TrinetraAI</h1>
          <p className="text-slate-500 text-sm mt-1">Autonomous SOC Platform</p>
        </div>

        <div className="glass-strong rounded-2xl p-8 border border-cyber-border">
          {sent ? (
            /* ── Success state ── */
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="text-center"
            >
              <div className="flex justify-center mb-5">
                <div className="w-14 h-14 rounded-2xl bg-neon-green/10 border border-neon-green/30 flex items-center justify-center">
                  <CheckCircle2 className="w-7 h-7 text-neon-green" />
                </div>
              </div>
              <h2 className="text-lg font-semibold text-white">Check your email</h2>
              <p className="text-sm text-slate-400 mt-2 leading-relaxed">
                If an account matches <strong className="text-slate-200">{email}</strong>,
                password reset instructions will be sent there.
              </p>
              <div className="mt-4 rounded-lg bg-cyber-surface border border-cyber-border/50 p-3 text-xs text-slate-500 leading-5 text-left">
                <strong className="text-slate-400">Note:</strong> This local development build does not yet have an email delivery provider configured. Contact your SOC administrator to perform a manual reset, or use the{' '}
                <Link to="/reset-password" className="text-neon-blue hover:underline">
                  reset password form
                </Link>{' '}
                directly if you have a token.
              </div>
              <Link
                to="/login"
                className="inline-flex items-center gap-2 mt-6 text-sm text-neon-blue hover:text-neon-cyan font-medium transition-colors"
              >
                <ArrowLeft className="w-4 h-4" /> Back to Sign In
              </Link>
            </motion.div>
          ) : (
            /* ── Form state ── */
            <>
              <h2 className="text-lg font-semibold text-white mb-1">Password Recovery</h2>
              <p className="text-sm text-slate-500 mb-6">
                Enter your email address and we'll send you reset instructions.
              </p>

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

              <form onSubmit={submit} className="space-y-4">
                <div>
                  <label htmlFor="reset-email" className="block text-xs font-medium text-slate-400 mb-1.5 uppercase tracking-wider">
                    Email Address
                  </label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                    <input
                      id="reset-email"
                      type="email"
                      required
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="analyst@company.com"
                      className="cyber-input w-full rounded-lg py-2.5 pl-9 pr-4 text-sm"
                    />
                  </div>
                </div>

                <button
                  id="reset-request-submit"
                  type="submit"
                  disabled={loading}
                  className="w-full btn-primary rounded-lg py-2.5 text-sm font-semibold flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Mail className="w-4 h-4" />}
                  {loading ? 'Submitting…' : 'Request Reset Link'}
                </button>
              </form>

              <Link
                to="/login"
                className="inline-flex items-center gap-2 mt-6 text-sm text-neon-blue hover:text-neon-cyan font-medium transition-colors"
              >
                <ArrowLeft className="w-4 h-4" /> Back to Sign In
              </Link>
            </>
          )}
        </div>
      </motion.div>
    </div>
  )
}
