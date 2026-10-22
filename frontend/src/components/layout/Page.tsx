import { useEffect, useRef, type ReactNode } from 'react';
import { cn } from '@/lib/utils';
import { pageEntrance } from '@/lib/motion';

export function PageContainer({ children, className }: { children: ReactNode; className?: string }) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => (ref.current ? pageEntrance(ref.current) : undefined), []);
  return (
    <div ref={ref} className={cn('mx-auto w-full max-w-content space-y-6 px-4 py-6 md:space-y-7 md:px-6 md:py-7 lg:px-8 lg:py-8 xl:px-10', className)}>
      {children}
    </div>
  );
}

export function PageHeader({ title, description, actions, meta }: { title: string; description?: string; actions?: ReactNode; meta?: ReactNode }) {
  return (
    <header data-reveal className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
      <div className="min-w-0">
        <h1 className="text-[30px] font-extrabold leading-tight tracking-tight md:text-[34px]">{title}</h1>
        {description && <p className="mt-1.5 max-w-2xl text-[15px] text-rp-muted">{description}</p>}
        {meta && <div className="mt-3 flex flex-wrap items-center gap-2">{meta}</div>}
      </div>
      {actions && <div className="flex flex-wrap items-center gap-2.5">{actions}</div>}
    </header>
  );
}
