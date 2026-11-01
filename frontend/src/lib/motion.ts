import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

export const MOTION = { y: 16, duration: 0.55, ease: 'power3.out', stagger: 0.07 } as const;
export const prefersReducedMotion = () =>
  typeof window !== 'undefined' && (
    window.matchMedia('(prefers-reduced-motion: reduce)').matches ||
    document.documentElement.dataset.motion === 'reduced'
  );

/** Reveal once on entry, including cards inserted after async data arrives. Content is visible without JS. */
export function pageEntrance(scope: HTMLElement, selector = '[data-reveal]') {
  if (prefersReducedMotion()) return () => undefined;
  const seen = new WeakSet<Element>();
  const ctx = gsap.context(() => {}, scope);
  const observer = new IntersectionObserver(entries => {
    const entering = entries.filter(entry => entry.isIntersecting);
    entering.forEach(({ target }, index) => {
      observer.unobserve(target);
      // Do not move an element while the user is interacting with it.
      if (target.contains(document.activeElement)) return;
      ctx.add(() => {
        gsap.fromTo(target, { opacity: .15, y: MOTION.y }, {
          opacity: 1, y: 0, duration: MOTION.duration, ease: MOTION.ease,
          delay: Math.min(index * MOTION.stagger, .21), clearProps: 'opacity,transform',
        });
      });
    });
  }, { threshold: .06 });

  const observe = () => {
    scope.querySelectorAll<HTMLElement>(selector).forEach(element => {
      if (seen.has(element)) return;
      seen.add(element);
      // A parent reveal already carries nested cards into view.
      const parent = element.parentElement?.closest(selector);
      if (parent && scope.contains(parent)) return;
      observer.observe(element);
    });
  };
  observe();
  const mutations = new MutationObserver(records => {
    if (records.some(record => record.addedNodes.length > 0)) observe();
  });
  mutations.observe(scope, { childList: true, subtree: true });
  const onFocus = (event: FocusEvent) => {
    const target = (event.target as HTMLElement).closest(selector);
    if (target && scope.contains(target)) {
      observer.unobserve(target);
      gsap.killTweensOf(target);
      gsap.set(target, { clearProps: 'opacity,transform' });
    }
  };
  scope.addEventListener('focusin', onFocus);
  return () => {
    observer.disconnect(); mutations.disconnect();
    scope.removeEventListener('focusin', onFocus);
    ctx.revert();
  };
}

export const scrollReveal = (scope: HTMLElement) => pageEntrance(scope, '[data-scroll]');
export { gsap, ScrollTrigger };
