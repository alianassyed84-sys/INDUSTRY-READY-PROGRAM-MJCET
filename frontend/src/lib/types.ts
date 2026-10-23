export type DataSource = 'live' | 'demo';

export interface Product {
  id: string;
  title: string;
  brand?: string;
  imageUrl?: string;
  asin?: string;
  marketplace?: string;
  price?: number;
  listPrice?: number;
  rating?: number;
  ratingCount?: number;
}

export type Sentiment = 'positive' | 'neutral' | 'negative';

export interface Review {
  id: string;
  text: string;
  rating?: number;
  date?: string;
  language?: string;
  sentiment?: Sentiment;
  source?: string;
}

export interface Topic {
  term: string;
  frequency: number;
  relevance: number;
  snippets?: string[];
}

export interface Insights {
  product: Product;
  analyzedAt: string;
  ratingBreakdown?: Record<'1' | '2' | '3' | '4' | '5', number>;
  sentiment?: { positive: number; neutral: number; negative: number; avgPolarity?: number };
  topics?: Topic[];
  themes?: { positive: string[]; negative: string[] };
  aspects?: { aspect: string; score: number; mentions: number }[];
  readability?: {
    fleschReadingEase: number;
    gradeLevel: number;
    distribution: { label: string; count: number }[];
    analyzed: number;
    excluded: number;
  };
  languages?: { code: string; label: string; count: number }[];
  priceHistory?: { observedAt: string; price: number }[];
}

export interface ApiEnvelope<T> {
  data: T;
  source: DataSource;
  /** Present when live retrieval failed and fixtures were used instead. */
  fallbackReason?: string;
  requestId?: string;
}

// ---------------------------------------------------------------------------
// Authoritative Backend Contracts (FastAPI Pydantic Schemas)
// ---------------------------------------------------------------------------

export interface BackendHealthResponse {
  status: string;
  service: string;
}

export interface BackendReadyResponse {
  status: 'ok' | 'not_ready';
  service: string;
  database: 'ok' | 'unconfigured' | 'not_verified' | 'unavailable';
}

export interface BackendProductListItem {
  product_id: string;
  product_name: string;
  category: string | null;
  rating: number | null;
  rating_count: number | null;
  discounted_price: number | null;
  actual_price: number | null;
  discount_percentage: number | null;
}

export interface BackendProductDetail extends BackendProductListItem {
  about_product: string | null;
  img_link: string | null;
  product_link: string | null;
  created_at: string | null;
}

export interface BackendPaginatedProducts {
  total_returned: number;
  limit: number;
  offset: number;
  items: BackendProductListItem[];
}

export interface BackendReviewListItem {
  review_id: string;
  product_id: string;
  user_id: string | null;
  rating: number | null;
  review_title: string | null;
  review_content: string | null;
  created_at: string | null;
}

export interface BackendPaginatedReviews {
  total_returned: number;
  limit: number;
  offset: number;
  items: BackendReviewListItem[];
}

export interface BackendRatingBreakdown {
  average_rating: number | null;
  total_ratings_count: number;
  stars_1: number;
  stars_2: number;
  stars_3: number;
  stars_4: number;
  stars_5: number;
}

export interface BackendSentimentCounts {
  positive: number;
  neutral: number;
  negative: number;
}

export interface BackendAspectInsight {
  aspect: string;
  average_polarity: number;
  label: 'positive' | 'negative' | 'neutral';
  mentions_count: number;
  snippets: string[];
}

export interface BackendTopicInsight {
  term: string;
  relevance_score: number;
  frequency: number;
  ngram_size: number;
}

export interface BackendSentimentInsightSummary {
  average_polarity: number;
  sentiment_label: 'positive' | 'negative' | 'neutral';
  counts: BackendSentimentCounts;
  top_positive_highlights: string[];
  top_negative_highlights: string[];
  aspects: Record<string, BackendAspectInsight>;
}

export interface BackendReadabilitySummary {
  average_reading_ease: number | null;
  consensus_grade_level: number | null;
  reading_level_label: string | null;
}

export interface BackendProductInsightsResponse {
  product_id: string;
  product_name: string;
  total_reviews_in_db: number;
  total_reviews_analyzed: number;
  ratings: BackendRatingBreakdown;
  sentiment: BackendSentimentInsightSummary;
  top_topics: BackendTopicInsight[];
  readability: BackendReadabilitySummary;
}

export interface BackendPriceSnapshot {
  price: number;
  original_price: number | null;
  currency: string;
  source: string;
  observed_at: string;
}

export interface BackendPriceHistoryResponse {
  product_id: string;
  observations_count: number;
  first_observed_price: number | null;
  latest_observed_price: number | null;
  current_price: number | null;
  highest_observed_price: number | null;
  lowest_observed_price: number | null;
  price_change_amount: number | null;
  price_change_percentage: number | null;
  currency: string;
  is_multi_currency: boolean;
  tracking_start: string | null;
  tracking_end: string | null;
  tracking_period_days: number;
  is_historical_peak: boolean;
  status_note: string;
  snapshots: BackendPriceSnapshot[];
}

export interface BackendProductUrlAnalysisResponse {
  asin: string;
  canonical_url: string;
  product: BackendProductDetail;
  price_history: BackendPriceHistoryResponse;
  insights: BackendProductInsightsResponse | null;
  status_note: string;
}

export interface BackendJobStatusResponse {
  id: number;
  source: string;
  status: string;
  products_seen: number;
  products_inserted: number;
  products_skipped: number;
  reviews_seen: number;
  reviews_inserted: number;
  reviews_skipped: number;
  warning_count: number;
  error_count: number;
  error_sample: string[];
  started_at: string | null;
  finished_at: string | null;
  created_at: string | null;
}

export interface BackendReadabilityScoreDetail {
  score: number | null;
  grade_level: number | null;
  interpretation: string | null;
  description: string;
}

export interface BackendReadabilityResponse {
  is_analyzable: boolean;
  reliability: 'high' | 'medium' | 'low' | 'unreliable';
  language: string;
  statistics: {
    character_count: number;
    letter_count: number;
    word_count: number;
    sentence_count: number;
    syllable_count: number;
    complex_word_count: number;
    unique_word_count: number;
    avg_words_per_sentence: number;
    avg_syllables_per_word: number;
    avg_letters_per_word: number;
    complex_word_percentage: number;
    type_token_ratio: number;
  };
  flesch_reading_ease: BackendReadabilityScoreDetail;
  flesch_kincaid_grade: BackendReadabilityScoreDetail;
  gunning_fog: BackendReadabilityScoreDetail;
  coleman_liau: BackendReadabilityScoreDetail;
  automated_readability_index: BackendReadabilityScoreDetail;
  consensus_grade_level: number | null;
  reading_time_seconds: number;
  limitations: string[];
}

export interface BackendLanguageCandidate {
  language_code: string;
  language_name: string;
  confidence: number;
  rank: number;
}

export interface BackendLanguageDetectionResponse {
  detected_language: string | null;
  detected_language_name: string | null;
  confidence: number;
  confidence_level: 'high' | 'medium' | 'low' | 'unreliable';
  is_reliable: boolean;
  script_fast_path: boolean;
  candidates: BackendLanguageCandidate[];
  character_count: number;
  analyzed_ngrams: number;
  limitations: string[];
}

export interface BackendPolarHighlight {
  token: string;
  raw_valence: number;
  adjusted_valence: number;
  modifiers: string[];
}

export interface BackendSentimentResponse {
  text_length: number;
  word_count: number;
  scores: {
    compound: number;
    positive: number;
    negative: number;
    neutral: number;
  };
  label: 'positive' | 'negative' | 'neutral';
  confidence: number;
  highlights: BackendPolarHighlight[];
  aspects: Record<string, BackendAspectInsight>;
  limitations: string[];
}

export interface BackendKeyphrase {
  term: string;
  score: number;
  term_frequency: number;
  document_frequency: number;
  ngram_size: number;
}

export interface BackendDocumentTopics {
  document_index: number;
  keyphrases: BackendKeyphrase[];
  token_count: number;
  limitations: string[];
}

export interface BackendTopicsResponse {
  corpus_size: number;
  focus_index: number | null;
  documents: BackendDocumentTopics[];
  preprocessing: Record<string, unknown>;
  limitations: string[];
}

export interface BackendFlipkartVariantAttribute {
  name: string;
  value: string;
}

export interface BackendFlipkartReviewItem {
  reviewId: string;
  reviewUrl?: string | null;
  productId: string;
  reviewProductId?: string | null;
  title?: string | null;
  text?: string | null;
  rating?: number | null;
  reviewer?: string | null;
  displayedDate?: string | null;
  certifiedBuyer?: boolean | null;
  verifiedPurchase?: boolean | null;
  helpfulCount?: number | null;
  unhelpfulCount?: number | null;
  variant?: BackendFlipkartVariantAttribute[];
}

export interface BackendFlipkartScrapeResponse {
  product_id: string;
  product_name: string;
  canonical_url: string;
  reviews_count: number;
  estimated_cost_usd: number;
  is_mock_provider: boolean;
  product: BackendProductDetail;
  reviews: BackendFlipkartReviewItem[];
  insights: BackendProductInsightsResponse | null;
  status_note: string;
}


