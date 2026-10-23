import { useState, type FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, ClipboardPaste, Link2 } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Badge } from '@/components/ui/Badge';
import { parseProductUrl, type UniversalUrlCheck } from '@/lib/flipkart';
import { ROUTES } from '@/lib/routes';

interface Props {
  initial?: string;
  onSubmit?: (url: string, check: UniversalUrlCheck) => void;
  cta?: string;
  loading?: boolean;
}

/** The unified URL entry point used across Landing, Dashboard and Review Harvester. */
export function UrlAnalyzer({ initial = '', onSubmit, cta = 'Analyze a Product', loading }: Props) {
  const [url, setUrl] = useState(initial);
  const [touched, setTouched] = useState(false);
  const nav = useNavigate();
  const check = parseProductUrl(url);
  const showError = touched && !check.valid;

  const submit = (e: FormEvent) => {
    e.preventDefault();
    setTouched(true);
    if (!check.valid) return;
    if (onSubmit) onSubmit(url.trim(), check);
    else nav(`${ROUTES.harvester}?url=${encodeURIComponent(url.trim())}`);
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
        <p className="mt-2.5 flex flex-wrap items-center gap-2 text-[13px] text-rp-muted" aria-live="polite">
          <Badge tone="success">URL format valid</Badge>
          <span>
            {check.marketplace === 'Flipkart' ? 'PID' : 'ASIN'} <b className="tnum text-rp-navy">{check.id}</b> · {check.marketplace}
          </span>
          {check.title && <span className="font-medium text-rp-primary">({check.title})</span>}
          <span>(format valid; ready for ingestion)</span>
        </p>
      )}
    </form>
  );
}
