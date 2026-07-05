import { create } from 'zustand'
import type { User } from '../types'
import { setAccessToken } from '../lib/api'

interface AppState {
  user: User | null
  isAuthenticated: boolean
  authInitialized: boolean
  setUser: (user: User) => void
  setToken: (token: string) => void
  authenticate: (token: string, user: User) => void
  logout: () => void
  setAuthInitialized: () => void
}

export const useAuthStore = create<AppState>()((set) => ({
  user: null,
  isAuthenticated: false,
  authInitialized: false,

  setUser: (user) => set({ user, isAuthenticated: true }),

  setToken: (token) => {
    setAccessToken(token)
  },

  authenticate: (token, user) => {
    setAccessToken(token)
    set({ user, isAuthenticated: true })
  },

  logout: () => {
    setAccessToken(null)
    set({ user: null, isAuthenticated: false })
  },

  setAuthInitialized: () => set({ authInitialized: true }),
}))

// Receive logout signal from the API interceptor (avoids circular import)
if (typeof window !== 'undefined') {
  window.addEventListener('lawgic:logout', () => {
    useAuthStore.getState().logout()
    window.location.href = '/login'
  })
}

export const useAppStore = useAuthStore
