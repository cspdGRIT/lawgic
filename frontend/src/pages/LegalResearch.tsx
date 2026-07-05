import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { researchAPI } from '../lib/api'

const CATEGORIES = [
  { id: 'statute', label: 'Statutes & Acts', icon: '📜' },
  { id: 'case', label: 'Case Law', icon: '⚖️' },
  { id: 'principle', label: 'Legal Principles', icon: '🧠' },
]

const QUICK_SEARCHES = [
  'Section 302 IPC Murder', 'Section 138 NI Act cheque bounce', 'Article 21 right to life',
  'Section 498A dowry harassment', 'RERA builder delay compensation', 'Consumer Protection Act 2019',
  'RTI Act exemptions', 'Section 376 rape punishment', 'Maneka Gandhi judgment', 'Shreya Singhal case',
]

interface SearchResult {
  title: string
  content: string
  category: string
  keywords?: string[]
  source?: string
}

export default function LegalResearch() {
  const [query, setQuery] = useState('')
  const [category, setCategory] = useState<string | undefined>(undefined)
  const [results, setResults] = useState<SearchResult[]>([])
  const [aiSummary, setAiSummary] = useState('')
  const [expandedIdx, setExpandedIdx] = useState<number | null>(null)

  const searchMutation = useMutation({
    mutationFn: (q: string) => researchAPI.search({ query: q, category }),
    onSuccess: (data: any) => {
      setResults(data.results || [])
      setAiSummary(data.ai_summary || '')
    },
  })

  function handleSearch(q?: string) {
    const searchQ = q || query
    if (!searchQ.trim()) return
    if (q) setQuery(q)
    searchMutation.mutate(searchQ)
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-6">
        <h1 className="font-serif text-2xl font-bold text-white">Legal Research</h1>
        <p className="text-gray-500 text-sm mt-0.5">Search Indian statutes, case law, and legal principles with AI</p>
      </div>

      {/* Search bar */}
      <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-5 mb-5">
        <div className="flex gap-3 mb-4">
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            placeholder="Search statutes, sections, judgments, legal principles..."
            className="flex-1 bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-2.5 text-white text-sm focus:outline-none focus:border-white transition-colors"
          />
          <button
            onClick={() => handleSearch()}
            disabled={!query.trim() || searchMutation.isPending}
            className="bg-white text-black font-semibold px-6 py-2.5 rounded-lg text-sm hover:bg-gray-100 transition-colors disabled:opacity-50"
          >
            {searchMutation.isPending ? 'Searching...' : 'Search'}
          </button>
        </div>

        <div className="flex flex-wrap gap-2">
          <span className="text-xs text-gray-600">Filter:</span>
          <button
            onClick={() => setCategory(undefined)}
            className={`text-xs px-2.5 py-1 rounded-full transition-colors ${!category ? 'bg-white text-black' : 'bg-zinc-800 text-gray-400 hover:text-white'}`}
          >
            All
          </button>
          {CATEGORIES.map((cat) => (
            <button
              key={cat.id}
              onClick={() => setCategory(cat.id === category ? undefined : cat.id)}
              className={`text-xs px-2.5 py-1 rounded-full transition-colors ${category === cat.id ? 'bg-white text-black' : 'bg-zinc-800 text-gray-400 hover:text-white'}`}
            >
              {cat.icon} {cat.label}
            </button>
          ))}
        </div>
      </div>

      {/* Quick searches */}
      {results.length === 0 && !searchMutation.isPending && (
        <div className="mb-8">
          <p className="text-xs text-gray-600 mb-3">Quick searches:</p>
          <div className="flex flex-wrap gap-2">
            {QUICK_SEARCHES.map((s) => (
              <button
                key={s}
                onClick={() => handleSearch(s)}
                className="text-xs bg-zinc-900 border border-zinc-800 text-gray-400 px-3 py-1.5 rounded-full hover:border-zinc-600 hover:text-white transition-colors"
              >
                {s}
              </button>
            ))}
          </div>
        </div>
      )}

      {searchMutation.isPending && (
        <div className="text-center py-12 text-gray-500">
          <div className="text-4xl mb-3 animate-pulse">🔍</div>
          <p>Searching Indian legal database...</p>
        </div>
      )}

      {/* AI Summary */}
      {aiSummary && (
        <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-5 mb-5">
          <div className="flex items-center gap-2 mb-3">
            <span className="text-sm">🤖</span>
            <span className="text-sm font-medium text-white">AI Legal Summary</span>
          </div>
          <p className="text-gray-400 text-sm leading-relaxed whitespace-pre-wrap">{aiSummary}</p>
        </div>
      )}

      {/* Results */}
      {results.length > 0 && (
        <div>
          <p className="text-xs text-gray-500 mb-3">{results.length} results for "{query}"</p>
          <div className="space-y-3">
            {results.map((result, i) => (
              <div key={i} className="bg-zinc-900 border border-zinc-800 rounded-2xl overflow-hidden">
                <div
                  className="p-5 cursor-pointer hover:bg-zinc-800 transition-colors"
                  onClick={() => setExpandedIdx(expandedIdx === i ? null : i)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-xs bg-zinc-800 text-gray-500 px-2 py-0.5 rounded-full capitalize">
                          {result.category}
                        </span>
                        {result.source && (
                          <span className="text-xs text-gray-600">{result.source}</span>
                        )}
                      </div>
                      <h3 className="font-medium text-white">{result.title}</h3>
                      <p className="text-gray-500 text-sm mt-1 line-clamp-2">{result.content}</p>
                    </div>
                    <span className="text-gray-600 ml-4 flex-shrink-0">{expandedIdx === i ? '▲' : '▼'}</span>
                  </div>
                </div>

                {expandedIdx === i && (
                  <div className="px-5 pb-5 border-t border-zinc-800 pt-4">
                    <p className="text-gray-300 text-sm leading-relaxed whitespace-pre-wrap">{result.content}</p>
                    {result.keywords?.length > 0 && (
                      <div className="mt-4 flex flex-wrap gap-1.5">
                        {result.keywords.map((kw) => (
                          <button
                            key={kw}
                            onClick={() => handleSearch(kw)}
                            className="text-xs bg-zinc-800 hover:bg-zinc-700 text-gray-400 px-2.5 py-1 rounded-full transition-colors"
                          >
                            {kw}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {searchMutation.isSuccess && results.length === 0 && (
        <div className="text-center py-12 bg-zinc-900 border border-zinc-800 rounded-2xl text-gray-500">
          <p>No results found. Try different keywords.</p>
        </div>
      )}
    </div>
  )
}
