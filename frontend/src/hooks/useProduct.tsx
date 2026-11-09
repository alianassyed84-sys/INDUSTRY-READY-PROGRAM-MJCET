import { createContext, useContext, useMemo, useState, type ReactNode } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { demoProducts } from '@/data/demo';
import type { ApiEnvelope, Insights, Product, Review } from '@/lib/types';

interface Ctx {
  products: Product[];
  productId: string | undefined;
  setProductId: (id: string) => void;
  addProduct: (product: Product) => void;
  loading: boolean;
  source: ApiEnvelope<unknown>['source'];
  fallbackReason?: string;
}
const ProductCtx = createContext<Ctx | null>(null);

export function ProductProvider({ children }: { children: ReactNode }) {
  const q = useQuery({ queryKey: ['products'], queryFn: ({ signal }) => api.products(signal), staleTime: 60_000 });
  const [picked, setPicked] = useState<string>();
  const [customProducts, setCustomProducts] = useState<Product[]>([]);

  // Seamlessly merge live API products with custom analyzed products and rich catalog fixtures
  const products = useMemo<Product[]>(() => {
    const list = [...(q.data?.data ?? [])];
    const seen = new Set(list.map((p) => p.id));

    // Custom analyzed products take highest priority
    for (const cp of customProducts) {
      const idx = list.findIndex((p) => p.id === cp.id);
      if (idx !== -1) {
        list[idx] = { ...list[idx], ...cp };
      } else {
        list.unshift(cp);
        seen.add(cp.id);
      }
    }

    // Rich demo catalog products backfill any missing items (e.g. B0H2FD3L97, iPhone 15 Pro, etc.)
    for (const dp of demoProducts) {
      if (!seen.has(dp.id)) {
        list.push(dp);
        seen.add(dp.id);
      }
    }
    return list;
  }, [q.data?.data, customProducts]);

  const addProduct = (product: Product) => {
    setCustomProducts((prev) => [product, ...prev.filter((p) => p.id !== product.id)]);
  };

  const value = useMemo<Ctx>(
    () => ({
      products,
      productId: picked ?? products.find((p) => Boolean(p.imageUrl))?.id ?? products[0]?.id,
      setProductId: setPicked,
      addProduct,
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

export function useN8nIntelligence() {
  const { productId } = useProductContext();
  return useQuery({
    queryKey: ['n8n-intelligence', productId],
    queryFn: ({ signal }) => api.n8nIntelligence(productId!, signal),
    enabled: !!productId,
    staleTime: 60_000,
    retry: false,
  });
}

export type InsightsResult = ApiEnvelope<Insights>;
export type ReviewsResult = ApiEnvelope<Review[]>;
