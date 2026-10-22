import { NavLink } from 'react-router-dom';
import { Settings, X } from 'lucide-react';
import { cn } from '@/lib/utils';
import { NAV_ITEMS, ROUTES } from '@/lib/routes';
import { Tooltip } from '@/components/ui/Tooltip';
import { Logo } from './Logo';

interface Props { collapsed: boolean; mobileOpen: boolean; onCloseMobile: () => void }

function Links({ collapsed, onNavigate }: { collapsed: boolean; onNavigate?: () => void }) {
  const link = (to: string, label: string, Icon: (typeof NAV_ITEMS)[number]['icon']) => {
    const el = (
      <NavLink
        key={to}
        to={to}
        onClick={onNavigate}
        className={({ isActive }) =>
          cn(
            'flex min-h-[44px] items-center gap-3 rounded-btn px-3.5 text-sm font-semibold transition-colors',
            collapsed && 'justify-center px-0',
            isActive ? 'bg-rp-primary text-white shadow-[0_8px_18px_-8px_rgba(113,56,245,.65)]' : 'text-rp-text hover:bg-rp-primary-light',
          )
        }
      >
        <Icon className="h-5 w-5 shrink-0" aria-hidden />
        <span className={cn(collapsed && 'sr-only')}>{label}</span>
      </NavLink>
    );
    return collapsed ? <Tooltip key={to} label={label}>{el}</Tooltip> : el;
  };
  return (
    <>
      <nav aria-label="Primary" className={cn('flex flex-1 flex-col gap-1', collapsed && 'items-stretch')}>
        {NAV_ITEMS.map((i) => link(i.to, i.label, i.icon))}
      </nav>
      <div className="border-t border-rp-border pt-3">{link(ROUTES.settings, 'Settings & Account', Settings)}</div>
    </>
  );
}

export function Sidebar({ collapsed, mobileOpen, onCloseMobile }: Props) {
  return (
    <>
      <aside
        className={cn(
          'fixed inset-y-0 left-0 z-30 hidden flex-col border-r border-rp-border bg-rp-surface px-3 py-5 transition-[width] duration-200 lg:flex',
          collapsed ? 'w-sidebar-collapsed' : 'w-sidebar',
        )}
      >
        <div className={cn('mb-6 flex h-10 items-center px-1.5', collapsed && 'justify-center px-0')}><Logo collapsed={collapsed} /></div>
        <Links collapsed={collapsed} />
      </aside>

      {mobileOpen && (
        <div className="fixed inset-0 z-50 lg:hidden" role="dialog" aria-modal="true" aria-label="Navigation">
          <button className="absolute inset-0 bg-rp-navy/40 backdrop-blur-sm" onClick={onCloseMobile} aria-label="Close navigation" />
          <aside className="absolute inset-y-0 left-0 flex w-[min(86vw,300px)] flex-col bg-rp-surface px-3 py-5 shadow-lift">
            <div className="mb-6 flex items-center justify-between px-1.5">
              <Logo />
              <button onClick={onCloseMobile} aria-label="Close navigation" className="grid h-11 w-11 place-items-center rounded-xl hover:bg-rp-primary-light"><X className="h-5 w-5" /></button>
            </div>
            <Links collapsed={false} onNavigate={onCloseMobile} />
          </aside>
        </div>
      )}
    </>
  );
}
