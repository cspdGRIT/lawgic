import { useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getAccessToken, getSSEUrl } from '../lib/api'
import { useSpeechRecognition } from '../hooks/useSpeechRecognition'

interface LawyerMatch {
  id: number
  full_name: string
  city: string
  state: string
  specializations: string[]
  rating: number
  hourly_rate: number
  consultation_fee: number
  languages: string[]
  match_reason?: string
}

interface IssueAnalysis {
  detected_language: string
  issue_type: string
  case_title: string
  plain_summary: string
  urgency: string
  limitation_warning: string | null
  recommended_forum: string
  forum_reasoning: string
  petition_or_document: string
  document_template_id: string | null
  relevant_statutes: string[]
  documents_needed: string[]
  estimated_court_fee: string
  estimated_lawyer_fee: string
  next_steps: string[]
  disclaimer: string
  confidence_score: number
  matched_lawyers: LawyerMatch[]
  saved_case_id: number | null
}

const EXAMPLES = [
  'Our neighbour built a wall that blocks our only path to the main road. He refuses to remove it.',
  'मेरे पति मुझे और मेरे बच्चों को पैसे नहीं देते और मारपीट करते हैं। मैं क्या करूं?',
  'A shopkeeper sold me a phone that stopped working in a week and refuses a refund.',
  "Someone is selling my company's logo and product designs as their own online.",
]

const URGENCY_STYLES: Record<string, string> = {
  low: 'bg-zinc-800 text-gray-300',
  medium: 'bg-yellow-950 text-yellow-400 border border-yellow-900',
  high: 'bg-orange-950 text-orange-400 border border-orange-900',
  critical: 'bg-red-950 text-red-400 border border-red-900',
}

function urgencyClass(urgency: string | null | undefined) {
  const key = Object.keys(URGENCY_STYLES).find((k) => urgency?.toLowerCase().startsWith(k))
  return URGENCY_STYLES[key || 'low']
}

export default function IssueNavigator() {
  const navigate = useNavigate()
  const [message, setMessage] = useState('')
  const [city, setCity] = useState('')
  const [loading, setLoading] = useState(false)
  const [streaming, setStreaming] = useState('')
  const [result, setResult] = useState<IssueAnalysis | null>(null)
  const [error, setError] = useState('')

  const baseMessageRef = useRef('')
  const { listening, start, stop, supported: micSupported } = useSpeechRecognition((r) => {
    const combined = (baseMessageRef.current ? baseMessageRef.current + ' ' : '') + r.transcript
    setMessage(combined)
    if (r.isFinal) baseMessageRef.current = combined
  })

  function toggleMic() {
    if (listening) { stop(); return }
    baseMessageRef.current = message
    start()
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!message.trim()) return
    setLoading(true)
    setStreaming('')
    setResult(null)
    setError('')

    const token = getAccessToken()
    try {
      const response = await fetch(getSSEUrl('/api/v1/issues/analyze'), {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message, city: city.trim() || undefined }),
      })

      if (!response.ok) {
        const body = await response.json().catch(() => ({}))
        if (response.status === 402 && body?.detail?.error === 'payment_required') {
          window.dispatchEvent(new Event('lawgic:access-pending'))
          return
        }
        if (response.status === 403) {
          throw new Error(body?.detail || 'Issue triage is for clients seeking representation.')
        }
        throw new Error(body?.detail?.message || body?.detail || 'Could not analyze your issue. Please try again.')
      }

      const reader = response.body!.getReader()
      const decoder = new TextDecoder()

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        const text = decoder.decode(value)
        for (const line of text.split('\n')) {
          if (!line.startsWith('data: ')) continue
          const data = JSON.parse(line.slice(6))
          if (data.type === 'token') setStreaming((s) => s + data.content)
          if (data.type === 'error') setError(data.content)
          if (data.type === 'done') setResult(data.analysis)
        }
      }
    } catch (err: any) {
      setError(err.message || 'Something went wrong. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  function reset() {
    setMessage('')
    setCity('')
    setStreaming('')
    setResult(null)
    setError('')
  }

  if (result) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center justify-between gap-3 mb-6">
          <div>
            <div className="text-xs text-gray-500 uppercase tracking-widest mb-1">Your action plan</div>
            <h1 className="font-serif text-2xl font-bold text-white">{result.case_title}</h1>
          </div>
          <button onClick={reset} className="text-sm text-gray-400 hover:text-white transition-colors flex-shrink-0">
            ← Describe another issue
          </button>
        </div>

        <div className="flex flex-wrap gap-2 mb-6">
          <span className="text-xs bg-zinc-800 text-gray-300 px-3 py-1 rounded-full">{result.issue_type}</span>
          <span className={`text-xs px-3 py-1 rounded-full ${urgencyClass(result.urgency)}`}>{result.urgency}</span>
          <span className="text-xs bg-zinc-800 text-gray-500 px-3 py-1 rounded-full">
            Detected language: {result.detected_language}
          </span>
        </div>

        {result.limitation_warning && (
          <div className="bg-red-950 border border-red-800 text-red-300 rounded-xl px-4 py-3 text-sm mb-6 flex gap-2">
            <span className="flex-shrink-0">⏰</span>
            <span>{result.limitation_warning}</span>
          </div>
        )}

        <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6 mb-6">
          <h3 className="font-medium text-white mb-2 text-sm">What you told us</h3>
          <p className="text-gray-400 text-sm leading-relaxed">{result.plain_summary}</p>
        </div>

        <div className="grid md:grid-cols-2 gap-4 mb-4">
          <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-5">
            <div className="text-xs text-gray-500 mb-1">Where to file — recommended forum</div>
            <div className="text-white font-semibold mb-2">{result.recommended_forum}</div>
            <p className="text-gray-400 text-sm leading-relaxed">{result.forum_reasoning}</p>
          </div>
          <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-5">
            <div className="text-xs text-gray-500 mb-1">What to file</div>
            <div className="text-white font-semibold mb-2">{result.petition_or_document}</div>
            {result.document_template_id && (
              <button
                onClick={() => navigate('/documents')}
                className="text-xs bg-white text-black font-semibold px-3 py-1.5 rounded-lg hover:bg-gray-100 transition-colors"
              >
                Draft this document →
              </button>
            )}
          </div>
        </div>

        <div className="grid md:grid-cols-2 gap-4 mb-4">
          <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-5">
            <div className="text-xs text-gray-500 mb-1">Estimated court/filing fee</div>
            <div className="text-white font-semibold">{result.estimated_court_fee}</div>
          </div>
          <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-5">
            <div className="text-xs text-gray-500 mb-1">Estimated lawyer fee</div>
            <div className="text-white font-semibold">{result.estimated_lawyer_fee}</div>
          </div>
        </div>

        <div className="grid md:grid-cols-2 gap-4 mb-6">
          {result.documents_needed?.length ? (
            <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-5">
              <h3 className="font-medium text-white mb-3 text-sm">Documents you'll need</h3>
              <ul className="space-y-1.5">
                {result.documents_needed.map((d, i) => (
                  <li key={i} className="text-gray-400 text-sm flex gap-2">
                    <span className="text-blue-500 flex-shrink-0">☐</span>{d}
                  </li>
                ))}
              </ul>
            </div>
          ) : null}

          {result.next_steps?.length ? (
            <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-5">
              <h3 className="font-medium text-white mb-3 text-sm">Next steps</h3>
              <ol className="space-y-1.5">
                {result.next_steps.map((s, i) => (
                  <li key={i} className="text-gray-400 text-sm flex gap-2">
                    <span className="text-yellow-500 flex-shrink-0">{i + 1}.</span>{s}
                  </li>
                ))}
              </ol>
            </div>
          ) : null}
        </div>

        {result.relevant_statutes?.length ? (
          <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-5 mb-6">
            <h3 className="font-medium text-white mb-3 text-sm">Relevant laws</h3>
            <ul className="flex flex-wrap gap-2">
              {result.relevant_statutes.map((s, i) => (
                <li key={i} className="text-xs bg-zinc-800 text-gray-300 px-3 py-1.5 rounded-full">§ {s}</li>
              ))}
            </ul>
          </div>
        ) : null}

        {result.matched_lawyers?.length ? (
          <div className="mb-6">
            <h3 className="font-medium text-white mb-3 text-sm">Lawyers who can help with this</h3>
            <div className="grid md:grid-cols-2 gap-4">
              {result.matched_lawyers.map((l) => (
                <div key={l.id} className="bg-zinc-900 border border-zinc-800 rounded-2xl p-5">
                  <div className="flex items-start justify-between gap-2 mb-1">
                    <div className="text-white font-semibold">{l.full_name}</div>
                    <div className="text-xs text-gray-500 flex-shrink-0">★ {l.rating.toFixed(1)}</div>
                  </div>
                  <div className="text-xs text-gray-500 mb-2">{l.city}, {l.state}</div>
                  {l.specializations?.length ? (
                    <div className="text-xs text-gray-400 mb-2">{l.specializations.join(', ')}</div>
                  ) : null}
                  <div className="text-xs text-gray-500 mb-3">
                    Consultation ₹{l.consultation_fee.toLocaleString('en-IN')} · ₹{l.hourly_rate.toLocaleString('en-IN')}/hr
                  </div>
                  {l.match_reason && <p className="text-gray-400 text-xs leading-relaxed mb-3">{l.match_reason}</p>}
                  <button
                    onClick={() => navigate('/lawyers')}
                    className="text-xs bg-zinc-800 border border-zinc-700 text-white px-3 py-1.5 rounded-lg hover:bg-zinc-700 transition-colors"
                  >
                    Connect →
                  </button>
                </div>
              ))}
            </div>
          </div>
        ) : null}

        <p className="text-xs text-gray-600 leading-relaxed border-t border-zinc-800 pt-4">{result.disclaimer}</p>
      </div>
    )
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="text-center mb-8">
        <h1 className="font-serif text-2xl font-bold text-white mb-2">Describe your issue</h1>
        <p className="text-gray-500 text-sm">
          Tell us what's going on, in your own words, in any language. We'll tell you exactly what to
          do next — which forum to approach, what to file, what documents you need, roughly what it
          costs, and lawyers who can help.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6 space-y-4">
        {error && (
          <div className="bg-red-950 border border-red-800 text-red-300 rounded-lg px-4 py-3 text-sm">{error}</div>
        )}

        <div className="relative">
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            required
            rows={6}
            disabled={loading}
            placeholder="e.g. My landlord is refusing to return my security deposit two months after I vacated..."
            className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-3 pr-12 text-white text-sm focus:outline-none focus:border-white transition-colors resize-none disabled:opacity-60"
          />
          {micSupported && (
            <button
              type="button"
              onClick={toggleMic}
              disabled={loading}
              title={listening ? 'Stop dictating' : 'Speak instead of typing'}
              aria-pressed={listening}
              aria-label={listening ? 'Stop dictating' : 'Speak instead of typing'}
              className={`absolute top-3 right-3 w-8 h-8 rounded-full flex items-center justify-center text-sm transition-colors ${
                listening ? 'bg-red-600 text-white animate-pulse' : 'bg-zinc-700 text-gray-300 hover:bg-zinc-600'
              }`}
            >
              🎤
              <span className="sr-only" aria-live="polite">{listening ? 'Listening' : ''}</span>
            </button>
          )}
        </div>

        <div>
          <label className="block text-sm text-gray-400 mb-1.5">City / state <span className="text-gray-600">(optional, helps find the right forum and nearby lawyers)</span></label>
          <input
            value={city}
            onChange={(e) => setCity(e.target.value)}
            disabled={loading}
            placeholder="e.g. Pune, Maharashtra"
            className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-3 text-white text-sm focus:outline-none focus:border-white transition-colors disabled:opacity-60"
          />
        </div>

        <button
          type="submit"
          disabled={loading || !message.trim()}
          className="w-full bg-white text-black font-semibold py-3 rounded-lg text-sm hover:bg-gray-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Analyzing your issue...' : 'Get my action plan'}
        </button>

        {loading && streaming && (
          <p className="text-gray-500 text-xs leading-relaxed italic">{streaming}</p>
        )}
      </form>

      <div className="mt-6">
        <div className="text-xs text-gray-600 uppercase tracking-widest mb-2">Try an example</div>
        <div className="flex flex-col gap-2">
          {EXAMPLES.map((ex, i) => (
            <button
              key={i}
              type="button"
              onClick={() => setMessage(ex)}
              disabled={loading}
              className="text-left text-sm text-gray-400 hover:text-white bg-zinc-900 border border-zinc-800 hover:border-zinc-700 rounded-lg px-4 py-2.5 transition-colors disabled:opacity-60"
            >
              {ex}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
