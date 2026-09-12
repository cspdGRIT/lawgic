import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useEffect, useState } from 'react'
import { useAuthStore } from './store'
import { authAPI } from './lib/api'
import { initVersionCheck } from './lib/versionCheck'
import QuickExit from './components/QuickExit'
import AppLayout from './components/layout/AppLayout'
import Landing from './pages/Landing'
import Login from './pages/auth/Login'
import Register from './pages/auth/Register'
import Dashboard from './pages/Dashboard'
import AccessPending from './pages/AccessPending'
import AdminRequests from './pages/AdminRequests'
import IssueNavigator from './pages/IssueNavigator'
import AiAssistant from './pages/AiAssistant'
import CaseAnalysis from './pages/CaseAnalysis'
import DocumentGenerator from './pages/DocumentGenerator'
import LawyerMarketplace from './pages/LawyerMarketplace'
import LegalResearch from './pages/LegalResearch'
import Education from './pages/Education'
import Pricing from './pages/Pricing'
import LegalAidCheck from './pages/LegalAidCheck'
import RightsCards from './pages/RightsCards'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: 1, staleTime: 1000 * 60 * 5 },
  },
})

function AuthInit({ children }: { children: React.ReactNode }) {
  const { authenticate, logout, setAuthInitialized, authInitialized } = useAuthStore()

  useEffect(() => {
    authAPI
      .refresh()
      .then((data) => {
        authenticate(data.access_token, data.user)
      })
      .catch(() => {
        logout()
      })
      .finally(() => {
        setAuthInitialized()
      })
  }, [])

  if (!authInitialized) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="w-6 h-6 border-2 border-white border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  return <>{children}</>
}

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />
}

function AdminRoute({ children }: { children: React.ReactNode }) {
  const user = useAuthStore((s) => s.user)
  return user?.user_type === 'admin' ? <>{children}</> : <Navigate to="/dashboard" replace />
}

// index.html has one static <title> for the whole app — every route showed the same
// tab title and the same browser-history entry name. Prefix-matched so /rights/:slug
// falls through to the /rights entry without needing one per slug.
const ROUTE_TITLES: [string, string][] = [
  ['/dashboard', 'Dashboard'],
  ['/issue-navigator', 'Describe Your Issue'],
  ['/legal-aid-check', 'Free Legal Aid Check'],
  ['/assistant', 'AI Assistant'],
  ['/cases', 'Case Analysis'],
  ['/documents', 'Document Generator'],
  ['/lawyers', 'Lawyer Marketplace'],
  ['/research', 'Legal Research'],
  ['/education', 'Education'],
  ['/pricing', 'Plans & Billing'],
  ['/admin/requests', 'Access Requests'],
  ['/access-pending', 'Access Pending'],
  ['/rights', 'Know Your Rights'],
  ['/register', 'Create Account'],
  ['/login', 'Sign In'],
]

function RouteTitle() {
  const { pathname } = useLocation()
  useEffect(() => {
    const match = ROUTE_TITLES.find(([prefix]) => pathname === prefix || pathname.startsWith(`${prefix}/`))
    document.title = match ? `${match[1]} — Lawgic` : 'Lawgic.com — The Legal AId'
  }, [pathname])
  return null
}

// A tab left open across a deploy keeps running the JS it loaded at page-load — that
// stale bundle calling into a changed API shape is what produced the "X is not a
// function" crashes people were hitting until they manually hard-refreshed. This
// polls for a new build and offers a one-click refresh instead.
function UpdateBanner() {
  return (
    <div className="fixed bottom-5 left-1/2 -translate-x-1/2 z-50 bg-white text-black rounded-full shadow-2xl px-5 py-2.5 flex items-center gap-3 text-sm font-medium">
      A new version of Lawgic is available
      <button
        onClick={() => window.location.reload()}
        className="bg-black text-white px-3 py-1.5 rounded-full text-xs font-semibold hover:bg-zinc-800 transition-colors"
      >
        Refresh
      </button>
    </div>
  )
}

export default function App() {
  const [updateAvailable, setUpdateAvailable] = useState(false)

  useEffect(() => {
    return initVersionCheck(() => setUpdateAvailable(true))
  }, [])

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <RouteTitle />
        <QuickExit />
        {updateAvailable && <UpdateBanner />}
        <AuthInit>
          <Routes>
            <Route path="/" element={<Landing />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            {/* Public and unauthenticated on purpose — shared rights cards need to
                open for anyone who clicks a link, not just logged-in users. */}
            <Route path="/rights" element={<RightsCards />} />
            <Route path="/rights/:slug" element={<RightsCards />} />
            <Route
              path="/access-pending"
              element={
                <ProtectedRoute>
                  <AccessPending />
                </ProtectedRoute>
              }
            />
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <AppLayout />
                </ProtectedRoute>
              }
            >
              <Route path="dashboard" element={<Dashboard />} />
              <Route path="issue-navigator" element={<IssueNavigator />} />
              <Route path="legal-aid-check" element={<LegalAidCheck />} />
              <Route path="assistant" element={<AiAssistant />} />
              <Route path="cases" element={<CaseAnalysis />} />
              <Route path="documents" element={<DocumentGenerator />} />
              <Route path="lawyers" element={<LawyerMarketplace />} />
              <Route path="research" element={<LegalResearch />} />
              <Route path="education" element={<Education />} />
              <Route path="pricing" element={<Pricing />} />
              <Route path="admin/requests" element={<AdminRoute><AdminRequests /></AdminRoute>} />
            </Route>
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </AuthInit>
      </BrowserRouter>
    </QueryClientProvider>
  )
}
