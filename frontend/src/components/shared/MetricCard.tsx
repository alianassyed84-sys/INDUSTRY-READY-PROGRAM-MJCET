import type { ReactNode } from 'react';
import { Card } from '@/components/ui/Card';
import { Tooltip } from '@/components/ui/Tooltip';
import { HelpCircle } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface MetricCardProps {
  label: string;
  value: ReactNode;
  hint?: string;
  tooltip?: string;
  icon?: ReactNode;
  className?: string;
}

/**
 * MetricCard: displays a single KPI metric.
 * Per spec: Every number has a plain-language meaning with a tooltip ("What does this mean?").
 */
export function MetricCard({ label, value, hint, tooltip, icon, className }: MetricCardProps) {
  return (
    <Card interactive data-reveal className={cn('rp-kpi !p-5', className)}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-1.5">
          <p className="text-[13px] font-semibold text-rp-muted">{label}</p>
          {tooltip && (
            <Tooltip label={tooltip} side="top">
              <button
                type="button"
                aria-label={`What does ${label} mean?`}
                className="text-rp-muted hover:text-rp-navy transition-colors inline-flex items-center justify-center p-0.5 rounded"
              >
                <HelpCircle className="h-3.5 w-3.5" aria-hidden="true" />
              </button>
            </Tooltip>
          )}
        </div>
        {icon && (
          <span className="grid h-9 w-9 place-items-center rounded-xl bg-rp-primary-light text-rp-primary">
            {icon}
          </span>
        )}
      </div>
      <p className="tnum mt-2 font-heading text-[32px] font-extrabold leading-none text-rp-navy">{value}</p>
      {hint && <p className="mt-2 text-xs text-rp-muted">{hint}</p>}
    </Card>
  );
}
