import { useEffect, useMemo, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { PageContainer, PageHeader } from '@/components/layout/Page';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { EmptyState, ErrorState, LoadingBlock } from '@/components/ui/states';
import { ProductSelect } from '@/components/shared/ProductSelect';
import { ReviewCard } from '@/components/shared/ReviewCard';
import { EMPTY_FILTERS, ReviewFilters, type FilterState } from '@/components/shared/ReviewFilters';
import { useProductContext, useReviews } from '@/hooks/useProduct';
import type { ApiError } from '@/lib/api';

const PAGE_SIZE = 8;

export default function Reviews() {
  const [params] = useSearchParams();
  const [filters, setFilters] = useState<FilterState>({ ...EMPTY_FILTERS, q: params.get('q') ?? '' });
  const [page, setPage] = useState(1);
  const { products, productId } = useProductContext();

  useEffect(() => {
    const urlQ = params.get('q');
    if (urlQ != null) {
      setFilters((prev) => (prev.q === urlQ ? prev : { ...prev, q: urlQ }));
      setPage(1);
    }
  }, [params]);
  const q = useReviews();
  const reviews = q.data?.data ?? [];
  const product = products.find((p) => p.id === productId);

  const available = useMemo(() => ({
    rating: reviews.some((r) => r.rating != null),
    language: reviews.some((r) => !!r.language),
    sentiment: reviews.some((r) => !!r.sentiment),
    date: reviews.some((r) => !!r.date),
  }), [reviews]);
  const languages = useMemo(() => [...new Set(reviews.map((r) => r.language).filter((l): l is string => !!l))], [reviews]);

  const list = useMemo(() => {
    const term = filters.q.trim().toLowerCase();
    const out = reviews.filter((r) =>
      (!term || r.text.toLowerCase().includes(term)) &&
      (!filters.rating || r.rating === Number(filters.rating)) &&
      (!filters.language || r.language === filters.language) &&
      (!filters.sentiment || r.sentiment === filters.sentiment));
    const t = (d?: string) => (d ? new Date(d).getTime() : 0);
    return [...out].sort((a, b) => filters.sort === 'oldest' ? t(a.date) - t(b.date) : filters.sort === 'high' ? (b.rating ?? 0) - (a.rating ?? 0) : filters.sort === 'low' ? (a.rating ?? 0) - (b.rating ?? 0) : t(b.date) - t(a.date));
  }, [reviews, filters]);

  const pages = Math.max(1, Math.ceil(list.length / PAGE_SIZE));
  const cur = Math.min(page, pages);
  const slice = list.slice((cur - 1) * PAGE_SIZE, cur * PAGE_SIZE);
  const onFilters = (v: FilterState) => { setFilters(v); setPage(1); };

  return (
    <PageContainer>
      <PageHeader title="Product Reviews" description="Search, filter and sort the reviews collected for a product." actions={<ProductSelect />} />

      <Card data-reveal tone="featured" className="!p-5">
        <div className="flex flex-wrap items-center gap-x-8 gap-y-2 text-sm">
          <p className="font-bold text-rp-navy">{product?.title ?? 'No product selected'}</p>
          <p className="text-rp-muted"><b className="tnum text-rp-navy">{reviews.length}</b> reviews loaded</p>
          {product?.rating != null && <p className="text-rp-muted">Product rating <b className="tnum text-rp-navy">{product.rating.toFixed(1)}</b> (aggregate, not per review)</p>}
        </div>
      </Card>

      <ReviewFilters value={filters} onChange={onFilters} available={available} languages={languages} />

      {q.isLoading ? <LoadingBlock label="Loading reviews" /> : q.isError ? (
        <ErrorState
          title="Could not load reviews"
          description={(q.error as ApiError)?.message ?? 'Check your connection and try again.'}
          requestId={(q.error as ApiError)?.requestId}
          onRetry={() => q.refetch()}
        />
      ) : reviews.length === 0 ? (
        <EmptyState title="No reviews for this product" description="Run the harvester to collect reviews first." />
      ) : list.length === 0 ? (
        <EmptyState title="No reviews match your filters" action={<Button variant="secondary" onClick={() => onFilters(EMPTY_FILTERS)}>Clear filters</Button>} />
      ) : (
        <>
          <p aria-live="polite" className="text-sm text-rp-muted">Showing <b className="tnum text-rp-navy">{slice.length}</b> of <b className="tnum text-rp-navy">{list.length}</b> matching reviews</p>
          <div className="grid gap-4 lg:grid-cols-2">{slice.map((r) => <ReviewCard key={r.id} review={r} />)}</div>
          <nav aria-label="Pagination" className="flex items-center justify-center gap-3 pt-2">
            <Button variant="secondary" disabled={cur <= 1} onClick={() => setPage(cur - 1)}><ChevronLeft className="h-4 w-4" aria-hidden />Previous</Button>
            <span className="tnum text-sm text-rp-muted">Page {cur} of {pages}</span>
            <Button variant="secondary" disabled={cur >= pages} onClick={() => setPage(cur + 1)}>Next<ChevronRight className="h-4 w-4" aria-hidden /></Button>
          </nav>
        </>
      )}
    </PageContainer>
  );
}
