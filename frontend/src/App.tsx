import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useEffect } from 'react'
import { useAuthStore } from './store'
import { authAPI } from './lib/api'
import AppLayout from './components/layout/AppLayout'
import Landing from './pages/Landing'
import Login from './pages/auth/Login'
import Register from './pages/auth/Register'
import Dashboard from './pages/Dashboard'
import AiAssistant from './pages/AiAssistant'
import CaseAnalysis from './pages/CaseAnalysis'
import DocumentGenerator from './pages/DocumentGenerator'
import LawyerMarketplace from './pages/LawyerMarketplace'
import LegalResearch from './pages/LegalResearch'
import Education from './pages/Education'
import Pricing from './pages/Pricing'

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

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthInit>
          <Routes>
            <Route path="/" element={<Landing />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <AppLayout />
                </ProtectedRoute>
              }
            >
              <Route path="dashboard" element={<Dashboard />} />
              <Route path="assistant" element={<AiAssistant />} />
              <Route path="cases" element={<CaseAnalysis />} />
              <Route path="documents" element={<DocumentGenerator />} />
              <Route path="lawyers" element={<LawyerMarketplace />} />
              <Route path="research" element={<LegalResearch />} />
              <Route path="education" element={<Education />} />
              <Route path="pricing" element={<Pricing />} />
            </Route>
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </AuthInit>
      </BrowserRouter>
    </QueryClientProvider>
  )
}
