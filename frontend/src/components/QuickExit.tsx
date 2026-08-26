import { useEffect } from 'react'

// Standard pattern on domestic-violence-support sites: someone researching this on a
// shared or monitored device needs to be able to leave instantly, without a confirm
// dialog or anything that costs a second click. Rendered globally (App.tsx), not just
// on issue/case pages — a person can feel unsafe at any point while browsing.
const EXIT_URL = 'https://www.google.com'

function exitNow() {
  // replace(), not href= — no back-button trail leading back to this site.
  window.location.replace(EXIT_URL)
}

export default function QuickExit() {
  useEffect(() => {
    let escCount = 0
    let escTimer: ReturnType<typeof setTimeout> | null = null

    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key !== 'Escape') return
      escCount += 1
      if (escTimer) clearTimeout(escTimer)
      if (escCount >= 3) {
        exitNow()
        return
      }
      escTimer = setTimeout(() => { escCount = 0 }, 1500)
    }

    document.addEventListener('keydown', onKeyDown)
    return () => document.removeEventListener('keydown', onKeyDown)
  }, [])

  return (
    <button
      onClick={exitNow}
      title="Leave this site immediately (or press Escape 3 times)"
      className="fixed top-3 right-3 z-[60] bg-zinc-800/90 hover:bg-red-900 text-gray-300 hover:text-white text-xs font-medium px-3 py-1.5 rounded-full backdrop-blur transition-colors border border-zinc-700"
    >
      Quick Exit
    </button>
  )
}
