import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { documentsAPI, getSSEUrl, getAccessToken } from '../lib/api'
import { formatDate } from '../lib/utils'

type Step = 1 | 2 | 3

const CATEGORIES = ['All', 'Criminal', 'Civil', 'Family', 'Property', 'Consumer', 'Corporate', 'Constitutional']

function getTemplateCategory(id: string): string {
  if (['bail_application', 'anticipatory_bail', 'fir_complaint', 'vakalatnama'].includes(id)) return 'Criminal'
  if (['rental_agreement', 'sale_deed', 'leave_license', 'agreement_to_sell'].includes(id)) return 'Property'
  if (['divorce_mutual', 'divorce_contested', 'child_custody'].includes(id)) return 'Family'
  if (['consumer_complaint', 'rera_complaint'].includes(id)) return 'Consumer'
  if (['nda', 'employment_contract', 'mou', 'partnership_deed', 'general_poa'].includes(id)) return 'Corporate'
  if (['writ_habeas_corpus', 'writ_mandamus', 'pil', 'writ_certiorari'].includes(id)) return 'Constitutional'
  return 'Civil'
}

export default function DocumentGenerator() {
  const [step, setStep] = useState<Step>(1)
  const [selectedTemplate, setSelectedTemplate] = useState<any>(null)
  const [formData, setFormData] = useState<Record<string, string>>({})
  const [streaming, setStreaming] = useState('')
  const [generatedDocId, setGeneratedDocId] = useState<number | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [category, setCategory] = useState('All')
  const [viewDoc, setViewDoc] = useState<any>(null)

  const { data: templates = [] } = useQuery({
    queryKey: ['templates'],
    queryFn: () => documentsAPI.getTemplates(),
    select: (d: any) => d || [],
  })

  const { data: documents = [] } = useQuery({
    queryKey: ['documents'],
    queryFn: () => documentsAPI.list(),
    select: (d: any) => d || [],
  })

  const filtered = category === 'All' ? templates : templates.filter((t: any) => getTemplateCategory(t.id) === category)

  async function handleGenerate() {
    if (!selectedTemplate) return
    setIsGenerating(true)
    setStreaming('')
    setStep(3)

    const token = getAccessToken()
    try {
      const response = await fetch(getSSEUrl('/api/v1/documents/generate'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ template_id: selectedTemplate.id, form_data: formData }),
      })

      if (response.status === 403) {
        const body = await response.json().catch(() => ({}))
        if (body?.detail?.error === 'access_pending') {
          window.dispatchEvent(new Event('lawgic:access-pending'))
          return
        }
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
          if (data.type === 'done') setGeneratedDocId(data.document_id)
        }
      }
    } catch (err) {
      console.error(err)
    } finally {
      setIsGenerating(false)
    }
  }

  function handleReset() {
    setStep(1)
    setSelectedTemplate(null)
    setFormData({})
    setStreaming('')
    setGeneratedDocId(null)
  }

  function downloadDoc() {
    const blob = new Blob([streaming], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${selectedTemplate?.name || 'document'}.txt`
    a.click()
  }

  if (viewDoc) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center gap-3 mb-6">
          <button onClick={() => setViewDoc(null)} className="text-gray-500 hover:text-white transition-colors text-sm">← Back</button>
          <h1 className="font-serif text-xl font-bold text-white">{viewDoc.title}</h1>
        </div>
        <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6">
          <pre className="text-gray-300 text-sm whitespace-pre-wrap leading-relaxed font-mono">{viewDoc.content}</pre>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-5xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="font-serif text-2xl font-bold text-white">Document Generator</h1>
          <p className="text-gray-500 text-sm mt-0.5">AI-drafted legal documents for Indian courts</p>
        </div>
        {step > 1 && (
          <button onClick={handleReset} className="text-gray-500 hover:text-white text-sm transition-colors">
            ← Start over
          </button>
        )}
      </div>

      {/* Step indicator */}
      <div className="flex items-center gap-4 mb-8">
        {[{ n: 1, label: 'Choose template' }, { n: 2, label: 'Fill details' }, { n: 3, label: 'Generated document' }].map(({ n, label }) => (
          <div key={n} className="flex items-center gap-2">
            <div className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold ${
              step === n ? 'bg-white text-black' :
              step > n ? 'bg-green-900 text-green-400' :
              'bg-zinc-800 text-gray-600'
            }`}>
              {step > n ? '✓' : n}
            </div>
            <span className={`text-sm hidden md:block ${step === n ? 'text-white' : 'text-gray-600'}`}>{label}</span>
            {n < 3 && <span className="text-gray-700 ml-2">→</span>}
          </div>
        ))}
      </div>

      {/* Step 1: Templates */}
      {step === 1 && (
        <div>
          <div className="flex gap-2 flex-wrap mb-5">
            {CATEGORIES.map((cat) => (
              <button
                key={cat}
                onClick={() => setCategory(cat)}
                className={`text-xs px-3 py-1.5 rounded-full transition-colors ${
                  category === cat ? 'bg-white text-black' : 'bg-zinc-900 border border-zinc-800 text-gray-400 hover:text-white'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {filtered.map((t: any) => (
              <button
                key={t.id}
                onClick={() => { setSelectedTemplate(t); setStep(2) }}
                className="bg-zinc-900 border border-zinc-800 rounded-xl p-4 text-left hover:border-zinc-600 transition-colors"
              >
                <div className="font-medium text-white text-sm mb-1">{t.name}</div>
                <div className="text-gray-500 text-xs leading-relaxed">{t.description}</div>
                {t.required_fields?.length > 0 && (
                  <div className="mt-2 text-xs text-gray-700">{t.required_fields.length} fields required</div>
                )}
              </button>
            ))}
          </div>

          {/* My documents */}
          {documents.length > 0 && (
            <div className="mt-10">
              <h2 className="text-sm font-medium text-gray-400 uppercase tracking-widest mb-4">My Documents</h2>
              <div className="space-y-2">
                {documents.map((d: any) => (
                  <div
                    key={d.id}
                    className="bg-zinc-900 border border-zinc-800 rounded-xl p-4 flex items-center justify-between cursor-pointer hover:border-zinc-600 transition-colors"
                    onClick={() => setViewDoc(d)}
                  >
                    <div>
                      <div className="font-medium text-white text-sm">{d.title}</div>
                      <div className="text-gray-500 text-xs mt-0.5">{d.document_type} · {formatDate(d.created_at)}</div>
                    </div>
                    {d.is_ai_generated && (
                      <span className="text-xs bg-zinc-800 text-gray-400 px-2 py-0.5 rounded-full ml-3">AI</span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Step 2: Form */}
      {step === 2 && selectedTemplate && (
        <div className="max-w-2xl">
          <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6 mb-5">
            <h2 className="font-medium text-white mb-1">{selectedTemplate.name}</h2>
            <p className="text-gray-500 text-sm">{selectedTemplate.description}</p>
          </div>

          <div className="space-y-4 mb-6">
            {selectedTemplate.required_fields?.map((field: string) => {
              const label = field.replace(/_/g, ' ').replace(/\b\w/g, (c: string) => c.toUpperCase())
              const isLong = field.includes('fact') || field.includes('detail') || field.includes('ground') || field.includes('description')
              return (
                <div key={field}>
                  <label className="block text-sm text-gray-400 mb-1.5">{label}</label>
                  {isLong ? (
                    <textarea
                      value={formData[field] || ''}
                      onChange={(e) => setFormData({ ...formData, [field]: e.target.value })}
                      rows={3}
                      className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-2.5 text-white text-sm focus:outline-none focus:border-white transition-colors resize-none"
                      placeholder={`Enter ${label.toLowerCase()}...`}
                    />
                  ) : (
                    <input
                      value={formData[field] || ''}
                      onChange={(e) => setFormData({ ...formData, [field]: e.target.value })}
                      className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-2.5 text-white text-sm focus:outline-none focus:border-white transition-colors"
                      placeholder={`Enter ${label.toLowerCase()}...`}
                    />
                  )}
                </div>
              )
            })}
          </div>

          <button
            onClick={handleGenerate}
            className="w-full bg-white text-black font-semibold py-3 rounded-xl text-sm hover:bg-gray-100 transition-colors"
          >
            Generate Document with AI →
          </button>
        </div>
      )}

      {/* Step 3: Result */}
      {step === 3 && (
        <div>
          {isGenerating && !streaming && (
            <div className="text-center py-12 text-gray-500">
              <div className="text-4xl mb-4 animate-bounce">📄</div>
              <p>AI is drafting your document...</p>
            </div>
          )}

          {streaming && (
            <div>
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  {isGenerating && <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />}
                  <span className="text-sm text-gray-400">{isGenerating ? 'Generating...' : 'Document ready'}</span>
                </div>
                {!isGenerating && (
                  <button onClick={downloadDoc} className="text-xs bg-zinc-800 hover:bg-zinc-700 text-gray-300 px-3 py-1.5 rounded-lg transition-colors">
                    Download .txt
                  </button>
                )}
              </div>
              <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6 max-h-[60vh] overflow-y-auto">
                <pre className="text-gray-300 text-sm whitespace-pre-wrap leading-relaxed font-mono">
                  {streaming}
                  {isGenerating && <span className="animate-pulse">▋</span>}
                </pre>
              </div>
              {!isGenerating && (
                <div className="flex gap-3 mt-4">
                  <button onClick={handleReset} className="flex-1 bg-zinc-900 border border-zinc-800 text-white font-semibold py-3 rounded-xl text-sm hover:bg-zinc-800 transition-colors">
                    Generate Another
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
