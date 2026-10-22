import type { ReactNode } from 'react';
import { Card } from '@/components/ui/Card';

export function KpiCard({ label, value, hint, icon }: { label: string; value: ReactNode; hint?: string; icon?: ReactNode }) {
  return (
    <Card interactive data-reveal className="!p-5">
      <div className="flex items-center justify-between">
        <p className="text-[13px] font-semibold text-rp-muted">{label}</p>
        {icon && <span className="grid h-9 w-9 place-items-center rounded-xl bg-rp-primary-light text-rp-primary">{icon}</span>}
      </div>
      <p className="tnum mt-2 font-heading text-[32px] font-extrabold leading-none text-rp-navy">{value}</p>
      {hint && <p className="mt-2 text-xs text-rp-muted">{hint}</p>}
    </Card>
  );
}
