import { useEffect } from 'react';
import { useParams, useNavigate, Navigate, NavLink } from 'react-router-dom';
import { useProductContext, useInsights, useReviews } from '@/hooks/useProduct';
import { productRoute, type ProductTab, PRODUCT_TABS } from '@/lib/routes';
import { Badge } from '@/components/ui/Badge';
import { EmptyState, LoadingState } from '@/components/ui/states';
import { cn } from '@/lib/utils';
import { Star, ShieldAlert, CheckCircle2 } from 'lucide-react';
import Overview from '@/pages/Overview';
import Reviews from '@/pages/Reviews';
import Analysis from '@/pages/Analysis';
import Topics from '@/pages/Topics';
import Language from '@/pages/Language';
import Readability from '@/pages/Readability';
import Analytics from '@/pages/Analytics';

const TAB_LABELS: Record<ProductTab, string> = {
  overview: 'Overview',
  reviews: 'Reviews',
  sentiment: 'Sentiment',
  topics: 'Topics',
  languages: 'Languages',
  readability: 'Readability',
  price: 'Price',
};

export default function ProductWorkspace() {
  const { id, tab } = useParams<{ id: string; tab: string }>();
  const navigate = useNavigate();
  const { products, productId, setProductId, loading } = useProductContext();

  const currentTab = (tab?.toLowerCase() as ProductTab) ?? 'overview';

  // Synchronize product context if id in URL differs
  useEffect(() => {
    if (id && id !== productId) {
      setProductId(id);
    }
  }, [id, productId, setProductId]);

  // If tab is not a recognized tab, redirect to overview
  if (tab && !PRODUCT_TABS.includes(currentTab)) {
    return <Navigate to={productRoute(id ?? '', 'overview')} replace />;
  }

  const product = products.find((p) => p.id === id);

  const { data: insightsData } = useInsights();
  const { data: reviewsData } = useReviews();

  if (loading && !product) {
    return <LoadingState label="Loading product workspace..." />;
  }

  if (!product) {
    return (
      <div className="mx-auto max-w-content px-4 py-8">
        <EmptyState
          title="Product not found"
          description="We could not find the selected product. Please select another product or add a new one."
          action={
            <button
              onClick={() => navigate('/products')}
              className="rounded-btn bg-rp-primary px-4 py-2 text-sm font-semibold text-white shadow-soft"
            >
              Back to all products
            </button>
          }
        />
      </div>
    );
  }

  const categoryPath = product.category
    ? product.category.includes('>')
      ? product.category
      : `Products > ${product.category}`
    : 'Products > General';

  const totalReviews = product.ratingCount ?? reviewsData?.data?.length ?? 0;
  const analyzedReviews = insightsData?.data?.sentiment
    ? (insightsData.data.sentiment.positive ?? 0) +
      (insightsData.data.sentiment.neutral ?? 0) +
      (insightsData.data.sentiment.negative ?? 0)
    : totalReviews;

  const reviewCountText =
    analyzedReviews < totalReviews
      ? `Based on ${analyzedReviews} of ${totalReviews} reviews`
      : `Based on ${totalReviews} reviews`;

  const isSample = product.id.startsWith('demo-');

  return (
    <div className="w-full">
      {/* Sticky Product Header */}
      <header className="sticky top-topbar z-10 border-b border-rp-border bg-rp-bg/95 backdrop-blur-md">
        <div className="mx-auto max-w-content px-4 py-4 md:px-6 lg:px-8">
          <nav aria-label="Breadcrumb" className="mb-1 text-xs font-semibold text-rp-muted">
            {categoryPath}
          </nav>
          <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div className="flex items-center gap-4 min-w-0">
              {product.imageUrl && (
                <div className="h-14 w-14 shrink-0 overflow-hidden rounded-xl border border-rp-border bg-white shadow-soft p-1 flex items-center justify-center">
                  <img
                    src={product.imageUrl}
                    alt={product.title}
                    className="h-full w-full object-contain"
                  />
                </div>
              )}
              <div className="min-w-0">
                <h1 className="truncate font-heading text-xl font-extrabold text-rp-navy md:text-2xl">
                  {product.title}
                </h1>
                <div className="mt-1.5 flex flex-wrap items-center gap-2 text-xs">
                {product.brand && (
                  <span className="font-semibold text-rp-navy bg-rp-surface px-2 py-0.5 rounded border border-rp-border">
                    {product.brand}
                  </span>
                )}
                {product.marketplace && (
                  <Badge tone="neutral" className="uppercase font-bold tracking-wider text-[10px]">
                    {product.marketplace}
                  </Badge>
                )}
                {product.price != null && (
                  <span className="font-bold text-rp-navy">₹{product.price.toLocaleString()}</span>
                )}
                {product.rating != null && (
                  <span className="flex items-center gap-1 font-bold text-rp-warning">
                    <Star className="h-3.5 w-3.5 fill-current" aria-hidden="true" />
                    {product.rating.toFixed(1)}
                  </span>
                )}
                <span className="text-rp-muted">· {reviewCountText}</span>
                {isSample ? (
                  <Badge tone="warning" className="flex items-center gap-1">
                    <ShieldAlert className="h-3 w-3" aria-hidden="true" /> Sample data
                  </Badge>
                ) : (
                  <Badge tone="success" className="flex items-center gap-1">
                    <CheckCircle2 className="h-3 w-3" aria-hidden="true" /> Live Harvested
                  </Badge>
                )}
              </div>
            </div>
          </div>
        </div>

          {/* Sticky Tab Bar */}
          <nav
            role="tablist"
            aria-label="Product workspace tabs"
            className="mt-4 flex gap-1 overflow-x-auto border-t border-rp-border/60 pt-2.5 scrollbar-none"
          >
            {PRODUCT_TABS.map((tabKey) => {
              const isActive = currentTab === tabKey;
              return (
                <NavLink
                  key={tabKey}
                  to={productRoute(product.id, tabKey)}
                  role="tab"
                  aria-selected={isActive}
                  className={cn(
                    'flex min-h-[40px] items-center whitespace-nowrap rounded-lg px-3.5 py-1.5 text-xs font-bold transition-all',
                    isActive
                      ? 'bg-rp-primary text-white shadow-soft'
                      : 'text-rp-muted hover:bg-rp-primary-light hover:text-rp-navy'
                  )}
                >
                  {TAB_LABELS[tabKey]}
                </NavLink>
              );
            })}
          </nav>
        </div>
      </header>

      {/* Tab Content Area */}
      <main className="mx-auto max-w-content px-4 py-6 md:px-6 md:py-8 lg:px-8">
        <section
          role="tabpanel"
          id={`tabpanel-${currentTab}`}
          aria-labelledby={`tab-${currentTab}`}
          className="space-y-6"
        >
          {currentTab === 'overview' && <Overview />}
          {currentTab === 'reviews' && <Reviews />}
          {currentTab === 'sentiment' && <Analysis />}
          {currentTab === 'topics' && <Topics />}
          {currentTab === 'languages' && <Language />}
          {currentTab === 'readability' && <Readability />}
          {currentTab === 'price' && <Analytics />}
        </section>
      </main>
    </div>
  );
}
