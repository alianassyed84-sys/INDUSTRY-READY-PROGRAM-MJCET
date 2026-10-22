import type { HTMLAttributes } from 'react';
import { cn } from '@/lib/utils';

export type BadgeTone = 'neutral' | 'primary' | 'success' | 'warning' | 'danger' | 'info';
const tones: Record<BadgeTone, string> = {
  neutral: 'bg-rp-border/50 text-rp-muted',
  primary: 'bg-rp-primary-light text-rp-primary-hover',
  success: 'bg-rp-success/15 text-rp-success',
  warning: 'bg-rp-warning/15 text-rp-warning',
  danger: 'bg-rp-coral/15 text-rp-coral',
  info: 'bg-rp-info/15 text-rp-info',
};

export function Badge({ tone = 'neutral', className, ...rest }: HTMLAttributes<HTMLSpanElement> & { tone?: BadgeTone }) {
  return (
    <span
      className={cn('inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-semibold', tones[tone], className)}
      {...rest}
    />
  );
}
