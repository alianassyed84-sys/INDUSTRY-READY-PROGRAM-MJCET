import type {
  ApiEnvelope,
  BackendFlipkartScrapeResponse,
  BackendHealthResponse,
  BackendJobStatusResponse,
  BackendLanguageDetectionResponse,
  BackendPaginatedProducts,
  BackendPaginatedReviews,
  BackendPriceHistoryResponse,
  BackendProductDetail,
  BackendProductUrlAnalysisResponse,
  BackendReadabilityResponse,
  BackendReadyResponse,
  BackendSentimentResponse,
  BackendTopicsResponse,
} from './types';
import { adaptInsights, adaptProduct, adaptReview } from './adapters';
import { demoInsights, demoProducts, demoReviews } from '@/data/demo';

export const API_BASE_URL: string =
  (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\/+$/, '') ?? 'http://localhost:8000';

export class ApiError extends Error {
  constructor(
    message: string,
    public status?: number,
    public requestId?: string,
    public details?: unknown,
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

function formatStatusMessage(status: number): string {
  switch (status) {
    case 401:
      return 'Authentication required (HTTP 401). Please sign in.';
    case 403:
      return 'Administrative privileges required (HTTP 403).';
    case 404:
      return 'Requested resource not found (HTTP 404).';
    case 422:
      return 'Validation error (HTTP 422). Please verify your input parameters.';
    case 429:
      return 'Rate limit exceeded (HTTP 429). Please try again shortly.';
    case 502:
      return 'Upstream provider gateway error (HTTP 502).';
    case 503:
      return 'Service unavailable (HTTP 503). Database or external provider is not configured.';
    default:
      return `Request failed with HTTP status ${status}.`;
  }
}

function getAuthBearerToken(): string {
  try {
    const raw = sessionStorage.getItem('rp.prototype.session');
    if (raw) {
      const parsed = JSON.parse(raw) as { token?: string };
      if (parsed.token) return `Bearer ${parsed.token}`;
    }
  } catch {
    // Session storage not accessible
  }
  // In development, the backend requires a Bearer header to pass FastAPI's
  // `get_current_user` dependency even when AUTH_ENABLED=False.
  // Passing `Bearer dev-token` satisfies the check and returns the test identity.
  return 'Bearer dev-bypass-token';
}

function generateRequestId(): string {
  if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
    return crypto.randomUUID();
  }
  return `rp-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
}

/**
 * Centralized HTTP request helper. Attaches X-Request-ID and Authorization Bearer header.
 */
export async function request<T>(path: string, init?: RequestInit & { signal?: AbortSignal }): Promise<T> {
  const reqId = generateRequestId();
  const headers: Record<string, string> = {
    Accept: 'application/json',
    'X-Request-ID': reqId,
    Authorization: getAuthBearerToken(),
    ...(init?.headers as Record<string, string> | undefined),
  };

  const url = path.startsWith('http') ? path : `${API_BASE_URL}${path}`;

  let res: Response;
  try {
    res = await fetch(url, {
      ...init,
      headers,
    });
  } catch (e) {
    if ((e as Error).name === 'AbortError') throw e;
    throw new ApiError('Backend unreachable', undefined, reqId);
  }

  const serverRequestId = res.headers.get('X-Request-ID') || reqId;

  if (!res.ok) {
    let errorDetail: string | undefined;
    let parsedBody: unknown;
    try {
      parsedBody = await res.json();
      if (parsedBody && typeof parsedBody === 'object' && 'detail' in parsedBody) {
        const d = (parsedBody as { detail: unknown }).detail;
        errorDetail = typeof d === 'string' ? d : JSON.stringify(d);
      }
    } catch {
      // Body is not JSON
    }

    const message = errorDetail || formatStatusMessage(res.status);
    throw new ApiError(message, res.status, serverRequestId, parsedBody);
  }

  return (await res.json()) as T;
}

/**
 * Tries the live backend first. If network is offline/unreachable, returns
 * clearly labelled demo fixtures. Real HTTP error responses (4xx, 5xx) are thrown
 * and never disguised as demo data.
 */
async function withDemoFallback<T>(live: () => Promise<T>, demo: () => T): Promise<ApiEnvelope<T>> {
  try {
    const data = await live();
    return { data, source: 'live' };
  } catch (e) {
    if ((e as Error).name === 'AbortError') throw e;
    if (e instanceof ApiError && e.status !== undefined) {
      throw e;
    }
    return { data: demo(), source: 'demo', fallbackReason: (e as Error).message };
  }
}

export const api = {
  // System probes
  health: (signal?: AbortSignal) =>
    request<BackendHealthResponse>('/api/v1/health', { signal }),
  ready: (signal?: AbortSignal) =>
    request<BackendReadyResponse>('/api/v1/ready', { signal }),

  // Products
  products: (signal?: AbortSignal) =>
    withDemoFallback(
      async () => {
        const paginated = await request<BackendPaginatedProducts>('/api/v1/harvester/products?limit=100', { signal });
        return paginated.items.map(adaptProduct);
      },
      () => demoProducts,
    ),

  product: (productId: string, signal?: AbortSignal) =>
    request<BackendProductDetail>(`/api/v1/harvester/products/${encodeURIComponent(productId)}`, { signal }),

  // Product Insights (aggregates insights, price history, and detail)
  insights: (productId: string, signal?: AbortSignal) =>
    withDemoFallback(
      async () => {
        const [insightsResp, historyResp, detailResp] = await Promise.all([
          request<any>(`/api/v1/harvester/products/${encodeURIComponent(productId)}/insights?limit=100`, { signal }),
          request<BackendPriceHistoryResponse>(`/api/v1/harvester/products/${encodeURIComponent(productId)}/price-history`, { signal }).catch(() => null),
          request<BackendProductDetail>(`/api/v1/harvester/products/${encodeURIComponent(productId)}`, { signal }).catch(() => null),
        ]);
        return adaptInsights(insightsResp, historyResp, detailResp);
      },
      () => demoInsights(productId),
    ),

  // Reviews
  reviews: (productId: string, signal?: AbortSignal) =>
    withDemoFallback(
      async () => {
        const paginated = await request<BackendPaginatedReviews>(
          `/api/v1/harvester/reviews?product_id=${encodeURIComponent(productId)}&limit=100`,
          { signal },
        );
        return paginated.items.map(adaptReview);
      },
      () => demoReviews(productId),
    ),

  // Price history and polling
  priceHistory: (productId: string, signal?: AbortSignal) =>
    request<BackendPriceHistoryResponse>(`/api/v1/harvester/products/${encodeURIComponent(productId)}/price-history`, { signal }),

  checkPrice: (productId: string, signal?: AbortSignal) =>
    request<BackendPriceHistoryResponse>(`/api/v1/harvester/products/${encodeURIComponent(productId)}/check-price`, {
      method: 'POST',
      signal,
    }),

  // URL Analysis (Amazon.in or Flipkart)
  analyzeUrl: (url: string, signal?: AbortSignal) =>
    request<BackendProductUrlAnalysisResponse>('/api/v1/harvester/analyze-url', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url }),
      signal,
    }),

  // Flipkart Review Scraper (Apify Actor: automation-lab/flipkart-product-reviews-scraper)
  scrapeFlipkart: (
    params: { url: string; max_items?: number; max_pages_per_product?: number },
    signal?: AbortSignal,
  ) =>
    request<BackendFlipkartScrapeResponse>('/api/v1/harvester/flipkart/scrape', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
      signal,
    }),

  // Harvester Jobs (Admin)
  startJob: (source = 'csv_amazon', signal?: AbortSignal) =>
    request<BackendJobStatusResponse>('/api/v1/harvester/jobs', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ source }),
      signal,
    }),

  getJob: (jobId: number, signal?: AbortSignal) =>
    request<BackendJobStatusResponse>(`/api/v1/harvester/jobs/${jobId}`, { signal }),

  // NLP Analysis Playground
  readability: (text: string, signal?: AbortSignal) =>
    request<BackendReadabilityResponse>('/api/v1/analysis/readability', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
      signal,
    }),

  detectLanguage: (text: string, signal?: AbortSignal) =>
    request<BackendLanguageDetectionResponse>('/api/v1/analysis/language', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
      signal,
    }),

  analyzeSentiment: (text: string, aspects?: string[], signal?: AbortSignal) =>
    request<BackendSentimentResponse>('/api/v1/analysis/sentiment', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, aspects: aspects && aspects.length ? aspects : undefined }),
      signal,
    }),

  extractTopics: (documents: string[], topN = 10, focusIndex?: number, signal?: AbortSignal) =>
    request<BackendTopicsResponse>('/api/v1/analysis/topics', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ documents, top_n: topN, focus_index: focusIndex }),
      signal,
    }),
};
