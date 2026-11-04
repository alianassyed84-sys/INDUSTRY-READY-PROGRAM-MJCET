import { useEffect, useState } from 'react';

interface Chapter {
  id: string;
  number: string;
  title: string;
  tagline: string;
}

const CHAPTERS: Chapter[] = [
  { id: 'chapter-hero', number: '01', title: 'The Core Pulse', tagline: 'Neural Engine' },
  { id: 'chapter-ingest', number: '02', title: 'Live Ingestion', tagline: 'Product Gateway' },
  { id: 'chapter-features', number: '03', title: 'Five Lenses', tagline: 'Multidimensional Scan' },
  { id: 'chapter-preview', number: '04', title: 'Intelligence', tagline: 'Authentic Data' },
  { id: 'chapter-journey', number: '05', title: 'Signal Odyssey', tagline: 'End-to-End Flow' },
  { id: 'chapter-trust', number: '06', title: 'Trust Shield', tagline: 'Verifiable Truth' },
];

/**
 * StoryNav:
 * Floating sci-fi narrative HUD rail that guides visitors through the ReviewPulse story.
 */
export function StoryNav() {
  const [activeChapter, setActiveChapter] = useState('chapter-hero');
  const [hoveredChapter, setHoveredChapter] = useState<string | null>(null);

  useEffect(() => {
    if (typeof window === 'undefined') return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting && entry.intersectionRatio >= 0.25) {
            setActiveChapter(entry.target.id);
          }
        });
      },
      { threshold: [0.25, 0.5, 0.75] }
    );

    CHAPTERS.forEach((ch) => {
      const el = document.getElementById(ch.id);
      if (el) observer.observe(el);
    });

    return () => observer.disconnect();
  }, []);

  const scrollTo = (id: string) => {
    const el = document.getElementById(id);
    if (!el) return;
    el.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  return (
    <nav
      aria-label="Story chapter navigation"
      className="fixed right-5 top-1/2 -translate-y-1/2 z-40 hidden xl:flex flex-col items-end gap-3.5 pointer-events-auto select-none"
    >
      <div className="flex flex-col items-center gap-3 p-2 rounded-full bg-rp-surface/75 border border-rp-border/80 backdrop-blur-md shadow-2xl">
        {CHAPTERS.map((ch) => {
          const isActive = activeChapter === ch.id;
          const isHovered = hoveredChapter === ch.id;

          return (
            <div
              key={ch.id}
              className="relative flex items-center justify-end"
              onMouseEnter={() => setHoveredChapter(ch.id)}
              onMouseLeave={() => setHoveredChapter(null)}
            >
              {/* Floating Tooltip Pill */}
              {(isHovered || isActive) && (
                <div
                  className={`absolute right-9 px-3 py-1.5 rounded-lg border whitespace-nowrap transition-all duration-300 pointer-events-none ${
                    isActive
                      ? 'bg-rp-surface/95 border-rp-primary/60 text-rp-navy shadow-lg shadow-rp-primary/20 scale-100 opacity-100'
                      : 'bg-rp-surface-soft/90 border-rp-border/70 text-rp-muted scale-95 opacity-85'
                  }`}
                >
                  <div className="flex items-center gap-2 text-xs font-mono">
                    <span className="text-rp-primary font-bold">{ch.number}</span>
                    <span className="font-semibold text-rp-navy">{ch.title}</span>
                    <span className="text-[10px] text-rp-muted">· {ch.tagline}</span>
                  </div>
                </div>
              )}

              {/* Chapter Pip Button */}
              <button
                type="button"
                onClick={() => scrollTo(ch.id)}
                aria-label={`Jump to Chapter ${ch.number}: ${ch.title}`}
                className={`relative flex items-center justify-center transition-all duration-300 rounded-full focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-rp-primary ${
                  isActive
                    ? 'w-7 h-7 bg-rp-primary/20 border-2 border-rp-primary shadow-glow scale-110'
                    : 'w-5 h-5 bg-rp-surface-soft border border-rp-border hover:border-rp-primary/60 hover:scale-105'
                }`}
              >
                <span
                  className={`rounded-full transition-all duration-300 ${
                    isActive
                      ? 'w-2.5 h-2.5 bg-rp-primary shadow-soft'
                      : 'w-1.5 h-1.5 bg-rp-muted/50 group-hover:bg-rp-primary'
                  }`}
                />
              </button>
            </div>
          );
        })}
      </div>
    </nav>
  );
}
