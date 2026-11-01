import { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { PolarAngleAxis, PolarGrid, PolarRadiusAxis, Radar, RadarChart, ResponsiveContainer, Tooltip as RTooltip } from 'recharts';
import { AlertOctagon, Clock, Lightbulb, MessageSquareText, Search, Sparkles, Star, TrendingDown, EyeOff, ThumbsDown } from 'lucide-react';
import { PageContainer } from '@/components/layout/Page';
import { Card, CardHeader } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { EmptyState, ErrorState, LoadingBlock, DataSourceBadge } from '@/components/ui/states';
import { KpiCard } from '@/components/shared/KpiCard';
import { ChartCard } from '@/components/shared/ChartCard';
import { ProductCard } from '@/components/shared/ProductCard';
import { UrlAnalyzer } from '@/components/shared/UrlAnalyzer';
import { CHART } from '@/components/shared/charts';
import { useInsights, useProductContext } from '@/hooks/useProduct';
import { ROUTES } from '@/lib/routes';
import { cn, fmtDate, pct } from '@/lib/utils';
import type { ApiError } from '@/lib/api';

const PROPS = [
  { icon: Sparkles, label: 'AI-powered insights' },
  { icon: MessageSquareText, label: 'Customer reviews' },
  { icon: EyeOff, label: 'Hidden problems' },
];

export default function Dashboard() {
  const { products, productId, setProductId, loading } = useProductContext();
  const [activeCategory, setActiveCategory] = useState<string>('All');
  const [searchQuery, setSearchQuery] = useState('');
  const q = useInsights();
  const ins = q.data?.data;
  const s = ins?.sentiment;
  const total = s ? s.positive + s.neutral + s.negative : 0;
  const selectedProduct = products.find((p) => p.id === productId);

  const categories = useMemo(() => {
    const cats = new Set<string>();
    products.forEach((p) => {
      if (p.brand) {
        if (p.brand.includes('Smartphones')) cats.add('Smartphones');
        else if (p.brand.includes('Perfumes') || p.brand.includes('Fragrance')) cats.add('Perfumes');
        else if (p.brand.includes('Audio') || p.brand.includes('Headphones')) cats.add('Audio');
        else if (p.brand.includes('Laptops') || p.brand.includes('Computers')) cats.add('Laptops');
        else if (p.brand.includes('Kaggle')) cats.add('Amazon Dataset');
        else cats.add(p.brand.split('|')[0].trim());
      }
    });
    return ['All', ...Array.from(cats)];
  }, [products]);

  const filteredProducts = useMemo(() => {
    return products.filter((p) => {
      const matchesCat =
        activeCategory === 'All' ||
        (activeCategory === 'Smartphones' && p.brand?.includes('Smartphones')) ||
        (activeCategory === 'Perfumes' && (p.brand?.includes('Perfumes') || p.brand?.includes('Fragrance'))) ||
        (activeCategory === 'Audio' && (p.brand?.includes('Audio') || p.brand?.includes('Headphones'))) ||
        (activeCategory === 'Laptops' && (p.brand?.includes('Laptops') || p.brand?.includes('Computers'))) ||
        (activeCategory === 'Amazon Dataset' && p.brand?.includes('Kaggle')) ||
        p.brand?.toLowerCase().includes(activeCategory.toLowerCase());

      const matchesSearch =
        !searchQuery.trim() ||
        p.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        p.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (p.brand && p.brand.toLowerCase().includes(searchQuery.toLowerCase()));

      return matchesCat && matchesSearch;
    });
  }, [products, activeCategory, searchQuery]);

  return (
    <PageContainer>
      {/* Hero */}
      <section data-reveal className="rp-hero relative overflow-hidden rounded-3xl border border-rp-primary-soft/70 p-6 md:p-9">
        <div aria-hidden className="pointer-events-none absolute -right-16 -top-20 h-64 w-64 rounded-full bg-rp-magenta/10 blur-3xl" />
        <h1 className="max-w-3xl text-page font-bold leading-tight md:text-[42px]">Explore the pulse of products</h1>
        <p className="mt-2 text-lg text-rp-muted">Discover what customers really think.</p>
        <ul className="mt-5 flex flex-wrap gap-2.5">
          {PROPS.map(({ icon: Icon, label }) => (
            <li key={label} className="inline-flex items-center gap-2 rounded-full border border-rp-border bg-rp-surface px-3.5 py-2 text-sm font-semibold text-rp-navy"><Icon className="h-4 w-4 text-rp-primary" aria-hidden />{label}</li>
          ))}
        </ul>
        <div className="mt-7 max-w-3xl"><UrlAnalyzer cta="Analyze a Product" /></div>
      </section>

      {q.isError && (
        <ErrorState
          title="Could not load analysis"
          description={(q.error as ApiError)?.message ?? 'The request failed unexpectedly.'}
          requestId={(q.error as ApiError)?.requestId}
          onRetry={() => q.refetch()}
        />
      )}

      {/* KPI summary */}
      <section aria-label="Summary" className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <KpiCard label="Products tracked" value={loading ? '–' : products.length} icon={<Star className="h-[18px] w-[18px]" />} hint="In the current data source" />
        <KpiCard label="Reviews analyzed" value={s ? total : '–'} icon={<MessageSquareText className="h-[18px] w-[18px]" />} hint={s ? 'Selected product' : 'Unavailable'} />
        <KpiCard label="Negative share" value={s ? `${pct(s.negative, total)}%` : '–'} icon={<ThumbsDown className="h-[18px] w-[18px]" />} hint="Of analyzed reviews" />
        <KpiCard label="Avg. polarity" value={s?.avgPolarity != null ? s.avgPolarity.toFixed(2) : '–'} icon={<TrendingDown className="h-[18px] w-[18px]" />} hint={s?.avgPolarity != null ? 'Scale −1 to +1' : 'Not provided by backend'} />
      </section>

      <div className="grid gap-6 xl:grid-cols-[minmax(0,1.6fr)_minmax(0,1fr)]">
        {/* Main insights column */}
        <div className="space-y-6">
          <ChartCard
            title="Negative Review Radar"
            subtitle="Aspect sentiment, from −1 (negative) to +1 (positive)"
            summary={ins?.aspects?.length ? `Radar of aspect sentiment: ${ins.aspects.map((a) => `${a.aspect} ${a.score.toFixed(2)}`).join(', ')}.` : 'Aspect sentiment unavailable.'}
            action={q.data && <DataSourceBadge source={q.data.source} reason={q.data.fallbackReason} />}
          >
            {q.isLoading ? <LoadingBlock label="Loading radar" /> : ins?.aspects?.length ? (
              <div className="h-[320px]">
                <ResponsiveContainer width="100%" height="100%">
                  <RadarChart data={ins.aspects} outerRadius="65%" margin={{ top: 12, right: 24, bottom: 12, left: 24 }}>
                    <PolarGrid stroke={CHART.grid} />
                    <PolarAngleAxis dataKey="aspect" tick={CHART.tick} />
                    <PolarRadiusAxis domain={[-1, 1]} tickCount={5} tick={CHART.tick} axisLine={false} />
                    <RTooltip {...CHART.tooltip} />
                    <Radar dataKey="score" name="Sentiment" stroke={CHART.primary} fill={CHART.primary} fillOpacity={0.22} />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            ) : <EmptyState title="No aspect analysis yet" description="Aspect-based sentiment appears here when the backend returns it." />}
          </ChartCard>

          <Card data-reveal>
            <CardHeader title="Trending Complaints" subtitle="Negative themes from the selected product's analysis" action={<AlertOctagon className="h-5 w-5 text-rp-coral" aria-hidden />} />
            {q.isLoading ? <LoadingBlock /> : ins?.themes?.negative?.length ? (
              <>
                <ol className="space-y-2.5">
                  {ins.themes.negative.map((t, i) => (
                    <li key={t} className="flex items-center gap-3 rounded-2xl border border-rp-border bg-rp-surface-soft/60 px-4 py-3">
                      <span className="tnum grid h-8 w-8 place-items-center rounded-full bg-rp-primary-light text-sm font-extrabold text-rp-primary-hover">{i + 1}</span>
                      <span className="font-semibold capitalize text-rp-navy">{t}</span>
                    </li>
                  ))}
                </ol>
                <p className="mt-3 text-xs text-rp-muted">Listed in the order returned by the analysis. No trend or percentage change is shown because only a single snapshot exists.</p>
              </>
            ) : <EmptyState title="No complaint themes" description="Negative themes appear once reviews have been analyzed." />}
          </Card>
        </div>

        {/* Right-hand analytics cards */}
        <div className="space-y-6">
          <Card data-reveal>
            <CardHeader title="Sentiment mix" />
            {s ? (
              <div className="space-y-3.5">
                {([['Positive', s.positive, 'bg-rp-success'], ['Neutral', s.neutral, 'bg-rp-muted'], ['Negative', s.negative, 'bg-rp-coral']] as const).map(([l, n, c]) => (
                  <div key={l}>
                    <div className="mb-1 flex justify-between text-sm"><span className="font-semibold">{l}</span><span className="tnum text-rp-muted">{n} · {pct(n, total)}%</span></div>
                    <div className="h-2.5 overflow-hidden rounded-full bg-rp-primary-light"><div className={`h-full rounded-full ${c}`} style={{ width: `${pct(n, total)}%` }} /></div>
                  </div>
                ))}
              </div>
            ) : <EmptyState title="No sentiment data" description="Sentiment analysis breakdown will appear once customer reviews are imported or analyzed." />}
          </Card>

          <Card data-reveal>
            <CardHeader title="Recent analysis activity" />
            {ins ? (
              <div className="flex items-start gap-3">
                <span className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-rp-primary-light text-rp-primary"><Clock className="h-5 w-5" aria-hidden /></span>
                <div className="min-w-0">
                  <p className="truncate font-semibold text-rp-navy">{ins.product.title}</p>
                  <p className="text-sm text-rp-muted">Analyzed {fmtDate(ins.analyzedAt)}</p>
                  <Link to={ROUTES.analysis} className="mt-1 inline-block text-sm font-semibold text-rp-primary hover:text-rp-primary-hover">Open analysis</Link>
                </div>
              </div>
            ) : <EmptyState title="No activity yet" description="Analyzed products will be listed here." />}
          </Card>

          <Card tone="featured" data-reveal>
            <Lightbulb className="mb-2 h-5 w-5 text-rp-primary" aria-hidden />
            <h3 className="text-[17px] font-bold">Dig deeper</h3>
            <p className="mt-1 text-sm text-rp-muted">Move from the overview to topics, languages and readability.</p>
            <div className="mt-3 flex flex-wrap gap-2">
              <Link to={ROUTES.topics}><Badge tone="primary">Topics</Badge></Link>
              <Link to={ROUTES.language}><Badge tone="primary">Languages</Badge></Link>
              <Link to={ROUTES.readability}><Badge tone="primary">Readability</Badge></Link>
            </div>
          </Card>
        </div>
      </div>

      {/* Product history */}
      <section aria-labelledby="history" data-reveal>
        <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 id="history" className="text-[22px] font-extrabold">Product Catalog & History</h2>
            <p className="text-xs text-rp-muted">Browse and select from all {products.length} imported products</p>
          </div>
          <Link to={ROUTES.harvester} className="text-sm font-semibold text-rp-primary hover:text-rp-primary-hover">
            + Add / Scrape new product
          </Link>
        </div>

        {/* Selected Product Action Banner */}
        {selectedProduct && (
          <div className="mb-5 flex flex-wrap items-center justify-between gap-4 rounded-2xl border border-rp-primary/30 bg-gradient-to-r from-rp-primary-light/60 via-rp-surface-soft to-rp-surface p-4 shadow-xs">
            <div className="flex items-center gap-3.5 min-w-0">
              <span className="grid h-11 w-11 shrink-0 place-items-center rounded-xl bg-rp-primary text-white font-extrabold shadow-sm">
                {selectedProduct.title.slice(0, 1)}
              </span>
              <div className="min-w-0">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold uppercase tracking-wider text-rp-primary">Selected Product</span>
                  <Badge tone="primary">{selectedProduct.brand?.split('|')[0]?.trim() ?? 'Product'}</Badge>
                </div>
                <p className="truncate font-bold text-rp-navy text-sm md:text-base">{selectedProduct.title}</p>
                <p className="text-xs text-rp-muted">
                  ID: <span className="font-mono font-medium text-rp-navy">{selectedProduct.id}</span>
                  {selectedProduct.price != null && ` · ₹${selectedProduct.price.toLocaleString('en-IN')}`}
                  {selectedProduct.rating != null && ` · ★ ${selectedProduct.rating.toFixed(1)}`}
                </p>
              </div>
            </div>
            <div className="flex flex-wrap items-center gap-2.5">
              <Link to={ROUTES.analysis}>
                <Button variant="primary" size="sm">
                  Deep-Dive Analysis →
                </Button>
              </Link>
              <Link to={ROUTES.reviews}>
                <Button variant="secondary" size="sm">
                  Browse Reviews →
                </Button>
              </Link>
            </div>
          </div>
        )}

        {/* Category pills & search bar */}
        <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex flex-wrap gap-1.5">
            {categories.map((cat) => (
              <button
                key={cat}
                type="button"
                onClick={() => setActiveCategory(cat)}
                className={cn(
                  'px-3 py-1.5 rounded-full text-xs font-bold transition-all',
                  activeCategory === cat
                    ? 'bg-rp-primary text-white shadow-xs'
                    : 'bg-rp-surface-soft text-rp-muted hover:text-rp-navy border border-rp-border',
                )}
              >
                {cat}
                {cat === 'All' ? ` (${products.length})` : ''}
              </button>
            ))}
          </div>
          <div className="w-full sm:w-64">
            <Input
              placeholder={`Search ${products.length} products...`}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              leading={<Search className="h-3.5 w-3.5 text-rp-muted" />}
              className="text-xs"
            />
          </div>
        </div>

        {loading ? (
          <LoadingBlock />
        ) : filteredProducts.length ? (
          <div className="grid gap-4 sm:grid-cols-2 md:grid-cols-3 xl:grid-cols-4">
            {filteredProducts.map((p) => (
              <div key={p.id}>
                <ProductCard
                  product={p}
                  selected={p.id === productId}
                  onSelect={() => setProductId(p.id)}
                />
              </div>
            ))}
          </div>
        ) : products.length === 0 ? (
          <EmptyState title="No products yet" description="Analyze a product to start building your history." />
        ) : (
          <EmptyState
            title="No matching products"
            description={`No products match "${searchQuery}" in category "${activeCategory}".`}
            action={
              <Button
                variant="secondary"
                size="sm"
                onClick={() => {
                  setActiveCategory('All');
                  setSearchQuery('');
                }}
              >
                Reset filters
              </Button>
            }
          />
        )}
      </section>
    </PageContainer>
  );
}
