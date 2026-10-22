import { useEffect, useState } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Database, History, Play } from 'lucide-react';
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
import { parseAmazonUrl, type UrlCheck } from '@/lib/amazon';
import { adaptProduct } from '@/lib/adapters';
import { ROUTES } from '@/lib/routes';

export default function Harvester() {
  const [params] = useSearchParams();
  const initial = params.get('url') ?? '';
  const [rawUrl, setRawUrl] = useState(initial);
  const [submitted, setSubmitted] = useState<UrlCheck | null>(initial ? parseAmazonUrl(initial) : null);
  const [confirmJob, setConfirmJob] = useState(false);
  const { products } = useProductContext();
  const queryClient = useQueryClient();

  useEffect(() => {
    const urlParam = params.get('url');
    if (urlParam && urlParam !== rawUrl) {
      setRawUrl(urlParam);
      setSubmitted(parseAmazonUrl(urlParam));
    }
  }, [params, rawUrl]);

  const health = useQuery({
    queryKey: ['health'],
    queryFn: ({ signal }) => api.health(signal),
    retry: false,
    staleTime: 15_000,
  });

  // Real backend URL analysis query
  const analyzeQuery = useQuery({
    queryKey: ['analyze-url', rawUrl],
    queryFn: ({ signal }) => api.analyzeUrl(rawUrl, signal),
    enabled: !!submitted?.valid && !!rawUrl,
    retry: false,
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
      detail: submitted?.valid ? `ASIN ${submitted.asin} · ${submitted.marketplace}` : submitted?.error,
    },
    {
      label: 'Provider retrieval',
      state: analyzeQuery.isLoading
        ? 'active'
        : analyzeQuery.isSuccess
          ? 'done'
          : err
            ? 'error'
            : submitted?.valid
              ? 'pending'
              : 'pending',
      detail: analyzeQuery.isLoading
        ? 'Querying product catalog / provider…'
        : analyzeQuery.isSuccess
          ? `ASIN ${analysisData?.asin} resolved successfully`
          : err
            ? `${err.message}${err.requestId ? ` (Req ID: ${err.requestId.slice(0, 8)})` : ''}`
            : submitted?.valid
              ? 'Ready to query backend.'
              : undefined,
    },
    {
      label: 'Persistence',
      state: analyzeQuery.isSuccess ? 'done' : 'pending',
      detail: analyzeQuery.isSuccess
        ? `${analysisData?.price_history.snapshots.length ?? 0} price snapshot(s) stored`
        : 'Starts after retrieval succeeds.',
    },
    {
      label: 'Review analysis',
      state: analyzeQuery.isSuccess ? 'done' : 'pending',
      detail: analyzeQuery.isSuccess
        ? analysisData?.status_note ?? 'Analysis complete.'
        : 'Starts after reviews are stored.',
    },
  ];

  return (
    <PageContainer>
      <PageHeader
        title="Review Harvester"
        description="Guided Amazon.in product analysis: validate, retrieve, store and analyze."
      />

      <Card data-reveal tone="featured" className="!p-6 md:!p-8">
        <h2 className="mb-1 text-[20px] font-extrabold">Product URL</h2>
        <p className="mb-5 text-sm text-rp-muted">
          Paste a full Amazon.in product link to analyze pricing and customer reviews.
        </p>
        <UrlAnalyzer
          initial={initial}
          cta="Analyze"
          loading={analyzeQuery.isLoading}
          onSubmit={(u, c) => {
            setRawUrl(u);
            setSubmitted(c);
          }}
        />
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
          <Badge tone="neutral">CSV harvester</Badge>
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
