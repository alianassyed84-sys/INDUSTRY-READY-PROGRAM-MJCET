import { Star } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { cn } from '@/lib/utils';
import type { Product } from '@/lib/types';

export function ProductCard({ product, selected, onSelect }: { product: Product; selected?: boolean; onSelect?: () => void }) {
  return (
    <Card interactive tone={selected ? 'featured' : 'default'} className={cn('!p-4', onSelect && 'cursor-pointer')} onClick={onSelect} role={onSelect ? 'button' : undefined} tabIndex={onSelect ? 0 : undefined} onKeyDown={(e) => onSelect && (e.key === 'Enter' || e.key === ' ') && onSelect()} aria-pressed={onSelect ? !!selected : undefined}>
      <div className="mb-3 grid h-24 place-items-center rounded-xl bg-rp-primary-light/70 font-heading text-3xl font-extrabold text-rp-primary/60" aria-hidden>
        {product.imageUrl ? <img src={product.imageUrl} alt="" loading="lazy" className="h-full w-full rounded-xl object-cover" /> : product.title.slice(0, 1)}
      </div>
      <p className="line-clamp-2 text-sm font-bold text-rp-navy">{product.title}</p>
      <p className="mt-0.5 text-xs text-rp-muted">{[product.brand, product.asin].filter(Boolean).join(' · ')}</p>
      <div className="mt-2.5 flex items-center justify-between text-sm">
        {product.rating != null ? <span className="tnum inline-flex items-center gap-1 font-semibold"><Star className="h-4 w-4 fill-rp-warning text-rp-warning" aria-hidden />{product.rating.toFixed(1)}</span> : <span className="text-xs text-rp-muted">No rating</span>}
        {product.price != null && <span className="tnum font-bold">₹{product.price.toLocaleString('en-IN')}</span>}
      </div>
    </Card>
  );
}
