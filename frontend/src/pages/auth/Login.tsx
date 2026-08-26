import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { GoogleLogin } from '@react-oauth/google'
import { useAuthStore } from '../../store'
import { authAPI } from '../../lib/api'

const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID || ''

// Isolated component so this is only mounted when GoogleOAuthProvider exists.
// Uses the <GoogleLogin> component (not useGoogleLogin's default implicit flow) —
// it yields a real signed ID token (`credential`) in onSuccess. useGoogleLogin's
// default flow returns an opaque OAuth2 access token instead, which the backend's
// id_token.verify_oauth2_token() cannot verify — that mismatch meant Google sign-in
// could never work even with GOOGLE_CLIENT_ID configured.
function GoogleSignInButton({ onSuccess, onError, disabled }: {
  onSuccess: (idToken: string) => void
  onError: () => void
  disabled: boolean
}) {
  return (
    <div className={disabled ? 'opacity-50 pointer-events-none flex justify-center' : 'flex justify-center'}>
      <GoogleLogin
        onSuccess={(cred) => cred.credential && onSuccess(cred.credential)}
        onError={onError}
        theme="filled_black"
        text="continue_with"
        shape="pill"
      />
    </div>
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

  async function handleGoogleSuccess(idToken: string) {
    setLoading(true)
    try {
      await handleAuth(await authAPI.googleAuth(idToken))
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
