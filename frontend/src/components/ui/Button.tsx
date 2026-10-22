import { forwardRef, type ButtonHTMLAttributes } from 'react';
import { Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

export type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger';
export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: 'md' | 'lg' | 'icon';
  loading?: boolean;
}

const variants: Record<ButtonVariant, string> = {
  primary: 'bg-rp-primary text-white shadow-[0_8px_20px_-8px_rgba(113,56,245,.6)] hover:bg-rp-primary-hover',
  secondary: 'border border-rp-border bg-rp-surface text-rp-navy hover:border-rp-primary-soft hover:bg-rp-primary-light',
  ghost: 'text-rp-text hover:bg-rp-primary-light',
  danger: 'bg-rp-coral text-white hover:brightness-95',
};
const sizes = { md: 'min-h-[44px] px-5 text-sm', lg: 'min-h-[52px] px-7 text-[15px]', icon: 'h-11 w-11' };

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ variant = 'primary', size = 'md', loading, disabled, className, children, ...rest }, ref) => (
    <button
      ref={ref}
      disabled={disabled || loading}
      className={cn(
        'inline-flex items-center justify-center gap-2 rounded-btn font-semibold transition-colors',
        'disabled:cursor-not-allowed disabled:opacity-55',
        variants[variant],
        sizes[size],
        className,
      )}
      {...rest}
    >
      {loading && <Loader2 className="h-4 w-4 animate-spin" aria-hidden />}
      {children}
    </button>
  ),
);
Button.displayName = 'Button';
