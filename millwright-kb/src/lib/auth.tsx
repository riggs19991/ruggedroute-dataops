import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from 'react'
import type { Session, User } from '@supabase/supabase-js'
import { supabase } from './supabase'
import type { Profile } from './types'

interface AuthState {
  session: Session | null
  user: User | null
  profile: Profile | null
  loading: boolean
  isAdmin: boolean
  refreshProfile: () => Promise<void>
  signOut: () => Promise<void>
}

const AuthContext = createContext<AuthState | null>(null)

async function loadProfile(user: User): Promise<Profile | null> {
  const { data } = await supabase.from('mw_profiles').select('id, display_name, is_admin, school').eq('id', user.id).maybeSingle()
  if (data) return data as Profile
  // Profile row missing (e.g. user created before the trigger existed): create it.
  const meta = (user.user_metadata ?? {}) as Record<string, string>
  const fallback: Profile = {
    id: user.id,
    display_name: meta.display_name || (user.email ?? '').split('@')[0],
    is_admin: false,
    school: meta.school || '',
  }
  const { data: created } = await supabase.from('mw_profiles').insert({ id: fallback.id, display_name: fallback.display_name, school: fallback.school }).select('id, display_name, is_admin, school').maybeSingle()
  return (created as Profile) ?? fallback
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<Session | null>(null)
  const [profile, setProfile] = useState<Profile | null>(null)
  const [loading, setLoading] = useState(true)

  const refreshProfile = useCallback(async () => {
    const { data } = await supabase.auth.getSession()
    const user = data.session?.user
    setProfile(user ? await loadProfile(user) : null)
  }, [])

  useEffect(() => {
    let cancelled = false
    supabase.auth.getSession().then(async ({ data }) => {
      if (cancelled) return
      setSession(data.session)
      setProfile(data.session?.user ? await loadProfile(data.session.user) : null)
      setLoading(false)
    })
    const { data: sub } = supabase.auth.onAuthStateChange((_event, next) => {
      setSession(next)
      if (next?.user) {
        // Defer the query: supabase-js warns against awaiting inside the callback.
        setTimeout(() => { loadProfile(next.user).then(setProfile) }, 0)
      } else {
        setProfile(null)
      }
    })
    return () => { cancelled = true; sub.subscription.unsubscribe() }
  }, [])

  const signOut = useCallback(async () => { await supabase.auth.signOut() }, [])

  const value: AuthState = {
    session,
    user: session?.user ?? null,
    profile,
    loading,
    isAdmin: !!profile?.is_admin,
    refreshProfile,
    signOut,
  }
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth outside AuthProvider')
  return ctx
}
