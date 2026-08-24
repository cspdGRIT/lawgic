import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useGoogleLogin } from '@react-oauth/google'
import { useAuthStore } from '../../store'
import { authAPI } from '../../lib/api'

const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID || ''

// Isolated component so useGoogleLogin is only called when GoogleOAuthProvider exists
function GoogleSignInButton({ onSuccess, onError, disabled }: {
  onSuccess: (token: string) => void
  onError: () => void
  disabled: boolean
}) {
  const login = useGoogleLogin({ onSuccess: (r) => onSuccess(r.access_token), onError })
  return (
    <button
      type="button"
      onClick={() => login()}
      disabled={disabled}
      className="w-full flex items-center justify-center gap-3 bg-zinc-800 border border-zinc-700 text-white py-3 rounded-lg text-sm hover:bg-zinc-700 transition-colors disabled:opacity-50"
    >
      <svg className="h-4 w-4" viewBox="0 0 24 24">
        <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
        <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
        <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z"/>
        <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
      </svg>
      Continue with Google
    </button>
  )
}

// Two-step passwordless flow: send a code, then verify it. Verifying auto-creates
// the account on a phone's first sign-in, same as Google auth does for email.
function MobileOtpForm({ onAuthenticated }: { onAuthenticated: (res: any) => void }) {
  const [phone, setPhone] = useState('')
  const [fullName, setFullName] = useState('')
  const [otp, setOtp] = useState('')
  const [stage, setStage] = useState<'phone' | 'otp'>('phone')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [cooldown, setCooldown] = useState(0)

  useEffect(() => {
    if (cooldown <= 0) return
    const t = setInterval(() => setCooldown((c) => Math.max(0, c - 1)), 1000)
    return () => clearInterval(t)
  }, [cooldown])

  async function sendOtp(e?: React.FormEvent) {
    e?.preventDefault()
    if (cooldown > 0) return
    setError('')
    setLoading(true)
    try {
      await authAPI.requestOtp(phone)
      setStage('otp')
      setCooldown(60)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Could not send code. Check the number and try again.')
    } finally {
      setLoading(false)
    }
  }

  async function verify(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      onAuthenticated(await authAPI.verifyOtp(phone, otp, fullName || undefined))
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Incorrect code')
    } finally {
      setLoading(false)
    }
  }

  if (stage === 'phone') {
    return (
      <form onSubmit={sendOtp} className="space-y-5">
        <div>
          <label className="block text-sm text-gray-400 mb-1.5">Mobile number</label>
          <input
            type="tel"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            required
            autoFocus
            placeholder="98765 43210"
            className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-3 text-white text-sm focus:outline-none focus:border-white transition-colors"
          />
        </div>
        <div>
          <label className="block text-sm text-gray-400 mb-1.5">
            Name <span className="text-gray-600">(only needed the first time)</span>
          </label>
          <input
            type="text"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            placeholder="Your name"
            className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-3 text-white text-sm focus:outline-none focus:border-white transition-colors"
          />
        </div>
        {error && (
          <div className="bg-red-950 border border-red-800 text-red-300 rounded-lg px-4 py-3 text-sm">{error}</div>
        )}
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-white text-black font-semibold py-3 rounded-lg text-sm hover:bg-gray-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Sending...' : 'Send code'}
        </button>
      </form>
    )
  }

  return (
    <form onSubmit={verify} className="space-y-5">
      <p className="text-sm text-gray-400">
        Code sent to <span className="text-white">{phone}</span>
      </p>
      <div>
        <label className="block text-sm text-gray-400 mb-1.5">6-digit code</label>
        <input
          type="text"
          inputMode="numeric"
          pattern="[0-9]*"
          maxLength={6}
          value={otp}
          onChange={(e) => setOtp(e.target.value.replace(/\D/g, ''))}
          required
          autoFocus
          placeholder="••••••"
          className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-3 text-white text-sm tracking-widest text-center focus:outline-none focus:border-white transition-colors"
        />
      </div>
      {error && (
        <div className="bg-red-950 border border-red-800 text-red-300 rounded-lg px-4 py-3 text-sm">{error}</div>
      )}
      <button
        type="submit"
        disabled={loading || otp.length < 4}
        className="w-full bg-white text-black font-semibold py-3 rounded-lg text-sm hover:bg-gray-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? 'Verifying...' : 'Verify & continue'}
      </button>
      <div className="flex justify-between text-sm">
        <button
          type="button"
          onClick={() => {
            setStage('phone')
            setOtp('')
            setError('')
          }}
          className="text-gray-500 hover:text-white transition-colors"
        >
          Change number
        </button>
        <button
          type="button"
          disabled={cooldown > 0 || loading}
          onClick={sendOtp}
          className="text-gray-500 hover:text-white transition-colors disabled:opacity-40 disabled:hover:text-gray-500"
        >
          {cooldown > 0 ? `Resend in ${cooldown}s` : 'Resend code'}
        </button>
      </div>
    </form>
  )
}

export default function Login() {
  const navigate = useNavigate()
  const authenticate = useAuthStore((s) => s.authenticate)
  const [mode, setMode] = useState<'email' | 'otp'>('email')
  const [form, setForm] = useState({ email: '', password: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleAuth(res: any) {
    authenticate(res.access_token, res.user)
    navigate('/dashboard')
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await handleAuth(await authAPI.login(form))
    } catch (err: any) {
      if (!err?.response) {
        setError('Cannot reach server. Please try again in a moment.')
      } else {
        setError(err.response.data?.detail || 'Invalid email or password')
      }
    } finally {
      setLoading(false)
    }
  }

  async function handleGoogleSuccess(accessToken: string) {
    setLoading(true)
    try {
      await handleAuth(await authAPI.googleAuth(accessToken))
    } catch {
      setError('Google sign-in failed. Try email login.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-black flex flex-col">
      <div className="flex-1 flex items-center justify-center px-4">
        <div className="w-full max-w-md">
          {/* Logo */}
          <div className="text-center mb-10">
            <Link to="/" className="inline-block">
              <span className="font-serif text-3xl font-bold text-white">Lawgic</span>
              <span className="text-xs ml-1 text-gray-500 uppercase tracking-widest">.com</span>
            </Link>
            <p className="mt-1 text-gray-500 text-xs uppercase tracking-widest">The Legal AId</p>
            <p className="mt-3 text-gray-400 text-sm">Sign in to your account</p>
          </div>

          <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-8 space-y-5">
            {/* Mode tabs */}
            <div className="flex bg-zinc-800 rounded-lg p-1 text-sm">
              <button
                type="button"
                onClick={() => { setMode('email'); setError('') }}
                className={`flex-1 py-2 rounded-md transition-colors ${mode === 'email' ? 'bg-white text-black font-semibold' : 'text-gray-400 hover:text-white'}`}
              >
                Email
              </button>
              <button
                type="button"
                onClick={() => { setMode('otp'); setError('') }}
                className={`flex-1 py-2 rounded-md transition-colors ${mode === 'otp' ? 'bg-white text-black font-semibold' : 'text-gray-400 hover:text-white'}`}
              >
                Mobile OTP
              </button>
            </div>

            {mode === 'email' ? (
              <form onSubmit={handleSubmit} className="space-y-5">
                {error && (
                  <div className="bg-red-950 border border-red-800 text-red-300 rounded-lg px-4 py-3 text-sm">
                    {error}
                  </div>
                )}

                <div>
                  <label className="block text-sm text-gray-400 mb-1.5">Email address</label>
                  <input
                    type="email"
                    value={form.email}
                    onChange={(e) => setForm({ ...form, email: e.target.value })}
                    required
                    className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-3 text-white text-sm focus:outline-none focus:border-white transition-colors"
                    placeholder="you@example.com"
                  />
                </div>

                <div>
                  <label className="block text-sm text-gray-400 mb-1.5">Password</label>
                  <input
                    type="password"
                    value={form.password}
                    onChange={(e) => setForm({ ...form, password: e.target.value })}
                    required
                    className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-3 text-white text-sm focus:outline-none focus:border-white transition-colors"
                    placeholder="••••••••"
                  />
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-white text-black font-semibold py-3 rounded-lg text-sm hover:bg-gray-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? 'Signing in...' : 'Sign in'}
                </button>
              </form>
            ) : (
              <>
                {error && (
                  <div className="bg-red-950 border border-red-800 text-red-300 rounded-lg px-4 py-3 text-sm">
                    {error}
                  </div>
                )}
                <MobileOtpForm onAuthenticated={handleAuth} />
              </>
            )}

            {GOOGLE_CLIENT_ID && (
              <>
                <div className="flex items-center gap-3">
                  <div className="flex-1 h-px bg-zinc-700" />
                  <span className="text-xs text-gray-500">or</span>
                  <div className="flex-1 h-px bg-zinc-700" />
                </div>
                <GoogleSignInButton
                  onSuccess={handleGoogleSuccess}
                  onError={() => setError('Google sign-in failed.')}
                  disabled={loading}
                />
              </>
            )}

            <p className="text-center text-sm text-gray-500">
              Don't have an account?{' '}
              <Link to="/register" className="text-white hover:underline">
                Create account
              </Link>
            </p>
          </div>

        </div>
      </div>
    </div>
  )
}
