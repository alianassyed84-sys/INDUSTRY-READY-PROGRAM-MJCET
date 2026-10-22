import { forwardRef, useId, type InputHTMLAttributes, type ReactNode } from 'react';
import { cn } from '@/lib/utils';

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  hint?: string;
  error?: string;
  leading?: ReactNode;
  trailing?: ReactNode;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, hint, error, leading, trailing, className, id, ...rest }, ref) => {
    const auto = useId();
    const inputId = id ?? auto;
    const describedBy = error ? `${inputId}-err` : hint ? `${inputId}-hint` : undefined;
    return (
      <div className={cn('w-full', className)}>
        {label && (
          <label htmlFor={inputId} className="mb-1.5 block text-sm font-semibold text-rp-navy">
            {label}
          </label>
        )}
        <div
          className={cn(
            'flex min-h-[48px] items-center gap-2 rounded-btn border bg-rp-surface px-3.5 transition-shadow',
            'focus-within:border-rp-primary focus-within:shadow-focus',
            error ? 'border-rp-coral' : 'border-rp-border',
          )}
        >
          {leading && <span className="text-rp-muted">{leading}</span>}
          <input
            ref={ref}
            id={inputId}
            aria-invalid={!!error}
            aria-describedby={describedBy}
            className="min-w-0 flex-1 bg-transparent py-3 text-[15px] text-rp-text outline-none placeholder:text-rp-muted/70 focus-visible:shadow-none"
            {...rest}
          />
          {trailing}
        </div>
        {error ? (
          <p id={`${inputId}-err`} role="alert" className="mt-1.5 text-[13px] text-rp-coral">{error}</p>
        ) : hint ? (
          <p id={`${inputId}-hint`} className="mt-1.5 text-[13px] text-rp-muted">{hint}</p>
        ) : null}
      </div>
    );
  },
);
Input.displayName = 'Input';
