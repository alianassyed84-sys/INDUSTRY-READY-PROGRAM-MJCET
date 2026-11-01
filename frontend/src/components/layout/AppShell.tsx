import { useEffect, useState } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { cn } from '@/lib/utils';
import { NAV_ITEMS, ROUTES } from '@/lib/routes';
import { useProductContext } from '@/hooks/useProduct';
import { Sidebar } from './Sidebar';
import { Topbar } from './Topbar';

export function AppShell() {
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const { pathname } = useLocation();
  const title =
    pathname === ROUTES.settings
      ? 'Settings'
      : pathname.startsWith('/product')
      ? 'Product Workspace'
      : NAV_ITEMS.find((n) => n.to === pathname)?.label ?? 'ReviewPulse';

  useEffect(() => { setMobileOpen(false); window.scrollTo({ top: 0 }); }, [pathname]);

  return (
    <div className="min-h-screen bg-rp-bg">
      <a href="#main" className="sr-only focus:not-sr-only focus:fixed focus:left-3 focus:top-3 focus:z-[60] focus:rounded-xl focus:bg-rp-action focus:px-4 focus:py-2 focus:text-white">Skip to content</a>
      <Sidebar collapsed={collapsed} mobileOpen={mobileOpen} onCloseMobile={() => setMobileOpen(false)} />
      <div className={cn('transition-[padding] duration-200', collapsed ? 'lg:pl-sidebar-collapsed' : 'lg:pl-sidebar')}>
        <Topbar title={title} onToggleSidebar={() => setCollapsed((c) => !c)} onOpenMobile={() => setMobileOpen(true)} />
        {source === 'demo' && (
          <aside
            aria-label="Cloud backend status"
            className="border-b border-amber-200/60 bg-amber-50/90 px-4 py-2 text-xs text-amber-900 backdrop-blur dark:border-amber-900/50 dark:bg-amber-950/40 dark:text-amber-200"
          >
            <div className="mx-auto flex max-w-7xl items-center justify-between gap-3">
              <div className="flex items-center gap-2 min-w-0">
                <span className="relative flex h-2 w-2 shrink-0">
                  <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-amber-400 opacity-75" />
                  <span className="relative inline-flex h-2 w-2 rounded-full bg-amber-500" />
                </span>
                <span className="truncate">
                  <strong>Cloud backend waking up</strong> — Render free tier resumes in ~30s on cold start. Connecting automatically...
                </span>
              </div>
              <button
                type="button"
                onClick={() => refetch()}
                disabled={loading}
                className="shrink-0 font-semibold text-amber-800 underline hover:text-amber-950 disabled:opacity-50 dark:text-amber-300 dark:hover:text-amber-100"
              >
                {loading ? 'Connecting...' : 'Retry now'}
              </button>
            </div>
          </aside>
        )}
        <main id="main" className="rp-ambient">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
