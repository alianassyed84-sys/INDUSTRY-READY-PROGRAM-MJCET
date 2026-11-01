import { useState, type FormEvent } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { LogOut, Menu, Package, PanelLeft, Search, Settings, User } from 'lucide-react';
import { MotionToggle } from '@/components/motion/MotionToggle';
import { Dropdown } from '@/components/ui/Dropdown';
import { Tooltip } from '@/components/ui/Tooltip';
import { productRoute, type ProductTab, PRODUCT_TABS, ROUTES } from '@/lib/routes';
import { useSession } from '@/hooks/useSession';
import { useProductContext } from '@/hooks/useProduct';

interface Props { onToggleSidebar: () => void; onOpenMobile: () => void; title: string }

export function Topbar({ onToggleSidebar, onOpenMobile, title }: Props) {
  const [q, setQ] = useState('');
  const nav = useNavigate();
  const location = useLocation();
  const { user, signOut } = useSession();
  const { products, productId, setProductId } = useProductContext();

  const initials = (user?.name ?? 'Guest').split(' ').map((s) => s[0]).slice(0, 2).join('').toUpperCase();
  const currentProduct = products.find((p) => p.id === productId);

  const submit = (e: FormEvent) => {
    e.preventDefault();
    const v = q.trim();
    if (v) nav(`${ROUTES.products}?q=${encodeURIComponent(v)}`);
  };

  const handleProductSelect = (newId: string) => {
    setProductId(newId);
    // If currently inside /product/:id/:tab, keep the current tab
    const match = location.pathname.match(/^\/product\/[^/]+\/([^/]+)/);
    const activeTab = match && PRODUCT_TABS.includes(match[1] as ProductTab)
      ? (match[1] as ProductTab)
      : 'overview';
    nav(productRoute(newId, activeTab));
  };

  return (
    <header className="rp-topbar sticky top-0 z-20 flex h-topbar items-center gap-1.5 border-b border-rp-border bg-rp-bg/85 px-4 backdrop-blur-md sm:gap-3 md:px-6 lg:px-8">
      <button onClick={onOpenMobile} aria-label="Open navigation" className="grid h-11 w-11 place-items-center rounded-xl hover:bg-rp-primary-light lg:hidden"><Menu className="h-5 w-5" /></button>
      <Tooltip label="Toggle sidebar" side="bottom">
        <button onClick={onToggleSidebar} aria-label="Toggle sidebar" className="hidden h-11 w-11 place-items-center rounded-xl hover:bg-rp-primary-light lg:grid"><PanelLeft className="h-5 w-5" /></button>
      </Tooltip>
      <p className="hidden shrink-0 font-heading text-[15px] font-bold text-rp-navy md:block">{title}</p>

      {/* Quick product switcher */}
      {products.length > 0 && (
        <div className="hidden sm:block">
          <Dropdown
            label="Quick product switcher"
            align="left"
            trigger={
              <span className="flex items-center gap-1.5 max-w-[190px] md:max-w-[240px] rounded-btn border border-rp-border bg-rp-surface px-3 py-2 text-xs font-semibold text-rp-navy hover:bg-rp-primary-light transition-colors">
                <Package className="h-3.5 w-3.5 shrink-0 text-rp-primary" aria-hidden="true" />
                <span className="truncate">{currentProduct ? currentProduct.title : 'Select product'}</span>
              </span>
            }
            items={products.map((p) => ({
              label: p.title,
              onSelect: () => handleProductSelect(p.id),
            }))}
          />
        </div>
      )}

      <form onSubmit={submit} role="search" className="mx-auto flex min-h-[48px] min-w-0 w-full max-w-xl items-center gap-2 rounded-btn border border-rp-border bg-rp-surface px-3.5 focus-within:border-rp-primary focus-within:shadow-focus">
        <Search className="h-4 w-4 text-rp-muted" aria-hidden />
        <input value={q} onChange={(e) => setQ(e.target.value)} aria-label="Search reviews" placeholder="Search reviews or products" className="min-w-0 flex-1 bg-transparent text-sm outline-none placeholder:text-rp-muted focus-visible:shadow-none" />
      </form>

      <MotionToggle />
      <Dropdown
        label="Account menu"
        trigger={<span className="grid h-11 w-11 place-items-center rounded-full bg-rp-primary-light font-heading text-sm font-extrabold text-rp-primary-hover">{user ? initials : <User className="h-5 w-5" />}</span>}
        items={[
          { label: 'Settings', icon: <Settings className="h-4 w-4" />, onSelect: () => nav(ROUTES.settings) },
          user
            ? { label: 'Log out', icon: <LogOut className="h-4 w-4" />, onSelect: () => { signOut(); nav(ROUTES.login); }, danger: true }
            : { label: 'Log in', icon: <User className="h-4 w-4" />, onSelect: () => nav(ROUTES.login) },
        ]}
      />
    </header>
  );
}
