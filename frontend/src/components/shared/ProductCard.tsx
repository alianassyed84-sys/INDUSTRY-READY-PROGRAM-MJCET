import { useState } from 'react';
import { Star, Package } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { cn } from '@/lib/utils';
import type { Product } from '@/lib/types';

export function ProductCard({ product, selected, onSelect }: { product: Product; selected?: boolean; onSelect?: () => void }) {
  const [imgError, setImgError] = useState(false);
  const effectiveImageUrl = !imgError ? (product.imageUrl || `/products/${product.id}.jpg`) : null;

  return (
    <Card
      interactive
      tone={selected ? 'featured' : 'default'}
      className={cn('!p-4 group flex flex-col justify-between', onSelect && 'cursor-pointer')}
      onClick={onSelect}
      role={onSelect ? 'button' : undefined}
      tabIndex={onSelect ? 0 : undefined}
      onKeyDown={(e) => onSelect && (e.key === 'Enter' || e.key === ' ') && onSelect()}
      aria-pressed={onSelect ? !!selected : undefined}
    >
      <div>
        <div className="relative mb-3 flex h-48 w-full items-center justify-center overflow-hidden rounded-xl bg-white border border-rp-border/80 p-3 shadow-xs">
          {effectiveImageUrl ? (
            <img
              src={effectiveImageUrl}
              alt={product.title}
              loading="lazy"
              onError={() => setImgError(true)}
              className="h-full w-full object-contain transition-transform duration-300 group-hover:scale-105"
            />
          ) : (
            <div className="flex flex-col items-center justify-center text-center p-3 text-rp-muted">
              <Package className="h-10 w-10 text-rp-muted/50 mb-1" aria-hidden />
              <span className="text-xs font-semibold">No product photo</span>
            </div>
          )}
          {effectiveImageUrl && (
            <div className="absolute top-2 right-2">
              <Badge tone="primary" className="text-[10px] font-bold py-0.5 px-1.5 shadow-xs">
                Photo
              </Badge>
            </div>
          )}
        </div>
        <p className="line-clamp-2 text-sm font-bold text-rp-navy group-hover:text-rp-primary transition-colors">
          {product.title}
        </p>
        <p className="mt-0.5 text-xs text-rp-muted">
          {[product.brand, product.asin].filter(Boolean).join(' · ')}
        </p>
      </div>

      <div className="mt-3 flex items-center justify-between text-sm pt-2 border-t border-rp-border/50">
        {product.rating != null ? (
          <span className="tnum inline-flex items-center gap-1 font-semibold text-amber-500">
            <Star className="h-4 w-4 fill-amber-400 text-amber-500" aria-hidden />
            {product.rating.toFixed(1)}
          </span>
        ) : (
          <span className="text-xs text-rp-muted">No rating</span>
        )}
        {product.price != null && (
          <span className="tnum font-extrabold text-rp-navy">₹{product.price.toLocaleString('en-IN')}</span>
        )}
      </div>
    </Card>
  );
}
