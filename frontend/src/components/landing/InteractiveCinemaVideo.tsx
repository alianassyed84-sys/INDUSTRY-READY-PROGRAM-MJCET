import { useEffect, useRef, useState } from 'react';
import {
  Play,
  Pause,
  RotateCcw,
  Sparkles,
  Link2,
  TrendingUp,
  CheckCircle2,
  Cpu,
  Layers,
  ShieldCheck,
  Volume2,
  VolumeX,
} from 'lucide-react';
import { useMotion } from '@/hooks/useMotion';

interface Chapter {
  id: number;
  title: string;
  tag: string;
  duration: number; // in seconds
  themeColor: string;
  glowColor: string;
}

const CHAPTERS: Chapter[] = [
  {
    id: 1,
    title: 'Live Link Ingestion & Anti-Redirect Guard',
    tag: 'Harvester Core',
    duration: 6,
    themeColor: '#3b82f6',
    glowColor: 'rgba(59, 130, 246, 0.25)',
  },
  {
    id: 2,
    title: 'Neural Customer Sentiment & Feature Scan',
    tag: 'NLP Analytics',
    duration: 6,
    themeColor: '#10b981',
    glowColor: 'rgba(16, 185, 129, 0.25)',
  },
  {
    id: 3,
    title: 'Linguistic Topic Matrix & Readability',
    tag: 'TF-IDF Clusters',
    duration: 6,
    themeColor: '#8b5cf6',
    glowColor: 'rgba(139, 92, 246, 0.25)',
  },
  {
    id: 4,
    title: 'Historical Price Radar & Deal Detection',
    tag: 'Price Timeline',
    duration: 6,
    themeColor: '#f59e0b',
    glowColor: 'rgba(245, 158, 11, 0.25)',
  },
];

const TOTAL_DURATION = CHAPTERS.reduce((acc, c) => acc + c.duration, 0);

export default function InteractiveCinemaVideo() {
  const { enabled } = useMotion();
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  const [isPlaying, setIsPlaying] = useState<boolean>(true);
  const [currentTime, setCurrentTime] = useState<number>(0);
  const [speed, setSpeed] = useState<number>(1);
  const [isMuted, setIsMuted] = useState<boolean>(true);
  const [activeChapterIndex, setActiveChapterIndex] = useState<number>(0);

  const activeChapter = CHAPTERS[activeChapterIndex] || CHAPTERS[0];

  // Helper: jump to specific chapter
  const seekToChapter = (index: number) => {
    let start = 0;
    for (let i = 0; i < index; i++) {
      start += CHAPTERS[i].duration;
    }
    setCurrentTime(start);
    setActiveChapterIndex(index);
    setIsPlaying(true);
  };

  // Timer loop for video playback simulation
  useEffect(() => {
    if (!isPlaying) return;

    const interval = setInterval(() => {
      setCurrentTime((prev) => {
        const next = prev + 0.1 * speed;
        if (next >= TOTAL_DURATION) {
          return 0; // loop seamlessly
        }

        // Determine active chapter
        let accumulated = 0;
        for (let i = 0; i < CHAPTERS.length; i++) {
          accumulated += CHAPTERS[i].duration;
          if (next < accumulated) {
            if (activeChapterIndex !== i) {
              setActiveChapterIndex(i);
            }
            break;
          }
        }

        return next;
      });
    }, 100);

    return () => clearInterval(interval);
  }, [isPlaying, speed, activeChapterIndex]);

  // Canvas particle stream effect (60 FPS)
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animId: number;
    let width = (canvas.width = canvas.offsetWidth);
    let height = (canvas.height = canvas.offsetHeight);

    const onResize = () => {
      if (!canvas) return;
      width = canvas.width = canvas.offsetWidth;
      height = canvas.height = canvas.offsetHeight;
    };
    window.addEventListener('resize', onResize);

    // Particle nodes
    const particleCount = enabled ? 38 : 12;
    const particles = Array.from({ length: particleCount }, () => ({
      x: Math.random() * width,
      y: Math.random() * height,
      vx: (Math.random() - 0.5) * 0.8,
      vy: (Math.random() - 0.5) * 0.8,
      radius: Math.random() * 2 + 1,
    }));

    const render = () => {
      ctx.clearRect(0, 0, width, height);

      // Draw faint connections
      ctx.strokeStyle = activeChapter.themeColor + '18';
      ctx.lineWidth = 1;
      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const dx = particles[i].x - particles[j].x;
          const dy = particles[i].y - particles[j].y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < 95) {
            ctx.beginPath();
            ctx.moveTo(particles[i].x, particles[i].y);
            ctx.lineTo(particles[j].x, particles[j].y);
            ctx.stroke();
          }
        }
      }

      // Draw particle nodes
      for (const p of particles) {
        p.x += p.vx;
        p.y += p.vy;

        if (p.x < 0) p.x = width;
        if (p.x > width) p.x = 0;
        if (p.y < 0) p.y = height;
        if (p.y > height) p.y = 0;

        ctx.fillStyle = activeChapter.themeColor + '60';
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        ctx.fill();
      }

      animId = requestAnimationFrame(render);
    };

    render();

    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener('resize', onResize);
    };
  }, [activeChapter.themeColor, enabled]);

  // Current chapter progress
  let chapterStartTime = 0;
  for (let i = 0; i < activeChapterIndex; i++) {
    chapterStartTime += CHAPTERS[i].duration;
  }
  const chapterElapsed = Math.max(0, currentTime - chapterStartTime);
  const chapterProgress = Math.min(100, (chapterElapsed / activeChapter.duration) * 100);

  // Time formatter
  const formatTime = (secs: number) => {
    const m = Math.floor(secs / 60);
    const s = Math.floor(secs % 60);
    return `${m}:${s < 10 ? '0' : ''}${s}`;
  };

  return (
    <section className="relative mx-auto my-12 max-w-content px-3 sm:px-5 lg:px-8">
      {/* Dynamic Ambient Background Glow */}
      <div
        className="pointer-events-none absolute -inset-x-4 top-1/2 -z-10 h-[480px] -translate-y-1/2 rounded-[40px] opacity-40 blur-3xl transition-colors duration-1000"
        style={{ background: `radial-gradient(ellipse at center, ${activeChapter.glowColor} 0%, transparent 70%)` }}
      />

      {/* Section Header */}
      <div className="mb-6 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <div className="inline-flex items-center gap-1.5 rounded-full border border-rp-primary/30 bg-rp-primary/10 px-3 py-1 text-xs font-bold text-rp-primary">
            <Sparkles className="h-3.5 w-3.5" />
            <span>Interactive Motion Preview</span>
          </div>
          <h2 className="mt-2 font-heading text-2xl font-black text-rp-navy sm:text-3xl">
            Watch ReviewPulse in Motion
          </h2>
          <p className="mt-1 text-sm text-rp-muted">
            From raw Amazon &amp; Flipkart product links to verified consumer intelligence in real time.
          </p>
        </div>

        {/* Playback Speed & Controls */}
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => setSpeed(speed === 1 ? 1.5 : speed === 1.5 ? 2 : 1)}
            className="rounded-lg border border-rp-border bg-rp-surface px-2.5 py-1 text-xs font-bold text-rp-navy shadow-xs hover:border-rp-primary transition-all"
            title="Toggle playback speed"
          >
            {speed}x Speed
          </button>
          <button
            type="button"
            onClick={() => setIsMuted(!isMuted)}
            className="rounded-lg border border-rp-border bg-rp-surface p-1.5 text-rp-navy shadow-xs hover:border-rp-primary transition-all"
            title={isMuted ? 'Simulated audio muted' : 'Audio active'}
          >
            {isMuted ? <VolumeX className="h-4 w-4" /> : <Volume2 className="h-4 w-4 text-rp-primary" />}
          </button>
        </div>
      </div>

      {/* Cinematic Cinema Window */}
      <div className="overflow-hidden rounded-2xl border border-slate-700/80 bg-[#0B0F19] text-white shadow-2xl transition-all">
        {/* Cinema Window Top Bar */}
        <div className="flex items-center justify-between border-b border-slate-800/80 bg-slate-900/90 px-4 py-3 backdrop-blur-md">
          <div className="flex items-center gap-2">
            <span className="h-3 w-3 rounded-full bg-rose-500/80 inline-block shadow-xs" />
            <span className="h-3 w-3 rounded-full bg-amber-500/80 inline-block shadow-xs" />
            <span className="h-3 w-3 rounded-full bg-emerald-500/80 inline-block shadow-xs" />
            <span className="ml-3 font-mono text-[11px] font-bold text-slate-400">
              REVIEWPULSE INTELLIGENCE RUNTIME · 60 FPS
            </span>
          </div>

          <div className="flex items-center gap-2">
            <span
              className="inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wider"
              style={{ backgroundColor: activeChapter.themeColor + '25', color: activeChapter.themeColor }}
            >
              <span className="h-1.5 w-1.5 rounded-full animate-ping" style={{ backgroundColor: activeChapter.themeColor }} />
              {activeChapter.tag}
            </span>
          </div>
        </div>

        {/* Video Canvas Stage */}
        <div className="relative h-[380px] w-full overflow-hidden bg-gradient-to-b from-[#0F172A] to-[#0B0F19] p-6 sm:h-[420px] md:h-[460px]">
          {/* 60 FPS Background Particles */}
          <canvas ref={canvasRef} className="absolute inset-0 h-full w-full pointer-events-none" />

          {/* SCENE 1: URL INGESTION & HARVESTER */}
          {activeChapterIndex === 0 && (
            <div className="relative z-10 flex h-full flex-col justify-between transition-all duration-500">
              <div className="space-y-4">
                <div className="flex flex-wrap items-center gap-2 text-xs font-semibold text-blue-400">
                  <Link2 className="h-4 w-4" />
                  <span>STAGE 01 · LINK PARSING &amp; ANTI-REDIRECT SHIELD</span>
                </div>

                {/* Animated URL Bar */}
                <div className="flex max-w-xl items-center gap-3 rounded-xl border border-blue-500/40 bg-slate-900/90 p-3 shadow-lg backdrop-blur-md">
                  <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-600/30 text-blue-400">
                    <Link2 className="h-4 w-4" />
                  </div>
                  <div className="min-w-0 flex-1 font-mono text-xs">
                    <span className="text-emerald-400">https://www.flipkart.com/</span>
                    <span className="text-slate-300">motorola-edge-50-fusion...</span>
                    <span className="text-amber-400 font-bold">?pid=MOBGTAGPNRQA7CS3</span>
                  </div>
                  <span className="rounded bg-emerald-500/20 px-2 py-0.5 font-mono text-[10px] font-bold text-emerald-300 border border-emerald-500/40">
                    VERIFIED
                  </span>
                </div>

                {/* Product Extraction Card */}
                <div className="grid max-w-xl gap-4 sm:grid-cols-2">
                  <div className="rounded-xl border border-slate-700 bg-slate-800/80 p-3.5 shadow-md">
                    <div className="flex items-center gap-2 text-xs font-bold text-slate-300">
                      <ShieldCheck className="h-4 w-4 text-emerald-400" />
                      <span>Redirect Defense</span>
                    </div>
                    <p className="mt-1 text-xs text-slate-400">
                      <code>is_live_page_relevant()</code> blocks sponsored iPhone redirects.
                    </p>
                  </div>

                  <div className="rounded-xl border border-slate-700 bg-slate-800/80 p-3.5 shadow-md">
                    <div className="flex items-center gap-2 text-xs font-bold text-slate-300">
                      <CheckCircle2 className="h-4 w-4 text-blue-400" />
                      <span>832px Studio Photography</span>
                    </div>
                    <p className="mt-1 text-xs text-slate-400">
                      Direct high-resolution Flipkart CDN delivery with <code>no-referrer</code>.
                    </p>
                  </div>
                </div>
              </div>

              {/* Bottom Ingestion Ticker */}
              <div className="flex items-center justify-between border-t border-slate-800/80 pt-3 text-xs text-slate-400">
                <span className="flex items-center gap-1.5">
                  <Cpu className="h-3.5 w-3.5 text-blue-400" /> Canonical PID Extracted: <strong className="text-white">MOBGTAGPNRQA7CS3</strong>
                </span>
                <span className="text-emerald-400 font-bold">Status 200 OK</span>
              </div>
            </div>
          )}

          {/* SCENE 2: NEURAL SENTIMENT & ABSA SCANNER */}
          {activeChapterIndex === 1 && (
            <div className="relative z-10 flex h-full flex-col justify-between transition-all duration-500">
              <div className="space-y-4">
                <div className="flex flex-wrap items-center gap-2 text-xs font-semibold text-emerald-400">
                  <Sparkles className="h-4 w-4" />
                  <span>STAGE 02 · VADER POLARITY &amp; ASPECT-BASED SENTIMENT (ABSA)</span>
                </div>

                {/* Laser Scanning Quote Box */}
                <div className="relative max-w-xl overflow-hidden rounded-xl border border-emerald-500/40 bg-slate-900/90 p-4 shadow-lg backdrop-blur-md">
                  <div className="absolute top-0 left-0 right-0 h-0.5 bg-gradient-to-r from-transparent via-emerald-400 to-transparent animate-pulse" />
                  <p className="text-sm italic text-slate-200">
                    &ldquo;Display is vibrant with smooth 144Hz scroll, but charging brick warms slightly under heavy duty.&rdquo;
                  </p>
                  <div className="mt-2.5 flex items-center justify-between text-xs">
                    <span className="text-slate-400 font-medium">Flipkart Verified Purchaser</span>
                    <span className="font-mono font-bold text-emerald-400">+0.82 Polarity Score</span>
                  </div>
                </div>

                {/* Aspect Polarity Chips */}
                <div className="flex flex-wrap gap-2 max-w-xl">
                  <div className="flex items-center gap-1.5 rounded-lg border border-emerald-500/40 bg-emerald-500/10 px-3 py-1 text-xs font-bold text-emerald-300">
                    <CheckCircle2 className="h-3.5 w-3.5" />
                    <span>Display Quality: +94% Favorable</span>
                  </div>
                  <div className="flex items-center gap-1.5 rounded-lg border border-emerald-500/40 bg-emerald-500/10 px-3 py-1 text-xs font-bold text-emerald-300">
                    <CheckCircle2 className="h-3.5 w-3.5" />
                    <span>Battery Endurance: +88% Favorable</span>
                  </div>
                  <div className="flex items-center gap-1.5 rounded-lg border border-amber-500/40 bg-amber-500/10 px-3 py-1 text-xs font-bold text-amber-300">
                    <span>Charging Heat: ~62% Neutral</span>
                  </div>
                </div>
              </div>

              {/* Bottom Sentiment Breakdown */}
              <div className="flex items-center justify-between border-t border-slate-800/80 pt-3 text-xs text-slate-400">
                <span>Distribution: <strong className="text-emerald-400">76% Favorable</strong> · <strong className="text-amber-400">18% Neutral</strong> · <strong className="text-rose-400">6% Critical</strong></span>
                <span className="text-slate-300 font-mono">VADER Evaluator Active</span>
              </div>
            </div>
          )}

          {/* SCENE 3: TOPIC MATRIX & READABILITY */}
          {activeChapterIndex === 2 && (
            <div className="relative z-10 flex h-full flex-col justify-between transition-all duration-500">
              <div className="space-y-4">
                <div className="flex flex-wrap items-center gap-2 text-xs font-semibold text-purple-400">
                  <Layers className="h-4 w-4" />
                  <span>STAGE 03 · TF-IDF N-GRAM KEYPHRASES &amp; READABILITY COMPLIANCE</span>
                </div>

                {/* Floating Interactive Clusters */}
                <div className="grid max-w-xl gap-3 sm:grid-cols-3">
                  <div className="rounded-xl border border-purple-500/40 bg-purple-500/10 p-3 text-center">
                    <span className="text-lg font-black text-purple-300">#1 Term</span>
                    <p className="mt-1 font-bold text-sm text-white">Curved Display</p>
                    <span className="text-[10px] text-purple-400 font-semibold">142 mentions</span>
                  </div>
                  <div className="rounded-xl border border-purple-500/40 bg-purple-500/10 p-3 text-center">
                    <span className="text-lg font-black text-purple-300">#2 Term</span>
                    <p className="mt-1 font-bold text-sm text-white">Battery Backup</p>
                    <span className="text-[10px] text-purple-400 font-semibold">98 mentions</span>
                  </div>
                  <div className="rounded-xl border border-purple-500/40 bg-purple-500/10 p-3 text-center">
                    <span className="text-lg font-black text-purple-300">#3 Term</span>
                    <p className="mt-1 font-bold text-sm text-white">Turbo Charging</p>
                    <span className="text-[10px] text-purple-400 font-semibold">74 mentions</span>
                  </div>
                </div>

                {/* Readability Meter */}
                <div className="max-w-xl rounded-xl border border-slate-700 bg-slate-800/80 p-3.5">
                  <div className="flex items-center justify-between text-xs font-bold text-slate-200">
                    <span>Flesch-Kincaid Linguistic Complexity</span>
                    <span className="font-mono text-purple-400">Grade 8.2 (Natural Human Opinion)</span>
                  </div>
                  <div className="mt-2 h-2 w-full overflow-hidden rounded-full bg-slate-700">
                    <div className="h-full rounded-full bg-purple-500 transition-all duration-700" style={{ width: '68%' }} />
                  </div>
                </div>
              </div>

              {/* Bottom Topic Ticker */}
              <div className="flex items-center justify-between border-t border-slate-800/80 pt-3 text-xs text-slate-400">
                <span>N-Gram Cluster Threshold: <strong className="text-white">0.05 Minimum Significance</strong></span>
                <span className="text-purple-400 font-bold">Multilingual Filter Passed</span>
              </div>
            </div>
          )}

          {/* SCENE 4: PRICE TRACKER & DEAL RADAR */}
          {activeChapterIndex === 3 && (
            <div className="relative z-10 flex h-full flex-col justify-between transition-all duration-500">
              <div className="space-y-4">
                <div className="flex flex-wrap items-center gap-2 text-xs font-semibold text-amber-400">
                  <TrendingUp className="h-4 w-4" />
                  <span>STAGE 04 · HISTORICAL OBSERVATIONS &amp; DEAL OPPORTUNITY RADAR</span>
                </div>

                {/* Price Stat Headline */}
                <div className="grid max-w-xl grid-cols-2 gap-4">
                  <div className="rounded-xl border border-amber-500/40 bg-amber-500/10 p-4">
                    <span className="text-xs font-semibold text-amber-300">Live Selling Price</span>
                    <div className="mt-1 flex items-baseline gap-2">
                      <span className="text-2xl font-black text-white">₹22,999</span>
                      <span className="text-xs text-slate-400 line-through">₹25,999</span>
                    </div>
                    <span className="mt-1 inline-block rounded bg-amber-500/20 px-2 py-0.5 text-[11px] font-bold text-amber-300">
                      12% Discount Active
                    </span>
                  </div>

                  <div className="rounded-xl border border-slate-700 bg-slate-800/80 p-4">
                    <span className="text-xs font-semibold text-slate-400">Lowest Recorded</span>
                    <div className="mt-1 text-2xl font-black text-emerald-400">₹21,499</div>
                    <span className="mt-1 inline-block text-[11px] text-slate-400">
                      Observed during Festival Deal
                    </span>
                  </div>
                </div>

                {/* Animated Line Illustration */}
                <div className="max-w-xl rounded-xl border border-slate-700 bg-slate-900/80 p-3">
                  <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
                    <span>90-Day Trend Observation</span>
                    <span className="font-mono text-emerald-400">Near 3-Month Low</span>
                  </div>
                  <div className="flex h-12 items-end gap-1.5 pt-2">
                    {[45, 52, 48, 60, 58, 40, 36, 42, 38, 30].map((h, i) => (
                      <div
                        key={i}
                        className={`flex-1 rounded-t transition-all duration-500 ${
                          i === 9 ? 'bg-amber-400' : 'bg-slate-700 hover:bg-slate-600'
                        }`}
                        style={{ height: `${h}%` }}
                      />
                    ))}
                  </div>
                </div>
              </div>

              {/* Bottom Price Ticker */}
              <div className="flex items-center justify-between border-t border-slate-800/80 pt-3 text-xs text-slate-400">
                <span>Database Table: <strong className="text-white">PriceSnapshot Entity</strong></span>
                <span className="text-amber-400 font-bold">Historical Peak Evaluated</span>
              </div>
            </div>
          )}
        </div>

        {/* Video Scrubber & Playback Controls Bar */}
        <div className="border-t border-slate-800 bg-slate-950 p-4">
          {/* Main Progress Bar */}
          <div
            className="group relative mb-3 h-2 w-full cursor-pointer overflow-hidden rounded-full bg-slate-800"
            onClick={(e) => {
              const rect = e.currentTarget.getBoundingClientRect();
              const clickX = e.clientX - rect.left;
              const ratio = Math.max(0, Math.min(1, clickX / rect.width));
              setCurrentTime(ratio * TOTAL_DURATION);
            }}
          >
            <div
              className="h-full rounded-full transition-all duration-100 ease-out"
              style={{
                width: `${(currentTime / TOTAL_DURATION) * 100}%`,
                backgroundColor: activeChapter.themeColor,
              }}
            />
          </div>

          {/* Chapter Selectors (4 Pills) */}
          <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
            {CHAPTERS.map((ch, idx) => {
              const isSelected = activeChapterIndex === idx;
              return (
                <button
                  key={ch.id}
                  type="button"
                  onClick={() => seekToChapter(idx)}
                  className={`flex flex-col items-start rounded-xl border p-2.5 text-left transition-all ${
                    isSelected
                      ? 'border-opacity-100 bg-slate-900 shadow-md'
                      : 'border-slate-800/80 bg-slate-950/60 opacity-60 hover:opacity-100'
                  }`}
                  style={{
                    borderColor: isSelected ? ch.themeColor : undefined,
                  }}
                >
                  <div className="flex w-full items-center justify-between">
                    <span className="font-mono text-[10px] font-bold text-slate-400">0{ch.id}</span>
                    {isSelected && (
                      <span className="h-1.5 w-1.5 rounded-full" style={{ backgroundColor: ch.themeColor }} />
                    )}
                  </div>
                  <span className="mt-1 line-clamp-1 text-xs font-bold text-white">
                    {ch.title.split(' ')[0]} {ch.title.split(' ')[1]}
                  </span>
                  {/* Sub-Progress bar for active chapter */}
                  <div className="mt-2 h-1 w-full overflow-hidden rounded-full bg-slate-800">
                    <div
                      className="h-full rounded-full transition-all duration-100"
                      style={{
                        width: isSelected ? `${chapterProgress}%` : idx < activeChapterIndex ? '100%' : '0%',
                        backgroundColor: ch.themeColor,
                      }}
                    />
                  </div>
                </button>
              );
            })}
          </div>

          {/* Play/Pause & Time Indicator */}
          <div className="mt-3 flex items-center justify-between border-t border-slate-800/80 pt-3 text-xs text-slate-400">
            <div className="flex items-center gap-3">
              <button
                type="button"
                onClick={() => setIsPlaying(!isPlaying)}
                className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-600 text-white shadow-soft transition-transform hover:scale-105 active:scale-95"
                title={isPlaying ? 'Pause simulation' : 'Play simulation'}
              >
                {isPlaying ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4 fill-current ml-0.5" />}
              </button>
              <button
                type="button"
                onClick={() => {
                  setCurrentTime(0);
                  setActiveChapterIndex(0);
                  setIsPlaying(true);
                }}
                className="rounded-lg p-1.5 text-slate-400 hover:text-white transition-colors"
                title="Replay from start"
              >
                <RotateCcw className="h-4 w-4" />
              </button>
              <span className="font-mono text-xs text-slate-300">
                {formatTime(currentTime)} / {formatTime(TOTAL_DURATION)}
              </span>
            </div>

            <div className="flex items-center gap-2 font-mono text-[11px] text-slate-400">
              <span>Chapter: {activeChapter.tag}</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
