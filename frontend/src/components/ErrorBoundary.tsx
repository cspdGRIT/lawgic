import { Component, type ReactNode } from 'react'

interface Props { children: ReactNode }
interface State { error: Error | null }

export default class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null }

  static getDerivedStateFromError(error: Error): State {
    return { error }
  }

  render() {
    const { error } = this.state
    if (!error) return this.props.children

    return (
      <div className="min-h-screen bg-black flex items-center justify-center p-8">
        <div className="max-w-lg w-full bg-zinc-900 border border-red-800 rounded-2xl p-6">
          <h1 className="text-red-400 font-bold text-lg mb-2">Something went wrong</h1>
          <pre className="text-gray-400 text-xs whitespace-pre-wrap break-all bg-zinc-800 rounded p-3 mt-3">
            {error.message}
            {'\n\n'}
            {error.stack}
          </pre>
          <button
            onClick={() => window.location.href = '/'}
            className="mt-4 w-full bg-white text-black text-sm font-semibold py-2 rounded-lg"
          >
            Go to homepage
          </button>
        </div>
      </div>
    )
  }
}
