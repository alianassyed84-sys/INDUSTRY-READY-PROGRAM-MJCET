import { useEffect, useState } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  Database,
  History,
  Play,
  ShoppingBag,
  Sparkles,
  ExternalLink,
  CheckCircle2,
  ThumbsUp,
  Tag,
  Coins,
} from 'lucide-react';
import { PageContainer, PageHeader } from '@/components/layout/Page';
import { Card, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Dialog } from '@/components/ui/Dialog';
import { UnavailableState } from '@/components/ui/states';
import { AnalysisProgress, type Stage } from '@/components/shared/AnalysisProgress';
import { UrlAnalyzer } from '@/components/shared/UrlAnalyzer';
import { ProductCard } from '@/components/shared/ProductCard';
import { useProductContext } from '@/hooks/useProduct';
import { api, API_BASE_URL, ApiError } from '@/lib/api';
import { parseProductUrl, type UniversalUrlCheck } from '@/lib/flipkart';
import { adaptProduct } from '@/lib/adapters';
import { ROUTES } from '@/lib/routes';
import type { BackendFlipkartScrapeResponse } from '@/lib/types';

export default function Harvester() {
  const [params] = useSearchParams();
  const initial = params.get('url') ?? '';
  const [rawUrl, setRawUrl] = useState(initial);
  const [submitted, setSubmitted] = useState<UniversalUrlCheck | null>(
    initial ? parseProductUrl(initial) : null,
  );
  const [confirmJob, setConfirmJob] = useState(false);
  const { products } = useProductContext();
  const queryClient = useQueryClient();

  // Flipkart Apify Scraper controls
  const [fkMaxItems, setFkMaxItems] = useState(25);
  const [fkMaxPages, setFkMaxPages] = useState(3);
  const [fkResult, setFkResult] = useState<BackendFlipkartScrapeResponse | null>(null);

  useEffect(() => {
    const urlParam = params.get('url');
    if (urlParam && urlParam !== rawUrl) {
      setRawUrl(urlParam);
      setSubmitted(parseProductUrl(urlParam));
    }
  }, [params, rawUrl]);

  const health = useQuery({
    queryKey: ['health'],
    queryFn: ({ signal }) => api.health(signal),
    retry: false,
    staleTime: 15_000,
  });

  // Real backend URL analysis query (handles both Amazon.in and Flipkart URLs)
  const analyzeQuery = useQuery({
    queryKey: ['analyze-url', rawUrl],
    queryFn: ({ signal }) => api.analyzeUrl(rawUrl, signal),
    enabled: !!submitted?.valid && !!rawUrl,
    retry: false,
  });

  // Flipkart Apify Actor scraping mutation
  const flipkartMutation = useMutation({
    mutationFn: (targetUrl: string) =>
      api.scrapeFlipkart({
        url: targetUrl,
        max_items: fkMaxItems,
        max_pages_per_product: fkMaxPages,
      }),
    onSuccess: (data) => {
      setFkResult(data);
      void queryClient.invalidateQueries({ queryKey: ['products'] });
      void analyzeQuery.refetch();
    },
  });

  // Admin CSV import job mutation
  const [jobResult, setJobResult] = useState<string | null>(null);
  const startJobMutation = useMutation({
    mutationFn: () => api.startJob('csv_amazon'),
    onSuccess: (data) => {
      setJobResult(
        `Job #${data.id} completed: ${data.products_inserted} products, ${data.reviews_inserted} reviews imported (${data.warning_count} warnings).`,
      );
      void queryClient.invalidateQueries({ queryKey: ['products'] });
    },
    onError: (err: ApiError) => {
      setJobResult(`Job failed: ${err.message} (HTTP ${err.status ?? 'error'})`);
    },
  });

  const err = analyzeQuery.error as ApiError | null;
  const analysisData = analyzeQuery.data;

  // Stages reflect genuine states from the server
  const stages: Stage[] = [
    {
      label: 'URL validation',
      state: submitted?.valid ? 'done' : submitted ? 'error' : 'pending',
      detail: submitted?.valid
        ? `${submitted.marketplace === 'Flipkart' ? 'PID' : 'ASIN'} ${submitted.id} · ${submitted.marketplace}`
        : submitted?.error,
    },
    {
      label: 'Provider retrieval',
      state: analyzeQuery.isLoading || flipkartMutation.isPending
        ? 'active'
        : analyzeQuery.isSuccess || fkResult
          ? 'done'
          : err || flipkartMutation.error
            ? 'error'
            : submitted?.valid
              ? 'pending'
              : 'pending',
      detail: analyzeQuery.isLoading || flipkartMutation.isPending
        ? `Querying ${submitted?.marketplace ?? 'catalog'} provider / Apify Actor…`
        : analyzeQuery.isSuccess
          ? `Product ${analysisData?.asin} resolved successfully`
          : fkResult
            ? `Exported ${fkResult.reviews_count} reviews (${fkResult.is_mock_provider ? 'Simulation' : 'Apify Live'})`
            : err
              ? `${err.message}${err.requestId ? ` (Req ID: ${err.requestId.slice(0, 8)})` : ''}`
              : submitted?.valid
                ? 'Ready to query backend.'
                : undefined,
    },
    {
      label: 'Persistence',
      state: analyzeQuery.isSuccess || fkResult ? 'done' : 'pending',
      detail: analyzeQuery.isSuccess
        ? `${analysisData?.price_history.snapshots.length ?? 0} price snapshot(s) stored`
        : fkResult
          ? `${fkResult.reviews_count} reviews persisted in database`
          : 'Starts after retrieval succeeds.',
    },
    {
      label: 'Review analysis',
      state: analyzeQuery.isSuccess || fkResult ? 'done' : 'pending',
      detail: analyzeQuery.isSuccess
        ? analysisData?.status_note ?? 'Analysis complete.'
        : fkResult
          ? fkResult.status_note
          : 'Starts after reviews are stored.',
    },
  ];

  return (
    <PageContainer>
      <PageHeader
        title="Review Harvester"
        description="Unified Amazon.in & Flipkart review intelligence: validate, scrape with Apify Actor, store and analyze."
      />

      {/* Main URL Ingestion Card */}
      <Card data-reveal tone="featured" className="!p-6 md:!p-8">
        <div className="flex flex-wrap items-center justify-between gap-2 mb-1">
          <h2 className="text-[20px] font-extrabold">Product URL Ingestion</h2>
          <div className="flex items-center gap-2">
            <Badge tone="primary">Amazon.in</Badge>
            <Badge tone="success">Flipkart (Apify Actor)</Badge>
          </div>
        </div>
        <p className="mb-5 text-sm text-rp-muted">
          Paste a full Amazon.in or Flipkart product link. Flipkart links trigger the official{' '}
          <code className="text-xs bg-rp-surface-soft px-1.5 py-0.5 rounded font-mono text-rp-navy">
            automation-lab/flipkart-product-reviews-scraper
          </code>{' '}
          Actor pipeline.
        </p>
        <UrlAnalyzer
          initial={initial}
          cta="Analyze"
          loading={analyzeQuery.isLoading || flipkartMutation.isPending}
          onSubmit={(u, c) => {
            setRawUrl(u);
            setSubmitted(c);
            setFkResult(null);
          }}
        />
      </Card>

      {/* Dedicated Flipkart Apify Scraper Studio Card */}
      <Card data-reveal className="!p-6 border-2 border-rp-primary/20 bg-gradient-to-br from-rp-surface via-rp-surface to-rp-primary/5">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-rp-border pb-4">
          <div className="flex items-center gap-3">
            <div className="grid h-10 w-10 place-items-center rounded-xl bg-rp-primary text-white shadow-md">
              <ShoppingBag className="h-5 w-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-base font-extrabold text-rp-navy">Flipkart Product Reviews Scraper</h3>
                <Badge tone="success">Apify Actor Ready</Badge>
              </div>
              <p className="text-xs text-rp-muted font-mono">automation-lab/flipkart-product-reviews-scraper</p>
            </div>
          </div>
          <div className="flex items-center gap-2 text-xs text-rp-muted bg-rp-surface-soft px-3 py-1.5 rounded-lg border border-rp-border">
            <Coins className="h-4 w-4 text-rp-primary" />
            <span>Pay-per-event: $0.0005 start + $0.00183/review</span>
          </div>
        </div>

        <div className="mt-4 grid gap-4 md:grid-cols-3">
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-rp-muted mb-1.5">
              Max Reviews Cap
            </label>
            <div className="flex gap-2">
              {[10, 25, 50, 100].map((num) => (
                <button
                  key={num}
                  type="button"
                  onClick={() => setFkMaxItems(num)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-colors ${
                    fkMaxItems === num
                      ? 'bg-rp-primary text-white shadow-sm'
                      : 'bg-rp-surface-soft text-rp-muted hover:text-rp-navy'
                  }`}
                >
                  {num}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-rp-muted mb-1.5">
              Max Pages Per Product
            </label>
            <div className="flex gap-2">
              {[1, 2, 3, 5].map((pages) => (
                <button
                  key={pages}
                  type="button"
                  onClick={() => setFkMaxPages(pages)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-colors ${
                    fkMaxPages === pages
                      ? 'bg-rp-primary text-white shadow-sm'
                      : 'bg-rp-surface-soft text-rp-muted hover:text-rp-navy'
                  }`}
                >
                  {pages} {pages === 1 ? 'page' : 'pages'}
                </button>
              ))}
            </div>
          </div>

          <div className="flex items-end">
            <Button
              variant="primary"
              className="w-full"
              loading={flipkartMutation.isPending}
              onClick={() => {
                const target =
                  rawUrl && rawUrl.includes('flipkart.com')
                    ? rawUrl
                    : 'https://www.flipkart.com/apple-iphone-15-black-128-gb/p/itm6ac6485515ae4?pid=MOBGTAGPNRQA7CS3';
                flipkartMutation.mutate(target);
              }}
            >
              <Sparkles className="h-4 w-4 mr-1.5" />
              Run Apify Flipkart Scraper
            </Button>
          </div>
        </div>

        {/* Scraper Live Result Box */}
        {fkResult && (
          <div className="mt-5 rounded-2xl bg-rp-surface-soft p-4 border border-rp-border">
            <div className="flex flex-wrap items-center justify-between gap-2 border-b border-rp-border/50 pb-3">
              <div>
                <span className="text-xs font-bold uppercase text-rp-primary">Scrape Succeeded</span>
                <h4 className="text-sm font-extrabold text-rp-navy">{fkResult.product_name}</h4>
                <p className="text-xs text-rp-muted">{fkResult.status_note}</p>
              </div>
              <div className="flex items-center gap-2">
                <Badge tone={fkResult.is_mock_provider ? 'neutral' : 'success'}>
                  {fkResult.is_mock_provider ? 'Simulation Mode' : 'Live Apify Run'}
                </Badge>
                <Link
                  to={ROUTES.analysis}
                  className="inline-flex items-center gap-1 text-xs font-bold text-rp-primary hover:underline bg-rp-primary/10 px-2.5 py-1 rounded-lg"
                >
                  Deep-Dive ABSA <ExternalLink className="h-3 w-3" />
                </Link>
              </div>
            </div>

            {/* Scraped Reviews Cards Carousel/Grid */}
            <div className="mt-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {fkResult.reviews.slice(0, 6).map((rev) => (
                <div
                  key={rev.reviewId}
                  className="rounded-xl bg-rp-surface p-3 border border-rp-border shadow-xs flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-center justify-between gap-1 mb-1">
                      <span className="text-xs font-extrabold text-rp-gold">
                        {'★'.repeat(Math.round(rev.rating ?? 5))}
                        <span className="text-rp-muted/40">{'★'.repeat(5 - Math.round(rev.rating ?? 5))}</span>
                      </span>
                      <span className="text-[11px] text-rp-muted">{rev.displayedDate ?? 'Recent'}</span>
                    </div>
                    {rev.title && <p className="text-xs font-bold text-rp-navy mb-1 line-clamp-1">{rev.title}</p>}
                    <p className="text-xs text-rp-muted line-clamp-3 mb-2">{rev.text}</p>
                  </div>

                  <div className="pt-2 border-t border-rp-border/50 text-[11px] space-y-1">
                    <div className="flex items-center justify-between text-rp-navy font-semibold">
                      <span>{rev.reviewer ?? 'Flipkart Customer'}</span>
                      {rev.certifiedBuyer && (
                        <span className="inline-flex items-center gap-0.5 text-rp-success font-bold text-[10px]">
                          <CheckCircle2 className="h-3 w-3" /> Certified
                        </span>
                      )}
                    </div>
                    {rev.variant && rev.variant.length > 0 && (
                      <div className="flex flex-wrap gap-1">
                        {rev.variant.map((v, i) => (
                          <span key={i} className="inline-flex items-center gap-0.5 bg-rp-primary-light text-rp-primary px-1.5 py-0.2 rounded text-[10px]">
                            <Tag className="h-2.5 w-2.5" /> {v.name}: {v.value}
                          </span>
                        ))}
                      </div>
                    )}
                    {(rev.helpfulCount !== undefined && rev.helpfulCount !== null && rev.helpfulCount > 0) && (
                      <span className="inline-flex items-center gap-1 text-[10px] text-rp-muted">
                        <ThumbsUp className="h-2.5 w-2.5" /> {rev.helpfulCount} found helpful
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </Card>

      <div className="grid gap-6 xl:grid-cols-[1fr_1fr]">
        <Card data-reveal>
          <CardHeader
            title="Analysis progress"
            subtitle="Real states only; nothing is simulated"
            action={
              submitted?.valid && (
                <Button
                  variant="secondary"
                  onClick={() => {
                    void analyzeQuery.refetch();
                    void health.refetch();
                  }}
                  loading={analyzeQuery.isFetching || health.isFetching}
                >
                  Retry
                </Button>
              )
            }
          />
          <AnalysisProgress stages={stages} />
          {submitted?.valid && (
            <p className="mt-4 rounded-2xl bg-rp-surface-soft p-3.5 text-sm text-rp-muted">
              Backend at <code className="rounded bg-rp-primary-light px-1.5 py-0.5 text-[13px]">{API_BASE_URL}</code>{' '}
              is{' '}
              {health.isLoading || health.isFetching ? (
                'being checked…'
              ) : health.isError ? (
                <b className="text-rp-coral">unreachable</b>
              ) : (
                <b className="text-rp-success">reachable</b>
              )}
              .{err && <span className="block mt-1 font-semibold text-rp-coral">{err.message}</span>}
            </p>
          )}
        </Card>

        <div className="space-y-6">
          <Card data-reveal>
            <CardHeader title="Product preview" />
            {analysisData?.product ? (
              <div className="space-y-4">
                <ProductCard product={adaptProduct(analysisData.product)} />
                <div className="flex justify-end">
                  <Link
                    to={ROUTES.analysis}
                    className="inline-flex items-center gap-1.5 text-sm font-bold text-rp-primary hover:underline"
                  >
                    View NLP Analysis & Reviews →
                  </Link>
                </div>
              </div>
            ) : err ? (
              <UnavailableState
                title="Analysis could not be completed"
                description={err.message}
              />
            ) : (
              <UnavailableState
                title="No provider data yet"
                description="A preview appears here once a real retrieval returns product details."
              />
            )}
          </Card>

          <Card data-reveal>
            <CardHeader
              title="Job Management (Admin)"
              action={<History className="h-5 w-5 text-rp-muted" aria-hidden />}
            />
            <p className="text-sm text-rp-muted">
              Synchronously triggers backend ingestion of the server-configured Amazon review CSV dataset.
            </p>
            <div className="mt-3 flex items-center gap-3">
              <Button
                variant="primary"
                onClick={() => setConfirmJob(true)}
                loading={startJobMutation.isPending}
              >
                <Play className="h-4 w-4 mr-1.5" />
                Run CSV Import Job
              </Button>
            </div>
            {jobResult && (
              <p className="mt-3 rounded-xl bg-rp-surface-soft p-3 text-xs font-mono text-rp-navy">
                {jobResult}
              </p>
            )}

            <Dialog open={confirmJob} onClose={() => setConfirmJob(false)} title="Confirm Dataset Ingestion">
              <div className="space-y-4">
                <p className="text-sm text-rp-muted">
                  This will trigger backend ingestion of the server-configured review dataset. Existing products and snapshots may be updated. Do you want to proceed?
                </p>
                <div className="flex justify-end gap-3 pt-2">
                  <Button variant="secondary" onClick={() => setConfirmJob(false)}>Cancel</Button>
                  <Button
                    variant="primary"
                    onClick={() => {
                      setConfirmJob(false);
                      startJobMutation.mutate();
                    }}
                  >
                    Run Ingestion
                  </Button>
                </div>
              </div>
            </Dialog>
          </Card>
        </div>
      </div>

      <section data-reveal aria-labelledby="csv">
        <div className="mb-4 flex items-center gap-2">
          <Database className="h-5 w-5 text-rp-primary" aria-hidden />
          <h2 id="csv" className="text-[20px] font-extrabold">Existing datasets</h2>
          <Badge tone="neutral">Catalog</Badge>
        </div>
        {products.length ? (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {products.map((p) => (
              <Link key={p.id} to={ROUTES.analysis} className="block rounded-card">
                <ProductCard product={p} />
              </Link>
            ))}
          </div>
        ) : (
          <UnavailableState title="No datasets found" />
        )}
      </section>
    </PageContainer>
  );
}
