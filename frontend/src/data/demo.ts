/**
 * DEMO FIXTURES ONLY. Entirely fictional, used when the backend is unreachable.
 * Always surfaced in the UI with a "Demo data" label; never merged with live results.
 */
import type { Insights, Product, Review, Sentiment } from '@/lib/types';

export const demoProducts: Product[] = [
  { id: 'demo-1', title: 'Sample Wireless Earbuds', brand: 'DemoBrand', asin: 'B0DEMO0001', marketplace: 'Amazon.in', price: 2499, listPrice: 3999, rating: 4.1, ratingCount: 1860 },
  { id: 'demo-2', title: 'Sample Smart Water Bottle', brand: 'DemoBrand', asin: 'B0DEMO0002', marketplace: 'Amazon.in', price: 1299, listPrice: 1799, rating: 3.8, ratingCount: 642 },
  { id: 'demo-3', title: 'Sample Mechanical Keyboard', brand: 'DemoBrand', asin: 'B0DEMO0003', marketplace: 'Amazon.in', price: 4599, listPrice: 5999, rating: 4.4, ratingCount: 2310 },
];

const texts: [string, number, Sentiment, string][] = [
  ['Sound quality is crisp and the bass is punchy for the price. Pairing was instant.', 5, 'positive', 'en'],
  ['Battery easily lasts a full day of calls and music. Very happy with this purchase.', 5, 'positive', 'en'],
  ['Right earbud stopped charging after three weeks. Support was slow to respond.', 1, 'negative', 'en'],
  ['Fit is comfortable but they slip out when I run. Okay for desk use.', 3, 'neutral', 'en'],
  ['Microphone picks up a lot of background noise on calls, colleagues complained.', 2, 'negative', 'en'],
  ['Bahut accha sound hai, battery bhi badhiya chalti hai. Paisa vasool.', 5, 'positive', 'hi'],
  ['Case feels cheap and the hinge creaks, but the earbuds themselves work fine.', 3, 'neutral', 'en'],
  ['Bluetooth drops randomly when the phone is in my pocket. Frustrating.', 2, 'negative', 'en'],
  ['Great value. Noise isolation is better than I expected at this price point.', 4, 'positive', 'en'],
  ['சவுண்ட் தரம் நன்றாக உள்ளது, ஆனால் சார்ஜிங் கேஸ் சிறிது பெரியது.', 4, 'positive', 'ta'],
  ['Delivery was quick and packaging was intact. Product matches the description.', 4, 'positive', 'en'],
  ['Touch controls are over-sensitive and pause my music when I adjust the fit.', 2, 'negative', 'en'],
  ['Average product. Nothing special, nothing terrible.', 3, 'neutral', 'en'],
  ['బ్యాటరీ బాగుంది, కానీ మైక్ నాణ్యత తక్కువగా ఉంది.', 3, 'neutral', 'te'],
  ['Connection is stable and latency is low for videos. Gaming mode works well.', 5, 'positive', 'en'],
  ['Stopped working after a month. Refund process was painful.', 1, 'negative', 'en'],
];

export const demoReviews = (productId: string): Review[] =>
  texts.map(([text, rating, sentiment, language], i) => ({
    id: `${productId}-r${i + 1}`,
    text,
    rating,
    sentiment,
    language,
    date: new Date(Date.UTC(2026, 8, 28 - i * 3)).toISOString(),
    source: 'Demo fixture',
  }));

const LANG_LABEL: Record<string, string> = { en: 'English', hi: 'Hindi', ta: 'Tamil', te: 'Telugu' };

export const demoInsights = (productId: string): Insights => {
  const product = demoProducts.find((p) => p.id === productId) ?? demoProducts[0];
  const reviews = demoReviews(product.id);
  const count = (s: Sentiment) => reviews.filter((r) => r.sentiment === s).length;
  const langs = new Map<string, number>();
  reviews.forEach((r) => r.language && langs.set(r.language, (langs.get(r.language) ?? 0) + 1));
  return {
    product,
    analyzedAt: new Date(Date.UTC(2026, 9, 20, 9, 30)).toISOString(),
    ratingBreakdown: { '5': 52, '4': 24, '3': 12, '2': 7, '1': 5 },
    sentiment: { positive: count('positive'), neutral: count('neutral'), negative: count('negative'), avgPolarity: 0.31 },
    topics: [
      { term: 'battery life', frequency: 14, relevance: 0.91, snippets: [texts[1][0], texts[5][0]] },
      { term: 'sound quality', frequency: 12, relevance: 0.88, snippets: [texts[0][0], texts[8][0]] },
      { term: 'bluetooth connection', frequency: 8, relevance: 0.74, snippets: [texts[7][0], texts[14][0]] },
      { term: 'microphone', frequency: 7, relevance: 0.69, snippets: [texts[4][0], texts[13][0]] },
      { term: 'charging case', frequency: 6, relevance: 0.63, snippets: [texts[6][0], texts[9][0]] },
      { term: 'touch controls', frequency: 4, relevance: 0.55, snippets: [texts[11][0]] },
      { term: 'customer support', frequency: 4, relevance: 0.52, snippets: [texts[2][0], texts[15][0]] },
    ],
    themes: {
      positive: ['battery life', 'sound quality', 'value for money', 'pairing'],
      negative: ['connection drops', 'microphone noise', 'build of case', 'support response'],
    },
    aspects: [
      { aspect: 'Battery', score: 0.62, mentions: 14 },
      { aspect: 'Sound', score: 0.55, mentions: 12 },
      { aspect: 'Connectivity', score: -0.28, mentions: 8 },
      { aspect: 'Microphone', score: -0.35, mentions: 7 },
    ],
    readability: {
      fleschReadingEase: 71.4,
      gradeLevel: 6.8,
      distribution: [
        { label: 'Very easy', count: 4 },
        { label: 'Easy', count: 6 },
        { label: 'Fairly easy', count: 3 },
        { label: 'Standard', count: 1 },
        { label: 'Difficult', count: 0 },
      ],
      analyzed: 14,
      excluded: 2,
    },
    languages: [...langs].map(([code, c]) => ({ code, label: LANG_LABEL[code] ?? code, count: c })),
    priceHistory: [
      { observedAt: '2026-08-01T00:00:00Z', price: 2999 },
      { observedAt: '2026-08-18T00:00:00Z', price: 2799 },
      { observedAt: '2026-09-05T00:00:00Z', price: 2899 },
      { observedAt: '2026-09-22T00:00:00Z', price: 2599 },
      { observedAt: '2026-10-10T00:00:00Z', price: 2499 },
    ],
  };
};
