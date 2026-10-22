import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Bar, BarChart, CartesianGrid, Cell, Pie, PieChart, ResponsiveContainer, Tooltip as RTooltip, XAxis, YAxis } from 'recharts';
import { Star } from 'lucide-react';
import { PageContainer, PageHeader } from '@/components/layout/Page';
import { Card, CardHeader } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { EmptyState, ErrorState, LoadingBlock, DataSourceBadge, UnavailableState } from '@/components/ui/states';
import { ChartCard } from '@/components/shared/ChartCard';
import { ProductSelect } from '@/components/shared/ProductSelect';
import { CHART } from '@/components/shared/charts';
import { useInsights } from '@/hooks/useProduct';
import { fmtDate, pct } from '@/lib/utils';
import { api, type ApiError } from '@/lib/api';

const Field = ({ label, value }: { label: string; value?: string | number }) => (
  <div>
    <dt className="text-xs font-semibold uppercase tracking-wide text-rp-muted">{label}</dt>
    <dd className="tnum mt-0.5 text-[15px] font-semibold text-rp-navy">{value ?? <span className="font-normal text-rp-muted">Unavailable</span>}</dd>
  </div>
);

export default function Analysis() {
  const q = useInsights();
  const env = q.data;
  const ins = env?.data;
  const [sentimentText, setSentimentText] = useState('');
  const [aspectInput, setAspectInput] = useState('battery, camera, quality');
  const sentimentMutation = useMutation({
    mutationFn: ({ text, aspects }: { text: string; aspects?: string[] }) =>
      api.analyzeSentiment(text, aspects),
  });
  const p = ins?.product;
  const rb = ins?.ratingBreakdown;
  const s = ins?.sentiment;
  const total = s ? s.positive + s.neutral + s.negative : 0;
  const missing = ins ? [!rb && 'rating breakdown', !s && 'sentiment', !ins.topics?.length && 'topics', !ins.aspects?.length && 'aspects', !ins.themes && 'themes'].filter(Boolean) as string[] : [];

  return (
    <PageContainer>
      <PageHeader title="Review Analysis" description="Product intelligence from collected customer reviews." actions={<ProductSelect />} meta={env && <DataSourceBadge source={env.source} reason={env.fallbackReason} />} />
      {q.isLoading && <LoadingBlock label="Loading analysis" />}
      {q.isError && (
        <ErrorState
          title="Could not load analysis"
          description={(q.error as ApiError)?.message}
          requestId={(q.error as ApiError)?.requestId}
          onRetry={() => q.refetch()}
        />
      )}
      {ins && p && (
        <div className="grid gap-6 xl:grid-cols-2">
          <div className="space-y-6">
            <Card data-reveal>
              <CardHeader title="Product overview" />
              <h2 className="text-xl font-extrabold">{p.title}</h2>
              <dl className="mt-5 grid grid-cols-2 gap-x-6 gap-y-4 sm:grid-cols-3">
                <Field label="Brand" value={p.brand} />
                <Field label="ASIN" value={p.asin} />
                <Field label="Marketplace" value={p.marketplace} />
                <Field label="Observed price" value={p.price != null ? `₹${p.price.toLocaleString('en-IN')}` : undefined} />
                <Field label="List price" value={p.listPrice != null ? `₹${p.listPrice.toLocaleString('en-IN')}` : undefined} />
                <Field label="Rating" value={p.rating != null ? `${p.rating.toFixed(1)} / 5` : undefined} />
                <Field label="Rating count" value={p.ratingCount?.toLocaleString('en-IN')} />
                <Field label="Analyzed" value={fmtDate(ins.analyzedAt)} />
                <Field label="Source" value={env?.source === 'demo' ? 'Demo fixture' : 'Backend'} />
              </dl>
            </Card>

            <ChartCard title="Rating distribution" subtitle="Share of ratings by star level" summary={rb ? `Rating distribution: ${(['5', '4', '3', '2', '1'] as const).map((k) => `${k} stars ${rb[k]}%`).join(', ')}.` : 'Rating distribution unavailable.'}>
              {rb ? (
                <div className="space-y-3">
                  {(['5', '4', '3', '2', '1'] as const).map((k) => (
                    <div key={k} className="flex items-center gap-3">
                      <span className="tnum flex w-10 items-center gap-1 text-sm font-semibold">{k}<Star className="h-3.5 w-3.5 fill-rp-warning text-rp-warning" aria-hidden /></span>
                      <div className="h-3 flex-1 overflow-hidden rounded-full bg-rp-primary-light"><div className="h-full rounded-full bg-rp-primary" style={{ width: `${rb[k]}%` }} /></div>
                      <span className="tnum w-12 text-right text-sm text-rp-muted">{rb[k]}%</span>
                    </div>
                  ))}
                </div>
              ) : <UnavailableState title="Rating breakdown unavailable" description="The backend did not return a distribution for this product." />}
            </ChartCard>

            <ChartCard title="Sentiment analysis" subtitle={s?.avgPolarity != null ? `Average polarity ${s.avgPolarity.toFixed(2)} (−1 to +1)` : undefined} summary={s ? `Sentiment: ${s.positive} positive, ${s.neutral} neutral, ${s.negative} negative of ${total} reviews.` : 'Sentiment unavailable.'}>
              {s ? (
                <div className="grid items-center gap-4 sm:grid-cols-[180px_1fr]">
                  <div className="h-[180px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie data={[{ n: 'Positive', v: s.positive }, { n: 'Neutral', v: s.neutral }, { n: 'Negative', v: s.negative }]} dataKey="v" nameKey="n" innerRadius={52} outerRadius={80} paddingAngle={3} stroke="none">
                          {[CHART.success, CHART.axis, CHART.coral].map((c) => <Cell key={c} fill={c} />)}
                        </Pie>
                        <RTooltip {...CHART.tooltip} />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                  <ul className="space-y-2 text-sm">
                    {([['Positive', s.positive, 'bg-rp-success'], ['Neutral', s.neutral, 'bg-rp-muted'], ['Negative', s.negative, 'bg-rp-coral']] as const).map(([l, n, c]) => (
                      <li key={l} className="flex items-center gap-2"><span className={`h-3 w-3 rounded-full ${c}`} aria-hidden /><span className="font-semibold">{l}</span><span className="tnum ml-auto text-rp-muted">{n} · {pct(n, total)}%</span></li>
                    ))}
                  </ul>
                </div>
              ) : <UnavailableState title="Sentiment unavailable" />}
            </ChartCard>
          </div>

          <div className="space-y-6">
            <Card data-reveal>
              <CardHeader title="Review themes" />
              {ins.themes ? (
                <div className="grid gap-5 sm:grid-cols-2">
                  {([['Positive', ins.themes.positive, 'success'], ['Negative', ins.themes.negative, 'danger']] as const).map(([l, items, tone]) => (
                    <div key={l}>
                      <p className="mb-2 text-sm font-bold">{l}</p>
                      <div className="flex flex-wrap gap-2">{items.length ? items.map((t) => <Badge key={t} tone={tone}>{t}</Badge>) : <span className="text-sm text-rp-muted">None found</span>}</div>
                    </div>
                  ))}
                </div>
              ) : <UnavailableState title="Themes unavailable" />}
            </Card>

            <ChartCard title="Aspect-based sentiment" subtitle="Score from −1 to +1" summary={ins.aspects?.length ? `Aspect scores: ${ins.aspects.map((a) => `${a.aspect} ${a.score.toFixed(2)}`).join(', ')}.` : 'Aspect analysis unavailable.'}>
              {ins.aspects?.length ? (
                <div className="h-[240px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={ins.aspects} layout="vertical" margin={{ left: 8, right: 16 }}>
                      <CartesianGrid stroke={CHART.grid} horizontal={false} />
                      <XAxis type="number" domain={[-1, 1]} tick={CHART.tick} axisLine={false} tickLine={false} />
                      <YAxis type="category" dataKey="aspect" width={92} tick={CHART.tick} axisLine={false} tickLine={false} />
                      <RTooltip {...CHART.tooltip} />
                      <Bar dataKey="score" radius={6}>{ins.aspects.map((a) => <Cell key={a.aspect} fill={a.score >= 0 ? CHART.success : CHART.coral} />)}</Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              ) : <UnavailableState title="No aspect analysis" description="Shown only when the backend provides aspect-level output." />}
            </ChartCard>

            <Card data-reveal>
              <CardHeader title="Topics and keyphrases" subtitle="TF-IDF extraction" />
              {ins.topics?.length ? (
                <div className="overflow-x-auto">
                  <table className="w-full min-w-[320px] text-sm">
                    <thead><tr className="border-b border-rp-border text-left text-xs uppercase tracking-wide text-rp-muted"><th className="pb-2 font-semibold">Term</th><th className="pb-2 text-right font-semibold">Frequency</th><th className="pb-2 text-right font-semibold">Relevance</th></tr></thead>
                    <tbody>{ins.topics.slice(0, 6).map((t) => (
                      <tr key={t.term} className="border-b border-rp-border/60 last:border-0"><td className="py-2.5 font-semibold capitalize">{t.term}</td><td className="tnum py-2.5 text-right">{t.frequency}</td><td className="tnum py-2.5 text-right">{t.relevance.toFixed(2)}</td></tr>
                    ))}</tbody>
                  </table>
                </div>
              ) : <EmptyState title="No topics extracted" description="No keyphrases or topics were found in the current review dataset. Try running the live keyphrase extractor below." />}
            </Card>

            <Card data-reveal tone={missing.length ? 'default' : 'featured'}>
              <CardHeader title="Data quality" />
              <ul className="space-y-1.5 text-sm text-rp-muted">
                <li>Source: <b className="text-rp-navy">{env?.source === 'demo' ? 'Demo fixture (backend unreachable)' : 'Backend'}</b></li>
                <li>Observed: <b className="text-rp-navy">{fmtDate(ins.analyzedAt)}</b></li>
                <li>{missing.length ? <>Partial analysis. Unavailable: <b className="text-rp-warning">{missing.join(', ')}</b>.</> : 'All analysis sections are populated.'}</li>
                <li>Single snapshot, so no historical trend is shown.</li>
              </ul>
            </Card>
          </div>
        </div>
      )}

      <Card data-reveal className="mt-6">
        <CardHeader
          title="On-Demand Review Sentiment & Aspect Evaluator"
          subtitle="Test rule-based polarity and targeted aspect sentiment on any custom review"
        />
        <div className="space-y-3">
          <textarea
            className="w-full rounded-2xl border border-rp-border bg-rp-surface p-3 text-sm focus:border-rp-primary focus:outline-none"
            rows={3}
            placeholder="Type or paste a review to evaluate (e.g. 'The battery life is stellar and camera is sharp, but charging takes forever.')..."
            value={sentimentText}
            onChange={(e) => setSentimentText(e.target.value)}
          />
          <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
            <input
              type="text"
              className="flex-1 rounded-xl border border-rp-border bg-rp-surface px-3 py-2 text-xs focus:border-rp-primary focus:outline-none"
              placeholder="Target aspects (comma-separated, e.g. battery, camera, charging)"
              value={aspectInput}
              onChange={(e) => setAspectInput(e.target.value)}
            />
            <Button
              variant="primary"
              size="md"
              disabled={!sentimentText.trim()}
              loading={sentimentMutation.isPending}
              onClick={() => {
                const aspects = aspectInput
                  .split(',')
                  .map((a) => a.trim())
                  .filter(Boolean);
                sentimentMutation.mutate({ text: sentimentText.trim(), aspects });
              }}
            >
              Analyze Sentiment
            </Button>
          </div>

          {sentimentMutation.data && (
            <div className="mt-3 space-y-3 rounded-2xl bg-rp-surface-soft p-3.5 text-xs">
              <div className="flex flex-wrap items-center justify-between gap-2 border-b border-rp-border/60 pb-2">
                <div>
                  <span className="font-semibold text-rp-navy">Classification: </span>
                  <Badge
                    tone={
                      sentimentMutation.data.label === 'positive'
                        ? 'success'
                        : sentimentMutation.data.label === 'negative'
                          ? 'danger'
                          : 'neutral'
                    }
                  >
                    {sentimentMutation.data.label.toUpperCase()}
                  </Badge>
                </div>
                <div>
                  <span className="font-semibold text-rp-navy">Compound Score: </span>
                  <span className="font-bold text-rp-primary">
                    {sentimentMutation.data.scores.compound >= 0 ? '+' : ''}
                    {sentimentMutation.data.scores.compound.toFixed(2)}
                  </span>
                </div>
                <div>
                  <span className="font-semibold text-rp-navy">Confidence: </span>
                  <span>{Math.round(sentimentMutation.data.confidence * 100)}%</span>
                </div>
              </div>

              {Object.keys(sentimentMutation.data.aspects).length > 0 && (
                <div>
                  <p className="mb-1 font-semibold text-rp-navy">Aspect Polarity:</p>
                  <div className="flex flex-wrap gap-2">
                    {Object.values(sentimentMutation.data.aspects).map((asp) => (
                      <span
                        key={asp.aspect}
                        className="inline-flex items-center gap-1.5 rounded-lg border border-rp-border bg-rp-surface px-2.5 py-1 text-xs font-semibold text-rp-navy"
                      >
                        <span className="capitalize">{asp.aspect}:</span>
                        <span
                          className={
                            asp.label === 'positive'
                              ? 'text-rp-success'
                              : asp.label === 'negative'
                                ? 'text-rp-coral'
                                : 'text-rp-muted'
                          }
                        >
                          {asp.average_polarity >= 0 ? '+' : ''}
                          {asp.average_polarity.toFixed(2)}
                        </span>
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {sentimentMutation.data.highlights.length > 0 && (
                <div>
                  <p className="mb-1 font-semibold text-rp-navy">Polar Highlights & Modifiers:</p>
                  <div className="flex flex-wrap gap-1.5">
                    {sentimentMutation.data.highlights.map((h, i) => (
                      <span
                        key={i}
                        className="rounded bg-rp-primary-light px-2 py-0.5 text-[11px] font-semibold text-rp-navy"
                        title={h.modifiers.length ? `Modifiers: ${h.modifiers.join(', ')}` : undefined}
                      >
                        “{h.token}” ({h.adjusted_valence >= 0 ? '+' : ''}
                        {h.adjusted_valence.toFixed(1)})
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {sentimentMutation.isError && (
            <p className="text-xs font-semibold text-rp-coral">
              Analysis failed: {(sentimentMutation.error as ApiError).message}
            </p>
          )}
        </div>
      </Card>
    </PageContainer>
  );
}
