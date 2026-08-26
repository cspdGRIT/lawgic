import { Link } from 'react-router-dom'
import { useAuthStore } from '../store'

const FEATURES = [
  {
    icon: '🧭',
    title: 'Describe Your Issue',
    desc: "Tell us what's happening in your own words, in any language. We tell you which forum to approach, what to file, what it costs, and match you with lawyers — no legal knowledge required.",
  },
  {
    icon: '⚖️',
    title: 'AI Case Analysis',
    desc: 'Upload your case facts and get win probability, legal strategy, relevant statutes, and next steps — in minutes.',
  },
  {
    icon: '📄',
    title: '30+ Legal Templates',
    desc: 'From Vakalatnama to PIL, generate court-ready documents for any Indian court, fully customized to your case.',
  },
  {
    icon: '🤖',
    title: '6 Specialized AI Agents',
    desc: 'Intent classifier routes your query to specialized agents — case analysis, research, translation, and more.',
  },
  {
    icon: '⚡',
    title: 'Legal Research Engine',
    desc: 'Search IPC, CrPC, CPC, Consumer Protection Act, RERA, RTI and 100+ Indian statutes with AI-powered summaries.',
  },
  {
    icon: '👨‍⚖️',
    title: 'Lawyer Marketplace',
    desc: 'AI matches you with the right advocate from 30+ verified lawyers across Delhi, Mumbai, Bangalore, Chennai, and more.',
  },
  {
    icon: '🤝',
    title: 'Free Legal Aid Check',
    desc: 'See in two minutes if you qualify for NALSA free legal aid — a real, government-funded program most people who qualify have never heard of.',
  },
  {
    icon: '📖',
    title: 'Know Your Rights',
    desc: 'Free, shareable plain-language guides on your rights during arrest, at work, as a tenant, and more — no account needed.',
  },
  {
    icon: '🇮🇳',
    title: '22 Indian Languages',
    desc: 'Access legal information and translate documents in all 22 scheduled Indian languages including Hindi, Tamil, and Bengali.',
  },
]

const STATS = [
  { value: '50,000+', label: 'Cases Analyzed' },
  { value: '30+', label: 'Document Templates' },
  { value: '22', label: 'Indian Languages' },
  { value: '98%', label: 'Accuracy Rate' },
]

const HOW_IT_WORKS = [
  { step: '01', title: 'Describe your situation', desc: 'Tell our AI about your legal problem in plain language — no legal jargon needed.' },
  { step: '02', title: 'AI agents analyze', desc: 'Our 6-agent LangGraph system routes your query to the right specialist AI for deep analysis.' },
  { step: '03', title: 'Get actionable guidance', desc: 'Receive case strategy, documents, and lawyer recommendations — ready to act immediately.' },
]

// Mirrors backend/app/api/v1/payments.py PLANS_META exactly — this used to show
// different prices/limits than the real checkout on /pricing, which is the kind of
// mismatch that breaks trust the moment someone compares the two.
const PRICING = [
  {
    name: 'Free',
    price: '₹0',
    period: 'forever',
    features: ['10 AI queries/month', '3 cases', '5 document drafts', '5 legal research searches', 'Community support'],
    cta: 'Get started',
    highlight: false,
  },
  {
    name: 'Pro',
    price: '₹499',
    period: 'per month',
    features: ['500 AI queries/month', '50 cases', '100 document drafts', '100 legal research searches', 'Priority support', 'Indian Kanoon case search'],
    cta: 'Start free trial',
    highlight: true,
  },
  {
    name: 'Firm',
    price: '₹1,999',
    period: 'per month',
    features: ['Unlimited AI queries', 'Unlimited cases', 'Unlimited documents', 'Unlimited research', 'Dedicated support'],
    cta: 'Contact sales',
    highlight: false,
  },
]

export default function Landing() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)

  return (
    <div className="min-h-screen bg-black text-white">
      {/* Nav */}
      <nav className="fixed top-0 left-0 right-0 z-50 border-b border-zinc-900 bg-black/80 backdrop-blur-sm">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="font-serif text-2xl font-bold">Lawgic</span>
            <span className="text-[10px] bg-zinc-800 text-gray-400 px-1.5 py-0.5 rounded uppercase tracking-widest">.com</span>
          </div>
          <div className="flex items-center gap-4">
            {isAuthenticated ? (
              <Link to="/dashboard" className="bg-white text-black text-sm font-semibold px-4 py-2 rounded-lg hover:bg-gray-100 transition-colors">
                Go to Dashboard
              </Link>
            ) : (
              <>
                <Link to="/login" className="text-gray-400 text-sm hover:text-white transition-colors">Sign in</Link>
                <Link to="/register" className="bg-white text-black text-sm font-semibold px-4 py-2 rounded-lg hover:bg-gray-100 transition-colors">
                  Get started free
                </Link>
              </>
            )}
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="pt-32 pb-20 px-6 text-center">
        <div className="max-w-4xl mx-auto">
          <div className="inline-flex items-center gap-2 bg-zinc-900 border border-zinc-800 rounded-full px-4 py-1.5 text-xs text-gray-400 mb-8">
            <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
            Powered by Groq + Claude + LangGraph Multi-Agent System
          </div>
          <h1 className="font-serif text-5xl md:text-7xl font-bold leading-tight mb-4">
            The Legal <span className="text-gray-400">AI</span>d
          </h1>
          <p className="text-gray-400 text-base md:text-lg max-w-xl mx-auto mb-3 leading-relaxed font-medium">
            India's AI-powered legal platform
          </p>
          <p className="text-gray-500 text-base md:text-lg max-w-2xl mx-auto mb-10 leading-relaxed">
            Analyze your case, draft court documents, find the right lawyer, and learn your rights — free to start, built for India.
          </p>
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <Link to="/register" className="bg-white text-black font-semibold px-8 py-3.5 rounded-xl hover:bg-gray-100 transition-colors text-sm">
              Start for free — no credit card
            </Link>
            <Link to="/login" className="bg-zinc-900 border border-zinc-700 text-white font-semibold px-8 py-3.5 rounded-xl hover:bg-zinc-800 transition-colors text-sm">
              Sign in
            </Link>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="py-12 px-6 border-y border-zinc-900">
        <div className="max-w-4xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
          {STATS.map((s) => (
            <div key={s.label}>
              <div className="font-serif text-4xl font-bold text-white mb-1">{s.value}</div>
              <div className="text-gray-500 text-sm">{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section className="py-20 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-14">
            <h2 className="font-serif text-4xl font-bold mb-3">Everything you need</h2>
            <p className="text-gray-500 text-lg">Built specifically for Indian law and Indian users</p>
          </div>
          <div className="grid md:grid-cols-3 gap-6">
            {FEATURES.map((f) => (
              <div key={f.title} className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6 hover:border-zinc-600 transition-colors">
                <div className="text-3xl mb-4">{f.icon}</div>
                <h3 className="font-semibold text-white mb-2">{f.title}</h3>
                <p className="text-gray-500 text-sm leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="py-20 px-6 border-t border-zinc-900">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-14">
            <h2 className="font-serif text-4xl font-bold mb-3">How it works</h2>
            <p className="text-gray-500">Three simple steps to legal clarity</p>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            {HOW_IT_WORKS.map((h) => (
              <div key={h.step} className="text-center">
                <div className="font-serif text-6xl font-bold text-zinc-800 mb-4">{h.step}</div>
                <h3 className="font-semibold text-white mb-2">{h.title}</h3>
                <p className="text-gray-500 text-sm leading-relaxed">{h.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Legal domains */}
      <section className="py-16 px-6 border-t border-zinc-900">
        <div className="max-w-5xl mx-auto text-center">
          <p className="text-gray-600 text-sm uppercase tracking-widest mb-6">Covers all major Indian legal domains</p>
          <div className="flex flex-wrap justify-center gap-3">
            {['IPC & Criminal Law', 'CrPC', 'CPC Civil Procedure', 'Consumer Protection Act', 'RTI Act', 'RERA', 'IBC Insolvency', 'NI Act 138', 'IT Act', 'GST & Tax', 'Labour Law', 'Family & Matrimonial', 'Property Law', 'Constitutional Law', 'POSH Act'].map((domain) => (
              <span key={domain} className="bg-zinc-900 border border-zinc-800 text-gray-400 text-xs px-3 py-1.5 rounded-full">
                {domain}
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section className="py-20 px-6 border-t border-zinc-900">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-14">
            <h2 className="font-serif text-4xl font-bold mb-3">Simple pricing</h2>
            <p className="text-gray-500">Start free, upgrade when you need more</p>
          </div>
          <div className="grid md:grid-cols-3 gap-6">
            {PRICING.map((plan) => (
              <div
                key={plan.name}
                className={`rounded-2xl p-6 ${
                  plan.highlight
                    ? 'bg-white text-black'
                    : 'bg-zinc-900 border border-zinc-800 text-white'
                }`}
              >
                <div className="mb-6">
                  <div className={`text-sm font-medium mb-1 ${plan.highlight ? 'text-gray-600' : 'text-gray-400'}`}>{plan.name}</div>
                  <div className="flex items-baseline gap-1">
                    <span className="font-serif text-4xl font-bold">{plan.price}</span>
                    <span className={`text-sm ${plan.highlight ? 'text-gray-500' : 'text-gray-500'}`}>/{plan.period}</span>
                  </div>
                </div>
                <ul className="space-y-2.5 mb-8">
                  {plan.features.map((f) => (
                    <li key={f} className={`flex items-start gap-2 text-sm ${plan.highlight ? 'text-gray-700' : 'text-gray-400'}`}>
                      <span className={`mt-0.5 ${plan.highlight ? 'text-black' : 'text-white'}`}>✓</span>
                      {f}
                    </li>
                  ))}
                </ul>
                <Link
                  to="/register"
                  className={`block text-center py-2.5 rounded-lg text-sm font-semibold transition-colors ${
                    plan.highlight
                      ? 'bg-black text-white hover:bg-zinc-800'
                      : 'bg-zinc-800 text-white hover:bg-zinc-700'
                  }`}
                >
                  {plan.cta}
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-6 border-t border-zinc-900 text-center">
        <div className="max-w-2xl mx-auto">
          <h2 className="font-serif text-4xl font-bold mb-4">Ready to take legal action?</h2>
          <p className="text-gray-500 mb-8">Join thousands of Indians who use Lawgic to understand and protect their legal rights.</p>
          <Link to="/register" className="inline-block bg-white text-black font-semibold px-10 py-4 rounded-xl hover:bg-gray-100 transition-colors">
            Get started for free
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-zinc-900 py-10 px-6">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <span className="font-serif font-bold">Lawgic</span>
            <span className="text-gray-600 text-xs">AI-powered legal tech for India</span>
          </div>
          <p className="text-gray-600 text-xs text-center">
            Lawgic provides AI-assisted legal information, not legal advice. For complex matters, consult a qualified advocate.
          </p>
          <p className="text-gray-700 text-xs">© 2025 Lawgic. All rights reserved.</p>
        </div>
      </footer>
    </div>
  )
}
