import { parseAmazonUrl } from './amazon';

export interface FlipkartUrlCheck {
  valid: boolean;
  pid?: string;
  marketplace?: string;
  titleHint?: string;
  error?: string;
}

export interface UniversalUrlCheck {
  valid: boolean;
  marketplace: 'Amazon.in' | 'Flipkart' | 'Unknown';
  id?: string;
  title?: string;
  error?: string;
}

const PID_REGEX = /^[A-Za-z0-9_]{6,32}$/;

/** Client-side Flipkart URL validation and PID extraction. */
export function parseFlipkartUrl(raw: string): FlipkartUrlCheck {
  const value = raw.trim();
  if (!value) return { valid: false, error: 'Paste a Flipkart product URL.' };

  let url: URL;
  try {
    url = new URL(/^https?:\/\//i.test(value) ? value : `https://${value}`);
  } catch {
    return { valid: false, error: 'That does not look like a valid URL.' };
  }

  const host = url.hostname.toLowerCase().replace(/^www\./, '');
  if (host !== 'flipkart.com' && host !== 'dl.flipkart.com' && host !== 'm.flipkart.com') {
    return { valid: false, error: 'Only Flipkart.com product URLs are supported.' };
  }

  const pid = (url.searchParams.get('pid') || url.searchParams.get('PID'))?.trim().toUpperCase();
  if (!pid) {
    return {
      valid: false,
      error: "Missing 'pid' parameter in URL. Copy a full link with '?pid=...'",
    };
  }

  if (!PID_REGEX.test(pid)) {
    return {
      valid: false,
      error: `"${pid}" is not a valid 6-32 character alphanumeric Flipkart PID.`,
    };
  }

  // Extract clean title hint from slug if possible
  const segments = url.pathname.split('/').filter(Boolean);
  let titleHint: string | undefined;
  if (segments.length > 0) {
    const slug = segments[0] === 'product-reviews' && segments[1] ? segments[1] : segments[0];
    if (slug && slug !== 'p' && slug !== 'dl') {
      titleHint = slug
        .split(/[-_]+/)
        .filter(Boolean)
        .map((w) => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase())
        .join(' ');
    }
  }

  return {
    valid: true,
    pid,
    marketplace: 'Flipkart',
    titleHint,
  };
}

/** Normalize Flipkart URLs by recovering PID from /p/itm... path when missing in query parameters. */
export function normalizeFlipkartUrl(raw: string): string {
  let val = raw.trim();
  if (!val) return val;
  if (!val.toLowerCase().includes('flipkart.com')) return val;
  if (!/^[a-zA-Z][a-zA-Z0-9+.-]*:\/\//.test(val)) {
    val = `https://${val}`;
  }
  if (!/[?&]pid=/i.test(val)) {
    const itmMatch = val.match(/\/p\/([a-zA-Z0-9_]{6,32})/i);
    if (itmMatch) {
      const sep = val.includes('?') ? '&' : '?';
      val = `${val}${sep}pid=${itmMatch[1].toUpperCase()}`;
    }
  }
  return val;
}

/** Unified product URL parser accepting either Amazon.in or Flipkart links. */
export function parseProductUrl(raw: string): UniversalUrlCheck {
  const value = raw.trim().toLowerCase();
  if (value.includes('flipkart.com')) {
    const normalized = normalizeFlipkartUrl(raw);
    const fk = parseFlipkartUrl(normalized);
    return {
      valid: fk.valid,
      marketplace: 'Flipkart',
      id: fk.pid,
      title: fk.titleHint,
      error: fk.error,
    };
  }

  const az = parseAmazonUrl(raw);
  return {
    valid: az.valid,
    marketplace: az.valid ? 'Amazon.in' : 'Unknown',
    id: az.asin,
    error: az.error,
  };
}

/**
 * Resolves high-fidelity studio product photography matching the product title/id.
 * Prevents broken images, 404s, or mismatched electric kettle fallbacks.
 */
export function resolveStudioImage(title?: string, id?: string, currentSrc?: string): string {
  const t = (title || '').toLowerCase();
  const i = (id || '').toUpperCase();
  const c = (currentSrc || '').toLowerCase();

  // 1. If an authentic live website image exists (from Flipkart CDN or Amazon CDN), PRESERVE IT!
  if (
    currentSrc &&
    !c.includes('amzn-kag-001') &&
    !c.includes('undefined') &&
    (c.startsWith('https://') || c.startsWith('http://') || c.startsWith('/products/'))
  ) {
    return currentSrc;
  }

  // 2. Exact smartphone / device mappings for fallback
  if (t.includes('motorola') || t.includes('edge 50') || t.includes('edge-50') || i === 'MOBGTAGPNRQA7CS3') {
    return '/products/MOBGTAGPNRQA7CS3.jpg';
  }
  if (t.includes('iphone') || t.includes('apple') || i.includes('IPHONE')) {
    return '/products/AMZN-IPHONE-15PRO.jpg';
  }
  if (t.includes('s24') || t.includes('galaxy s24') || i === 'MOBGTAGPTB3VS24W' || i.includes('S24')) {
    return '/products/MOBGTAGPTB3VS24W.jpg';
  }
  if (t.includes('nothing') || t.includes('phone (2a)') || t.includes('phone 2a') || i === 'MOBHQC8ZMRCP62TS') {
    return '/products/MOBHQC8ZMRCP62TS.jpg';
  }
  if (t.includes('macbook') || t.includes('laptop') || t.includes('notebook')) {
    return '/products/AMZN-MACBOOK-AIR-M3.jpg';
  }
  if (t.includes('sony') || t.includes('wh1000') || t.includes('wh-1000')) {
    return '/products/AMZN-SONY-WH1000XM5.jpg';
  }
  if (t.includes('airpod')) {
    return '/products/AMZN-AIRPODS-PRO2.jpg';
  }
  if (t.includes('oneplus')) {
    return '/products/AMZN-ONEPLUS-12.jpg';
  }
  if (
    t.includes('boat') ||
    t.includes('basshead') ||
    t.includes('earphone') ||
    t.includes('headphone') ||
    t.includes('airdopes') ||
    i === 'B071Z8M4KX'
  ) {
    return '/products/B071Z8M4KX.jpg';
  }
  if (t.includes('tab') || t.includes('tablet') || t.includes('ipad') || t.includes('lenovo') || i === 'B0H2FD3L97') {
    return '/products/B0H2FD3L97.jpg';
  }
  if (t.includes('sauvage') || t.includes('dior')) {
    return '/products/AMZN-DIOR-SAUVAGE.jpg';
  }
  if (t.includes('bleu') || t.includes('chanel')) {
    return '/products/AMZN-BLEU-CHANEL.jpg';
  }
  if (t.includes('eros') || t.includes('versace')) {
    return '/products/AMZN-VERSACE-EROS.jpg';
  }
  if (t.includes('perfume') || t.includes('parfum') || t.includes('fragrance') || t.includes('cologne')) {
    return '/products/AMZN-YSL-BLACKOPIUM.jpg';
  }
  if (t.includes('kettle') || i === 'AMZN-KAG-001') {
    return '/products/AMZN-KAG-001.jpg';
  }
  if (t.includes('samsung') || t.includes('galaxy')) {
    return '/products/AMZN-SAMSUNG-S24U.jpg';
  }
  if (t.includes('phone') || t.includes('mobile') || t.includes('5g') || t.includes('smartphone')) {
    return '/products/AMZN-ONEPLUS-12.jpg';
  }

  // Safe default: high-res clean tech asset
  return '/products/AMZN-IPHONE-15PRO.jpg';
}
