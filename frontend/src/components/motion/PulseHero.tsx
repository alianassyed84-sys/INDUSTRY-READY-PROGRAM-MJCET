import { useEffect, useId, useLayoutEffect, useRef, useState, type CSSProperties } from 'react';
import { useMotion } from '@/hooks/useMotion';
import { gsap, ScrollTrigger } from '@/lib/motion';
import './pulse-hero.css';

// Deterministic particles keep the scene stable across renders and StrictMode mounts.
const STARS = Array.from({ length: 64 }, (_, i) => ({
  x: (i * 137.508 + 17) % 800,
  y: (i * 89.31 + 29) % 640,
  r: i % 11 === 0 ? 2.2 : i % 3 === 0 ? 1.3 : .7,
}));
const SIGNALS = [
  { panel: 'review', path: 'M350 300 C292 270 300 185 220 185' },
  { panel: 'context', path: 'M350 340 C290 347 265 354 184 354' },
  { panel: 'trend', path: 'M357 370 C300 395 308 460 258 485' },
  { panel: 'sentiment', path: 'M454 291 C510 252 500 174 564 161' },
  { panel: 'health', path: 'M459 326 C504 326 550 326 614 326' },
  { panel: 'topics', path: 'M452 367 C514 398 509 471 578 489' },
];
const PANEL_SEQUENCE = [
  { panel: 'review', at: 1.05 },
  { panel: 'sentiment', at: 1.19 },
  { panel: 'context', at: 1.31 },
  { panel: 'health', at: 1.43 },
  { panel: 'trend', at: 1.55 },
  { panel: 'topics', at: 1.67 },
] as const;
const STAR = 'M0 -7 2 -2 7 -2 3 1 4 6 0 3 -4 6 -3 1 -7 -2 -2 -2Z';

/** Reference-inspired illustration. Every chart and review here is decorative, not live data. */
export default function PulseHero() {
  const id = useId().replace(/:/g, '');
  const root = useRef<HTMLDivElement>(null);
  const trigger = useRef<ScrollTrigger | null>(null);
  const { enabled, systemReduced } = useMotion();
  const [visible, setVisible] = useState(true);
  const [pageVisible, setPageVisible] = useState(!document.hidden);
  const active = enabled && visible && pageVisible;
  const paint = (name: string) => `url(#${id}-${name})`;

  useEffect(() => {
    const node = root.current;
    if (!node) return;
    const observer = new IntersectionObserver(([entry]) => setVisible(entry.isIntersecting), { threshold: .05 });
    observer.observe(node);
    const update = () => setPageVisible(!document.hidden);
    document.addEventListener('visibilitychange', update);
    return () => { observer.disconnect(); document.removeEventListener('visibilitychange', update); };
  }, []);

  useLayoutEffect(() => {
    const node = root.current;
    if (!node) return;
    const ctx = gsap.context(() => {
      if (systemReduced) {
        gsap.set('[data-heartbeat]', { strokeDasharray: 1, strokeDashoffset: 0 });
        gsap.set('[data-core], [data-heartlight], [data-aura], [data-bag], [data-signal], [data-panel], [data-scene-copy]', {
          autoAlpha: 1,
          clearProps: 'filter,transform',
        });
        return;
      }

      node.dataset.scrollReady = 'true';
      const isSmallScreen = () => window.matchMedia('(max-width: 639px)').matches;

      // Initial visual setup for rapid orchestral entrance
      gsap.set('[data-heartbeat]', { strokeDasharray: 1, strokeDashoffset: 0, autoAlpha: 0.88 });
      gsap.set('[data-heartlight]', { autoAlpha: 0.35 });
      gsap.set('[data-aura]', { autoAlpha: 0.9 });
      gsap.set('[data-bag]', { autoAlpha: 1 });
      gsap.set('[data-scene-copy]', { autoAlpha: 1, attr: { transform: 'translate(0 0)' } });
      gsap.set('[data-signal]', { autoAlpha: 0 });
      gsap.set('[data-signal-path]', { strokeDasharray: 1, strokeDashoffset: 1 });
      gsap.set('[data-panel]', {
        autoAlpha: 0,
        y: isSmallScreen() ? 8 : 16,
        scale: 0.92,
        filter: 'blur(3px)',
        transformOrigin: 'center center',
      });

      // Orchestrated intro choreography: plays immediately on page arrival
      const intro = gsap.timeline({ defaults: { ease: 'power3.out' } });
      intro
        .to('[data-heartbeat]', { autoAlpha: 1, duration: 0.4 }, 0)
        .to('[data-heartlight]', { autoAlpha: 0.6, duration: 0.4 }, 0.1)
        .to('[data-aura]', { autoAlpha: 1, duration: 0.6 }, 0.1)
        .fromTo(
          '[data-core]',
          { attr: { transform: `translate(400 325) scale(${isSmallScreen() ? 1.25 : 1.15}) translate(-400 -325)` } },
          { attr: { transform: 'translate(400 325) scale(1) translate(-400 -325)' }, duration: 0.75, ease: 'back.out(1.3)' },
          0.1
        );

      PANEL_SEQUENCE.forEach(({ panel }, idx) => {
        const at = 0.22 + idx * 0.09;
        intro
          .to(`[data-signal="${panel}"]`, { autoAlpha: 0.85, duration: 0.18 }, at)
          .to(`[data-signal-path="${panel}"]`, { strokeDashoffset: 0, duration: 0.45, ease: 'power2.out' }, at)
          .to(
            `[data-panel="${panel}"]`,
            {
              autoAlpha: 1,
              y: 0,
              scale: 1,
              filter: 'blur(0px)',
              duration: 0.5,
              ease: 'back.out(1.25)',
            },
            at + 0.05
          );
      });

      // Smooth scroll parallax exit into Chapter 2 (unpinned, responsive)
      const hero = node.closest<HTMLElement>('.rp-cinematic-hero');
      if (hero) {
        trigger.current = ScrollTrigger.create({
          trigger: hero,
          start: 'top top',
          end: 'bottom top',
          scrub: 0.5,
          onUpdate: (self) => {
            if (node) {
              const p = self.progress;
              gsap.set(node, {
                y: p * 50,
                opacity: 1 - p * 0.35,
                scale: 1 - p * 0.06,
              });
            }
          },
        });
      }
    }, node);

    return () => {
      trigger.current?.kill(true);
      trigger.current = null;
      ctx.revert();
      delete node.dataset.scrollReady;
    };
  }, [systemReduced]);

  useLayoutEffect(() => {
    const scrollTrigger = trigger.current;
    if (!scrollTrigger) return;
    if (enabled && pageVisible) {
      scrollTrigger.enable();
      scrollTrigger.update();
      scrollTrigger.getTween()?.resume();
    } else {
      scrollTrigger.disable(false);
    }
  }, [enabled, pageVisible, systemReduced]);

  useEffect(() => {
    if (!active && root.current) {
      root.current.style.setProperty('--scene-x', '0deg');
      root.current.style.setProperty('--scene-y', '0deg');
    }
  }, [active]);

  useEffect(() => {
    const scene = root.current;
    const hitArea = scene?.closest<HTMLElement>('.rp-cinematic-hero');
    if (!scene || !hitArea || !active || window.matchMedia('(max-width: 639px)').matches) return;

    const move = (event: globalThis.PointerEvent) => {
      if (event.pointerType !== 'mouse') return;
      const box = hitArea.getBoundingClientRect();
      const x = Math.max(-.5, Math.min(.5, (event.clientX - box.left) / box.width - .5));
      const y = Math.max(-.5, Math.min(.5, (event.clientY - box.top) / box.height - .5));
      scene.style.setProperty('--scene-x', `${x * 6.5}deg`);
      scene.style.setProperty('--scene-y', `${-y * 5.2}deg`);
    };
    const reset = () => {
      scene.style.setProperty('--scene-x', '0deg');
      scene.style.setProperty('--scene-y', '0deg');
    };

    hitArea.addEventListener('pointermove', move);
    hitArea.addEventListener('pointerleave', reset);
    return () => {
      hitArea.removeEventListener('pointermove', move);
      hitArea.removeEventListener('pointerleave', reset);
    };
  }, [active]);

  return (
    <figure className="pulse-figure" aria-label="Illustration of product reviews connecting to sentiment, price, and review health insights">
      <div ref={root} className="pulse-scene" data-active={active}>
        <svg viewBox="0 0 800 640" className="pulse-art" aria-hidden="true" focusable="false">
          <defs>
            <radialGradient id={`${id}-aura`}><stop stopColor="#9d3bff" stopOpacity=".42" /><stop offset=".55" stopColor="#7922d8" stopOpacity=".12" /><stop offset="1" stopColor="#7922d8" stopOpacity="0" /></radialGradient>
            <linearGradient id={`${id}-panel`} x2=".8" y2="1"><stop stopColor="#39254f" stopOpacity=".94" /><stop offset="1" stopColor="#171020" stopOpacity=".97" /></linearGradient>
            <linearGradient id={`${id}-edge`} x2="1" y2="1"><stop stopColor="#d1a3ff" stopOpacity=".7" /><stop offset=".45" stopColor="#a16add" stopOpacity=".22" /><stop offset="1" stopColor="#d1a3ff" stopOpacity=".4" /></linearGradient>
            <linearGradient id={`${id}-bag`} x1="0" y1="0" x2="1" y2="1"><stop stopColor="#a775e4" stopOpacity=".7" /><stop offset=".45" stopColor="#493065" /><stop offset="1" stopColor="#221230" /></linearGradient>
            <linearGradient id={`${id}-handle`} x2="1" y2=".5"><stop stopColor="#602b99" /><stop offset=".4" stopColor="#d4a9ff" /><stop offset=".7" stopColor="#8651bd" /><stop offset="1" stopColor="#482266" /></linearGradient>
            <linearGradient id={`${id}-pulse`}><stop stopColor="#b36aff" /><stop offset=".5" stopColor="#f4bcff" /><stop offset="1" stopColor="#c667ff" /></linearGradient>
            <linearGradient id={`${id}-chart`} x1="0" y1="0" x2="0" y2="1"><stop stopColor="#ba57ff" stopOpacity=".45" /><stop offset="1" stopColor="#ba57ff" stopOpacity="0" /></linearGradient>
            <linearGradient id={`${id}-gauge`}><stop stopColor="#a35aff" /><stop offset=".55" stopColor="#ee6aea" /><stop offset="1" stopColor="#a5a5ff" /></linearGradient>
            <filter id={`${id}-glow`} x="-50%" y="-100%" width="200%" height="300%"><feGaussianBlur stdDeviation="4" /><feMerge><feMergeNode /><feMergeNode in="SourceGraphic" /></feMerge></filter>
            <filter id={`${id}-soft-glow`} x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="10" /></filter>
          </defs>

          <g className="pulse-stars">
            {STARS.map((star, i) => <circle key={i} cx={star.x} cy={star.y} r={star.r} fill={i % 5 === 0 ? '#ead7ff' : '#b684f3'} className="pulse-star" style={{ '--i': i, opacity: .2 + (i % 5) * .12 } as CSSProperties} />)}
          </g>

          {SIGNALS.map(({ panel, path }, i) => <g data-signal={panel} key={panel}>
            <path d={path} fill="none" stroke="#a769e0" strokeWidth="1" strokeOpacity=".35" />
            <path data-signal-path={panel} d={path} pathLength="1" fill="none" stroke={i === 3 ? '#55e3c8' : '#d6a0ff'} strokeWidth="1.8" strokeLinecap="round" filter={paint('glow')} className="pulse-signal" style={{ '--i': i } as CSSProperties} />
          </g>)}

          <g data-core>
          <g className="pulse-bag-float">
            <g data-aura>
              <circle cx="400" cy="325" r="220" fill={paint('aura')} />
              <circle className="pulse-ring pulse-ring-one" cx="400" cy="325" r="138" fill="none" stroke="#bd80ff" strokeOpacity=".3" strokeWidth=".8" />
              <circle className="pulse-ring pulse-ring-two" cx="400" cy="325" r="156" fill="none" stroke="#b68bdf" strokeOpacity=".18" strokeWidth=".7" />
              <g className="pulse-orbit">
                <circle cx="400" cy="169" r="3" fill="#e1bdff" filter={paint('glow')} />
                <circle cx="400" cy="481" r="2" fill="#62dec9" />
              </g>
            </g>
            <g data-bag>
              <ellipse cx="402" cy="438" rx="82" ry="12" fill="#b25bff" opacity=".25" filter={paint('soft-glow')} />
              <path d="M330 264 466 258 485 420 Q486 437 468 441 L326 433 Q313 431 315 416Z" fill="#311542" stroke={paint('edge')} strokeWidth="2" />
              <path d="m466 258 12 11 9 147q1 18-19 25l-8-18Z" fill="#8a51ba" opacity=".55" />
              <path d="M331 265 459 268 472 420 Q473 429 461 431 L329 425 Q321 425 323 412Z" fill={paint('bag')} stroke={paint('edge')} strokeWidth="2" />
              <path d="M333 271 455 274 459 338 326 381Z" fill="#dcc1ff" opacity=".08" />
              <path d="M360 278v-34c0-58 76-58 76 0v34" fill="none" stroke="#391d53" strokeWidth="16" strokeLinecap="round" />
              <path d="M358 274v-34c0-55 76-55 76 0v34" fill="none" stroke={paint('handle')} strokeWidth="11" strokeLinecap="round" />
              <path d="M358 249v-10c0-49 76-49 76 0" fill="none" stroke="#deb6ff" strokeOpacity=".65" strokeWidth="2" />
              {[358, 434].map(x => <g key={x}><ellipse cx={x} cy="279" rx="10" ry="7" fill="#251132" stroke="#b987e8" strokeWidth="2" /><path d={`M${x} 268v10`} stroke="#b991de" strokeWidth="6" strokeLinecap="round" /></g>)}
            </g>
            <path data-heartbeat className="pulse-heartbeat" pathLength="1" d="M321 354h35l11-27 17 58 18-89 17 71 13-35 12 22h31" fill="none" stroke={paint('pulse')} strokeWidth="4" strokeLinejoin="round" strokeLinecap="round" filter={paint('glow')} />
            <path data-heartlight className="pulse-heartlight" d="M321 354h35l11-27 17 58 18-89 17 71 13-35 12 22h31" fill="none" stroke="#edabff" strokeWidth="9" opacity=".3" filter={paint('soft-glow')} />
            <path className="pulse-heart-runner" pathLength="1" d="M321 354h35l11-27 17 58 18-89 17 71 13-35 12 22h31" fill="none" stroke="#fff4ff" strokeWidth="2.4" strokeLinejoin="round" strokeLinecap="round" filter={paint('glow')} />
          </g>
          </g>

          <g data-panel="review" className="pulse-panel" style={{ '--i': 0 } as CSSProperties}>
            <g transform="translate(56 109) rotate(-7 92 60)">
              <rect width="198" height="129" rx="13" fill={paint('panel')} stroke={paint('edge')} />
              <circle cx="27" cy="30" r="13" fill="#70489b" /><circle cx="27" cy="27" r="4" fill="#dfc8fa" /><path d="M20 37q7-12 14 0" fill="#dfc8fa" />
              <text x="49" y="29" className="pulse-label">Customer review</text>
              <text x="19" y="61" className="pulse-copy">“Exactly what I needed.”</text>
              <path d="M19 76h117m-117 9h83" stroke="#89719e" strokeWidth="3" strokeLinecap="round" opacity=".45" />
              {[0,1,2,3,4].map(i=><path key={i} d={STAR} transform={`translate(${29+i*26} 108)`} fill="#f0c56a" />)}
            </g>
          </g>
          <g data-panel="context" className="pulse-panel pulse-panel-secondary" style={{ '--i': 1 } as CSSProperties}>
            <g transform="translate(35 303) rotate(5 80 43)">
              <rect width="158" height="88" rx="12" fill={paint('panel')} stroke={paint('edge')} />
              <text x="16" y="27" className="pulse-label">Every voice matters</text>
              <path d="M17 43h116m-116 11h94" stroke="#a48abb" strokeWidth="4" strokeLinecap="round" opacity=".4" />
              <circle cx="22" cy="72" r="3" fill="#46ddbd" /><text x="32" y="76" className="pulse-small">Reviews connected</text>
            </g>
          </g>
          <g data-panel="trend" className="pulse-panel" style={{ '--i': 2 } as CSSProperties}>
            <g transform="translate(82 459) rotate(-6 111 63)">
              <rect width="222" height="130" rx="13" fill={paint('panel')} stroke={paint('edge')} />
              <text x="17" y="26" className="pulse-label">Signals over time</text>
              {[50,76,102].map(y=><path key={y} d={`M19 ${y}h184`} stroke="#c99bea" strokeOpacity=".12" />)}
              <path d="M20 109 50 85 80 92 115 58 149 73 201 40V113H20Z" fill={paint('chart')} />
              <path className="pulse-chart-line" d="M20 109 50 85 80 92 115 58 149 73 201 40" fill="none" stroke="#ce91ff" strokeWidth="2.5" strokeLinecap="round" />
              {[[20,109],[50,85],[80,92],[115,58],[149,73],[201,40]].map(([x,y])=><circle key={x} cx={x} cy={y} r="3" fill="#ebd7ff" stroke="#b96cff" strokeWidth="2" />)}
            </g>
          </g>
          <g data-panel="sentiment" className="pulse-panel" style={{ '--i': 3 } as CSSProperties}>
            <g transform="translate(532 99) rotate(7 100 55)">
              <rect width="206" height="111" rx="13" fill={paint('panel')} stroke={paint('edge')} />
              <circle cx="37" cy="45" r="21" fill="#46ddbd" fillOpacity=".15" />
              <path d="m28 45 7 7 12-15" fill="none" stroke="#61edd0" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
              <text x="70" y="34" className="pulse-label">Sentiment</text>
              <rect x="70" y="45" width="111" height="5" rx="2.5" fill="#5b4376" />
              <rect x="70" y="45" width="87" height="5" rx="2.5" fill="#46ddbd" />
              <rect x="70" y="57" width="68" height="5" rx="2.5" fill="#bb85f6" />
              <text x="19" y="91" className="pulse-copy">Understand the feeling.</text>
            </g>
          </g>
          <g data-panel="health" className="pulse-panel" style={{ '--i': 4 } as CSSProperties}>
            <g transform="translate(567 267) rotate(5 101 80)">
              <rect width="203" height="159" rx="14" fill={paint('panel')} stroke={paint('edge')} />
              <path d="M29 102a72 72 0 0 1 144 0" fill="none" stroke="#49365c" strokeWidth="13" strokeLinecap="round" />
              <path d="M29 102a72 72 0 0 1 132-39" fill="none" stroke={paint('gauge')} strokeWidth="13" strokeLinecap="round" />
              <path className="pulse-needle" d="m101 102 57-35" stroke="#efdbff" strokeWidth="2.5" strokeLinecap="round" />
              <circle cx="101" cy="102" r="4" fill="#f3dfff" />
              <text x="101" y="133" textAnchor="middle" className="pulse-label">Customer satisfaction</text>
            </g>
          </g>
          <g data-panel="topics" className="pulse-panel pulse-panel-secondary" style={{ '--i': 5 } as CSSProperties}>
            <g transform="translate(514 477) rotate(6 112 48)">
              <rect width="223" height="99" rx="12" fill={paint('panel')} stroke={paint('edge')} />
              <text x="17" y="28" className="pulse-label">The themes that connect</text>
              <rect x="16" y="43" width="85" height="25" rx="12.5" fill="#543374" /><text x="29" y="60" className="pulse-small">Build quality</text>
              <rect x="109" y="43" width="96" height="25" rx="12.5" fill="#21433f" /><text x="122" y="60" className="pulse-small" fill="#71e9cd">Battery life</text>
              <path d="M20 83h134" stroke="#9a7ab7" strokeWidth="3" strokeLinecap="round" opacity=".3" />
            </g>
          </g>
          <g data-panel="sentiment" className="pulse-chat" transform="translate(501 400)">
            <path d="M0 8q0-8 8-8h30q8 0 8 8v19q0 8-8 8h-8l-7 9v-9H8q-8 0-8-8Z" fill="#31bca4" />
            {[12,23,34].map(x=><circle key={x} cx={x} cy="17" r="2.4" fill="#eafffa" />)}
          </g>
          <g data-scene-copy>
            <text x="400" y="494" textAnchor="middle" className="pulse-wordmark">Review<tspan fill="#bd85ff">Pulse</tspan></text>
            <text x="400" y="516" textAnchor="middle" className="pulse-small" letterSpacing="2">EVERY REVIEW. A SIGNAL.</text>
          </g>
        </svg>
      </div>
    </figure>
  );
}
