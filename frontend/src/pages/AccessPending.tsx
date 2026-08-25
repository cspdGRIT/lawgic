import { useEffect, useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { accessAPI, authAPI } from '../lib/api'
import { useAuthStore } from '../store'

export default function AccessPending() {
  const qc = useQueryClient()
  const { user, setUser, logout } = useAuthStore()
  const [utr, setUtr] = useState('')
  const [note, setNote] = useState('')
  const [error, setError] = useState('')

  const { data: status } = useQuery({
    queryKey: ['access-status'],
    queryFn: accessAPI.status,
    refetchInterval: 10000, // polls so an approval unlocks this tab without a manual reload
  })

  // ProtectedRoute gates on user.access_status from the auth store, not this query's
  // data — sync the two the moment an approval lands so the app actually unlocks.
  useEffect(() => {
    if (user && status?.access_status && status.access_status !== user.access_status) {
      setUser({ ...user, access_status: status.access_status })
    }
  }, [status?.access_status])

  const { data: payment } = useQuery({
    queryKey: ['access-payment-info'],
    queryFn: accessAPI.paymentInfo,
    retry: false,
  })

  const submitMutation = useMutation({
    mutationFn: () => accessAPI.submitRequest({ utr_reference: utr || undefined, note: note || undefined }),
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
    } catch {
      /* ignore — interceptor handles a real auth failure */
    }
  }

  const latest = status?.latest_request
  const isRejected = latest?.status === 'rejected'
  const isPending = latest?.status === 'pending'

  return (
    <div className="min-h-screen bg-black flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-lg">
        <div className="text-center mb-8">
          <span className="font-serif text-2xl font-bold text-white">Lawgic</span>
          <p className="mt-3 text-gray-400 text-sm">
            Hi {user?.full_name?.split(' ')[0] || 'there'} — your account needs a quick approval before you can use Lawgic.
          </p>
        </div>

        <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-8 space-y-6">
          {isPending ? (
            <div className="text-center space-y-3">
              <div className="text-4xl">⏳</div>
              <h2 className="font-serif text-lg font-bold text-white">Submitted — awaiting review</h2>
              <p className="text-gray-500 text-sm">
                We've received your request. This page checks automatically and will unlock the moment it's approved
                — no need to keep refreshing.
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

              <div className="text-center">
                <p className="text-gray-400 text-sm mb-4">
                  Scan to pay <span className="text-white font-semibold">₹{payment?.amount_rupees ?? 72}</span> via
                  any UPI app, then submit below for approval.
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
