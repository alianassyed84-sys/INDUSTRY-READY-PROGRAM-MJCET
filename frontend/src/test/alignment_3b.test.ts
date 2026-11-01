import { describe, it, expect, vi, beforeEach } from 'vitest';
import { withDemoFallback, ApiError } from '@/lib/api';

describe('Phase 3b: Demo fallback behavior', () => {
  beforeEach(() => {
    vi.unstubAllEnvs();
  });

  it('rejects with plain error when backend unreachable and VITE_ENABLE_DEMO is false/unset', async () => {
    vi.stubEnv('VITE_ENABLE_DEMO', '');

    const liveReject = () => Promise.reject(new ApiError('Backend unreachable'));
    const demoFn = () => ({ id: 'demo' });

    await expect(withDemoFallback(liveReject, demoFn)).rejects.toThrow(
      /backend.*unreachable.*try again/i,
    );
  });

  it('falls back to demo fixtures ONLY when VITE_ENABLE_DEMO is explicitly "true"', async () => {
    vi.stubEnv('VITE_ENABLE_DEMO', 'true');

    const liveReject = () => Promise.reject(new ApiError('Backend unreachable'));
    const demoFn = () => ({ id: 'demo-data' });

    const result = await withDemoFallback(liveReject, demoFn);
    expect(result.source).toBe('demo');
    expect(result.data).toEqual({ id: 'demo-data' });
  });
});
