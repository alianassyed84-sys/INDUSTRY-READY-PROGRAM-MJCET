import '@testing-library/jest-dom/vitest';

// jsdom lacks these browser APIs; GSAP and charts touch them at import time.
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: (query: string) => ({
    matches: true, // reports prefers-reduced-motion, so motion is skipped in tests
    media: query, onchange: null,
    addEventListener() {}, removeEventListener() {}, addListener() {}, removeListener() {},
    dispatchEvent: () => false,
  }),
});
class Noop { observe() {} unobserve() {} disconnect() {} takeRecords() { return []; } }
vi.stubGlobal('ResizeObserver', Noop);
vi.stubGlobal('IntersectionObserver', Noop);
HTMLDialogElement.prototype.showModal ??= function () { this.open = true; };
HTMLDialogElement.prototype.close ??= function () { this.open = false; };
window.scrollTo = vi.fn() as unknown as typeof window.scrollTo;
