import { parseAmazonUrl } from '@/lib/amazon';

describe('parseAmazonUrl', () => {
  it('accepts a full Amazon.in product URL and extracts the ASIN', () => {
    const r = parseAmazonUrl('https://www.amazon.in/Some-Product/dp/B0ABCDE123/ref=sr_1_1?x=1');
    expect(r).toMatchObject({ valid: true, asin: 'B0ABCDE123', marketplace: 'Amazon.in' });
  });
  it('rejects an incomplete /dp/ URL with no ASIN', () => {
    const r = parseAmazonUrl('https://www.amazon.in/dp/');
    expect(r.valid).toBe(false);
    expect(r.error).toMatch(/No ASIN/);
  });
  it('rejects other marketplaces', () => {
    expect(parseAmazonUrl('https://www.amazon.com/dp/B0ABCDE123').valid).toBe(false);
  });
  it('rejects malformed ASINs and empty input', () => {
    expect(parseAmazonUrl('https://amazon.in/dp/SHORT').valid).toBe(false);
    expect(parseAmazonUrl('   ').valid).toBe(false);
  });
});
