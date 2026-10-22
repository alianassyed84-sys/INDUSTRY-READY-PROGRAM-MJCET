import { useMemo, useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip as RTooltip, XAxis, YAxis } from 'recharts';
import { PageContainer, PageHeader } from '@/components/layout/Page';
import { Card, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { DataSourceBadge, EmptyState, ErrorState, LoadingBlock, UnavailableState } from '@/components/ui/states';
import { KpiCard } from '@/components/shared/KpiCard';
import { ChartCard } from '@/components/shared/ChartCard';
import { ProductSelect } from '@/components/shared/ProductSelect';
import { ReviewCard } from '@/components/shared/ReviewCard';
import { CHART } from '@/components/shared/charts';
import { useInsights, useReviews } from '@/hooks/useProduct';
import { pct } from '@/lib/utils';
import { api, type ApiError } from '@/lib/api';

const NAMES: Record<string, string> = { en: 'English', hi: 'Hindi', ta: 'Tamil', te: 'Telugu', kn: 'Kannada', ml: 'Malayalam', bn: 'Bengali', mr: 'Marathi' };

export default function Language() {
  const ins = useInsights();
  const rev = useReviews();
  const [lang, setLang] = useState('');
  const [inputText, setInputText] = useState('');
  const detectMutation = useMutation({
    mutationFn: (text: string) => api.detectLanguage(text),
  });
  const reviews = rev.data?.data ?? [];

  // Counts come from insights if provided, otherwise from review-level labels. Denominator = total reviews loaded.
  const dist = useMemo(() => {
    const given = ins.data?.data.languages;
    if (given?.length) return given.map((l) => ({ code: l.code, label: l.label, count: l.count }));
    const m = new Map<string, number>();
    reviews.forEach((r) => r.language && m.set(r.language, (m.get(r.language) ?? 0) + 1));
    return [...m].map(([code, count]) => ({ code, label: NAMES[code] ?? code.toUpperCase(), count }));
  }, [ins.data, reviews]);

  const classified = dist.reduce((a, b) => a + b.count, 0);
  const total = reviews.length || classified;
  const countable = total > 0 && classified > 0;
  const sorted = [...dist].sort((a, b) => b.count - a.count);
  const samples = reviews.filter((r) => r.language && (!lang || r.language === lang)).slice(0, 6);
  const env = ins.data;

  return (
    <PageContainer>
      <PageHeader title="Language Detection" description="Which languages the reviews are written in, and how much was classified." actions={<ProductSelect />} meta={env && <DataSourceBadge source={env.source} reason={env.fallbackReason} />} />
      {(ins.isLoading || rev.isLoading) && <LoadingBlock label="Loading language analysis" />}
      {(ins.isError || rev.isError) && (
        <ErrorState
          title="Could not load language data"
          description={
            (ins.error as ApiError)?.message ||
            (rev.error as ApiError)?.message ||
            'Failed to load language analysis.'
          }
          requestId={(ins.error as ApiError)?.requestId || (rev.error as ApiError)?.requestId}
          onRetry={() => {
            void ins.refetch();
            void rev.refetch();
          }}
        />
      )}

      {!ins.isLoading && !rev.isLoading && !countable && (
        <UnavailableState title="Language analysis unavailable" description="Neither the insights endpoint nor the review records include language labels for this product, so no chart is shown." />
      )}

      {countable && (
        <>
          <section aria-label="Classification coverage" className="grid gap-4 sm:grid-cols-3">
            <KpiCard label="Total reviews" value={total} hint="Denominator for all percentages" />
            <KpiCard label="Classified" value={classified} hint={`${pct(classified, total)}% of total`} />
            <KpiCard label="Unclassified" value={Math.max(0, total - classified)} hint={`${pct(Math.max(0, total - classified), total)}% of total`} />
          </section>

          <div className="grid gap-6 xl:grid-cols-[1.4fr_1fr]">
            <ChartCard title="Language distribution" subtitle="Reviews per detected language" summary={`Language counts: ${sorted.map((d) => `${d.label} ${d.count}`).join(', ')}.`}>
              <div className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={sorted} margin={{ left: -12, right: 8 }}>
                    <CartesianGrid stroke={CHART.grid} vertical={false} />
                    <XAxis dataKey="label" tick={CHART.tick} axisLine={false} tickLine={false} />
                    <YAxis allowDecimals={false} tick={CHART.tick} axisLine={false} tickLine={false} />
                    <RTooltip {...CHART.tooltip} />
                    <Bar dataKey="count" name="Reviews" radius={[8, 8, 0, 0]}>{sorted.map((d, i) => <Cell key={d.code} fill={i === 0 ? CHART.primary : CHART.primarySoft} />)}</Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </ChartCard>

            <Card data-reveal>
              <CardHeader title="Counts and percentages" subtitle={`Of ${total} total reviews`} />
              <table className="w-full text-sm">
                <thead><tr className="border-b border-rp-border text-left text-xs uppercase tracking-wide text-rp-muted"><th className="pb-2 font-semibold">Language</th><th className="pb-2 text-right font-semibold">Count</th><th className="pb-2 text-right font-semibold">Share</th></tr></thead>
                <tbody>{sorted.map((d) => <tr key={d.code} className="border-b border-rp-border/60 last:border-0"><td className="py-2.5 font-semibold">{d.label} <span className="font-normal text-rp-muted">({d.code})</span></td><td className="tnum py-2.5 text-right">{d.count}</td><td className="tnum py-2.5 text-right">{pct(d.count, total)}%</td></tr>)}</tbody>
              </table>
            </Card>
          </div>

          <section data-reveal>
            <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
              <h2 className="text-[22px] font-extrabold">Analyzed review samples</h2>
              <label className="sr-only" htmlFor="lang-filter">Filter by language</label>
              <select id="lang-filter" value={lang} onChange={(e) => setLang(e.target.value)} className="min-h-[48px] rounded-btn border border-rp-border bg-rp-surface px-3.5 text-sm font-semibold">
                <option value="">All languages</option>
                {sorted.map((d) => <option key={d.code} value={d.code}>{d.label}</option>)}
              </select>
            </div>
            {samples.length ? <div className="grid gap-4 lg:grid-cols-2">{samples.map((r) => <ReviewCard key={r.id} review={r} />)}</div> : <EmptyState title="No labelled samples" description="Review-level language labels were not returned." />}
          </section>
        </>
      )}

      <Card data-reveal className="mt-6">
        <CardHeader
          title="On-Demand Language Identifier"
          subtitle="Test language identification on any custom text using the backend n-gram engine"
        />
        <div className="space-y-3">
          <textarea
            className="w-full rounded-2xl border border-rp-border bg-rp-surface p-3 text-sm focus:border-rp-primary focus:outline-none"
            rows={3}
            placeholder="Type or paste any text to detect its language (e.g. English, Hindi, German, Spanish, French, etc.)..."
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
          />
          <Button
            variant="primary"
            size="md"
            disabled={!inputText.trim()}
            loading={detectMutation.isPending}
            onClick={() => detectMutation.mutate(inputText.trim())}
          >
            Identify Language
          </Button>
          {detectMutation.data && (
            <div className="mt-3 space-y-2 rounded-2xl bg-rp-surface-soft p-3.5 text-xs">
              <div className="flex justify-between">
                <span className="font-semibold text-rp-navy">Detected Language:</span>
                <span className="font-bold text-rp-primary">
                  {detectMutation.data.detected_language_name ?? 'Unknown'} (
                  {detectMutation.data.detected_language ?? '–'})
                </span>
              </div>
              <div className="flex justify-between">
                <span className="font-semibold text-rp-navy">Confidence Level:</span>
                <span className="capitalize">
                  {detectMutation.data.confidence_level} ({Math.round(detectMutation.data.confidence * 100)}%)
                </span>
              </div>
              <div className="flex justify-between">
                <span className="font-semibold text-rp-navy">Fast-Path Method:</span>
                <span>{detectMutation.data.script_fast_path ? 'Script Fast-Path (Non-Latin)' : 'Full N-Gram Profiling'}</span>
              </div>
              {detectMutation.data.candidates.length > 0 && (
                <div className="pt-1">
                  <span className="font-semibold text-rp-navy">Top Candidates: </span>
                  <span>
                    {detectMutation.data.candidates
                      .slice(0, 4)
                      .map((c) => `${c.language_name} (${Math.round(c.confidence * 100)}%)`)
                      .join(', ')}
                  </span>
                </div>
              )}
            </div>
          )}
          {detectMutation.isError && (
            <p className="text-xs font-semibold text-rp-coral">
              Detection failed: {(detectMutation.error as ApiError).message}
            </p>
          )}
        </div>
      </Card>
    </PageContainer>
  );
}
