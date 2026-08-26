/**
 * Detects when a new frontend build has been deployed while this tab has been open.
 * A long-lived tab keeps running the JS it loaded at page-load time — after a deploy,
 * that in-memory bundle can be calling an API shape (or shared chunk) that no longer
 * matches, which is what produced the "X is not a function" crashes users hit until
 * they manually hard-refreshed. This polls for the deployed build's asset hash and
 * prompts a refresh instead of leaving people to rediscover that workaround.
 */

function extractBuildId(html: string): string | null {
  const match = html.match(/\/assets\/index-([A-Za-z0-9_-]+)\.js/)
  return match ? match[1] : null
}

async function fetchBuildId(): Promise<string | null> {
  try {
    const res = await fetch('/', { cache: 'no-store' })
    if (!res.ok) return null
    return extractBuildId(await res.text())
  } catch {
    return null // transient network hiccup — not a signal either way
  }
}

const CHECK_INTERVAL_MS = 5 * 60 * 1000

export function initVersionCheck(onNewVersion: () => void): () => void {
  let currentBuildId: string | null = null
  let cancelled = false

  fetchBuildId().then((id) => {
    if (!cancelled) currentBuildId = id
  })

  const check = async () => {
    const latest = await fetchBuildId()
    if (!cancelled && latest && currentBuildId && latest !== currentBuildId) {
      onNewVersion()
    }
  }

  const interval = setInterval(check, CHECK_INTERVAL_MS)
  const onVisible = () => {
    if (document.visibilityState === 'visible') check()
  }
  document.addEventListener('visibilitychange', onVisible)

  return () => {
    cancelled = true
    clearInterval(interval)
    document.removeEventListener('visibilitychange', onVisible)
  }
}
