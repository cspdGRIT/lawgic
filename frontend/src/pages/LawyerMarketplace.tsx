import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { lawyersAPI } from '../lib/api'
import { formatINR } from '../lib/utils'

const CITIES = ['All', 'Delhi', 'Mumbai', 'Bangalore', 'Chennai', 'Hyderabad', 'Kolkata', 'Ahmedabad', 'Pune']
const PRACTICE_AREAS = ['All', 'Criminal Law', 'Family Law', 'Property Law', 'Consumer Law', 'Corporate Law', 'Labour Law', 'Tax Law', 'IP Law', 'Constitutional Law']

function StarRating({ rating }: { rating: number }) {
  return (
    <span className="text-yellow-500 text-xs">
      {'★'.repeat(Math.floor(rating))}{'☆'.repeat(5 - Math.floor(rating))}
      <span className="text-gray-500 ml-1">{rating.toFixed(1)}</span>
    </span>
  )
}

function LawyerCard({ lawyer, onSelect }: { lawyer: any; onSelect: () => void }) {
  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-5 hover:border-zinc-600 transition-colors">
      <div className="flex items-start justify-between mb-3">
        <div>
          <div className="font-medium text-white">{lawyer.full_name}</div>
          <div className="text-gray-500 text-xs mt-0.5">{lawyer.city}, {lawyer.state}</div>
        </div>
        <div className="flex flex-col items-end gap-1">
          {lawyer.verified && (
            <span className="text-xs bg-green-950 text-green-400 px-2 py-0.5 rounded-full">Verified ✓</span>
          )}
          <StarRating rating={lawyer.rating} />
          <span className="text-gray-600 text-xs">({lawyer.review_count} reviews)</span>
        </div>
      </div>

      <div className="flex flex-wrap gap-1.5 mb-3">
        {lawyer.specializations?.slice(0, 3).map((s: string) => (
          <span key={s} className="text-xs bg-zinc-800 text-gray-400 px-2 py-0.5 rounded-full">{s}</span>
        ))}
      </div>

      <p className="text-gray-500 text-xs leading-relaxed mb-4 line-clamp-2">{lawyer.bio}</p>

      <div className="flex flex-wrap gap-1.5 mb-4">
        {lawyer.languages?.slice(0, 4).map((lang: string) => (
          <span key={lang} className="text-xs text-gray-600">🗣 {lang}</span>
        ))}
      </div>

      <div className="flex items-center justify-between pt-3 border-t border-zinc-800">
        <div>
          <div className="text-white text-sm font-medium">{formatINR(lawyer.consultation_fee)}</div>
          <div className="text-gray-600 text-xs">consultation</div>
        </div>
        <div className="text-right">
          <div className="text-gray-400 text-sm">{formatINR(lawyer.hourly_rate)}/hr</div>
          <div className="text-gray-600 text-xs">{lawyer.years_experience} yrs exp</div>
        </div>
        <button
          onClick={onSelect}
          className="bg-white text-black text-xs font-semibold px-4 py-2 rounded-lg hover:bg-gray-100 transition-colors"
        >
          Contact
        </button>
      </div>

      {lawyer.match_score && (
        <div className="mt-3 pt-3 border-t border-zinc-800">
          <div className="flex items-center justify-between">
            <span className="text-xs text-gray-500">AI Match Score</span>
            <span className="text-xs text-green-400 font-medium">{Math.round(lawyer.match_score * 100)}%</span>
          </div>
          {lawyer.match_reason && (
            <p className="text-xs text-gray-600 mt-1 italic">{lawyer.match_reason}</p>
          )}
        </div>
      )}
    </div>
  )
}

export default function LawyerMarketplace() {
  const [city, setCity] = useState('All')
  const [practiceArea, setPracticeArea] = useState('All')
  const [matchQuery, setMatchQuery] = useState('')
  const [matchResults, setMatchResults] = useState<any[]>([])
  const [selectedLawyer, setSelectedLawyer] = useState<any>(null)

  const { data: lawyers = [], isLoading } = useQuery({
    queryKey: ['lawyers', city, practiceArea],
    queryFn: () => lawyersAPI.list({
      city: city !== 'All' ? city : undefined,
      practice_area: practiceArea !== 'All' ? practiceArea : undefined,
    }),
    select: (d: any) => d || [],
  })

  const matchMutation = useMutation({
    mutationFn: (query: string) => lawyersAPI.match({ case_description: query }),
    onSuccess: (data: any) => setMatchResults(data.matches || []),
  })

  const displayLawyers = matchResults.length > 0 ? matchResults : lawyers

  if (selectedLawyer) {
    return (
      <div className="max-w-2xl mx-auto">
        <button onClick={() => setSelectedLawyer(null)} className="text-gray-500 hover:text-white text-sm mb-6 transition-colors">
          ← Back to search
        </button>
        <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <h2 className="font-serif text-2xl font-bold text-white">{selectedLawyer.full_name}</h2>
              <div className="text-gray-500 text-sm mt-1">{selectedLawyer.city}, {selectedLawyer.state}</div>
              <div className="mt-1"><StarRating rating={selectedLawyer.rating} /></div>
            </div>
            {selectedLawyer.verified && (
              <span className="text-xs bg-green-950 text-green-400 px-3 py-1 rounded-full">Bar Council Verified</span>
            )}
          </div>

          <p className="text-gray-400 text-sm leading-relaxed mb-5">{selectedLawyer.bio}</p>

          <div className="grid grid-cols-2 gap-4 mb-5">
            <div className="bg-zinc-800 rounded-xl p-4">
              <div className="text-xs text-gray-500 mb-1">Bar Council Number</div>
              <div className="text-white text-sm font-mono">{selectedLawyer.bar_council_number}</div>
            </div>
            <div className="bg-zinc-800 rounded-xl p-4">
              <div className="text-xs text-gray-500 mb-1">Experience</div>
              <div className="text-white text-sm">{selectedLawyer.years_experience} years</div>
            </div>
            <div className="bg-zinc-800 rounded-xl p-4">
              <div className="text-xs text-gray-500 mb-1">Consultation Fee</div>
              <div className="text-white text-sm">{formatINR(selectedLawyer.consultation_fee)}</div>
            </div>
            <div className="bg-zinc-800 rounded-xl p-4">
              <div className="text-xs text-gray-500 mb-1">Hourly Rate</div>
              <div className="text-white text-sm">{formatINR(selectedLawyer.hourly_rate)}/hr</div>
            </div>
          </div>

          <div className="mb-5">
            <div className="text-xs text-gray-500 mb-2">Practice Areas</div>
            <div className="flex flex-wrap gap-2">
              {selectedLawyer.practice_areas?.map((a: string) => (
                <span key={a} className="text-xs bg-zinc-800 text-gray-300 px-2.5 py-1 rounded-full">{a}</span>
              ))}
            </div>
          </div>

          <div className="mb-5">
            <div className="text-xs text-gray-500 mb-2">Courts</div>
            <div className="flex flex-wrap gap-2">
              {selectedLawyer.court_levels?.map((c: string) => (
                <span key={c} className="text-xs bg-zinc-800 text-gray-400 px-2.5 py-1 rounded-full">{c}</span>
              ))}
            </div>
          </div>

          <div className="mb-6">
            <div className="text-xs text-gray-500 mb-2">Languages</div>
            <div className="flex flex-wrap gap-2">
              {selectedLawyer.languages?.map((l: string) => (
                <span key={l} className="text-xs text-gray-400">🗣 {l}</span>
              ))}
            </div>
          </div>

          <div className="bg-zinc-800 rounded-xl p-4 text-center">
            <p className="text-gray-500 text-sm mb-3">Book a consultation with {selectedLawyer.full_name.split(' ')[1]}</p>
            <button className="bg-white text-black font-semibold px-8 py-2.5 rounded-xl text-sm hover:bg-gray-100 transition-colors">
              Schedule Consultation — {formatINR(selectedLawyer.consultation_fee)}
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-5xl mx-auto">
      <div className="mb-6">
        <h1 className="font-serif text-2xl font-bold text-white">Lawyer Marketplace</h1>
        <p className="text-gray-500 text-sm mt-0.5">30+ verified advocates across India, AI-matched to your case</p>
      </div>

      {/* AI Match */}
      <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-5 mb-6">
        <div className="flex items-center gap-2 mb-3">
          <span className="text-lg">🤖</span>
          <span className="font-medium text-white text-sm">AI Lawyer Matching</span>
        </div>
        <div className="flex gap-3">
          <input
            value={matchQuery}
            onChange={(e) => setMatchQuery(e.target.value)}
            placeholder="Describe your legal situation (e.g., 'cheque bounce case in Mumbai, budget ₹5000/hr')"
            className="flex-1 bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-2.5 text-white text-sm focus:outline-none focus:border-white transition-colors"
            onKeyDown={(e) => e.key === 'Enter' && matchMutation.mutate(matchQuery)}
          />
          <button
            onClick={() => matchMutation.mutate(matchQuery)}
            disabled={!matchQuery.trim() || matchMutation.isPending}
            className="bg-white text-black font-semibold px-5 py-2.5 rounded-lg text-sm hover:bg-gray-100 transition-colors disabled:opacity-50"
          >
            {matchMutation.isPending ? 'Matching...' : 'Find Match'}
          </button>
          {matchResults.length > 0 && (
            <button onClick={() => setMatchResults([])} className="text-gray-500 hover:text-white text-sm transition-colors px-2">
              Clear
            </button>
          )}
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-4 mb-6">
        <div>
          <label className="text-xs text-gray-500 block mb-1.5">City</label>
          <div className="flex flex-wrap gap-1.5">
            {CITIES.map((c) => (
              <button
                key={c}
                onClick={() => { setCity(c); setMatchResults([]) }}
                className={`text-xs px-3 py-1.5 rounded-full transition-colors ${
                  city === c ? 'bg-white text-black' : 'bg-zinc-900 border border-zinc-800 text-gray-400 hover:text-white'
                }`}
              >
                {c}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Practice area filter */}
      <div className="flex gap-2 flex-wrap mb-6">
        {PRACTICE_AREAS.map((p) => (
          <button
            key={p}
            onClick={() => { setPracticeArea(p); setMatchResults([]) }}
            className={`text-xs px-3 py-1.5 rounded-full transition-colors ${
              practiceArea === p ? 'bg-white text-black' : 'bg-zinc-900 border border-zinc-800 text-gray-400 hover:text-white'
            }`}
          >
            {p}
          </button>
        ))}
      </div>

      {matchResults.length > 0 && (
        <div className="flex items-center gap-2 mb-4 text-sm text-gray-400">
          <span className="text-green-500">✓</span>
          Showing {matchResults.length} AI-matched lawyers for your case
        </div>
      )}

      {isLoading ? (
        <div className="text-center py-12 text-gray-500">Loading lawyers...</div>
      ) : displayLawyers.length === 0 ? (
        <div className="text-center py-12 bg-zinc-900 border border-zinc-800 rounded-2xl text-gray-500">
          No lawyers found for the selected filters.
        </div>
      ) : (
        <div className="grid sm:grid-cols-2 gap-4">
          {displayLawyers.map((lawyer: any) => (
            <LawyerCard key={lawyer.id} lawyer={lawyer} onSelect={() => setSelectedLawyer(lawyer)} />
          ))}
        </div>
      )}
    </div>
  )
}
