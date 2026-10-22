import { useState, type FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { LogOut, Menu, PanelLeft, Search, Settings, User } from 'lucide-react';
import { Dropdown } from '@/components/ui/Dropdown';
import { Tooltip } from '@/components/ui/Tooltip';
import { ROUTES } from '@/lib/routes';
import { useSession } from '@/hooks/useSession';

interface Props { onToggleSidebar: () => void; onOpenMobile: () => void; title: string }

export function Topbar({ onToggleSidebar, onOpenMobile, title }: Props) {
  const [q, setQ] = useState('');
  const nav = useNavigate();
  const { user, signOut } = useSession();
  const initials = (user?.name ?? 'Guest').split(' ').map((s) => s[0]).slice(0, 2).join('').toUpperCase();

  const submit = (e: FormEvent) => {
    e.preventDefault();
    const v = q.trim();
    if (v) nav(`${ROUTES.reviews}?q=${encodeURIComponent(v)}`);
  };

  return (
    <header className="sticky top-0 z-20 flex h-topbar items-center gap-3 border-b border-rp-border bg-rp-bg/85 px-4 backdrop-blur-md md:px-6 lg:px-8">
      <button onClick={onOpenMobile} aria-label="Open navigation" className="grid h-11 w-11 place-items-center rounded-xl hover:bg-rp-primary-light lg:hidden"><Menu className="h-5 w-5" /></button>
      <Tooltip label="Toggle sidebar" side="bottom">
        <button onClick={onToggleSidebar} aria-label="Toggle sidebar" className="hidden h-11 w-11 place-items-center rounded-xl hover:bg-rp-primary-light lg:grid"><PanelLeft className="h-5 w-5" /></button>
      </Tooltip>
      <p className="hidden shrink-0 font-heading text-[15px] font-bold text-rp-navy md:block">{title}</p>

      <form onSubmit={submit} role="search" className="mx-auto flex min-h-[48px] w-full max-w-xl items-center gap-2 rounded-btn border border-rp-border bg-rp-surface px-3.5 focus-within:border-rp-primary focus-within:shadow-focus">
        <Search className="h-4 w-4 text-rp-muted" aria-hidden />
        <input value={q} onChange={(e) => setQ(e.target.value)} aria-label="Search reviews" placeholder="Search within product reviews" className="min-w-0 flex-1 bg-transparent text-sm outline-none placeholder:text-rp-muted/70 focus-visible:shadow-none" />
      </form>

      <Dropdown
        label="Account menu"
        trigger={<span className="grid h-11 w-11 place-items-center rounded-full bg-rp-primary-light font-heading text-sm font-extrabold text-rp-primary-hover">{user ? initials : <User className="h-5 w-5" />}</span>}
        items={[
          { label: 'Settings & profile', icon: <Settings className="h-4 w-4" />, onSelect: () => nav(ROUTES.settings) },
          user
            ? { label: 'Log out', icon: <LogOut className="h-4 w-4" />, onSelect: () => { signOut(); nav(ROUTES.login); }, danger: true }
            : { label: 'Log in', icon: <User className="h-4 w-4" />, onSelect: () => nav(ROUTES.login) },
        ]}
      />
    </header>
  );
}
