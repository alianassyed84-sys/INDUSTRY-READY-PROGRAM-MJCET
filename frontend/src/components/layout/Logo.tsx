import { Link } from 'react-router-dom';
import { cn } from '@/lib/utils';
import { ROUTES } from '@/lib/routes';

export function LogoMark({ className }: { className?: string }) {
  return (
    <span className={cn('grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-rp-primary shadow-[0_8px_18px_-6px_rgba(113,56,245,.6)]', className)}>
      <svg viewBox="0 0 32 32" className="h-6 w-6" aria-hidden>
        <path d="M4 17h5l3-8 5 14 3-6h8" fill="none" stroke="#fff" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    </span>
  );
}

export function Logo({ collapsed }: { collapsed?: boolean }) {
  return (
    <Link to={ROUTES.landing} className="flex items-center gap-3 rounded-xl" aria-label="ReviewPulse home">
      <LogoMark />
      {!collapsed && <span className="font-heading text-xl font-extrabold tracking-tight text-rp-navy">Review<span className="text-rp-primary">Pulse</span></span>}
    </Link>
  );
}
