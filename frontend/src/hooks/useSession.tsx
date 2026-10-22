import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from 'react';

/**
 * PROTOTYPE SESSION. The repository has no verified auth endpoints yet, so this only
 * keeps a display name and email in sessionStorage. No password is ever stored.
 */
export interface SessionUser { name: string; email: string }
interface Ctx { user: SessionUser | null; signIn: (u: SessionUser) => void; signOut: () => void; prototype: true }
const KEY = 'rp.prototype.session';
const SessionCtx = createContext<Ctx | null>(null);

const read = (): SessionUser | null => {
  try { const raw = sessionStorage.getItem(KEY); return raw ? (JSON.parse(raw) as SessionUser) : null; } catch { return null; }
};

export function SessionProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<SessionUser | null>(read);
  const signIn = useCallback((u: SessionUser) => { try { sessionStorage.setItem(KEY, JSON.stringify(u)); } catch { /* storage unavailable */ } setUser(u); }, []);
  const signOut = useCallback(() => { try { sessionStorage.removeItem(KEY); } catch { /* ignore */ } setUser(null); }, []);
  const value = useMemo(() => ({ user, signIn, signOut, prototype: true as const }), [user, signIn, signOut]);
  return <SessionCtx.Provider value={value}>{children}</SessionCtx.Provider>;
}

export function useSession() {
  const c = useContext(SessionCtx);
  if (!c) throw new Error('useSession must be used inside SessionProvider');
  return c;
}
