import { describe, it, expect, vi, beforeEach } from 'vitest';
import { request, ApiError } from '@/lib/api';

describe('Phase 3e: Plain-language Error Handling for 4xx/5xx', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('surfaces backend 503 detail message in plain words when provider is disabled', async () => {
    const detailMsg = "Product 'B08XYZ' is not in database and provider is not configured: Amazon provider is disabled.";
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 503,
      headers: new Headers({ 'X-Request-ID': 'req-test-503' }),
      json: async () => ({ detail: detailMsg }),
    } as any);

    await expect(request('/api/v1/harvester/analyze-url', { method: 'POST' })).rejects.toThrow(
      detailMsg,
    );
  });

  it('surfaces FastAPI 422 array validation details in readable plain words', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 422,
      headers: new Headers({ 'X-Request-ID': 'req-test-422' }),
      json: async () => ({
        detail: [
          { loc: ['body', 'url'], msg: 'Invalid Amazon.in URL format.' },
        ],
      }),
    } as any);

    try {
      await request('/api/v1/harvester/analyze-url', { method: 'POST' });
      expect.fail('Should have thrown ApiError');
    } catch (e) {
      expect(e).toBeInstanceOf(ApiError);
      expect((e as ApiError).message).toBe('Invalid Amazon.in URL format.');
    }
  });
});
