import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { accessAPI, authAPI } from '../lib/api'
import { useAuthStore } from '../store'

export default function AccessPending() {
  const navigate = useNavigate()
  const qc = useQueryClient()
  const { user, setUser, logout } = useAuthStore()
  const [pack, setPack] = useState('starter')
  const [utr, setUtr] = useState('')
  const [note, setNote] = useState('')
  const [error, setError] = useState('')
  // True only for the "was pending, just flipped to approved while I was on this page"
  // transition — not "has an approved purchase somewhere in history", so a returning
  // user who wants to buy more credits later sees the pack picker, not a stale success screen.
  const [justUnlocked, setJustUnlocked] = useState(false)
  const [prevStatus, setPrevStatus] = useState<string | null>(null)

  const { data: status } = useQuery({
    queryKey: ['access-status'],
    queryFn: accessAPI.status,
    refetchInterval: (query) => (query.state.data?.latest_request?.status !== 'pending' ? false : 10000),
  })

  const { data: packs } = useQuery({ queryKey: ['credit-packs'], queryFn: accessAPI.packs })

  useEffect(() => {
    const current = status?.latest_request?.status ?? null
    if (prevStatus === 'pending' && current === 'approved') setJustUnlocked(true)
    if (current !== prevStatus) setPrevStatus(current)
  }, [status?.latest_request?.status])

  // Keep the store's copy current — the credit balance shows in the sidebar/header too.
  useEffect(() => {
    if (user && status && status.access_status !== user.access_status) {
      setUser({ ...user, access_status: status.access_status })
    }
  }, [status?.access_status])

  const { data: payment } = useQuery({
    queryKey: ['access-payment-info', pack],
    queryFn: () => accessAPI.paymentInfo(pack),
    retry: false,
  })

  const submitMutation = useMutation({
    mutationFn: () => accessAPI.submitRequest({ pack, utr_reference: utr || undefined, note: note || undefined }),
    onSuccess: () => {
      setError('')
      qc.invalidateQueries({ queryKey: ['access-status'] })
    },
    onError: (err: any) => setError(err.response?.data?.detail || 'Could not submit. Please try again.'),
  })

  async function refreshSession() {
    try {
      const data = await authAPI.me()
      setUser(data)
      qc.invalidateQueries({ queryKey: ['access-status'] })
    } catch {
      /* ignore — interceptor handles a real auth failure */
    }
  }

  const latest = status?.latest_request
  const justApproved = justUnlocked
  const isRejected = latest?.status === 'rejected'
  const isPending = latest?.status === 'pending'
  const credits = status?.credit_balance ?? 0

  return (
    <div className="min-h-screen bg-black flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-lg">
        <div className="flex items-center justify-between mb-4">
          <button onClick={() => navigate(-1)} className="text-sm text-gray-500 hover:text-white transition-colors">
            ← Back
          </button>
          <span className="text-xs text-gray-500">
            Credit balance: <span className="text-white font-semibold">{credits}</span>
          </span>
        </div>

        <div className="text-center mb-8">
          <span className="font-serif text-2xl font-bold text-white">Lawgic</span>
          <p className="mt-3 text-gray-400 text-sm">
            {justApproved
              ? `You're topped up, ${user?.full_name?.split(' ')[0] || 'there'} — go ahead and try that again.`
              : "This one needs a credit — browsing the rest of Lawgic stays free, and you get 3 free credits on signup."}
          </p>
        </div>

        <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-8 space-y-6">
          {justApproved ? (
            <div className="text-center space-y-4">
              <div className="text-4xl">✅</div>
              <h2 className="font-serif text-lg font-bold text-white">Credits added</h2>
              <p className="text-gray-500 text-sm">{latest?.credits} credits landed in your account — head back and pick up where you left off.</p>
              <button
                onClick={() => navigate('/dashboard')}
                className="w-full bg-white text-black font-semibold py-3 rounded-lg text-sm hover:bg-gray-100 transition-colors"
              >
                Continue
              </button>
            </div>
          ) : isPending ? (
            <div className="text-center space-y-3">
              <div className="text-4xl">⏳</div>
              <h2 className="font-serif text-lg font-bold text-white">Submitted — awaiting review</h2>
              <p className="text-gray-500 text-sm">
                {latest?.credits} credits for ₹{latest?.amount_rupees}, under review. This page checks automatically
                and unlocks the moment it's approved.
              </p>
              {latest?.utr_reference && (
                <p className="text-gray-600 text-xs">Reference you submitted: {latest.utr_reference}</p>
              )}
            </div>
          ) : (
            <>
              {isRejected && (
                <div className="bg-red-950 border border-red-800 text-red-300 rounded-lg px-4 py-3 text-sm">
                  Your last request wasn't approved. Double-check the payment went through and submit again below.
                </div>
              )}

              {/* Pack picker */}
              <div className="grid grid-cols-3 gap-2">
                {packs && Object.entries(packs).map(([key, p]: [string, any]) => (
                  <button
                    key={key}
                    onClick={() => setPack(key)}
                    className={`rounded-xl border p-3 text-center transition-colors ${
                      pack === key ? 'border-white bg-zinc-800' : 'border-zinc-800 hover:border-zinc-600'
                    }`}
                  >
                    <div className="text-white font-semibold text-sm">{p.credits} credit{p.credits > 1 ? 's' : ''}</div>
                    <div className="text-gray-500 text-xs mt-0.5">₹{p.price_rupees}</div>
                    {p.credits > 1 && (
                      <div className="text-gray-600 text-[10px] mt-0.5">₹{Math.round(p.price_rupees / p.credits)}/ea</div>
                    )}
                  </button>
                ))}
              </div>

              <div className="text-center">
                <p className="text-gray-400 text-sm mb-4">
                  Scan to pay <span className="text-white font-semibold">₹{payment?.amount_rupees ?? '—'}</span> via
                  any UPI app for {payment?.credits ?? '—'} credit{(payment?.credits ?? 0) > 1 ? 's' : ''}.
                </p>
                {payment?.qr_data_uri ? (
                  <img
                    src={payment.qr_data_uri}
                    alt="UPI payment QR code"
                    className="mx-auto rounded-xl border border-zinc-700 bg-white p-2"
                    width={220}
                    height={220}
                  />
                ) : (
                  <div className="h-[220px] flex items-center justify-center text-gray-600 text-sm">
                    Loading payment details...
                  </div>
                )}
                {payment?.upi_id && (
                  <p className="text-gray-500 text-xs mt-3">
                    UPI ID: <span className="text-gray-300 font-mono">{payment.upi_id}</span>
                  </p>
                )}
              </div>

              <div>
                <label className="block text-sm text-gray-400 mb-1.5">
                  UPI transaction ref <span className="text-gray-600">(optional, speeds up review)</span>
                </label>
                <input
                  value={utr}
                  onChange={(e) => setUtr(e.target.value)}
                  placeholder="e.g. 12-digit UTR from your payment app"
                  className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-2.5 text-white text-sm focus:outline-none focus:border-white transition-colors"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1.5">Note <span className="text-gray-600">(optional)</span></label>
                <textarea
                  value={note}
                  onChange={(e) => setNote(e.target.value)}
                  rows={2}
                  className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-2.5 text-white text-sm focus:outline-none focus:border-white transition-colors resize-none"
                  placeholder="Anything that helps us match your payment"
                />
              </div>

              {error && (
                <div className="bg-red-950 border border-red-800 text-red-300 rounded-lg px-4 py-3 text-sm">{error}</div>
              )}

              <button
                onClick={() => submitMutation.mutate()}
                disabled={submitMutation.isPending}
                className="w-full bg-white text-black font-semibold py-3 rounded-lg text-sm hover:bg-gray-100 transition-colors disabled:opacity-50"
              >
                {submitMutation.isPending ? 'Submitting...' : "I've paid — submit for approval"}
              </button>

              <div className="flex items-center gap-3">
                <div className="flex-1 h-px bg-zinc-800" />
                <span className="text-xs text-gray-600">or</span>
                <div className="flex-1 h-px bg-zinc-800" />
              </div>
              <button
                onClick={() => navigate('/pricing')}
                className="w-full bg-zinc-800 border border-zinc-700 text-white font-semibold py-3 rounded-lg text-sm hover:bg-zinc-700 transition-colors"
              >
                Subscribe instead — unlimited-ish, better value if you'll use this a lot
              </button>
            </>
          )}

          <div className="flex items-center justify-between text-xs text-gray-600 pt-2 border-t border-zinc-800">
            <button onClick={refreshSession} className="hover:text-white transition-colors">
              Check again
            </button>
            <button onClick={logout} className="hover:text-white transition-colors">
              Sign out
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
