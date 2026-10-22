import { useId, useState, type ReactNode } from 'react';
import { cn } from '@/lib/utils';

export function Tooltip({ label, side = 'right', children }: { label: string; side?: 'right' | 'top' | 'bottom'; children: ReactNode }) {
  const id = useId();
  const [open, setOpen] = useState(false);
  const pos = { right: 'left-full top-1/2 ml-3 -translate-y-1/2', top: 'bottom-full left-1/2 mb-2 -translate-x-1/2', bottom: 'top-full left-1/2 mt-2 -translate-x-1/2' }[side];
  return (
    <span
      className="relative inline-flex"
      onMouseEnter={() => setOpen(true)}
      onMouseLeave={() => setOpen(false)}
      onFocus={() => setOpen(true)}
      onBlur={() => setOpen(false)}
      aria-describedby={open ? id : undefined}
    >
      {children}
      {open && (
        <span id={id} role="tooltip" className={cn('pointer-events-none absolute z-50 whitespace-nowrap rounded-lg bg-rp-navy px-2.5 py-1.5 text-xs font-medium text-white shadow-lift', pos)}>
          {label}
        </span>
      )}
    </span>
  );
}
