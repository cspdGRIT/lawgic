import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { accessAPI } from '../lib/api'
import { formatDate } from '../lib/utils'

const TABS = [
  { key: 'pending', label: 'Pending' },
  { key: 'approved', label: 'Approved' },
  { key: 'rejected', label: 'Rejected' },
]

export default function AdminRequests() {
  const qc = useQueryClient()
  const [tab, setTab] = useState<'pending' | 'approved' | 'rejected'>('pending')

  const { data: requests, isLoading } = useQuery({
    queryKey: ['admin-access-requests', tab],
    queryFn: () => accessAPI.adminListRequests(tab),
  })

  const approve = useMutation({
    mutationFn: (id: number) => accessAPI.adminApprove(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['admin-access-requests'] }),
  })
  const reject = useMutation({
    mutationFn: (id: number) => accessAPI.adminReject(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['admin-access-requests'] }),
  })

  return (
    <div className="max-w-3xl mx-auto">
      <div className="mb-6">
        <h1 className="font-serif text-2xl font-bold text-white">Access Requests</h1>
        <p className="text-gray-500 text-sm mt-0.5">Review self-reported UPI payments and grant access</p>
      </div>

      <div className="flex bg-zinc-800 rounded-lg p-1 text-sm mb-6 w-fit">
        {TABS.map((t) => (
          <button
            key={t.key}
            onClick={() => setTab(t.key as typeof tab)}
            className={`px-4 py-2 rounded-md transition-colors ${
              tab === t.key ? 'bg-white text-black font-semibold' : 'text-gray-400 hover:text-white'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {isLoading ? (
        <p className="text-gray-500 text-sm">Loading...</p>
      ) : !requests?.length ? (
        <div className="text-center py-16 bg-zinc-900 border border-zinc-800 rounded-2xl">
          <div className="text-4xl mb-3">📭</div>
          <p className="text-gray-500 text-sm">No {tab} requests</p>
        </div>
      ) : (
        <div className="space-y-3">
          {requests.map((r: any) => (
            <div key={r.id} className="bg-zinc-900 border border-zinc-800 rounded-2xl p-5">
              <div className="flex items-start justify-between gap-4">
                <div className="min-w-0">
                  <div className="text-white font-medium">{r.user_full_name}</div>
                  <div className="text-gray-500 text-sm">{r.user_email}</div>
                  <div className="flex flex-wrap items-center gap-3 mt-2 text-xs text-gray-600">
                    <span>{r.credits} credit{r.credits > 1 ? 's' : ''} · ₹{r.amount_rupees}</span>
                    <span>·</span>
                    <span>{formatDate(r.created_at)}</span>
                    {r.utr_reference && (
                      <>
                        <span>·</span>
                        <span className="font-mono">UTR: {r.utr_reference}</span>
                      </>
                    )}
                  </div>
                  {r.note && <p className="text-gray-400 text-sm mt-2">{r.note}</p>}
                </div>

                {tab === 'pending' ? (
                  <div className="flex gap-2 flex-shrink-0">
                    <button
                      onClick={() => approve.mutate(r.id)}
                      disabled={approve.isPending || reject.isPending}
                      className="bg-white text-black text-xs font-semibold px-3 py-1.5 rounded-lg hover:bg-gray-100 transition-colors disabled:opacity-50"
                    >
                      Approve
                    </button>
                    <button
                      onClick={() => reject.mutate(r.id)}
                      disabled={approve.isPending || reject.isPending}
                      className="bg-zinc-800 border border-zinc-700 text-white text-xs font-semibold px-3 py-1.5 rounded-lg hover:bg-zinc-700 transition-colors disabled:opacity-50"
                    >
                      Reject
                    </button>
                  </div>
                ) : (
                  <span
                    className={`text-xs px-2.5 py-1 rounded-full capitalize flex-shrink-0 ${
                      r.status === 'approved' ? 'bg-green-950 text-green-400' : 'bg-red-950 text-red-400'
                    }`}
                  >
                    {r.status}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
