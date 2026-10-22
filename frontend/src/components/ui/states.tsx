import type { ReactNode } from 'react';
import { AlertTriangle, Inbox, Hammer, FlaskConical } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from './Button';
import { Badge } from './Badge';
import type { DataSource } from '@/lib/types';

export function Skeleton({ className }: { className?: string }) {
  return <div aria-hidden className={cn('animate-pulse rounded-xl bg-rp-primary-light/70', className)} />;
}

export function LoadingBlock({ label = 'Loading' }: { label?: string }) {
  return (
    <div role="status" aria-live="polite" className="space-y-3">
      <span className="sr-only">{label}</span>
      <Skeleton className="h-6 w-1/3" />
      <Skeleton className="h-28 w-full" />
      <Skeleton className="h-4 w-2/3" />
    </div>
  );
}

interface StateProps { title: string; description?: string; action?: ReactNode; className?: string }

function StateShell({ icon, tone, title, description, action, className }: StateProps & { icon: ReactNode; tone: string }) {
  return (
    <div className={cn('flex flex-col items-center rounded-card border border-dashed border-rp-border bg-rp-surface-soft/50 px-6 py-10 text-center', className)}>
      <span className={cn('mb-3 grid h-12 w-12 place-items-center rounded-2xl', tone)}>{icon}</span>
      <h3 className="text-base font-bold">{title}</h3>
      {description && <p className="mt-1.5 max-w-md text-sm text-rp-muted">{description}</p>}
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}

export const EmptyState = (p: StateProps) => <StateShell {...p} tone="bg-rp-primary-light text-rp-primary" icon={<Inbox className="h-6 w-6" />} />;
export const UnavailableState = (p: StateProps) => <StateShell {...p} tone="bg-rp-warning/15 text-rp-warning" icon={<Hammer className="h-6 w-6" />} />;

export function ErrorState({
  title = 'Something went wrong',
  description,
  requestId,
  onRetry,
}: {
  title?: string;
  description?: string;
  requestId?: string;
  onRetry?: () => void;
}) {
  return (
    <div role="alert" className="flex items-start gap-3 rounded-2xl border border-rp-coral/30 bg-rp-coral/10 p-4">
      <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-rp-coral" aria-hidden />
      <div className="flex-1">
        <p className="font-semibold text-rp-coral">{title}</p>
        {description && <p className="mt-0.5 text-sm text-rp-text/85">{description}</p>}
        {requestId && (
          <p className="mt-1 font-mono text-xs text-rp-muted">
            Request ID: <span className="text-rp-navy">{requestId}</span>
          </p>
        )}
      </div>
      {onRetry && <Button variant="secondary" onClick={onRetry}>Retry</Button>}
    </div>
  );
}

export function DataSourceBadge({ source, reason }: { source: DataSource; reason?: string }) {
  return source === 'demo' ? (
    <Badge tone="warning" title={reason ? `Backend unreachable: ${reason}` : 'Fixture data'}>
      <FlaskConical className="h-3.5 w-3.5" aria-hidden /> Demo data
    </Badge>
  ) : (
    <Badge tone="success">Live data</Badge>
  );
}
