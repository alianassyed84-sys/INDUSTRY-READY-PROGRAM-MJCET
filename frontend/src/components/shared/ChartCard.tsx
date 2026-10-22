import type { ReactNode } from 'react';
import { Card, CardHeader } from '@/components/ui/Card';

/** Chart container. `summary` is a text alternative announced to assistive tech. */
export function ChartCard({ title, subtitle, summary, action, children, className }: { title: string; subtitle?: string; summary: string; action?: ReactNode; children: ReactNode; className?: string }) {
  return (
    <Card className={className} data-reveal>
      <CardHeader title={title} subtitle={subtitle} action={action} />
      <div role="img" aria-label={summary}>{children}</div>
      <p className="sr-only">{summary}</p>
    </Card>
  );
}
