import { parseFlipkartUrl, parseProductUrl } from '@/lib/flipkart';

describe('parseFlipkartUrl', () => {
  it('accepts full Flipkart product URL and extracts PID and title hint', () => {
    const res = parseFlipkartUrl(
      'https://www.flipkart.com/apple-iphone-15-black-128-gb/p/itm6ac6485515ae4?pid=MOBGTAGPNRQA7CS3',
    );
    expect(res).toMatchObject({
      valid: true,
      pid: 'MOBGTAGPNRQA7CS3',
      marketplace: 'Flipkart',
      titleHint: 'Apple Iphone 15 Black 128 Gb',
    });
  });

  it('rejects Flipkart URL missing pid query parameter', () => {
    const res = parseFlipkartUrl(
      'https://www.flipkart.com/apple-iphone-15-black-128-gb/p/itm6ac6485515ae4',
    );
    expect(res.valid).toBe(false);
    expect(res.error).toMatch(/Missing 'pid'/);
  });

  it('rejects non-Flipkart domain', () => {
    const res = parseFlipkartUrl(
      'https://www.amazon.in/dp/B084J4MZK6?pid=MOBGTAGPNRQA7CS3',
    );
    expect(res.valid).toBe(false);
    expect(res.error).toMatch(/Only Flipkart.com/);
  });

  it('rejects empty input', () => {
    expect(parseFlipkartUrl('  ').valid).toBe(false);
  });
});

describe('parseProductUrl', () => {
  it('identifies Flipkart URLs', () => {
    const res = parseProductUrl(
      'https://www.flipkart.com/product/p/itm?pid=MOB1234567890ABC',
    );
    expect(res.valid).toBe(true);
    expect(res.marketplace).toBe('Flipkart');
    expect(res.id).toBe('MOB1234567890ABC');
  });

  it('identifies Amazon.in URLs', () => {
    const res = parseProductUrl(
      'https://www.amazon.in/dp/B084J4MZK6',
    );
    expect(res.valid).toBe(true);
    expect(res.marketplace).toBe('Amazon.in');
    expect(res.id).toBe('B084J4MZK6');
  });
});
