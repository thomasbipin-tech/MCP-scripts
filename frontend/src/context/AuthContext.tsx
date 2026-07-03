import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react'
import { apiGet, clearToken, getToken, setToken } from '../lib/api'
import type { AuthUser } from '../types/api'

interface AuthContextValue {
  token: string | null
  user: AuthUser | null
  loading: boolean
  login: (token: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setTok] = useState<string | null>(() => getToken())
  const [user, setUser] = useState<AuthUser | null>(null)
  const [loading, setLoading] = useState<boolean>(() => getToken() !== null)

  const hydrate = useCallback(async () => {
    try {
      const me = await apiGet<AuthUser>('/auth/me')
      setUser(me)
    } catch {
      clearToken()
      setTok(null)
      setUser(null)
    }
  }, [])

  useEffect(() => {
    if (!getToken()) {
      setLoading(false)
      return
    }
    setLoading(true)
    hydrate().finally(() => setLoading(false))
  }, [hydrate])

  const login = useCallback(
    async (tok: string) => {
      setToken(tok)
      setTok(tok)
      setLoading(true)
      try {
        await hydrate()
      } finally {
        setLoading(false)
      }
    },
    [hydrate],
  )

  const logout = useCallback(() => {
    clearToken()
    setTok(null)
    setUser(null)
  }, [])

  const value = useMemo(
    () => ({ token, user, loading, login, logout }),
    [token, user, loading, login, logout],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
