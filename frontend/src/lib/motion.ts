import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

export const MOTION = { y: 12, duration: 0.45, ease: 'power2.out', stagger: 0.08 } as const;
export const prefersReducedMotion = () =>
  typeof window !== 'undefined' && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

/** Page entrance: fades and lifts direct `[data-reveal]` children. Returns a cleanup function. */
export function pageEntrance(scope: HTMLElement, selector = '[data-reveal]') {
  if (prefersReducedMotion()) return () => undefined;
  const ctx = gsap.context(() => {
    gsap.from(selector, {
      opacity: 0,
      y: MOTION.y,
      duration: MOTION.duration,
      ease: MOTION.ease,
      stagger: MOTION.stagger,
      clearProps: 'opacity,transform',
    });
  }, scope);
  return () => ctx.revert();
}

/** Scroll-triggered reveal for landing sections. */
export function scrollReveal(scope: HTMLElement, selector = '[data-scroll]') {
  if (prefersReducedMotion()) return () => undefined;
  const ctx = gsap.context(() => {
    gsap.utils.toArray<HTMLElement>(selector).forEach((el) => {
      gsap.from(el, {
        opacity: 0,
        y: 24,
        duration: 0.55,
        ease: MOTION.ease,
        clearProps: 'opacity,transform',
        scrollTrigger: { trigger: el, start: 'top 88%', once: true },
      });
    });
  }, scope);
  return () => ctx.revert();
}

export { gsap, ScrollTrigger };
