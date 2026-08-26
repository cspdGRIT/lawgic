import { Link, useParams } from 'react-router-dom'
import { RIGHTS_CARDS } from '../data/rightsCards'

function ShareButton({ title, url }: { title: string; url: string }) {
  async function share() {
    if (navigator.share) {
      try {
        await navigator.share({ title: `Lawgic — ${title}`, url })
        return
      } catch {
        /* user cancelled the native share sheet — fall through to clipboard */
      }
    }
    try {
      await navigator.clipboard.writeText(url)
      alert('Link copied — paste it anywhere, including WhatsApp.')
    } catch {
      /* clipboard blocked — nothing more we can do silently */
    }
  }
  return (
    <button
      onClick={share}
      className="text-xs bg-white text-black font-semibold px-4 py-2 rounded-lg hover:bg-gray-100 transition-colors"
    >
      Share this
    </button>
  )
}

function CardDetail({ slug }: { slug: string }) {
  const card = RIGHTS_CARDS.find((c) => c.slug === slug)
  const url = `${window.location.origin}/rights/${slug}`

  if (!card) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-16 text-center">
        <p className="text-gray-400">That rights card doesn't exist.</p>
        <Link to="/rights" className="text-white underline text-sm mt-3 inline-block">← All rights cards</Link>
      </div>
    )
  }

  return (
    <div className="max-w-2xl mx-auto px-4 py-10">
      <Link to="/rights" className="text-gray-500 hover:text-white transition-colors text-sm">← All rights cards</Link>

      <div className="mt-4 mb-6">
        <div className="text-5xl mb-3">{card.icon}</div>
        <h1 className="font-serif text-2xl font-bold text-white">{card.title}</h1>
        <p className="text-gray-500 text-sm mt-2">{card.situation}</p>
      </div>

      <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6 mb-4">
        <h2 className="font-medium text-white mb-3 text-sm">Your rights</h2>
        <ul className="space-y-2">
          {card.rights.map((r, i) => (
            <li key={i} className="text-gray-400 text-sm flex gap-2"><span className="text-green-500 flex-shrink-0">✓</span>{r}</li>
          ))}
        </ul>
      </div>

      <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6 mb-4">
        <h2 className="font-medium text-white mb-3 text-sm">What to do</h2>
        <ol className="space-y-2">
          {card.whatToDo.map((s, i) => (
            <li key={i} className="text-gray-400 text-sm flex gap-2"><span className="text-yellow-500 flex-shrink-0">{i + 1}.</span>{s}</li>
          ))}
        </ol>
      </div>

      <p className="text-xs text-gray-600 mb-6">Relevant law: {card.law}</p>

      <div className="flex items-center gap-3 mb-8">
        <ShareButton title={card.title} url={url} />
        <Link to="/register" className="text-xs bg-zinc-800 border border-zinc-700 text-white px-4 py-2 rounded-lg hover:bg-zinc-700 transition-colors">
          Get help with a real situation like this →
        </Link>
      </div>

      <p className="text-xs text-gray-700 border-t border-zinc-800 pt-4">
        This is general information, not legal advice for your specific situation. Laws and procedures can vary by
        state. For anything urgent, contact the police (100), Women Helpline (181), or NALSA's free legal aid
        helpline (15100).
      </p>
    </div>
  )
}

function CardList() {
  return (
    <div className="max-w-3xl mx-auto px-4 py-10">
      <div className="text-center mb-8">
        <span className="font-serif text-2xl font-bold text-white">Lawgic</span>
        <h1 className="font-serif text-xl font-bold text-white mt-4">Know Your Rights</h1>
        <p className="text-gray-500 text-sm mt-2 max-w-md mx-auto">
          Short, plain-language guides to common legal situations in India. Free to read, no account needed —
          share whatever might help someone you know.
        </p>
      </div>
      <div className="grid sm:grid-cols-2 gap-3">
        {RIGHTS_CARDS.map((c) => (
          <Link
            key={c.slug}
            to={`/rights/${c.slug}`}
            className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 hover:border-zinc-600 transition-colors"
          >
            <div className="text-3xl mb-2">{c.icon}</div>
            <div className="font-medium text-white text-sm mb-1">{c.title}</div>
            <div className="text-gray-500 text-xs leading-relaxed">{c.situation}</div>
          </Link>
        ))}
      </div>
      <div className="text-center mt-10">
        <Link to="/login" className="text-sm text-gray-500 hover:text-white transition-colors">
          Already have a Lawgic account? Sign in →
        </Link>
      </div>
    </div>
  )
}

export default function RightsCards() {
  const { slug } = useParams()
  return (
    <div className="min-h-screen bg-black">
      {slug ? <CardDetail slug={slug} /> : <CardList />}
    </div>
  )
}
