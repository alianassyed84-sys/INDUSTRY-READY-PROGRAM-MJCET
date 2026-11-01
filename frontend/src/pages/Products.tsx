import { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { PageContainer, PageHeader } from '@/components/layout/Page';
import { useProductContext } from '@/hooks/useProduct';
import { productRoute } from '@/lib/routes';
import { ProductCard } from '@/components/shared/ProductCard';
import { EmptyState, LoadingState } from '@/components/ui/states';
import { Input } from '@/components/ui/Input';
import { Search } from 'lucide-react';

export default function Products() {
  const navigate = useNavigate();
  const { products, loading } = useProductContext();
  const [search, setSearch] = useState('');
  const [sourceFilter, setSourceFilter] = useState<'all' | 'featured' | 'amazon' | 'flipkart'>('all');
  const [sortBy, setSortBy] = useState<'title' | 'rating' | 'reviews'>('title');

  const filteredProducts = useMemo(() => {
    return products
      .filter((p) => {
        if (!p.title.toLowerCase().includes(search.toLowerCase())) return false;
        if (sourceFilter === 'featured') return Boolean(p.imageUrl);
        if (sourceFilter === 'amazon') return p.marketplace === 'Amazon.in';
        if (sourceFilter === 'flipkart') return p.marketplace === 'Flipkart';
        return true;
      })
      .sort((a, b) => {
        // Products with authentic images always appear first
        const aHasImg = Boolean(a.imageUrl);
        const bHasImg = Boolean(b.imageUrl);
        if (aHasImg !== bHasImg) return aHasImg ? -1 : 1;

        if (sortBy === 'rating') return (b.rating ?? 0) - (a.rating ?? 0);
        if (sortBy === 'reviews') return (b.ratingCount ?? 0) - (a.ratingCount ?? 0);
        return a.title.localeCompare(b.title);
      });
  }, [products, search, sourceFilter, sortBy]);

  return (
    <PageContainer>
      <PageHeader
        title="All Products"
        subtitle="Search, filter, and choose a product to open its dedicated workspace."
      />

      {/* Filter and Search Bar */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between rounded-card border border-rp-border bg-rp-surface p-4">
        <div className="relative flex-1 max-w-md">
          <Input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search products by title..."
            leading={<Search className="h-4 w-4 text-rp-muted" aria-hidden />}
            aria-label="Search products"
          />
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <div className="flex items-center gap-1 rounded-btn border border-rp-border p-1 bg-rp-surface-soft text-xs font-semibold">
            <button
              onClick={() => setSourceFilter('all')}
              className={`rounded px-2.5 py-1 ${sourceFilter === 'all' ? 'bg-rp-primary text-white shadow-soft' : 'text-rp-muted'}`}
            >
              All Sources
            </button>
            <button
              onClick={() => setSourceFilter('featured')}
              className={`rounded px-2.5 py-1 ${sourceFilter === 'featured' ? 'bg-rp-primary text-white shadow-soft' : 'text-rp-muted'}`}
            >
              ⭐ Featured Photos
            </button>
            <button
              onClick={() => setSourceFilter('amazon')}
              className={`rounded px-2.5 py-1 ${sourceFilter === 'amazon' ? 'bg-rp-primary text-white shadow-soft' : 'text-rp-muted'}`}
            >
              Amazon
            </button>
            <button
              onClick={() => setSourceFilter('flipkart')}
              className={`rounded px-2.5 py-1 ${sourceFilter === 'flipkart' ? 'bg-rp-primary text-white shadow-soft' : 'text-rp-muted'}`}
            >
              Flipkart
            </button>
          </div>

          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as 'title' | 'rating' | 'reviews')}
            className="rounded-btn border border-rp-border bg-rp-surface px-3 py-1.5 text-xs font-semibold text-rp-navy outline-none"
            aria-label="Sort products"
          >
            <option value="title">Sort by Title</option>
            <option value="rating">Highest Rating</option>
            <option value="reviews">Most Reviews</option>
          </select>
        </div>
      </div>

      {loading ? (
        <LoadingState label="Loading product library..." />
      ) : filteredProducts.length === 0 ? (
        <EmptyState
          title="No products found"
          description={
            search
              ? `No products match your search "${search}". Try clearing your filters.`
              : 'No products are currently available. Paste a link or import a dataset to get started.'
          }
        />
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {filteredProducts.map((product) => (
            <ProductCard
              key={product.id}
              product={product}
              onSelect={() => navigate(productRoute(product.id, 'overview'))}
            />
          ))}
        </div>
      )}
    </PageContainer>
  );
}
