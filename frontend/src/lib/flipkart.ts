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
  if (host !== 'flipkart.com' && host !== 'dl.flipkart.com') {
    return { valid: false, error: 'Only Flipkart.com product URLs are supported.' };
  }

  const pid = url.searchParams.get('pid')?.trim().toUpperCase();
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

/** Unified product URL parser accepting either Amazon.in or Flipkart links. */
export function parseProductUrl(raw: string): UniversalUrlCheck {
  const value = raw.trim().toLowerCase();
  if (value.includes('flipkart.com')) {
    const fk = parseFlipkartUrl(raw);
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
