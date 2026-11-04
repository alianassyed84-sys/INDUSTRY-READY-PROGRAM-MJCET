import { useEffect } from 'react';
import Lenis from 'lenis';
import { gsap, ScrollTrigger } from '@/lib/motion';

export function useLenis(enabled: boolean) {
  useEffect(() => {
    // Only initialize smooth scroll in browser with motion enabled and non-reduced-motion
    if (
      !enabled ||
      typeof window === 'undefined' ||
      !window.requestAnimationFrame ||
      window.matchMedia('(prefers-reduced-motion: reduce)').matches
    ) {
      return;
    }

    let lenis: Lenis | null = null;
    let rafId: number | null = null;

    try {
      lenis = new Lenis({
        duration: 1.15,
        easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
        orientation: 'vertical',
        smoothWheel: true,
        wheelMultiplier: 0.9,
      });

      // Synchronize with GSAP ScrollTrigger
      lenis.on('scroll', ScrollTrigger.update);

      const updateTicker = (time: number) => {
        lenis?.raf(time * 1000);
      };

      gsap.ticker.add(updateTicker);
      gsap.ticker.lagSmoothing(0);

      return () => {
        gsap.ticker.remove(updateTicker);
        if (rafId !== null) cancelAnimationFrame(rafId);
        lenis?.destroy();
      };
    } catch {
      // Fallback gracefully if smooth scrolling context is unsupported
      return;
    }
  }, [enabled]);
}
