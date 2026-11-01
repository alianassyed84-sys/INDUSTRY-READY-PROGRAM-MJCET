import { describe, it, expect } from 'vitest';
import { adaptProduct, adaptReview, adaptInsights } from '@/lib/adapters';
import type { BackendProductListItem, BackendProductDetail, BackendReviewListItem, BackendProductInsightsResponse } from '@/lib/types';

describe('Phase 3a Alignment: Data Honesty & Adapters', () => {
  it('adaptProduct derives marketplace from product_link domain and does not confuse brand with category', () => {
    const itemWithLink: BackendProductDetail = {
      product_id: 'B0TEST123',
      product_name: 'Test Amazon Product',
      category: 'Electronics | Headphones',
      rating: 4.2,
      rating_count: 100,
      discounted_price: 1999,
      actual_price: 2999,
      discount_percentage: 33,
      about_product: 'About product',
      img_link: 'https://example.com/img.jpg',
      product_link: 'https://www.amazon.in/dp/B0TEST123',
      created_at: '2026-10-20T10:00:00Z',
    };

    const adaptedAmz = adaptProduct(itemWithLink);
    expect(adaptedAmz.marketplace).toBe('Amazon.in');
    // Brand should NOT be category
    expect(adaptedAmz.brand).toBeUndefined();

    const fkItem: BackendProductDetail = {
      ...itemWithLink,
      product_id: 'FK123',
      product_link: 'https://www.flipkart.com/product/p/itm123?pid=FK123',
    };
    const adaptedFk = adaptProduct(fkItem);
    expect(adaptedFk.marketplace).toBe('Flipkart');

    const itemWithoutLink: BackendProductListItem = {
      product_id: 'UNKNOWN1',
      product_name: 'Unknown Item',
      category: 'General',
      rating: null,
      rating_count: null,
      discounted_price: null,
      actual_price: null,
      discount_percentage: null,
    };
    const adaptedUnknown = adaptProduct(itemWithoutLink);
    expect(adaptedUnknown.marketplace).toBeUndefined();
    expect(adaptedUnknown.rating).toBeNull();
    expect(adaptedUnknown.price).toBeNull();
  });

  it('adaptReview hides created_at import time as review date and avoids hardcoded Amazon.in source', () => {
    const reviewItem: BackendReviewListItem = {
      review_id: 'rev-001',
      product_id: 'B0TEST123',
      user_id: 'u-1',
      rating: null,
      review_title: 'Good sound',
      review_content: 'Clear treble and decent bass',
      created_at: '2026-10-31T09:30:00Z', // Import timestamp in DB
    };

    const adapted = adaptReview(reviewItem);
    // created_at must NOT be exposed as the review publication date
    expect(adapted.date).toBeUndefined();
    // source must NOT be hardcoded to Amazon.in
    expect(adapted.source).toBeUndefined();
    expect(adapted.rating).toBeNull();
  });

  it('adaptInsights preserves null for missing readability values instead of converting to 0', () => {
    const dummyInsights: BackendProductInsightsResponse = {
      product_id: 'B0TEST123',
      product_name: 'Test Product',
      total_reviews_in_db: 10,
      total_reviews_analyzed: 0,
      ratings: {
        average_rating: null,
        total_ratings_count: 0,
        stars_1: 0,
        stars_2: 0,
        stars_3: 0,
        stars_4: 0,
        stars_5: 0,
      },
      sentiment: {
        average_polarity: 0,
        sentiment_label: 'neutral',
        counts: { positive: 0, neutral: 0, negative: 0 },
        top_positive_highlights: [],
        top_negative_highlights: [],
        aspects: {},
      },
      top_topics: [],
      readability: {
        average_reading_ease: null,
        consensus_grade_level: null,
        reading_level_label: null,
      },
    };

    const adapted = adaptInsights(dummyInsights, null, null);
    expect(adapted.readability?.fleschReadingEase).toBeNull();
    expect(adapted.readability?.gradeLevel).toBeNull();
    expect(adapted.product.marketplace).toBeUndefined();
  });
});
