export interface UrlCheck {
  valid: boolean;
  asin?: string;
  marketplace?: string;
  error?: string;
}

const ASIN = /^[A-Z0-9]{10}$/i;

/** Client-side URL validation only. It does not prove the provider can retrieve the product. */
export function parseAmazonUrl(raw: string): UrlCheck {
  const value = raw.trim();
  if (!value) return { valid: false, error: 'Paste an Amazon.in product URL.' };
  let url: URL;
  try {
    url = new URL(/^https?:\/\//i.test(value) ? value : `https://${value}`);
  } catch {
    return { valid: false, error: 'That does not look like a valid URL.' };
  }
  const host = url.hostname.toLowerCase().replace(/^www\./, '');
  if (host !== 'amazon.in') return { valid: false, error: 'Only Amazon.in product URLs are supported.' };
  const m = url.pathname.match(/\/(?:dp|gp\/product|product-reviews)\/([^/?#]*)/i);
  if (!m || !m[1]) return { valid: false, error: 'No ASIN found. Use a full product link, not just /dp/.' };
  if (!ASIN.test(m[1])) return { valid: false, error: `"${m[1]}" is not a valid 10-character ASIN.` };
  return { valid: true, asin: m[1].toUpperCase(), marketplace: 'Amazon.in' };
}
