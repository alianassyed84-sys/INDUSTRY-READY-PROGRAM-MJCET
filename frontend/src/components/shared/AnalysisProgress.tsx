import { AlertCircle, Check, Circle, Loader2, Minus } from 'lucide-react';
import { cn } from '@/lib/utils';

export type StageState = 'done' | 'active' | 'pending' | 'error' | 'unavailable';
export interface Stage { label: string; state: StageState; detail?: string }

const icon = (s: StageState) => ({
  done: <Check className="h-4 w-4" />, active: <Loader2 className="h-4 w-4 animate-spin" />, pending: <Circle className="h-3.5 w-3.5" />,
  error: <AlertCircle className="h-4 w-4" />, unavailable: <Minus className="h-4 w-4" />,
}[s]);
const ring: Record<StageState, string> = {
  done: 'bg-rp-success text-white', active: 'bg-rp-primary text-white', pending: 'bg-rp-primary-light text-rp-muted',
  error: 'bg-rp-coral text-white', unavailable: 'bg-rp-warning/15 text-rp-warning',
};

/** Shows only real states handed to it; it never advances on its own. */
export function AnalysisProgress({ stages }: { stages: Stage[] }) {
  return (
    <ol className="space-y-3" aria-label="Analysis progress">
      {stages.map((s) => (
        <li key={s.label} className="flex items-start gap-3" aria-current={s.state === 'active' ? 'step' : undefined}>
          <span className={cn('mt-0.5 grid h-7 w-7 shrink-0 place-items-center rounded-full', ring[s.state])}>{icon(s.state)}</span>
          <div>
            <p className="text-sm font-semibold text-rp-navy">{s.label}</p>
            {s.detail && <p className="text-[13px] text-rp-muted">{s.detail}</p>}
          </div>
        </li>
      ))}
    </ol>
  );
}
