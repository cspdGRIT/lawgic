import { useState, useRef, useEffect, useCallback } from 'react'
import { generateSessionId, getWSUrl, getAccessToken } from '../lib/api'
import { useSpeechRecognition } from '../hooks/useSpeechRecognition'
import { clsx } from 'clsx'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  agent?: string
  confidence?: number
  loading?: boolean
}

const SUGGESTIONS = [
  'What are my rights if I receive a cheque bounce notice?',
  'How do I file an FIR if police refuse to register it?',
  'My builder delayed possession by 2 years. What can I do under RERA?',
  'Explain Section 498A of IPC',
  'How do I draft a legal notice for property dispute?',
  'What documents do I need for a mutual consent divorce?',
]

export default function AiAssistant() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content: 'Namaste! I am Lawgic AI, your Indian legal assistant powered by Claude AI and a 6-agent system. I can help you with case analysis, legal research, document drafting, lawyer matching, and translation across 22 Indian languages. What legal matter can I assist you with today?',
      agent: 'Lawgic AI',
    },
  ])
  const [input, setInput] = useState('')
  const [connected, setConnected] = useState(false)
  const [sessionId] = useState(() => generateSessionId())
  const wsRef = useRef<WebSocket | null>(null)
  const bottomRef = useRef<HTMLDivElement>(null)
  const baseInputRef = useRef('')
  const { listening, start, stop, supported: micSupported } = useSpeechRecognition((r) => {
    const combined = (baseInputRef.current ? baseInputRef.current + ' ' : '') + r.transcript
    setInput(combined)
    if (r.isFinal) baseInputRef.current = combined
  })
  function toggleMic() {
    if (listening) { stop(); return }
    baseInputRef.current = input
    start()
  }
  const inputRef = useRef<HTMLTextAreaElement>(null)

  const scrollToBottom = () => bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  useEffect(scrollToBottom, [messages])

  const connectWS = useCallback(() => {
    const token = getAccessToken()
    if (!token) return

    const ws = new WebSocket(getWSUrl(sessionId, token))
    wsRef.current = ws

    ws.onopen = () => setConnected(true)
    ws.onclose = () => {
      setConnected(false)
      setTimeout(connectWS, 3000)
    }

    ws.onmessage = (evt) => {
      const data = JSON.parse(evt.data)

      if (data.type === 'typing') {
        setMessages((prev) => {
          const last = prev[prev.length - 1]
          if (last?.loading) return prev
          return [...prev, { id: Date.now().toString(), role: 'assistant', content: '', loading: true }]
        })
      } else if (data.type === 'token') {
        setMessages((prev) => {
          const last = prev[prev.length - 1]
          if (last?.loading || last?.role === 'assistant') {
            return prev.map((m, i) =>
              i === prev.length - 1 ? { ...m, content: m.content + data.content, loading: false } : m
            )
          }
          return prev
        })
      } else if (data.type === 'done') {
        setMessages((prev) =>
          prev.map((m, i) =>
            i === prev.length - 1
              ? { ...m, loading: false, agent: data.agent, confidence: data.confidence_score }
              : m
          )
        )
      } else if (data.type === 'error') {
        setMessages((prev) => {
          const filtered = prev.filter((m) => !m.loading)
          return [...filtered, { id: Date.now().toString(), role: 'assistant', content: `Error: ${data.content}` }]
        })
      }
    }
  }, [sessionId])

  useEffect(() => {
    connectWS()
    return () => wsRef.current?.close()
  }, [connectWS])

  function sendMessage() {
    const text = input.trim()
    if (!text || !connected) return

    setMessages((prev) => [...prev, { id: Date.now().toString(), role: 'user', content: text }])
    wsRef.current?.send(JSON.stringify({ message: text }))
    setInput('')
    inputRef.current?.focus()
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div className="flex flex-col h-[calc(100vh-5rem)] max-w-3xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-4 flex-shrink-0">
        <div>
          <h1 className="font-serif text-2xl font-bold text-white">AI Legal Assistant</h1>
          <p className="text-gray-500 text-sm">6-agent system · Specialized in Indian law</p>
        </div>
        <div className={clsx('flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-full', connected ? 'bg-green-950 text-green-400' : 'bg-zinc-800 text-gray-500')}>
          <span className={clsx('w-1.5 h-1.5 rounded-full', connected ? 'bg-green-500 animate-pulse' : 'bg-gray-600')} />
          {connected ? 'Live' : 'Connecting...'}
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-4 pb-4">
        {messages.map((msg) => (
          <div key={msg.id} className={clsx('flex', msg.role === 'user' ? 'justify-end' : 'justify-start')}>
            <div className={clsx('max-w-[80%]', msg.role === 'user' ? 'items-end' : 'items-start', 'flex flex-col gap-1')}>
              {msg.role === 'assistant' && msg.agent && (
                <span className="text-xs text-gray-600 ml-1">{msg.agent}</span>
              )}
              <div
                className={clsx(
                  'rounded-2xl px-4 py-3 text-sm leading-relaxed',
                  msg.role === 'user'
                    ? 'bg-white text-black rounded-br-sm'
                    : 'bg-zinc-900 border border-zinc-800 text-gray-200 rounded-bl-sm'
                )}
              >
                {msg.loading ? (
                  <span className="flex gap-1 items-center h-5">
                    <span className="w-1.5 h-1.5 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                    <span className="w-1.5 h-1.5 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                    <span className="w-1.5 h-1.5 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                  </span>
                ) : (
                  <span className="whitespace-pre-wrap">{msg.content}</span>
                )}
              </div>
              {msg.confidence !== undefined && (
                <span className="text-xs text-gray-700 ml-1">
                  Confidence: {Math.round(msg.confidence * 100)}%
                </span>
              )}
            </div>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      {/* Suggestions */}
      {messages.length <= 1 && (
        <div className="flex-shrink-0 mb-3">
          <p className="text-xs text-gray-600 mb-2">Try asking:</p>
          <div className="flex flex-wrap gap-2">
            {SUGGESTIONS.map((s) => (
              <button
                key={s}
                onClick={() => setInput(s)}
                className="text-xs bg-zinc-900 border border-zinc-800 text-gray-400 px-3 py-1.5 rounded-full hover:border-zinc-600 hover:text-white transition-colors"
              >
                {s}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input */}
      <div className="flex-shrink-0 bg-zinc-900 border border-zinc-800 rounded-2xl p-3 flex gap-2 items-end">
        <textarea
          ref={inputRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about your legal matter... (Enter to send)"
          rows={1}
          className="flex-1 bg-transparent text-white text-sm resize-none outline-none placeholder-gray-600 max-h-32"
          style={{ minHeight: '24px' }}
        />
        {micSupported && (
          <button
            onClick={toggleMic}
            title={listening ? 'Stop dictating' : 'Speak instead of typing'}
            className={`w-9 h-9 rounded-xl flex items-center justify-center text-sm flex-shrink-0 transition-colors ${
              listening ? 'bg-red-600 text-white animate-pulse' : 'bg-zinc-800 text-gray-300 hover:bg-zinc-700'
            }`}
          >
            🎤
          </button>
        )}
        <button
          onClick={sendMessage}
          disabled={!input.trim() || !connected}
          className="bg-white text-black text-xs font-semibold px-4 py-2 rounded-xl hover:bg-gray-100 transition-colors disabled:opacity-40 disabled:cursor-not-allowed flex-shrink-0"
        >
          Send
        </button>
      </div>
    </div>
  )
}
