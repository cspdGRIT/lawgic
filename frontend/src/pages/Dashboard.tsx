import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { useAuthStore } from '../store'
import { casesAPI, documentsAPI } from '../lib/api'
import { formatDate } from '../lib/utils'

// roles omitted = shown to everyone — mirrors the same client-only split as the sidebar.
const QUICK_ACTIONS = [
  { label: 'Describe Your Issue', icon: '🧭', href: '/issue-navigator', desc: 'Get an action plan', roles: ['client'] },
  { label: 'Analyze a Case', icon: '⚖️', href: '/cases', desc: 'Get AI-powered case strategy' },
  { label: 'Draft Document', icon: '📄', href: '/documents', desc: '30+ Indian legal templates' },
  { label: 'Ask AI Lawyer', icon: '🤖', href: '/assistant', desc: 'Chat with Lawgic AI' },
  { label: 'Find Advocate', icon: '👨‍⚖️', href: '/lawyers', desc: 'AI-matched lawyers', roles: ['client'] },
  { label: 'Legal Research', icon: '🔍', href: '/research', desc: 'Search statutes & cases' },
  { label: 'Learn Law', icon: '📚', href: '/education', desc: '10 courses on Indian law' },
]

function StatCard({ value, label, icon }: { value: string | number; label: string; icon: string }) {
  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5">
      <div className="text-2xl mb-1">{icon}</div>
      <div className="font-serif text-3xl font-bold text-white mt-2">{value}</div>
      <div className="text-gray-500 text-sm mt-0.5">{label}</div>
    </div>
  )
}

export default function Dashboard() {
  const user = useAuthStore((s) => s.user)

  const { data: cases = [] } = useQuery({
    queryKey: ['cases'],
    queryFn: () => casesAPI.list(),
    select: (d: any) => d?.items || d || [],
  })

  const { data: documents = [] } = useQuery({
    queryKey: ['documents'],
    queryFn: () => documentsAPI.list(),
    select: (d: any) => d || [],
  })

  const hour = new Date().getHours()
  const greeting = hour < 12 ? 'Good morning' : hour < 18 ? 'Good afternoon' : 'Good evening'

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Welcome */}
      <div>
        <h1 className="font-serif text-3xl font-bold text-white">
          {greeting}, {user?.full_name?.split(' ')[0] || 'there'}
        </h1>
        <p className="text-gray-500 mt-1 text-sm">Your legal command center</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard value={cases.length} label="Cases" icon="⚖️" />
        <StatCard value={documents.length} label="Documents" icon="📄" />
        <StatCard
          value={cases.filter((c: any) => c.status === 'analyzed').length}
          label="Analyzed"
          icon="🔍"
        />
        <StatCard value="Active" label="Subscription" icon="✅" />
      </div>

      {/* Quick actions */}
      <div>
        <h2 className="text-sm font-medium text-gray-400 uppercase tracking-widest mb-4">Quick actions</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {QUICK_ACTIONS.filter((a) => !a.roles || a.roles.includes(user?.user_type as string)).map((action) => (
            <Link
              key={action.label}
              to={action.href}
              className="bg-zinc-900 border border-zinc-800 rounded-xl p-4 hover:border-zinc-600 transition-colors group"
            >
              <div className="text-2xl mb-3">{action.icon}</div>
              <div className="font-medium text-white text-sm group-hover:text-white">{action.label}</div>
              <div className="text-gray-600 text-xs mt-0.5">{action.desc}</div>
            </Link>
          ))}
        </div>
      </div>

      {/* Recent cases + documents */}
      <div className="grid md:grid-cols-2 gap-6">
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-medium text-gray-400 uppercase tracking-widest">Recent Cases</h2>
            <Link to="/cases" className="text-xs text-gray-500 hover:text-white transition-colors">View all →</Link>
          </div>
          <div className="space-y-2">
            {cases.length === 0 && (
              <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 text-center text-gray-600 text-sm">
                No cases yet.{' '}
                <Link to="/cases" className="text-white hover:underline">
                  Analyze your first case
                </Link>
              </div>
            )}
            {cases.slice(0, 4).map((c: any) => (
              <div key={c.id} className="bg-zinc-900 border border-zinc-800 rounded-xl p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="font-medium text-white text-sm truncate">{c.title}</div>
                    <div className="text-gray-500 text-xs mt-0.5">{c.case_type} · {formatDate(c.created_at)}</div>
                  </div>
                  <span className={`ml-3 text-xs px-2 py-0.5 rounded-full capitalize flex-shrink-0 ${
                    c.status === 'analyzed' ? 'bg-green-950 text-green-400' :
                    c.status === 'pending' ? 'bg-yellow-950 text-yellow-400' :
                    'bg-zinc-800 text-gray-400'
                  }`}>
                    {c.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-medium text-gray-400 uppercase tracking-widest">Recent Documents</h2>
            <Link to="/documents" className="text-xs text-gray-500 hover:text-white transition-colors">View all →</Link>
          </div>
          <div className="space-y-2">
            {documents.length === 0 && (
              <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 text-center text-gray-600 text-sm">
                No documents yet.{' '}
                <Link to="/documents" className="text-white hover:underline">
                  Draft your first document
                </Link>
              </div>
            )}
            {documents.slice(0, 4).map((d: any) => (
              <div key={d.id} className="bg-zinc-900 border border-zinc-800 rounded-xl p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="font-medium text-white text-sm truncate">{d.title}</div>
                    <div className="text-gray-500 text-xs mt-0.5">{d.document_type} · {formatDate(d.created_at)}</div>
                  </div>
                  {d.is_ai_generated && (
                    <span className="ml-3 text-xs bg-zinc-800 text-gray-400 px-2 py-0.5 rounded-full flex-shrink-0">AI</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Info banner */}
      <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-5 flex items-start gap-4">
        <div className="text-2xl">⚠️</div>
        <div>
          <div className="font-medium text-white text-sm">Legal disclaimer</div>
          <div className="text-gray-500 text-xs mt-1 leading-relaxed">
            Lawgic provides AI-assisted legal information and document drafting. This is not a substitute for qualified legal advice. For complex matters or court appearances, always consult a licensed advocate.
          </div>
        </div>
      </div>
    </div>
  )
}
