import { Pause, Play } from 'lucide-react';
import { useMotion } from '@/hooks/useMotion';

export function MotionToggle() {
  const { enabled, systemReduced, toggle } = useMotion();
  const label = systemReduced ? 'Animations off: reduced motion is enabled on your device' : enabled ? 'Pause animations' : 'Resume animations';
  return (
    <button type="button" onClick={toggle} disabled={systemReduced} aria-label={label} title={label}
      className="rp-motion-toggle grid h-11 w-11 shrink-0 place-items-center rounded-xl border border-rp-border/70 text-rp-muted transition-colors hover:border-rp-primary-soft hover:bg-rp-primary-light hover:text-rp-primary disabled:cursor-default">
      {enabled ? <Pause className="h-4 w-4" aria-hidden /> : <Play className="h-4 w-4" aria-hidden />}
    </button>
  );
}
