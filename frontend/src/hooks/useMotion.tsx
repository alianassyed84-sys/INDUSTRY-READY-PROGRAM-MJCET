import { createContext, useContext, useEffect, useState, type ReactNode } from 'react';

const STORAGE_KEY = 'rp.motion.paused';
const QUERY = '(prefers-reduced-motion: reduce)';
interface MotionSettings { enabled: boolean; systemReduced: boolean; toggle: () => void }
const MotionContext = createContext<MotionSettings | null>(null);

/** A presentation preference only; never changes session or server state. */
export function MotionProvider({ children }: { children: ReactNode }) {
  const [systemReduced, setSystemReduced] = useState(() => window.matchMedia(QUERY).matches);
  const [paused, setPaused] = useState(() => {
    try { return localStorage.getItem(STORAGE_KEY) === 'true'; } catch { return false; }
  });
  const enabled = !systemReduced && !paused;

  useEffect(() => {
    const media = window.matchMedia(QUERY);
    const update = () => setSystemReduced(media.matches);
    update();
    media.addEventListener('change', update);
    return () => media.removeEventListener('change', update);
  }, []);

  useEffect(() => {
    document.documentElement.dataset.motion = enabled ? 'full' : 'reduced';
    return () => { delete document.documentElement.dataset.motion; };
  }, [enabled]);

  useEffect(() => {
    const update = () => { document.documentElement.dataset.pageHidden = String(document.hidden); };
    update();
    document.addEventListener('visibilitychange', update);
    return () => {
      document.removeEventListener('visibilitychange', update);
      delete document.documentElement.dataset.pageHidden;
    };
  }, []);

  const toggle = () => {
    if (systemReduced) return;
    setPaused(value => {
      try { localStorage.setItem(STORAGE_KEY, String(!value)); } catch { /* Private browsing can disable storage. */ }
      return !value;
    });
  };

  return <MotionContext.Provider value={{ enabled, systemReduced, toggle }}>{children}</MotionContext.Provider>;
}

export function useMotion() {
  const settings = useContext(MotionContext);
  if (!settings) throw new Error('useMotion must be used inside MotionProvider');
  return settings;
}
