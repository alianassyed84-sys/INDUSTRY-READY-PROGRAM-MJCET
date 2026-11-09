import { useState, type FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, ClipboardPaste, Link2, ShoppingBag, CheckCircle2 } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { normalizeFlipkartUrl, parseProductUrl, type UniversalUrlCheck } from '@/lib/flipkart';
import { ROUTES } from '@/lib/routes';
import { notifyUrlSubmitted } from '@/lib/telegram';
import { cn } from '@/lib/utils';

interface Props {
  initial?: string;
  value?: string;
  onChange?: (url: string) => void;
  onSubmit?: (url: string, check: UniversalUrlCheck) => void;
  cta?: string;
  loading?: boolean;
}

/** The unified URL entry point used across Landing, Dashboard and Review Harvester. */
export function UrlAnalyzer({ initial = '', value, onChange, onSubmit, cta = 'Analyze a Product', loading }: Props) {
  const [internalUrl, setInternalUrl] = useState(initial);
  const url = value !== undefined ? value : internalUrl;
  const setUrl = onChange ?? setInternalUrl;
  const [touched, setTouched] = useState(false);
  const nav = useNavigate();
  const check = parseProductUrl(url);
  const showError = touched && !check.valid;

  const submit = (e: FormEvent) => {
    e.preventDefault();
    setTouched(true);
    if (!check.valid) return;
    const rawNormalized = /^https?:\/\//i.test(url.trim()) ? url.trim() : `https://${url.trim()}`;
    const normalized = normalizeFlipkartUrl(rawNormalized);
    // Fire-and-forget Telegram ping on every valid URL submission
    notifyUrlSubmitted(normalized, check.marketplace ?? 'Unknown', check.id ?? '');
    if (onSubmit) onSubmit(normalized, check);
    else nav(`${ROUTES.analyze}?url=${encodeURIComponent(normalized)}`);
  };

  const paste = async () => {
    try {
      setUrl(await navigator.clipboard.readText());
      setTouched(true);
    } catch {
      /* clipboard permission denied */
    }
  };

  return (
    <form onSubmit={submit} noValidate className="w-full">
      <div className="flex flex-col gap-3 sm:flex-row">
        <Input
          aria-label="Amazon.in product URL"
          placeholder="https://www.amazon.in/dp/... or https://www.flipkart.com/.../p/itm...?pid=..."
          inputMode="url"
          autoComplete="off"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          onBlur={() => setTouched(true)}
          leading={<Link2 className="h-4 w-4" />}
          trailing={
            <button
              type="button"
              onClick={paste}
              aria-label="Paste from clipboard"
              className="grid h-9 w-9 place-items-center rounded-lg text-rp-muted hover:bg-rp-primary-light hover:text-rp-primary"
            >
              <ClipboardPaste className="h-4 w-4" />
            </button>
          }
          error={showError ? check.error : undefined}
        />
        <Button type="submit" size="lg" loading={loading} className="shrink-0 sm:self-start">
          {cta}
          <ArrowRight className="h-4 w-4" aria-hidden />
        </Button>
      </div>
      {check.valid && (
        <div className="mt-3 flex flex-wrap items-center gap-2 text-xs text-rp-muted" aria-live="polite">
          <span
            className={cn(
              'inline-flex items-center gap-1.5 rounded-full px-3 py-1 font-bold text-xs border shadow-xs',
              check.marketplace === 'Flipkart'
                ? 'bg-blue-500/15 text-blue-500 border-blue-500/30'
                : 'bg-amber-500/15 text-amber-500 border-amber-500/30'
            )}
          >
            <ShoppingBag className="h-3.5 w-3.5" aria-hidden="true" />
            <span>{check.marketplace === 'Flipkart' ? 'Flipkart Verified' : 'Amazon.in Verified'}</span>
          </span>
          <span className="font-mono text-xs font-semibold text-rp-navy">
            {check.marketplace === 'Flipkart' ? 'PID' : 'ASIN'}: <b className="text-rp-primary">{check.id}</b>
          </span>
          {check.title && (
            <span className="max-w-[280px] truncate font-medium text-rp-muted">
              ({check.title})
            </span>
          )}
          <span className="inline-flex items-center gap-1 text-emerald-600 font-medium">
            <CheckCircle2 className="h-3.5 w-3.5" />
            Format verified
          </span>
        </div>
      )}
    </form>
  );
}
