import { useMemo, useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip as RTooltip, XAxis, YAxis } from 'recharts';
import { Download } from 'lucide-react';
import { PageContainer, PageHeader } from '@/components/layout/Page';
import { Card, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { DataSourceBadge, ErrorState, LoadingBlock, UnavailableState, EmptyState } from '@/components/ui/states';
import { KpiCard } from '@/components/shared/KpiCard';
import { ChartCard } from '@/components/shared/ChartCard';
import { ProductSelect } from '@/components/shared/ProductSelect';
import { CHART } from '@/components/shared/charts';
import { useInsights, useProductContext } from '@/hooks/useProduct';
import { fmtDate, pct } from '@/lib/utils';
import { api, type ApiError } from '@/lib/api';

const inr = (n: number) => `₹${n.toLocaleString('en-IN')}`;

export default function Analytics() {
  const q = useInsights();
  const { products } = useProductContext();
  const queryClient = useQueryClient();
  const env = q.data;
  const ins = env?.data;
  const [from, setFrom] = useState('');
  const [to, setTo] = useState('');
  const [priceCheckMsg, setPriceCheckMsg] = useState<string | null>(null);

  const checkPriceMutation = useMutation({
    mutationFn: () => api.checkPrice(ins!.product.id),
    onSuccess: (data) => {
      setPriceCheckMsg(
        `Recorded new snapshot: ₹${data.latest_observed_price?.toLocaleString('en-IN') ?? '–'} (${data.observations_count} snapshots total).`,
      );
      void queryClient.invalidateQueries({ queryKey: ['insights', ins!.product.id] });
    },
    onError: (err: ApiError) => {
      setPriceCheckMsg(err.message);
    },
  });

  const all = ins?.priceHistory ?? [];
  const history = useMemo(() => all.filter((h) => (!from || h.observedAt >= from) && (!to || h.observedAt <= `${to}T23:59:59Z`)), [all, from, to]);
  const high = history.length ? Math.max(...history.map((h) => h.price)) : undefined;
  const s = ins?.sentiment;
  const total = s ? s.positive + s.neutral + s.negative : 0;
  const enough = history.length >= 2;

  return (
    <PageContainer>
      <PageHeader
        title="Analytics & Reports"
        description="Ratings, sentiment and price observations for a product."
        actions={<ProductSelect />}
        meta={env && <DataSourceBadge source={env.source} reason={env.fallbackReason} />}
      />
      {q.isLoading && <LoadingBlock />}
      {q.isError && (
        <ErrorState
          title="Could not load price analytics"
          description={(q.error as ApiError)?.message ?? 'The analytics request failed.'}
          requestId={(q.error as ApiError)?.requestId}
          onRetry={() => q.refetch()}
        />
      )}

      {!q.isLoading && !q.isError && !ins && (
        <EmptyState
          title="No product loaded"
          description="Select a product from the top selector or analyze an Amazon product to view rating and price history analytics."
        />
      )}

      {ins && (
        <>
          <section aria-label="Summary" className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <KpiCard label="Aggregate rating" value={ins.product.rating != null ? ins.product.rating.toFixed(1) : '–'} hint={ins.product.ratingCount != null ? `${ins.product.ratingCount.toLocaleString('en-IN')} ratings` : 'Rating count unavailable'} />
            <KpiCard label="Positive share" value={s ? `${pct(s.positive, total)}%` : '–'} hint="Of analyzed reviews" />
            <KpiCard label="Negative share" value={s ? `${pct(s.negative, total)}%` : '–'} hint="Of analyzed reviews" />
            <KpiCard label="Price snapshots" value={all.length} hint="Stored observations" />
          </section>

          <Card data-reveal>
            <CardHeader title="Date range" subtitle="Applies to stored price observations" />
            <div className="grid gap-3 sm:grid-cols-2 lg:max-w-xl">
              <Input label="From" type="date" value={from} onChange={(e) => setFrom(e.target.value)} />
              <Input label="To" type="date" value={to} onChange={(e) => setTo(e.target.value)} />
            </div>
          </Card>

          <div className="grid gap-6 xl:grid-cols-[1.5fr_1fr]">
            <ChartCard title="Price history" subtitle="Stored observations only" summary={enough ? `Price history from ${fmtDate(history[0].observedAt)} to ${fmtDate(history[history.length - 1].observedAt)}, ${history.length} snapshots.` : 'Not enough observations for a price trend.'}>
              {enough ? (
                <div className="h-[290px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={history.map((h) => ({ ...h, label: fmtDate(h.observedAt) }))} margin={{ left: 0, right: 12 }}>
                      <CartesianGrid stroke={CHART.grid} vertical={false} />
                      <XAxis dataKey="label" tick={CHART.tick} axisLine={false} tickLine={false} />
                      <YAxis domain={['dataMin - 100', 'dataMax + 100']} tickFormatter={(v: number) => inr(v)} width={64} tick={CHART.tick} axisLine={false} tickLine={false} />
                      <RTooltip {...CHART.tooltip} formatter={(v) => [inr(Number(v)), 'Price']} />
                      <Line type="monotone" dataKey="price" stroke={CHART.primary} strokeWidth={3} dot={{ r: 4, fill: '#fff', strokeWidth: 2 }} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <EmptyState title="Not enough price observations" description={`A trend needs at least 2 stored snapshots in the selected range. There ${history.length === 1 ? 'is 1' : `are ${history.length}`}. Analyze this product again on later dates to build history.`} />
              )}
            </ChartCard>

            <Card data-reveal>
              <CardHeader
                title="Price facts"
                action={
                  <Button
                    variant="secondary"
                    size="md"
                    loading={checkPriceMutation.isPending}
                    onClick={() => checkPriceMutation.mutate()}
                  >
                    Poll Fresh Price
                  </Button>
                }
              />
              {priceCheckMsg && (
                <p className="mb-3 rounded-xl bg-rp-surface-soft p-2.5 text-xs font-semibold text-rp-navy">
                  {priceCheckMsg}
                </p>
              )}
              <dl className="space-y-3.5 text-sm">
                {([
                  ['Current observed price', ins.product.price != null ? inr(ins.product.price) : undefined],
                  ['Highest observed (tracked period)', high != null ? inr(high) : undefined],
                  ['Tracking started', history[0] ? fmtDate(history[0].observedAt) : undefined],
                  ['Latest observation', history.length ? fmtDate(history[history.length - 1].observedAt) : undefined],
                  ['Snapshots in range', String(history.length)],
                ] as const).map(([k, v]) => (
                  <div key={k} className="flex items-baseline justify-between gap-3 border-b border-rp-border/60 pb-2.5 last:border-0"><dt className="text-rp-muted">{k}</dt><dd className="tnum font-bold text-rp-navy">{v ?? 'Unavailable'}</dd></div>
                ))}
              </dl>
              <p className="mt-3 text-xs text-rp-muted">“Highest observed” covers only the stored period, not the product’s all-time high.</p>
            </Card>
          </div>

          <div className="grid gap-6 lg:grid-cols-2">
            <Card data-reveal>
              <CardHeader title="Topic trends" />
              <UnavailableState title="Needs repeated analyses" description="Topic trends compare analyses over time. Only a single analysis snapshot exists, so no trend is drawn." />
            </Card>
            <Card data-reveal>
              <CardHeader title="Product comparison" subtitle="Aggregate rating and observed price" />
              {products.length > 1 ? (
                <div className="overflow-x-auto">
                  <table className="w-full min-w-[420px] text-sm">
                    <thead><tr className="border-b border-rp-border text-left text-xs uppercase tracking-wide text-rp-muted"><th className="pb-2 font-semibold">Product</th><th className="pb-2 text-right font-semibold">Rating</th><th className="pb-2 text-right font-semibold">Price</th></tr></thead>
                    <tbody>{products.map((p) => <tr key={p.id} className="border-b border-rp-border/60 last:border-0"><td className="py-2.5 font-semibold">{p.title}</td><td className="tnum py-2.5 text-right">{p.rating?.toFixed(1) ?? '–'}</td><td className="tnum py-2.5 text-right">{p.price != null ? inr(p.price) : '–'}</td></tr>)}</tbody>
                  </table>
                </div>
              ) : <EmptyState title="Add another product to compare" description="Comparison requires at least two products in your workspace. Use the Harvester or Amazon analyzer to load additional products." />}
            </Card>
          </div>

          <Card data-reveal>
            <CardHeader title="Reports" />
            <UnavailableState title="Report export is not available yet" description="The backend has no report generation endpoint, so nothing can be generated or downloaded." action={<Button variant="secondary" disabled><Download className="h-4 w-4" aria-hidden />Export report</Button>} />
          </Card>
        </>
      )}
    </PageContainer>
  );
}
