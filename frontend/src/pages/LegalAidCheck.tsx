import { useState } from 'react'
import { legalAidAPI } from '../lib/api'

interface Result {
  eligible: boolean
  matched_criteria: string[]
  guidance: string
  helpline: string
  website: string
}

const CRITERIA: { key: string; label: string }[] = [
  { key: 'is_woman', label: 'I am a woman' },
  { key: 'is_child', label: 'This concerns a child (under 18)' },
  { key: 'is_sc_st', label: 'I belong to a Scheduled Caste or Scheduled Tribe' },
  { key: 'is_disabled', label: 'I have a disability' },
  { key: 'is_industrial_workman', label: 'I am an industrial workman' },
  { key: 'is_victim_of_trafficking_or_begar', label: 'I am a victim of trafficking or forced labour' },
  { key: 'is_victim_of_mass_disaster', label: 'I am affected by a flood, drought, earthquake, industrial disaster, or ethnic/caste violence' },
  { key: 'is_in_custody', label: 'I am (or a family member is) in custody, a protective home, or a psychiatric institution' },
]

export default function LegalAidCheck() {
  const [form, setForm] = useState<Record<string, boolean>>({})
  const [income, setIncome] = useState('')
  const [forum, setForum] = useState<'high_court_or_below' | 'supreme_court'>('high_court_or_below')
  const [result, setResult] = useState<Result | null>(null)
  const [loading, setLoading] = useState(false)

  async function handleCheck() {
    setLoading(true)
    try {
      const data = await legalAidAPI.checkEligibility({
        ...form,
        annual_income_rupees: income ? Number(income) : undefined,
        forum,
      })
      setResult(data)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="text-center mb-8">
        <h1 className="font-serif text-2xl font-bold text-white mb-2">Free Legal Aid Check</h1>
        <p className="text-gray-500 text-sm">
          India runs a real, government-funded free legal aid program — the National Legal Services
          Authority (NALSA). Many people who qualify have never heard of it. Answer a few questions to
          see if you likely do.
        </p>
      </div>

      {!result ? (
        <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6 space-y-4">
          <p className="text-xs text-gray-600">
            Nothing here is saved or sent anywhere except to compute this result — these answers aren't stored.
          </p>
          {CRITERIA.map((c) => (
            <label key={c.key} className="flex items-center gap-3 text-sm text-gray-300 cursor-pointer">
              <input
                type="checkbox"
                checked={!!form[c.key]}
                onChange={(e) => setForm({ ...form, [c.key]: e.target.checked })}
                className="w-4 h-4 accent-white"
              />
              {c.label}
            </label>
          ))}

          <div className="pt-2">
            <label className="block text-sm text-gray-400 mb-1.5">Your annual income (₹, optional)</label>
            <input
              type="number"
              value={income}
              onChange={(e) => setIncome(e.target.value)}
              placeholder="e.g. 200000"
              className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-2.5 text-white text-sm focus:outline-none focus:border-white transition-colors"
            />
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-1.5">Which court would your matter go to?</label>
            <select
              value={forum}
              onChange={(e) => setForum(e.target.value as typeof forum)}
              className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-2.5 text-white text-sm focus:outline-none focus:border-white transition-colors"
            >
              <option value="high_court_or_below">District Court / High Court</option>
              <option value="supreme_court">Supreme Court</option>
            </select>
          </div>

          <button
            onClick={handleCheck}
            disabled={loading}
            className="w-full bg-white text-black font-semibold py-3 rounded-lg text-sm hover:bg-gray-100 transition-colors disabled:opacity-50"
          >
            {loading ? 'Checking...' : 'Check eligibility'}
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          <div className={`rounded-2xl p-6 text-center border ${
            result.eligible ? 'bg-green-950 border-green-800' : 'bg-zinc-900 border-zinc-800'
          }`}>
            <div className="text-4xl mb-3">{result.eligible ? '✅' : 'ℹ️'}</div>
            <h2 className="font-serif text-lg font-bold text-white mb-2">
              {result.eligible ? 'You likely qualify for free legal aid' : 'You may not automatically qualify'}
            </h2>
            <p className="text-gray-400 text-sm">{result.guidance}</p>
          </div>

          {result.matched_criteria.length > 0 && (
            <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-5">
              <h3 className="font-medium text-white mb-3 text-sm">Matched criteria</h3>
              <ul className="space-y-1.5">
                {result.matched_criteria.map((c, i) => (
                  <li key={i} className="text-gray-400 text-sm flex gap-2"><span className="text-green-500 flex-shrink-0">✓</span>{c}</li>
                ))}
              </ul>
            </div>
          )}

          <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-5">
            <h3 className="font-medium text-white mb-2 text-sm">Contact NALSA directly</h3>
            <p className="text-gray-400 text-sm mb-3">
              This check is guidance, not a determination — only your local Legal Services Authority can confirm
              eligibility and assign you a free lawyer.
            </p>
            <div className="flex flex-wrap gap-3 text-sm">
              <a href={`tel:${result.helpline}`} className="bg-white text-black font-semibold px-4 py-2 rounded-lg">
                Call {result.helpline} (toll-free)
              </a>
              <a href={result.website} target="_blank" rel="noreferrer" className="bg-zinc-800 border border-zinc-700 text-white px-4 py-2 rounded-lg">
                Visit nalsa.gov.in
              </a>
            </div>
          </div>

          <button
            onClick={() => { setResult(null); setForm({}); setIncome('') }}
            className="text-sm text-gray-500 hover:text-white transition-colors"
          >
            ← Check again
          </button>
        </div>
      )}
    </div>
  )
}
