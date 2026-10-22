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

/**
 * Maps backend ProductListItem or ProductDetail to frontend Product model.
 * Guarantees asin, title, price, listPrice, rating, and imageUrl are derived correctly.
 */
export function adaptProduct(item: BackendProductListItem | BackendProductDetail): Product {
  const detail = item as Partial<BackendProductDetail>;
  return {
    id: item.product_id,
    title: item.product_name,
    asin: item.product_id,
    brand: item.category ?? undefined,
    marketplace: 'Amazon.in',
    price: item.discounted_price ?? undefined,
    listPrice: item.actual_price ?? undefined,
    rating: item.rating ?? undefined,
    ratingCount: item.rating_count ?? undefined,
    imageUrl: detail.img_link ?? undefined,
  };
}

/**
 * Maps backend ReviewListItem to frontend Review model.
 */
export function adaptReview(item: BackendReviewListItem): Review {
  return {
    id: item.review_id,
    text: item.review_content || item.review_title || '(No review text provided)',
    rating: item.rating ?? undefined,
    date: item.created_at ? new Date(item.created_at).toISOString() : undefined,
    source: 'Amazon.in',
  };
}

/**
 * Maps backend ProductInsightsResponse (and optional price history / detail) to frontend Insights model.
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
        marketplace: 'Amazon.in',
        rating: backend.ratings.average_rating ?? undefined,
        ratingCount: backend.ratings.total_ratings_count ?? undefined,
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
      fleschReadingEase: backend.readability.average_reading_ease ?? 0,
      gradeLevel: backend.readability.consensus_grade_level ?? 0,
      distribution: [],
      analyzed: backend.total_reviews_analyzed,
      excluded: Math.max(0, backend.total_reviews_in_db - backend.total_reviews_analyzed),
    },
    priceHistory: history,
  };
}
