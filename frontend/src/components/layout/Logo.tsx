import { Link } from 'react-router-dom';
import { cn } from '@/lib/utils';
import { ROUTES } from '@/lib/routes';

export function LogoMark({ className }: { className?: string }) {
  return (
    <span className={cn('relative grid h-11 w-11 shrink-0 place-items-center', className)}>
      <span aria-hidden className="absolute inset-1 rounded-full bg-rp-primary/20 blur-md" />
      <img
        src="/reviewpulse-logo.png"
        alt=""
        width="44"
        height="44"
        draggable="false"
        className="relative h-11 w-11 object-contain drop-shadow-[0_5px_9px_rgba(143,47,220,0.32)]"
      />
    </span>
  );
}

export function Logo({ collapsed }: { collapsed?: boolean }) {
  return (
    <Link to={ROUTES.landing} className="flex items-center gap-2.5 rounded-xl" aria-label="ReviewPulse home">
      <LogoMark />
      {!collapsed && <span className="font-heading text-xl font-extrabold tracking-tight text-rp-navy">Review<span className="text-rp-primary">Pulse</span></span>}
    </Link>
  );
}
