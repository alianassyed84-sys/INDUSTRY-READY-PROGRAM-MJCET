import { createContext, useContext, useMemo, useState, type ReactNode } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import type { ApiEnvelope, Insights, Product, Review } from '@/lib/types';

interface Ctx {
  products: Product[];
  productId: string | undefined;
  setProductId: (id: string) => void;
  loading: boolean;
  source: ApiEnvelope<unknown>['source'];
  fallbackReason?: string;
}
const ProductCtx = createContext<Ctx | null>(null);

export function ProductProvider({ children }: { children: ReactNode }) {
  const q = useQuery({ queryKey: ['products'], queryFn: ({ signal }) => api.products(signal), staleTime: 60_000 });
  const [picked, setPicked] = useState<string>();
  const products = q.data?.data ?? [];
  const value = useMemo<Ctx>(
    () => ({
      products,
      productId: picked ?? products[0]?.id,
      setProductId: setPicked,
      loading: q.isLoading,
      source: q.data?.source ?? 'demo',
      fallbackReason: q.data?.fallbackReason,
    }),
    [products, picked, q.isLoading, q.data?.source, q.data?.fallbackReason],
  );
  return <ProductCtx.Provider value={value}>{children}</ProductCtx.Provider>;
}

export function useProductContext() {
  const c = useContext(ProductCtx);
  if (!c) throw new Error('useProductContext must be used inside ProductProvider');
  return c;
}

export function useInsights() {
  const { productId } = useProductContext();
  return useQuery({
    queryKey: ['insights', productId],
    queryFn: ({ signal }) => api.insights(productId!, signal),
    enabled: !!productId,
  });
}

export function useReviews() {
  const { productId } = useProductContext();
  return useQuery({
    queryKey: ['reviews', productId],
    queryFn: ({ signal }) => api.reviews(productId!, signal),
    enabled: !!productId,
  });
}

export type InsightsResult = ApiEnvelope<Insights>;
export type ReviewsResult = ApiEnvelope<Review[]>;
