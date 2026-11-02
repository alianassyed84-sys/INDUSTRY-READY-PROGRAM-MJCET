import type {
  BackendAspectInsight,
  BackendPriceHistoryResponse,
  BackendProductDetail,
  BackendProductInsightsResponse,
  BackendProductListItem,
  BackendReviewListItem,
  Insights,
  Product,
  Review,
  Topic,
} from './types';
import { resolveStudioImage } from './flipkart';

/**
 * Derives marketplace name from the canonical product URL domain.
 * Returns undefined if missing or unrecognized so the UI hides the badge rather than guessing.
 */
export function deriveMarketplace(url?: string | null): string | undefined {
  if (!url) return undefined;
  const lower = url.toLowerCase();
  if (lower.includes('amazon.')) return 'Amazon.in';
  if (lower.includes('flipkart.')) return 'Flipkart';
  return undefined;
}

/**
 * Maps backend ProductListItem or ProductDetail to frontend Product model.
 * Never sets brand to category. Derives marketplace from URL or leaves undefined.
 * Missing backend numbers become null (never 0).
 */
export function adaptProduct(item: BackendProductListItem | BackendProductDetail): Product {
  const detail = item as Partial<BackendProductDetail>;
  return {
    id: item.product_id,
    title: item.product_name,
    asin: item.product_id,
    brand: undefined,
    category: item.category ?? undefined,
    marketplace: deriveMarketplace(detail.product_link),
    price: item.discounted_price ?? null,
    listPrice: item.actual_price ?? null,
    rating: item.rating ?? null,
    ratingCount: item.rating_count ?? null,
    imageUrl:
      item.img_link && !item.img_link.includes('AMZN-KAG-001')
        ? item.img_link
        : detail.img_link && !detail.img_link.includes('AMZN-KAG-001')
          ? detail.img_link
          : resolveStudioImage(item.product_name, item.product_id, item.img_link ?? detail.img_link ?? undefined),
  };
}

/**
 * Maps backend ReviewListItem to frontend Review model.
 * Does NOT expose created_at (import/insertion timestamp) as the review publication date.
 * Does NOT hardcode 'Amazon.in' as source.
 */
export function adaptReview(item: BackendReviewListItem): Review {
  return {
    id: item.review_id,
    text: item.review_content || item.review_title || '(No review text provided)',
    rating: item.rating ?? null,
    date: undefined,
    source: undefined,
  };
}

/**
 * Maps backend ProductInsightsResponse (and optional price history / detail) to frontend Insights model.
 * Missing readability metrics preserve null rather than coercing to 0.
 */
export function adaptInsights(
  backend: BackendProductInsightsResponse,
  priceHistory?: BackendPriceHistoryResponse | null,
  productDetail?: BackendProductDetail | null,
): Insights {
  const totalRatings = backend.ratings.total_ratings_count || 1;
  const ratingBreakdown: Record<'1' | '2' | '3' | '4' | '5', number> = {
    '1': Math.round((backend.ratings.stars_1 / totalRatings) * 100),
    '2': Math.round((backend.ratings.stars_2 / totalRatings) * 100),
    '3': Math.round((backend.ratings.stars_3 / totalRatings) * 100),
    '4': Math.round((backend.ratings.stars_4 / totalRatings) * 100),
    '5': Math.round((backend.ratings.stars_5 / totalRatings) * 100),
  };

  const aspects = Object.values(backend.sentiment.aspects || {}).map((a: BackendAspectInsight) => ({
    aspect: a.aspect,
    score: a.average_polarity,
    mentions: a.mentions_count,
  }));

  const topics: Topic[] = (backend.top_topics || []).map((t) => ({
    term: t.term,
    frequency: t.frequency,
    relevance: t.relevance_score,
  }));

  const snapshots = priceHistory?.snapshots || [];
  const history = snapshots.map((s) => ({
    observedAt: s.observed_at,
    price: s.price,
  }));

  const baseProduct: Product = productDetail
    ? adaptProduct(productDetail)
    : {
        id: backend.product_id,
        title: backend.product_name,
        asin: backend.product_id,
        brand: undefined,
        category: undefined,
        marketplace: undefined,
        rating: backend.ratings.average_rating ?? null,
        ratingCount: backend.ratings.total_ratings_count ?? null,
      };

  return {
    product: baseProduct,
    analyzedAt: new Date().toISOString(),
    ratingBreakdown,
    sentiment: {
      positive: backend.sentiment.counts.positive,
      neutral: backend.sentiment.counts.neutral,
      negative: backend.sentiment.counts.negative,
      avgPolarity: backend.sentiment.average_polarity,
    },
    topics,
    themes: {
      positive: backend.sentiment.top_positive_highlights || [],
      negative: backend.sentiment.top_negative_highlights || [],
    },
    aspects,
    readability: {
      fleschReadingEase: backend.readability.average_reading_ease ?? null,
      gradeLevel: backend.readability.consensus_grade_level ?? null,
      distribution: [],
      analyzed: backend.total_reviews_analyzed,
      excluded: Math.max(0, backend.total_reviews_in_db - backend.total_reviews_analyzed),
    },
    priceHistory: history,
  };
}
