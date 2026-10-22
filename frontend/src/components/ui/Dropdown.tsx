import { useEffect, useRef, useState, type ReactNode } from 'react';
import { cn } from '@/lib/utils';

export interface DropdownItem { label: string; icon?: ReactNode; onSelect: () => void; danger?: boolean }

export function Dropdown({ trigger, items, label, align = 'right' }: { trigger: ReactNode; items: DropdownItem[]; label: string; align?: 'left' | 'right' }) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!open) return;
    const onDoc = (e: MouseEvent) => !ref.current?.contains(e.target as Node) && setOpen(false);
    const onKey = (e: KeyboardEvent) => e.key === 'Escape' && setOpen(false);
    document.addEventListener('mousedown', onDoc);
    document.addEventListener('keydown', onKey);
    return () => { document.removeEventListener('mousedown', onDoc); document.removeEventListener('keydown', onKey); };
  }, [open]);
  return (
    <div ref={ref} className="relative">
      <button type="button" aria-haspopup="menu" aria-expanded={open} aria-label={label} onClick={() => setOpen((o) => !o)} className="rounded-btn">
        {trigger}
      </button>
      {open && (
        <div role="menu" className={cn('absolute top-full z-50 mt-2 min-w-[200px] rounded-2xl border border-rp-border bg-rp-surface p-1.5 shadow-lift', align === 'right' ? 'right-0' : 'left-0')}>
          {items.map((it) => (
            <button
              key={it.label}
              role="menuitem"
              onClick={() => { setOpen(false); it.onSelect(); }}
              className={cn('flex min-h-[44px] w-full items-center gap-2.5 rounded-xl px-3 text-left text-sm font-medium hover:bg-rp-primary-light', it.danger && 'text-rp-coral')}
            >
              {it.icon}{it.label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
