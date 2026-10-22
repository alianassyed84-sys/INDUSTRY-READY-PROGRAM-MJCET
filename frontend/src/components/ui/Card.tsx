import type { HTMLAttributes, ReactNode } from 'react';
import { cn } from '@/lib/utils';

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  /** `featured` is the lavender surface used for primary and selected content. */
  tone?: 'default' | 'featured';
  interactive?: boolean;
}

export function Card({ tone = 'default', interactive, className, ...rest }: CardProps) {
  return (
    <div
      className={cn(
        'rp-card',
        tone === 'featured' && 'border-rp-primary-soft bg-gradient-to-br from-rp-primary-light to-rp-surface-soft',
        interactive && 'rp-lift',
        className,
      )}
      {...rest}
    />
  );
}

export function CardHeader({ title, action, subtitle }: { title: string; action?: ReactNode; subtitle?: string }) {
  return (
    <div className="mb-4 flex items-start justify-between gap-3">
      <div>
        <h3 className="text-[17px] font-bold">{title}</h3>
        {subtitle && <p className="mt-0.5 text-[13px] text-rp-muted">{subtitle}</p>}
      </div>
      {action}
    </div>
  );
}
