import { useProductContext } from '@/hooks/useProduct';
import { DataSourceBadge } from '@/components/ui/states';

export function ProductSelect({ showSource = true }: { showSource?: boolean }) {
  const { products, productId, setProductId, source, fallbackReason, loading } = useProductContext();
  return (
    <div className="flex flex-wrap items-center gap-2.5">
      <label className="sr-only" htmlFor="product-select">Product</label>
      <select
        id="product-select"
        value={productId ?? ''}
        disabled={loading || products.length === 0}
        onChange={(e) => setProductId(e.target.value)}
        className="min-h-[48px] max-w-full rounded-btn border border-rp-border bg-rp-surface px-3.5 text-sm font-semibold text-rp-navy focus:border-rp-primary"
      >
        {products.length === 0 && <option value="">No products available</option>}
        {products.map((p) => <option key={p.id} value={p.id}>{p.title}</option>)}
      </select>
      {showSource && <DataSourceBadge source={source} reason={fallbackReason} />}
    </div>
  );
}
