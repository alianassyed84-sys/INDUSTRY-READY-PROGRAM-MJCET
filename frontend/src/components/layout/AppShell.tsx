import { useEffect, useState } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { cn } from '@/lib/utils';
import { NAV_ITEMS, ROUTES } from '@/lib/routes';
import { Sidebar } from './Sidebar';
import { Topbar } from './Topbar';

export function AppShell() {
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const { pathname } = useLocation();
  const title = pathname === ROUTES.settings ? 'Settings & Account' : NAV_ITEMS.find((n) => n.to === pathname)?.label ?? 'ReviewPulse';

  useEffect(() => { setMobileOpen(false); window.scrollTo({ top: 0 }); }, [pathname]);

  return (
    <div className="min-h-screen bg-rp-bg">
      <a href="#main" className="sr-only focus:not-sr-only focus:fixed focus:left-3 focus:top-3 focus:z-[60] focus:rounded-xl focus:bg-rp-primary focus:px-4 focus:py-2 focus:text-white">Skip to content</a>
      <Sidebar collapsed={collapsed} mobileOpen={mobileOpen} onCloseMobile={() => setMobileOpen(false)} />
      <div className={cn('transition-[padding] duration-200', collapsed ? 'lg:pl-sidebar-collapsed' : 'lg:pl-sidebar')}>
        <Topbar title={title} onToggleSidebar={() => setCollapsed((c) => !c)} onOpenMobile={() => setMobileOpen(true)} />
        <main id="main" className="rp-ambient">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
