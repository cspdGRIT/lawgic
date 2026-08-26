import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { GoogleLogin } from '@react-oauth/google'
import { useAuthStore } from '../../store'
import { authAPI } from '../../lib/api'

const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID || ''

// See Login.tsx for why this uses <GoogleLogin> (real ID token) instead of
// useGoogleLogin's default implicit flow (opaque access token the backend can't verify).
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

export default function Register() {
  const navigate = useNavigate()
  const authenticate = useAuthStore((s) => s.authenticate)
  const [userType, setUserType] = useState<'client' | 'lawyer'>('client')
  const [form, setForm] = useState({
    full_name: '',
    email: '',
    phone: '',
    password: '',
    confirm_password: '',
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleAuth(res: any) {
    authenticate(res.access_token, res.user)
    navigate('/dashboard')
  }

  async function handleGoogleSuccess(idToken: string) {
    setLoading(true)
    try {
      await handleAuth(await authAPI.googleAuth(idToken))
    } catch {
      setError('Google sign-in failed. Try email registration.')
    } finally {
      setLoading(false)
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    if (form.password !== form.confirm_password) {
      setError('Passwords do not match')
      return
    }
    if (form.password.length < 8) {
      setError('Password must be at least 8 characters')
      return
    }
    setLoading(true)
    try {
      await handleAuth(await authAPI.register({ ...form, user_type: userType }))
    } catch (err: any) {
      if (!err?.response) {
        setError('Cannot reach server. Please try again in a moment.')
      } else {
        setError(err.response.data?.detail || 'Registration failed. Please try again.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-black flex flex-col">
      <div className="flex-1 flex items-center justify-center px-4 py-8">
        <div className="w-full max-w-md">
          <div className="text-center mb-10">
            <Link to="/" className="inline-block">
              <span className="font-serif text-3xl font-bold text-white">Lawgic</span>
              <span className="text-xs ml-2 text-gray-500 uppercase tracking-widest">AI</span>
            </Link>
            <p className="mt-3 text-gray-400 text-sm">Create your free account</p>
          </div>

          <form onSubmit={handleSubmit} className="bg-zinc-900 border border-zinc-800 rounded-2xl p-8 space-y-5">
            {error && (
              <div className="bg-red-950 border border-red-800 text-red-300 rounded-lg px-4 py-3 text-sm">
                {error}
              </div>
            )}

            {/* User type toggle */}
            <div>
              <label className="block text-sm text-gray-400 mb-2">I am a</label>
              <div className="grid grid-cols-2 gap-2">
                {(['client', 'lawyer'] as const).map((type) => (
                  <button
                    key={type}
                    type="button"
                    onClick={() => setUserType(type)}
                    className={`py-2.5 rounded-lg text-sm font-medium capitalize transition-colors ${
                      userType === type
                        ? 'bg-white text-black'
                        : 'bg-zinc-800 text-gray-400 hover:bg-zinc-700'
                    }`}
                  >
                    {type === 'client' ? 'Client / Individual' : 'Lawyer / Advocate'}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-1.5">Full name</label>
              <input
                type="text"
                value={form.full_name}
                onChange={(e) => setForm({ ...form, full_name: e.target.value })}
                required
                className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-3 text-white text-sm focus:outline-none focus:border-white transition-colors"
                placeholder="Rajesh Kumar"
              />
            </div>

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
              <label className="block text-sm text-gray-400 mb-1.5">Phone number</label>
              <input
                type="tel"
                value={form.phone}
                onChange={(e) => setForm({ ...form, phone: e.target.value })}
                className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-3 text-white text-sm focus:outline-none focus:border-white transition-colors"
                placeholder="+91 98765 43210"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
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
              <div>
                <label className="block text-sm text-gray-400 mb-1.5">Confirm</label>
                <input
                  type="password"
                  value={form.confirm_password}
                  onChange={(e) => setForm({ ...form, confirm_password: e.target.value })}
                  required
                  className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-3 text-white text-sm focus:outline-none focus:border-white transition-colors"
                  placeholder="••••••••"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-white text-black font-semibold py-3 rounded-lg text-sm hover:bg-gray-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Creating account...' : 'Create account'}
            </button>

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
              Already have an account?{' '}
              <Link to="/login" className="text-white hover:underline">
                Sign in
              </Link>
            </p>
          </form>
        </div>
      </div>
    </div>
  )
}
