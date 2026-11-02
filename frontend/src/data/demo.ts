/**
 * Realistic catalog fixtures and dynamic product generation.
 * Supports Lenovo Tab, iPhone 15 Pro, Samsung S24 Ultra, MacBook Air M3,
 * Sony WH-1000XM5, AirPods Pro, boAt Bassheads, luxury fragrances, and dynamic URL generation.
 */
import type { Insights, Product, Review, Sentiment } from '@/lib/types';

export const demoProducts: Product[] = [
  {
    id: 'B0H2FD3L97',
    title: 'Lenovo Idea Tab (Smartchoice) with Folio Keyboard + Tab Pen',
    brand: 'Lenovo',
    asin: 'B0H2FD3L97',
    marketplace: 'Amazon.in',
    price: 31998,
    listPrice: 52000,
    rating: 4.4,
    ratingCount: 110,
    imageUrl: '/products/B0H2FD3L97.jpg',
  },
  {
    id: 'AMZN-IPHONE-15PRO',
    title: 'Apple iPhone 15 Pro (128 GB) - Natural Titanium',
    brand: 'Apple',
    asin: 'AMZN-IPHONE-15PRO',
    marketplace: 'Amazon.in',
    price: 127990,
    listPrice: 134900,
    rating: 4.6,
    ratingCount: 2840,
    imageUrl: '/products/AMZN-IPHONE-15PRO.jpg',
  },
  {
    id: 'AMZN-SAMSUNG-S24U',
    title: 'Samsung Galaxy S24 Ultra 5G (Titanium Gray, 12GB, 256GB)',
    brand: 'Samsung',
    asin: 'AMZN-SAMSUNG-S24U',
    marketplace: 'Amazon.in',
    price: 129999,
    listPrice: 134999,
    rating: 4.5,
    ratingCount: 1980,
    imageUrl: '/products/AMZN-SAMSUNG-S24U.jpg',
  },
  {
    id: 'AMZN-MACBOOK-AIR-M3',
    title: 'Apple MacBook Air M3 (13-inch, 16GB Unified Memory, 512GB SSD) - Space Grey',
    brand: 'Apple',
    asin: 'AMZN-MACBOOK-AIR-M3',
    marketplace: 'Amazon.in',
    price: 114900,
    listPrice: 124900,
    rating: 4.7,
    ratingCount: 940,
    imageUrl: '/products/AMZN-MACBOOK-AIR-M3.jpg',
  },
  {
    id: 'AMZN-SONY-WH1000XM5',
    title: 'Sony WH-1000XM5 Wireless Active Noise Cancelling Headphones - Silver',
    brand: 'Sony',
    asin: 'AMZN-SONY-WH1000XM5',
    marketplace: 'Amazon.in',
    price: 29990,
    listPrice: 34990,
    rating: 4.6,
    ratingCount: 4320,
    imageUrl: '/products/AMZN-SONY-WH1000XM5.jpg',
  },
  {
    id: 'AMZN-AIRPODS-PRO2',
    title: 'Apple AirPods Pro (2nd Generation) with MagSafe Case (USB-C)',
    brand: 'Apple',
    asin: 'AMZN-AIRPODS-PRO2',
    marketplace: 'Amazon.in',
    price: 24900,
    listPrice: 26900,
    rating: 4.6,
    ratingCount: 6120,
    imageUrl: '/products/AMZN-AIRPODS-PRO2.jpg',
  },
  {
    id: 'AMZN-ONEPLUS-12',
    title: 'OnePlus 12 (Flowy Emerald, 16GB RAM, 512GB Storage)',
    brand: 'OnePlus',
    asin: 'AMZN-ONEPLUS-12',
    marketplace: 'Amazon.in',
    price: 64999,
    listPrice: 69999,
    rating: 4.5,
    ratingCount: 1450,
    imageUrl: '/products/AMZN-ONEPLUS-12.jpg',
  },
  {
    id: 'B071Z8M4KX',
    title: 'boAt Bassheads 100 in Ear Wired Earphones with Mic (Black)',
    brand: 'boAt',
    asin: 'B071Z8M4KX',
    marketplace: 'Amazon.in',
    price: 399,
    listPrice: 999,
    rating: 4.1,
    ratingCount: 412850,
    imageUrl: '/products/B071Z8M4KX.jpg',
  },
  {
    id: 'AMZN-DIOR-SAUVAGE',
    title: 'Dior Sauvage Eau De Parfum for Men (100 ml)',
    brand: 'Dior',
    asin: 'AMZN-DIOR-SAUVAGE',
    marketplace: 'Amazon.in',
    price: 13500,
    listPrice: 15000,
    rating: 4.7,
    ratingCount: 3890,
    imageUrl: '/products/AMZN-DIOR-SAUVAGE.jpg',
  },
  {
    id: 'AMZN-BLEU-CHANEL',
    title: 'Bleu de Chanel Eau de Parfum (100 ml)',
    brand: 'Chanel',
    asin: 'AMZN-BLEU-CHANEL',
    marketplace: 'Amazon.in',
    price: 14200,
    listPrice: 16000,
    rating: 4.8,
    ratingCount: 2150,
    imageUrl: '/products/AMZN-BLEU-CHANEL.jpg',
  },
  {
    id: 'AMZN-VERSACE-EROS',
    title: 'Versace Eros Eau de Toilette (100 ml)',
    brand: 'Versace',
    asin: 'AMZN-VERSACE-EROS',
    marketplace: 'Amazon.in',
    price: 7800,
    listPrice: 9200,
    rating: 4.5,
    ratingCount: 1740,
    imageUrl: '/products/AMZN-VERSACE-EROS.jpg',
  },
  {
    id: 'MOBGTAGPNRQA7CS3',
    title: 'Motorola Edge 50 Fusion 5G (Marshmallow Blue, 256 GB)',
    brand: 'Motorola',
    asin: 'MOBGTAGPNRQA7CS3',
    marketplace: 'Flipkart',
    price: 22999,
    listPrice: 25999,
    rating: 4.4,
    ratingCount: 45120,
    imageUrl: '/products/MOBGTAGPNRQA7CS3.jpg',
  },
  {
    id: 'MOBGTAGPTB3VS24W',
    title: 'Samsung Galaxy S24 5G (Onyx Black, 128 GB)',
    brand: 'Samsung',
    asin: 'MOBGTAGPTB3VS24W',
    marketplace: 'Flipkart',
    price: 64999,
    listPrice: 79999,
    rating: 4.5,
    ratingCount: 12400,
    imageUrl: '/products/MOBGTAGPTB3VS24W.jpg',
  },
  {
    id: 'MOBHQC8ZMRCP62TS',
    title: 'Nothing Phone (2a) 5G (Black, 128 GB)',
    brand: 'Nothing',
    asin: 'MOBHQC8ZMRCP62TS',
    marketplace: 'Flipkart',
    price: 23999,
    listPrice: 25999,
    rating: 4.4,
    ratingCount: 28900,
    imageUrl: '/products/MOBHQC8ZMRCP62TS.jpg',
  },
  {
    id: 'demo-1',
    title: 'Sample Wireless Earbuds',
    brand: 'DemoBrand',
    asin: 'B0DEMO0001',
    marketplace: 'Amazon.in',
    price: 2499,
    listPrice: 3999,
    rating: 4.1,
    ratingCount: 1860,
    imageUrl: '/products/AMZN-AIRPODS-PRO2.jpg',
  },
  {
    id: 'demo-2',
    title: 'Sample Smart Water Bottle',
    brand: 'DemoBrand',
    asin: 'B0DEMO0002',
    marketplace: 'Amazon.in',
    price: 1299,
    listPrice: 1799,
    rating: 3.8,
    ratingCount: 642,
    imageUrl: '/products/AMZN-KAG-024.jpg',
  },
  {
    id: 'demo-3',
    title: 'Sample Mechanical Keyboard',
    brand: 'DemoBrand',
    asin: 'B0DEMO0003',
    marketplace: 'Amazon.in',
    price: 4599,
    listPrice: 5999,
    rating: 4.4,
    ratingCount: 2310,
    imageUrl: '/products/B0H2FD3L97.jpg',
  },
];

// Product-specific customized review collections
const PRODUCT_REVIEWS: Record<string, [string, number, Sentiment, string][]> = {
  B0H2FD3L97: [
    ['Customers find the tablet to be a great product and consider it good value for money. The display is crisp and keyboard typing feel is great.', 5, 'positive', 'en'],
    ['Value for money device for students. Good quality screen and pen response is smooth for note taking. The battery life receives mixed reviews, lasts about 7 hours with heavy usage.', 4, 'positive', 'en'],
    ['Superb display and sound quality. Quad speakers produce punchy sound for movies. Bundled pen and keyboard make it a proper budget laptop replacement.', 5, 'positive', 'en'],
    ['Good hardware, battery drains faster with keyboard. The tablet performance is solid but keeping the folio keyboard attached drains standby battery noticeably.', 3, 'neutral', 'en'],
    ['Bahut badhiya tablet hai student ke liye. Screen aur keyboard dono mast hain.', 5, 'positive', 'hi'],
    ['Best student tablet in this price bracket. Stylus palm rejection works surprisingly well on OneNote.', 5, 'positive', 'en'],
    ['Keyboard trackpad could have been slightly larger, but typing key travel is comfortable.', 4, 'positive', 'en'],
    ['టాబ్లెట్ స్క్రీన్ చాలా స్పష్టంగా ఉంది. కీబోర్డ్ మరియు పెన్ కూడా చాలా బాగున్నాయి.', 5, 'positive', 'te'],
    ['Performance is snappy for multitasking. 2.5K high refresh screen is a treat for reading PDFs.', 5, 'positive', 'en'],
    ['Battery backup is around 6-7 hours with keyboard connected instead of advertised 10 hours.', 2, 'negative', 'en'],
    ['Charging is a bit slow with the in-box 20W charger, takes over 2 hours for full charge.', 3, 'neutral', 'en'],
    ['టాబ్లెట్ బిల్డ్ క్వాలిటీ చాలా దృఢంగా ఉంది.', 4, 'positive', 'te'],
  ],
  'AMZN-IPHONE-15PRO': [
    ['The Natural Titanium finish feels extraordinarily light compared to the 14 Pro stainless steel. 48MP main sensor takes studio-grade portraits.', 5, 'positive', 'en'],
    ['A17 Pro chip plays console games without thermal throttling. USB-C with 10Gbps transfer speed makes video editing on external SSDs seamless.', 5, 'positive', 'en'],
    ['Battery easily powers through a 14-hour workday with 7.5 hours screen on time. Action button shortcut is genuinely useful.', 5, 'positive', 'en'],
    ['Fast charging still caps around 27W, which lags behind Android flagships, but overall reliability is unbeatable.', 4, 'positive', 'en'],
    ['Camera zoom and optical stabilization make low light concerts look cinematic.', 5, 'positive', 'en'],
    ['Iphone ka titanium build bahut premium feel deta hai, haath me bilkul halka lagta hai.', 5, 'positive', 'hi'],
  ],
  'AMZN-SAMSUNG-S24U': [
    ['The flat anti-reflective Gorilla Armor glass is unbelievable outdoors. Zero reflections even under direct afternoon sunlight.', 5, 'positive', 'en'],
    ['S-Pen integration is unmatched for signing PDFs and taking handwritten notes. 5x 50MP periscope zoom is crisp.', 5, 'positive', 'en'],
    ['Galaxy AI Circle to Search and live translation features save me hours every single week.', 5, 'positive', 'en'],
    ['Phone is undeniably heavy at 232g, but the titanium side rails give it exceptional grip.', 4, 'positive', 'en'],
    ['Display aur camera quality top notch hai. Battery poora din araam se chalti hai.', 5, 'positive', 'hi'],
  ],
  'AMZN-MACBOOK-AIR-M3': [
    ['M3 efficiency is astonishing. 18 hours of real battery life, fanless silent operation, and liquid smooth Xcode builds.', 5, 'positive', 'en'],
    ['Space Grey anodization with the new seal significantly reduces fingerprint smudges.', 5, 'positive', 'en'],
    ['Dual external display support with lid closed was the missing feature I needed for my home desk setup.', 5, 'positive', 'en'],
    ['Keyboard typing feel and Force Touch trackpad remain the industry gold standard.', 5, 'positive', 'en'],
  ],
  'AMZN-SONY-WH1000XM5': [
    ['Industry-leading noise cancellation. Erases airplane engine drone and noisy coffee shop chatter completely.', 5, 'positive', 'en'],
    ['Call quality with the 8 beamforming microphones is dramatically clearer than the XM4.', 5, 'positive', 'en'],
    ['Lightweight headband is comfortable for 6-hour flights without temple pressure.', 4, 'positive', 'en'],
    ['Cannot fold into a compact pouch like XM4, but audio tuning and detail resolution are sublime.', 4, 'positive', 'en'],
  ],
  'AMZN-AIRPODS-PRO2': [
    ['Adaptive Audio seamlessly blends transparency and active noise cancellation based on your surroundings.', 5, 'positive', 'en'],
    ['USB-C case with speaker chime makes finding it with Find My instantaneous.', 5, 'positive', 'en'],
    ['Soundstage and sub-bass extension are best-in-class for true wireless earbuds.', 5, 'positive', 'en'],
  ],
  'AMZN-ONEPLUS-12': [
    ['100W SuperVOOC charger tops the 5400 mAh battery from 1% to 100% in 26 minutes flat.', 5, 'positive', 'en'],
    ['4500 nits peak brightness 2K display with Aqua Touch works even with wet fingers.', 5, 'positive', 'en'],
    ['Hasselblad color calibration produces vibrant, natural skin tones.', 5, 'positive', 'en'],
  ],
  'B071Z8M4KX': [
    ['Bass is punchy and deep for ₹399. Best budget wired earphones for rough daily use.', 5, 'positive', 'en'],
    ['Braided cable near the 3.5mm jack prevents tangling in pockets.', 4, 'positive', 'en'],
    ['Microphone button works reliably for answering calls and skipping music.', 4, 'positive', 'en'],
    ['Ear tips are soft and comfortable for long online lectures.', 4, 'positive', 'en'],
  ],
  'AMZN-DIOR-SAUVAGE': [
    ['Iconic fresh bergamot and ambroxan opening. Projects strongly for 4+ hours and stays on clothes all day.', 5, 'positive', 'en'],
    ['The most compliment-getting signature fragrance in my entire collection.', 5, 'positive', 'en'],
    ['Versatile for office wear or evening dinners. Truly a masterpiece.', 5, 'positive', 'en'],
  ],
  'AMZN-BLEU-CHANEL': [
    ['Sophisticated blend of grapefruit, mint, and cedarwood. Refined, gentlemanly, and never overpowering.', 5, 'positive', 'en'],
    ['Magnetic cap and bottle presentation are pure luxury. Longevity easily reaches 8 hours.', 5, 'positive', 'en'],
  ],
  'AMZN-VERSACE-EROS': [
    ['Crisp mint, Italian lemon, and rich vanilla tonka bean. The definitive club and party fragrance.', 5, 'positive', 'en'],
    ['Performance and silage are incredible. One spray lasts the entire evening.', 5, 'positive', 'en'],
  ],
  MOBGTAGPNRQA7CS3: [
    ['144Hz curved pOLED display is stunning at this price point. Marshmallow Blue vegan leather back looks gorgeous.', 5, 'positive', 'en'],
    ['Sony LYT-700C camera sensor with OIS takes crisp low-light photos. Clean Moto UI with zero bloatware.', 5, 'positive', 'en'],
    ['IP68 water and dust resistance gives peace of mind in heavy rain.', 5, 'positive', 'en'],
    ['Snapdragon 7s Gen 2 handles daily tasks and casual gaming smoothly.', 4, 'positive', 'en'],
  ],
};

const DEFAULT_REVIEWS: [string, number, Sentiment, string][] = [
  ['Quality exceeded my expectations. Matches the description accurately and feels premium.', 5, 'positive', 'en'],
  ['Great value for money purchase. Packaging was intact and delivery was on time.', 4, 'positive', 'en'],
  ['Satisfied with overall build and performance. Works reliably for daily use.', 5, 'positive', 'en'],
  ['Decent product, though accessories could have had slightly better finish.', 3, 'neutral', 'en'],
  ['Paisa vasool product hai, bilkul original aur badhiya.', 5, 'positive', 'hi'],
  ['Reliable performance with clean aesthetics. Would recommend to friends.', 4, 'positive', 'en'],
];

export const demoReviews = (productId: string): Review[] => {
  const list = PRODUCT_REVIEWS[productId] || DEFAULT_REVIEWS;
  return list.map(([text, rating, sentiment, language], i) => ({
    id: `${productId}-r${i + 1}`,
    text,
    rating,
    sentiment,
    language,
    date: new Date(Date.UTC(2026, 8, 28 - i * 2)).toISOString(),
    source: 'Verified Purchase',
  }));
};

const LANG_LABEL: Record<string, string> = { en: 'English', hi: 'Hindi', ta: 'Tamil', te: 'Telugu' };

export const demoInsights = (productId: string): Insights => {
  const product = demoProducts.find((p) => p.id === productId) ?? demoProducts[0];
  const reviews = demoReviews(product.id);
  const count = (s: Sentiment) => reviews.filter((r) => r.sentiment === s).length;
  const langs = new Map<string, number>();
  reviews.forEach((r) => r.language && langs.set(r.language, (langs.get(r.language) ?? 0) + 1));

  // Product specific tailored metrics
  let ratingBreakdown: Record<string, number> = { '5': 65, '4': 20, '3': 8, '2': 3, '1': 4 };
  let topics = [
    { term: 'Quality', frequency: 18, relevance: 0.92, snippets: [reviews[0]?.text || ''] },
    { term: 'Value for money', frequency: 15, relevance: 0.88, snippets: [reviews[1]?.text || ''] },
    { term: 'Performance', frequency: 12, relevance: 0.81, snippets: [reviews[2]?.text || ''] },
    { term: 'Durability', frequency: 8, relevance: 0.72, snippets: [reviews[3]?.text || ''] },
  ];
  let themes = {
    positive: ['Quality', 'Value for money', 'Reliability'],
    negative: ['Accessories finish', 'Delivery packaging'],
  };
  let aspects = [
    { aspect: 'Build & Quality', score: 0.72, mentions: 18 },
    { aspect: 'Value for Money', score: 0.65, mentions: 15 },
    { aspect: 'Performance', score: 0.58, mentions: 12 },
    { aspect: 'Accessories', score: -0.15, mentions: 6 },
  ];

  if (productId === 'B0H2FD3L97') {
    // Exact match for Lenovo Tab screenshot: 4.4 rating, 70% 5-star, 18% 4-star, 4% 3-star, 1% 2-star, 7% 1-star
    ratingBreakdown = { '5': 70, '4': 18, '3': 4, '2': 1, '1': 7 };
    topics = [
      { term: 'Quality', frequency: 42, relevance: 0.94, snippets: [reviews[0]?.text || '', reviews[5]?.text || ''] },
      { term: 'Value for money', frequency: 38, relevance: 0.91, snippets: [reviews[0]?.text || '', reviews[1]?.text || ''] },
      { term: 'Battery life', frequency: 29, relevance: 0.85, snippets: [reviews[1]?.text || '', reviews[3]?.text || '', reviews[9]?.text || ''] },
      { term: 'Display & Screen', frequency: 26, relevance: 0.83, snippets: [reviews[2]?.text || '', reviews[8]?.text || ''] },
      { term: 'Folio Keyboard', frequency: 22, relevance: 0.79, snippets: [reviews[0]?.text || '', reviews[6]?.text || ''] },
      { term: 'Tab Pen / Stylus', frequency: 19, relevance: 0.76, snippets: [reviews[1]?.text || '', reviews[5]?.text || ''] },
    ];
    themes = {
      positive: ['Quality', 'Value for money', 'Display & Screen', 'Folio Keyboard', 'Tab Pen'],
      negative: ['Battery life drains faster with keyboard', 'Charging speed'],
    };
    aspects = [
      { aspect: 'Quality', score: 0.88, mentions: 42 },
      { aspect: 'Value for Money', score: 0.82, mentions: 38 },
      { aspect: 'Display', score: 0.79, mentions: 26 },
      { aspect: 'Keyboard & Pen', score: 0.71, mentions: 22 },
      { aspect: 'Battery Life', score: 0.18, mentions: 29 },
    ];
  } else if (productId === 'AMZN-IPHONE-15PRO') {
    ratingBreakdown = { '5': 78, '4': 14, '3': 4, '2': 2, '1': 2 };
    topics = [
      { term: 'Titanium Design', frequency: 54, relevance: 0.96, snippets: [reviews[0]?.text || ''] },
      { term: 'Camera System', frequency: 48, relevance: 0.92, snippets: [reviews[4]?.text || ''] },
      { term: 'A17 Pro Performance', frequency: 39, relevance: 0.88, snippets: [reviews[1]?.text || ''] },
      { term: 'USB-C Speed', frequency: 31, relevance: 0.82, snippets: [reviews[1]?.text || ''] },
    ];
    themes = {
      positive: ['Lightweight Titanium', '48MP Camera', 'A17 Pro Gaming', 'USB-C versatility'],
      negative: ['27W charging speed ceiling'],
    };
    aspects = [
      { aspect: 'Chassis & Build', score: 0.94, mentions: 54 },
      { aspect: 'Camera', score: 0.91, mentions: 48 },
      { aspect: 'Performance', score: 0.89, mentions: 39 },
      { aspect: 'Battery', score: 0.65, mentions: 28 },
    ];
  } else if (productId === 'AMZN-SAMSUNG-S24U') {
    ratingBreakdown = { '5': 75, '4': 17, '3': 5, '2': 2, '1': 1 };
    topics = [
      { term: 'Anti-Reflective Screen', frequency: 52, relevance: 0.95, snippets: [reviews[0]?.text || ''] },
      { term: 'Galaxy AI', frequency: 45, relevance: 0.91, snippets: [reviews[2]?.text || ''] },
      { term: 'S-Pen Writing', frequency: 38, relevance: 0.87, snippets: [reviews[1]?.text || ''] },
      { term: 'Zoom Camera', frequency: 34, relevance: 0.84, snippets: [reviews[1]?.text || ''] },
    ];
    themes = {
      positive: ['Anti-reflective glass', 'Circle to Search', 'S-Pen', 'Periscope Zoom'],
      negative: ['Chunky weight in pocket'],
    };
    aspects = [
      { aspect: 'Display', score: 0.95, mentions: 52 },
      { aspect: 'Productivity (S-Pen & AI)', score: 0.90, mentions: 45 },
      { aspect: 'Camera', score: 0.87, mentions: 34 },
      { aspect: 'Ergonomics & Weight', score: 0.35, mentions: 22 },
    ];
  }

  const basePrice = typeof product.price === 'number' && product.price > 0 ? product.price : 2499;
  const priceHistory = [
    { observedAt: '2026-08-01T00:00:00Z', price: Math.round(basePrice * 1.15) },
    { observedAt: '2026-08-20T00:00:00Z', price: Math.round(basePrice * 1.10) },
    { observedAt: '2026-09-10T00:00:00Z', price: Math.round(basePrice * 1.05) },
    { observedAt: '2026-09-28T00:00:00Z', price: Math.round(basePrice * 1.02) },
    { observedAt: '2026-10-18T00:00:00Z', price: basePrice },
  ];

  return {
    product,
    analyzedAt: new Date(Date.UTC(2026, 9, 20, 9, 30)).toISOString(),
    ratingBreakdown,
    sentiment: { positive: count('positive'), neutral: count('neutral'), negative: count('negative'), avgPolarity: 0.42 },
    topics,
    themes,
    aspects,
    readability: {
      fleschReadingEase: 72.8,
      gradeLevel: 6.4,
      distribution: [
        { label: 'Very easy', count: 5 },
        { label: 'Easy', count: 4 },
        { label: 'Fairly easy', count: 2 },
        { label: 'Standard', count: 1 },
        { label: 'Difficult', count: 0 },
      ],
      analyzed: reviews.length,
      excluded: 0,
    },
    languages: [...langs].map(([code, c]) => ({ code, label: LANG_LABEL[code] ?? code, count: c })),
    priceHistory,
  };
};
