import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { casesAPI, getSSEUrl, getAccessToken } from '../lib/api'
import { formatDate } from '../lib/utils'

const CASE_TYPES = ['Criminal', 'Civil', 'Family', 'Property', 'Consumer', 'Labour', 'Corporate', 'Constitutional', 'Revenue', 'Intellectual Property', 'Other']
const JURISDICTIONS = ['Delhi', 'Mumbai', 'Bangalore', 'Chennai', 'Hyderabad', 'Kolkata', 'Ahmedabad', 'Pune', 'Other']
const COURT_LEVELS = ['District Court', 'High Court', 'Supreme Court', 'Consumer Forum', 'Family Court', 'Labour Court', 'RERA Authority', 'NCLT', 'Arbitral Tribunal']

interface AnalysisResult {
  summary?: string
  win_probability?: number
  key_issues?: string[]
  legal_strategy?: string[]
  relevant_statutes?: string[]
  similar_cases?: string[]
  next_steps?: string[]
  risk_factors?: string[]
  estimated_duration?: string
  estimated_cost?: string
}

function WinGauge({ probability }: { probability: number }) {
  // Backend sends win_probability as an integer 0-100 already (case_agent.py's
  // schema), not a 0-1 fraction — multiplying by 100 here produced "7800%".
  const pct = Math.round(probability)
  const color = pct >= 60 ? '#22c55e' : pct >= 40 ? '#eab308' : '#ef4444'
  const circumference = 2 * Math.PI * 52
  const offset = circumference - (pct / 100) * circumference

  return (
    <div className="flex flex-col items-center">
      <div className="relative w-32 h-32">
        <svg className="transform -rotate-90 w-32 h-32">
          <circle cx="64" cy="64" r="52" fill="none" stroke="#27272a" strokeWidth="12" />
          <circle
            cx="64" cy="64" r="52" fill="none"
            stroke={color} strokeWidth="12"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            style={{ transition: 'stroke-dashoffset 1s ease' }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="font-serif text-3xl font-bold text-white">{pct}%</span>
          <span className="text-xs text-gray-500">win probability</span>
        </div>
      </div>
    </div>
  )
}

export default function CaseAnalysis() {
  const qc = useQueryClient()
  const [view, setView] = useState<'list' | 'new' | 'detail'>('list')
  const [selectedCase, setSelectedCase] = useState<any>(null)
  const [streaming, setStreaming] = useState('')
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null)
  const [analysisUnlocked, setAnalysisUnlocked] = useState(false)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [isUnlocking, setIsUnlocking] = useState(false)
  const [unlockError, setUnlockError] = useState('')
  const [form, setForm] = useState({
    title: '',
    description: '',
    case_type: 'Criminal',
    jurisdiction: 'Delhi',
    court_level: 'District Court',
    opposing_party: '',
    key_facts: '',
  })

  const { data: casesData } = useQuery({
    queryKey: ['cases'],
    queryFn: () => casesAPI.list(),
    select: (d: any) => d?.items || d || [],
  })
  const cases = casesData || []

  const createMutation = useMutation({
    mutationFn: (data: any) => casesAPI.create(data),
    onSuccess: (newCase) => {
      qc.invalidateQueries({ queryKey: ['cases'] })
      setSelectedCase(newCase)
      setView('detail')
    },
  })

  function handleCreate(e: React.FormEvent) {
    e.preventDefault()
    createMutation.mutate(form)
  }

  async function handleAnalyze(caseId: number) {
    setIsAnalyzing(true)
    setStreaming('')
    setAnalysisResult(null)
    const token = getAccessToken()
    const url = getSSEUrl(`/api/v1/cases/${caseId}/analyze`)

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      })
      const reader = response.body!.getReader()
      const decoder = new TextDecoder()

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        const text = decoder.decode(value)
        const lines = text.split('\n')
        for (const line of lines) {
          if (!line.startsWith('data: ')) continue
          const data = JSON.parse(line.slice(6))
          if (data.type === 'token') setStreaming((s) => s + data.content)
          if (data.type === 'done') {
            setAnalysisResult(data.analysis || {})
            setAnalysisUnlocked(!!data.unlocked)
            qc.invalidateQueries({ queryKey: ['cases'] })
          }
        }
      }
    } catch (err) {
      console.error(err)
    } finally {
      setIsAnalyzing(false)
    }
  }

  async function handleUnlockAnalysis() {
    if (!selectedCase) return
    setIsUnlocking(true)
    setUnlockError('')
    try {
      const updated = await casesAPI.unlock(selectedCase.id)
      setAnalysisResult(updated.ai_analysis || {})
      setAnalysisUnlocked(true)
      qc.invalidateQueries({ queryKey: ['cases'] })
    } catch (err: any) {
      if (err.response?.status === 402) {
        window.dispatchEvent(new Event('lawgic:access-pending'))
        return
      }
      setUnlockError(err.response?.data?.detail || 'Could not unlock. Please try again.')
    } finally {
      setIsUnlocking(false)
    }
  }

  if (view === 'new') {
    return (
      <div className="max-w-2xl mx-auto">
        <div className="flex items-center gap-3 mb-6">
          <button onClick={() => setView('list')} className="text-gray-500 hover:text-white transition-colors text-sm">← Back</button>
          <h1 className="font-serif text-2xl font-bold text-white">New Case</h1>
        </div>

        <form onSubmit={handleCreate} className="space-y-5">
          <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6 space-y-4">
            <div>
              <label className="block text-sm text-gray-400 mb-1.5">Case Title</label>
              <input
                value={form.title}
                onChange={(e) => setForm({ ...form, title: e.target.value })}
                required
                className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-2.5 text-white text-sm focus:outline-none focus:border-white transition-colors"
                placeholder="e.g., Cheque dishonour against ABC Company"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-gray-400 mb-1.5">Case Type</label>
                <select
                  value={form.case_type}
                  onChange={(e) => setForm({ ...form, case_type: e.target.value })}
                  className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-2.5 text-white text-sm focus:outline-none focus:border-white transition-colors"
                >
                  {CASE_TYPES.map((t) => <option key={t}>{t}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1.5">Jurisdiction</label>
                <select
                  value={form.jurisdiction}
                  onChange={(e) => setForm({ ...form, jurisdiction: e.target.value })}
                  className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-2.5 text-white text-sm focus:outline-none focus:border-white transition-colors"
                >
                  {JURISDICTIONS.map((j) => <option key={j}>{j}</option>)}
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-1.5">Court Level</label>
              <select
                value={form.court_level}
                onChange={(e) => setForm({ ...form, court_level: e.target.value })}
                className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-2.5 text-white text-sm focus:outline-none focus:border-white transition-colors"
              >
                {COURT_LEVELS.map((c) => <option key={c}>{c}</option>)}
              </select>
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-1.5">Opposing Party</label>
              <input
                value={form.opposing_party}
                onChange={(e) => setForm({ ...form, opposing_party: e.target.value })}
                className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-2.5 text-white text-sm focus:outline-none focus:border-white transition-colors"
                placeholder="Name of defendant / opposite party"
              />
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-1.5">Brief Description</label>
              <textarea
                value={form.description}
                onChange={(e) => setForm({ ...form, description: e.target.value })}
                rows={3}
                required
                className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-2.5 text-white text-sm focus:outline-none focus:border-white transition-colors resize-none"
                placeholder="Briefly describe the legal matter"
              />
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-1.5">Key Facts</label>
              <textarea
                value={form.key_facts}
                onChange={(e) => setForm({ ...form, key_facts: e.target.value })}
                rows={5}
                className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-2.5 text-white text-sm focus:outline-none focus:border-white transition-colors resize-none"
                placeholder="List the key facts of your case (dates, amounts, events, witnesses, evidence available...)"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={createMutation.isPending}
            className="w-full bg-white text-black font-semibold py-3 rounded-xl text-sm hover:bg-gray-100 transition-colors disabled:opacity-50"
          >
            {createMutation.isPending ? 'Creating...' : 'Create Case & Analyze →'}
          </button>
        </form>
      </div>
    )
  }

  if (view === 'detail' && selectedCase) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center gap-3 mb-6">
          <button onClick={() => { setView('list'); setAnalysisResult(null); setAnalysisUnlocked(false); setStreaming('') }} className="text-gray-500 hover:text-white transition-colors text-sm">← Back</button>
          <h1 className="font-serif text-2xl font-bold text-white truncate">{selectedCase.title}</h1>
          <span className="text-xs bg-zinc-800 text-gray-400 px-2 py-0.5 rounded-full">{selectedCase.status}</span>
        </div>

        <div className="grid md:grid-cols-3 gap-4 mb-6">
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4">
            <div className="text-xs text-gray-500 mb-1">Case Type</div>
            <div className="text-white font-medium">{selectedCase.case_type}</div>
          </div>
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4">
            <div className="text-xs text-gray-500 mb-1">Jurisdiction</div>
            <div className="text-white font-medium">{selectedCase.jurisdiction}</div>
          </div>
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4">
            <div className="text-xs text-gray-500 mb-1">Court Level</div>
            <div className="text-white font-medium">{selectedCase.court_level}</div>
          </div>
        </div>

        {!analysisResult && !streaming && (
          <div className="text-center py-12 bg-zinc-900 border border-zinc-800 rounded-2xl">
            <div className="text-4xl mb-4">⚖️</div>
            <h2 className="font-serif text-xl font-bold text-white mb-2">Ready for AI Analysis</h2>
            <p className="text-gray-500 text-sm mb-6 max-w-md mx-auto">
              Our case analysis agent will assess win probability, identify legal strategy, cite relevant statutes, and suggest next steps.
            </p>
            <button
              onClick={() => handleAnalyze(selectedCase.id)}
              disabled={isAnalyzing}
              className="bg-white text-black font-semibold px-8 py-3 rounded-xl text-sm hover:bg-gray-100 transition-colors disabled:opacity-50"
            >
              {isAnalyzing ? 'Analyzing...' : 'Run AI Analysis'}
            </button>
          </div>
        )}

        {streaming && !analysisResult && (
          <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6">
            <div className="flex items-center gap-2 mb-4">
              <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              <span className="text-sm text-gray-400">Analyzing your case...</span>
            </div>
            <p className="text-gray-300 text-sm leading-relaxed whitespace-pre-wrap font-mono">{streaming}<span className="animate-pulse">▋</span></p>
          </div>
        )}

        {analysisResult && (
          <div className="space-y-4">
            {/* Win probability */}
            {analysisResult.win_probability !== undefined && (
              <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6 flex flex-col md:flex-row items-center gap-6">
                <WinGauge probability={analysisResult.win_probability} />
                <div>
                  <h3 className="font-semibold text-white mb-2">Case Assessment</h3>
                  <p className="text-gray-400 text-sm leading-relaxed">{analysisResult.summary}</p>
                </div>
              </div>
            )}

            {/* Preview-then-pay: full breakdown (statutes, strategy, next steps, risk
                factors, similar cases, cost/duration) needs a credit or quota — the
                assessment above is always free. */}
            {!analysisUnlocked && (
              <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6 text-center">
                <h3 className="font-semibold text-white mb-1">Unlock the full breakdown</h3>
                <p className="text-gray-500 text-sm mb-4">
                  Key legal issues, relevant statutes, strategy, next steps, risk factors, and cost/duration estimates.
                </p>
                {unlockError && (
                  <div className="bg-red-950 border border-red-800 text-red-300 rounded-lg px-4 py-3 text-sm mb-4">{unlockError}</div>
                )}
                <button
                  onClick={handleUnlockAnalysis}
                  disabled={isUnlocking}
                  className="bg-white text-black font-semibold px-6 py-2.5 rounded-xl text-sm hover:bg-gray-100 transition-colors disabled:opacity-50"
                >
                  {isUnlocking ? 'Unlocking...' : 'Unlock full analysis (1 credit)'}
                </button>
              </div>
            )}

            <div className="grid md:grid-cols-2 gap-4">
              {/* Key issues */}
              {analysisResult.key_issues?.length ? (
                <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-5">
                  <h3 className="font-medium text-white mb-3 text-sm">Key Legal Issues</h3>
                  <ul className="space-y-1.5">
                    {analysisResult.key_issues.map((issue, i) => (
                      <li key={i} className="text-gray-400 text-sm flex gap-2"><span className="text-red-500 flex-shrink-0">•</span>{issue}</li>
                    ))}
                  </ul>
                </div>
              ) : null}

              {/* Relevant statutes */}
              {analysisResult.relevant_statutes?.length ? (
                <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-5">
                  <h3 className="font-medium text-white mb-3 text-sm">Relevant Statutes</h3>
                  <ul className="space-y-1.5">
                    {analysisResult.relevant_statutes.map((s, i) => (
                      <li key={i} className="text-gray-400 text-sm flex gap-2"><span className="text-blue-500 flex-shrink-0">§</span>{s}</li>
                    ))}
                  </ul>
                </div>
              ) : null}

              {/* Strategy */}
              {analysisResult.legal_strategy?.length ? (
                <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-5">
                  <h3 className="font-medium text-white mb-3 text-sm">Legal Strategy</h3>
                  <ul className="space-y-1.5">
                    {analysisResult.legal_strategy.map((s, i) => (
                      <li key={i} className="text-gray-400 text-sm flex gap-2"><span className="text-green-500 flex-shrink-0">{i + 1}.</span>{s}</li>
                    ))}
                  </ul>
                </div>
              ) : null}

              {/* Next steps */}
              {analysisResult.next_steps?.length ? (
                <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-5">
                  <h3 className="font-medium text-white mb-3 text-sm">Next Steps</h3>
                  <ul className="space-y-1.5">
                    {analysisResult.next_steps.map((s, i) => (
                      <li key={i} className="text-gray-400 text-sm flex gap-2"><span className="text-yellow-500 flex-shrink-0">→</span>{s}</li>
                    ))}
                  </ul>
                </div>
              ) : null}
            </div>

            {/* Cost & duration */}
            {(analysisResult.estimated_duration || analysisResult.estimated_cost) && (
              <div className="grid grid-cols-2 gap-4">
                {analysisResult.estimated_duration && (
                  <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4">
                    <div className="text-xs text-gray-500 mb-1">Estimated Duration</div>
                    <div className="text-white font-medium">{analysisResult.estimated_duration}</div>
                  </div>
                )}
                {analysisResult.estimated_cost && (
                  <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4">
                    <div className="text-xs text-gray-500 mb-1">Estimated Cost</div>
                    <div className="text-white font-medium">{analysisResult.estimated_cost}</div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    )
  }

  // List view
  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="font-serif text-2xl font-bold text-white">Case Analysis</h1>
          <p className="text-gray-500 text-sm mt-0.5">AI-powered legal case assessment</p>
        </div>
        <button
          onClick={() => setView('new')}
          className="bg-white text-black text-sm font-semibold px-5 py-2.5 rounded-xl hover:bg-gray-100 transition-colors"
        >
          + New Case
        </button>
      </div>

      {cases.length === 0 ? (
        <div className="text-center py-20 bg-zinc-900 border border-zinc-800 rounded-2xl">
          <div className="text-5xl mb-4">⚖️</div>
          <h2 className="font-serif text-xl font-bold text-white mb-2">No cases yet</h2>
          <p className="text-gray-500 text-sm mb-6">Create your first case to get AI-powered legal analysis</p>
          <button onClick={() => setView('new')} className="bg-white text-black font-semibold px-6 py-2.5 rounded-xl text-sm hover:bg-gray-100 transition-colors">
            Create Case
          </button>
        </div>
      ) : (
        <div className="space-y-3">
          {cases.map((c: any) => (
            <div
              key={c.id}
              className="bg-zinc-900 border border-zinc-800 rounded-2xl p-5 cursor-pointer hover:border-zinc-600 transition-colors"
              onClick={() => { setSelectedCase(c); setView('detail'); setAnalysisResult(c.ai_analysis || null); setAnalysisUnlocked(!!c.analysis_unlocked) }}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <div className="font-medium text-white">{c.title}</div>
                  <div className="text-gray-500 text-sm mt-1 truncate">{c.description}</div>
                  <div className="flex items-center gap-3 mt-2">
                    <span className="text-xs text-gray-600">{c.case_type}</span>
                    <span className="text-xs text-gray-600">·</span>
                    <span className="text-xs text-gray-600">{c.jurisdiction}</span>
                    <span className="text-xs text-gray-600">·</span>
                    <span className="text-xs text-gray-600">{formatDate(c.created_at)}</span>
                  </div>
                </div>
                <div className="ml-4 flex flex-col items-end gap-2">
                  <span className={`text-xs px-2.5 py-1 rounded-full capitalize ${
                    c.status === 'analyzed' ? 'bg-green-950 text-green-400' :
                    c.status === 'pending' ? 'bg-yellow-950 text-yellow-400' :
                    'bg-zinc-800 text-gray-400'
                  }`}>
                    {c.status}
                  </span>
                  {c.confidence_score && (
                    <span className="text-xs text-gray-600">{Math.round(c.confidence_score * 100)}% confidence</span>
                  )}
                  {c.ai_analysis && !c.analysis_unlocked && (
                    <span className="text-xs bg-yellow-950 text-yellow-400 px-2 py-0.5 rounded-full">🔒 Preview</span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
