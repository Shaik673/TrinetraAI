import { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Shield, Loader2, AlertTriangle, CheckCircle2 } from 'lucide-react'
import { useAuthStore } from '../../store/authStore'
import { api, getApiErrorMessage } from '../../api/client'
import toast from 'react-hot-toast'

/**
 * OAuthCallbackPage
 *
 * This page lives at /auth/callback and handles two scenarios:
 *
 * A) Backend redirects here with ?access_token=...&refresh_token=...&provider=...
 *    after a successful OAuth exchange (social login flow).
 *
 * B) Backend redirects here with ?error=... when something went wrong.
 *
 * In scenario A we save the tokens into the auth store and navigate to /dashboard.
 */
export default function OAuthCallbackPage() {
  const [searchParams] = useSearchParams()
  const { login } = useAuthStore()
  const navigate = useNavigate()
  const [status, setStatus] = useState('processing') // 'processing' | 'success' | 'error'
  const [errorMsg, setErrorMsg] = useState('')

  useEffect(() => {
    const accessToken = searchParams.get('access_token')
    const refreshToken = searchParams.get('refresh_token')
    const provider = searchParams.get('provider')
    const error = searchParams.get('error')

    if (error) {
      const messages = {
        provider_denied_google: 'Google login was cancelled or denied.',
        provider_denied_github: 'GitHub login was cancelled or denied.',
        provider_denied_facebook: 'Facebook login was cancelled or denied.',
        token_exchange_failed: 'Failed to exchange authorization code. Please try again.',
        missing_email_or_id: 'Your social account did not provide a verified email. Please use email/password login.',
        account_error: 'Could not create or find your account. Please try again.',
        network_error: 'Network error during authentication. Check your connection.',
        missing_code: 'Authorization code missing. Please retry the login.',
      }
      setErrorMsg(messages[error] || `Authentication error: ${error}`)
      setStatus('error')
      return
    }

    if (!accessToken || !refreshToken) {
      setErrorMsg('Authentication tokens missing. Please try logging in again.')
      setStatus('error')
      return
    }

    // Fetch current user profile using the new access token to populate the store
    const finish = async () => {
      try {
        // Temporarily set the token so the /me request is authenticated
        const tempData = {
          access_token: accessToken,
          refresh_token: refreshToken,
          user: null,
        }
        login(tempData)

        const { data: user } = await api.getMe()
        login({ access_token: accessToken, refresh_token: refreshToken, user })

        setStatus('success')
        toast.success(`Signed in via ${provider || 'social provider'}`)
        setTimeout(() => navigate('/dashboard', { replace: true }), 800)
      } catch (err) {
        setErrorMsg(getApiErrorMessage(err, 'Failed to load your profile. Please try again.'))
        setStatus('error')
      }
    }

    finish()
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <div className="min-h-screen bg-hero-gradient cyber-grid-bg flex items-center justify-center p-4 relative overflow-hidden">
      <div className="absolute top-1/3 left-1/3 w-96 h-96 bg-neon-blue/5 rounded-full blur-3xl pointer-events-none" />

      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.4 }}
        className="w-full max-w-sm text-center"
      >
        <div className="glass-strong rounded-2xl p-10 border border-cyber-border">
          {/* Icon */}
          <div className="flex justify-center mb-6">
            {status === 'processing' && (
              <div className="w-16 h-16 rounded-2xl bg-neon-blue/10 border border-neon-blue/30 flex items-center justify-center">
                <Loader2 className="w-8 h-8 text-neon-blue animate-spin" />
              </div>
            )}
            {status === 'success' && (
              <motion.div
                initial={{ scale: 0.5 }}
                animate={{ scale: 1 }}
                transition={{ type: 'spring', stiffness: 300 }}
                className="w-16 h-16 rounded-2xl bg-neon-green/10 border border-neon-green/30 flex items-center justify-center"
              >
                <CheckCircle2 className="w-8 h-8 text-neon-green" />
              </motion.div>
            )}
            {status === 'error' && (
              <div className="w-16 h-16 rounded-2xl bg-threat-critical/10 border border-threat-critical/30 flex items-center justify-center">
                <AlertTriangle className="w-8 h-8 text-threat-critical" />
              </div>
            )}
          </div>

          {/* Shield logo */}
          <div className="flex items-center justify-center gap-2 mb-4">
            <Shield className="w-5 h-5 text-neon-blue" />
            <span className="font-bold gradient-text">TrinetraAI</span>
          </div>

          {/* Status text */}
          {status === 'processing' && (
            <>
              <h2 className="text-lg font-semibold text-white">Authenticating…</h2>
              <p className="text-sm text-slate-500 mt-2">Verifying your identity with the provider</p>
              <div className="mt-5 flex justify-center gap-1">
                {[0, 1, 2].map((i) => (
                  <motion.span
                    key={i}
                    className="w-2 h-2 rounded-full bg-neon-blue"
                    animate={{ opacity: [0.3, 1, 0.3] }}
                    transition={{ duration: 1.2, repeat: Infinity, delay: i * 0.2 }}
                  />
                ))}
              </div>
            </>
          )}

          {status === 'success' && (
            <>
              <h2 className="text-lg font-semibold text-white">Authentication Successful</h2>
              <p className="text-sm text-slate-500 mt-2">Redirecting you to the dashboard…</p>
            </>
          )}

          {status === 'error' && (
            <>
              <h2 className="text-lg font-semibold text-white">Authentication Failed</h2>
              <p className="text-sm text-threat-critical mt-2">{errorMsg}</p>
              <div className="mt-6 flex flex-col gap-2">
                <button
                  onClick={() => navigate('/login', { replace: true })}
                  className="btn-primary rounded-lg py-2.5 text-sm font-semibold w-full"
                >
                  Back to Sign In
                </button>
                <button
                  onClick={() => navigate('/signup', { replace: true })}
                  className="py-2.5 text-sm font-medium text-slate-400 hover:text-slate-200 transition-colors"
                >
                  Create an account instead
                </button>
              </div>
            </>
          )}
        </div>
      </motion.div>
    </div>
  )
}
