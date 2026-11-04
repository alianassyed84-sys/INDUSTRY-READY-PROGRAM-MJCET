import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  UploadCloud,
  Sparkles,
  MessageSquare,
  TrendingUp,
  Layers,
  Cpu,
  ShieldCheck,
  Compass,
} from 'lucide-react';
import { useMotion } from '@/hooks/useMotion';
import PulseHero from '@/components/motion/PulseHero';
import FeatureGallery from '@/components/motion/FeatureGallery';
import AnalysisPreview from '@/components/motion/AnalysisPreview';
import SignalJourney from '@/components/motion/SignalJourney';
import DataTrust from '@/components/motion/DataTrust';
import { UrlAnalyzer } from '@/components/shared/UrlAnalyzer';
import { Button } from '@/components/ui/Button';
import { scrollReveal, gsap } from '@/lib/motion';
import { demoInsights } from '@/data/demo';
import { ROUTES } from '@/lib/routes';
import VantaBackground from '@/components/vanta/VantaBackground';
import { StoryNav } from '@/components/story/StoryNav';
import { CosmicAura, LaserHorizon } from '@/components/story/CosmicAura';
import { SpotlightCard } from '@/components/reactbits/SpotlightCard';
import { BorderBeam } from '@/components/reactbits/BorderBeam';
import { DecryptedText } from '@/components/reactbits/DecryptedText';
import { MagneticButton } from '@/components/reactbits/MagneticButton';
import { ShinyText } from '@/components/reactbits/ShinyText';

const DEMO_SAMPLES = [
  { label: 'Wireless Earbuds', url: 'https://www.amazon.in/dp/B0DEMO0001', icon: '🎧' },
  { label: 'Smart Water Bottle', url: 'https://www.amazon.in/dp/B0DEMO0002', icon: '💧' },
  { label: 'Mechanical Keyboard', url: 'https://www.amazon.in/dp/B0DEMO0003', icon: '⌨️' },
];

const MOOD_SNIPPETS = {
  positive: {
    label: 'Favorable',
    pct: '68%',
    tone: 'text-rp-success bg-rp-success/15 border-rp-success/30',
    quote: 'Sound quality is crisp and the bass is punchy for the price. Pairing was instant.',
    aspects: ['+ Sound clarity', '+ Battery life', '+ Instant pairing'],
  },
  neutral: {
    label: 'Neutral',
    pct: '22%',
    tone: 'text-rp-warning bg-rp-warning/15 border-rp-warning/30',
    quote: 'Fit is comfortable but they slip out when I run. Okay for desk use.',
    aspects: ['~ Desk ergonomics', '~ Case hinge', '~ Medium isolation'],
  },
  negative: {
    label: 'Critical',
    pct: '10%',
    tone: 'text-rp-coral bg-rp-coral/15 border-rp-coral/30',
    quote: 'Microphone picks up a lot of background noise on calls, colleagues complained.',
    aspects: ['- Background noise', '- Touch sensitivity', '- Bluetooth drops'],
  },
};

export default function Landing() {
  const root = useRef<HTMLDivElement>(null);
  const moodContainerRef = useRef<HTMLDivElement>(null);
  const { enabled, systemReduced } = useMotion();
  const nav = useNavigate();

  const [sampleUrl, setSampleUrl] = useState('');
  const [activeMood, setActiveMood] = useState<'positive' | 'neutral' | 'negative'>('positive');

  useEffect(() => {
    const el = root.current;
    if (!el || !enabled) return;
    const stop = scrollReveal(el);
    return stop;
  }, [enabled]);

  // GSAP kinetic transition when mood switches
  const handleMoodChange = (mood: 'positive' | 'neutral' | 'negative') => {
    setActiveMood(mood);
    if (enabled && !systemReduced && moodContainerRef.current) {
      gsap.fromTo(
        moodContainerRef.current,
        { opacity: 0.35, y: 4 },
        { opacity: 1, y: 0, duration: 0.35, ease: 'power2.out' }
      );
    }
  };

  const d = demoInsights('demo-1');
  const s = d.sentiment!;
  const currentMoodData = MOOD_SNIPPETS[activeMood];

  return (
    <div ref={root} className="relative min-w-0 bg-[#0A0711] text-rp-text selection:bg-rp-primary/30">
      {/* Floating Story HUD Rail */}
      <StoryNav />

      {/* Atmospheric Celestial Nebulae */}
      <CosmicAura />

      {/* ========================================================================= */}
      {/* CHAPTER 1: THE CORE PULSE (Standout Cinematic Scene)                       */}
      {/* ========================================================================= */}
      <section
        id="chapter-hero"
        className="rp-cinematic-hero rp-ambient relative overflow-hidden border-b border-rp-border/50 h-[calc(100svh-76px)] max-h-[calc(100svh-76px)] flex flex-col items-center justify-center pt-1"
      >
        {/* Vanta 3D Interactive Geometric Mesh Background */}
        <VantaBackground
          className="z-0 opacity-100"
          particleCount={90}
          maxDistance={195}
          mouseRepulsion={true}
        />

        {/* Ambient Top World Tagline */}
        <div className="relative z-10 text-center mb-0.5 select-none pointer-events-none">
          <div className="inline-flex items-center gap-2 px-3 py-0.5 rounded-full text-[11px] sm:text-xs font-mono uppercase tracking-widest bg-rp-surface/85 border border-rp-primary/35 text-rp-primary shadow-lg backdrop-blur-md">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
            <span>Chapter I · The Neural Core</span>
            <span className="text-rp-muted">/</span>
            <span className="text-slate-300">Live Pulse</span>
          </div>
        </div>

        <div className="rp-cinematic-stage w-full max-w-7xl mx-auto px-2 sm:px-6 lg:px-10 relative z-10">
          <div className="rp-cinematic-canvas relative z-10 min-w-0">
            <PulseHero />
          </div>
        </div>
      </section>

      {/* Laser Horizon Divider */}
      <LaserHorizon glowColor="#BF89FF" />

      {/* ========================================================================= */}
      {/* CHAPTER 2: THE INGESTION GATEWAY (Interactive Product Terminal)           */}
      {/* ========================================================================= */}
      <section id="chapter-ingest" className="relative z-20 mx-auto mb-20 max-w-4xl px-4 scroll-mt-24">
        {/* Story Intro Header */}
        <div className="text-center mb-8" data-scroll>
          <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full text-xs font-mono tracking-widest uppercase bg-rp-primary/10 text-rp-primary border border-rp-primary/25 mb-3 shadow-sm">
            <Compass className="w-3.5 h-3.5 text-rp-primary" />
            <span>Chapter II · The Ingestion Gateway</span>
          </div>
          <h2 className="font-heading text-2xl sm:text-4xl font-extrabold text-rp-navy tracking-tight">
            <ShinyText speed={4}>Connect Any Live Product Listing</ShinyText>
          </h2>
          <p className="text-sm sm:text-base text-rp-muted mt-2 max-w-xl mx-auto leading-relaxed">
            Feed in a live marketplace link or test curated real-world consumer hardware to see the neural pipeline in action.
          </p>
        </div>

        <SpotlightCard
          spotlightColor="rgba(191, 137, 255, 0.22)"
          borderGlowColor="rgba(191, 137, 255, 0.55)"
          className="p-6 md:p-8 shadow-2xl backdrop-blur-xl border border-rp-border/80 bg-rp-surface/95"
        >
          {/* React Bits Border Beam */}
          <BorderBeam
            size={340}
            duration={9}
            borderWidth={1.8}
            colorFrom="#BF89FF"
            colorTo="#7D2DE1"
          />

          <div className="flex items-center justify-between gap-2 mb-1.5">
            <h3 className="font-heading text-lg md:text-xl font-bold text-rp-navy flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-rp-primary" />
              <span>Analyze Reviews</span>
            </h3>
            <span className="text-[11px] font-semibold text-rp-primary bg-rp-primary-light px-2.5 py-0.5 rounded-full border border-rp-primary/20">
              Interactive preview
            </span>
          </div>
          <p className="text-xs sm:text-sm text-rp-muted">
            Paste any Amazon.in or Flipkart link, or try a sample product below.
          </p>

          {/* Interactive Quick Sample Chips with Magnetic Button attraction */}
          <div className="mt-4 flex flex-wrap items-center gap-2">
            <span className="text-xs font-semibold text-rp-navy">Quick test:</span>
            {DEMO_SAMPLES.map((sample) => (
              <MagneticButton key={sample.label} strength={0.22}>
                <button
                  type="button"
                  onClick={() => setSampleUrl(sample.url)}
                  className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all duration-200 border ${
                    sampleUrl === sample.url
                      ? 'bg-rp-primary text-white border-rp-primary shadow-soft scale-105'
                      : 'bg-rp-surface-soft text-rp-text border-rp-border hover:bg-rp-primary-light hover:border-rp-primary/40'
                  }`}
                >
                  <span aria-hidden>{sample.icon}</span>
                  <span>{sample.label}</span>
                </button>
              </MagneticButton>
            ))}
          </div>

          <div className="mt-5">
            <UrlAnalyzer
              value={sampleUrl || undefined}
              onChange={setSampleUrl}
              cta="Analyze link"
            />
          </div>

          {/* Live Interactive Mood Pulse Simulator */}
          <div className="mt-6 rounded-xl border border-rp-border/80 bg-rp-surface-soft/60 p-4 transition-all">
            <div className="flex flex-wrap items-center justify-between gap-2 border-b border-rp-border/50 pb-2.5">
              <span className="text-xs font-bold uppercase tracking-wider text-rp-muted flex items-center gap-1.5">
                <TrendingUp className="h-3.5 w-3.5 text-rp-primary" />
                <DecryptedText text="Live Customer Signal" speed={35} maxIterations={8} />
              </span>
              <div className="flex items-center gap-1.5" role="tablist" aria-label="Customer mood preview">
                {(['positive', 'neutral', 'negative'] as const).map((m) => (
                  <MagneticButton key={m} strength={0.15}>
                    <button
                      type="button"
                      role="tab"
                      aria-selected={activeMood === m}
                      onClick={() => handleMoodChange(m)}
                      className={`px-2.5 py-1 rounded-md text-xs font-bold transition-all duration-200 ${
                        activeMood === m
                          ? 'bg-rp-surface text-rp-navy shadow-sm border border-rp-border'
                          : 'text-rp-muted hover:text-rp-navy'
                      }`}
                    >
                      {MOOD_SNIPPETS[m].label} ({MOOD_SNIPPETS[m].pct})
                    </button>
                  </MagneticButton>
                ))}
              </div>
            </div>

            {/* Animated Quote & Aspects */}
            <div ref={moodContainerRef} className="mt-3.5 space-y-2.5">
              <div className="flex items-start gap-2.5 text-xs sm:text-sm">
                <MessageSquare className="h-4 w-4 text-rp-primary shrink-0 mt-0.5" />
                <p className="italic text-rp-text leading-relaxed">
                  &ldquo;{currentMoodData.quote}&rdquo;
                </p>
              </div>

              <div className="flex flex-wrap items-center gap-1.5 pt-1">
                {currentMoodData.aspects.map((aspect) => (
                  <span
                    key={aspect}
                    className={`px-2.5 py-0.5 rounded text-[11px] font-semibold border ${currentMoodData.tone}`}
                  >
                    {aspect}
                  </span>
                ))}
              </div>
            </div>
          </div>

          <div className="mt-5 flex flex-wrap items-center justify-between gap-3 border-t border-rp-border/60 pt-4">
            <span className="text-xs text-rp-muted">
              Have a dataset file? Amazon/Flipkart CSV or JSON supported.
            </span>
            <MagneticButton strength={0.28}>
              <Button
                type="button"
                variant="secondary"
                onClick={() => nav(ROUTES.data)}
                className="shrink-0 text-xs py-2 px-3.5"
              >
                <UploadCloud className="mr-1.5 h-4 w-4" />
                Upload a dataset
              </Button>
            </MagneticButton>
          </div>
        </SpotlightCard>
      </section>

      {/* Laser Horizon Divider */}
      <LaserHorizon glowColor="#E063EF" />

      {/* ========================================================================= */}
      {/* CHAPTER 3: THE FIVE SENSORY LENSES (Prism Dimensions)                    */}
      {/* ========================================================================= */}
      <section id="chapter-features" className="relative z-10 scroll-mt-20">
        <div className="text-center mb-4" data-scroll>
          <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full text-xs font-mono tracking-widest uppercase bg-rp-primary/10 text-rp-primary border border-rp-primary/25 mb-2">
            <Layers className="w-3.5 h-3.5 text-rp-primary" />
            <span>Chapter III · Multidimensional Analysis</span>
          </div>
        </div>
        <FeatureGallery />
      </section>

      {/* Laser Horizon Divider */}
      <LaserHorizon glowColor="#46DDBD" />

      {/* ========================================================================= */}
      {/* CHAPTER 4: SYNTHESIZED INTELLIGENCE (Authentic Metrics)                   */}
      {/* ========================================================================= */}
      <section id="chapter-preview" className="relative z-10 scroll-mt-20">
        <div className="text-center mb-4" data-scroll>
          <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full text-xs font-mono tracking-widest uppercase bg-rp-primary/10 text-rp-primary border border-rp-primary/25 mb-2">
            <Cpu className="w-3.5 h-3.5 text-rp-primary" />
            <span>Chapter IV · Synthesized Clarity</span>
          </div>
        </div>
        <AnalysisPreview productTitle={d.product.title} sentiment={s} topics={d.topics ?? []} />
      </section>

      {/* Laser Horizon Divider */}
      <LaserHorizon glowColor="#87BBFF" />

      {/* ========================================================================= */}
      {/* CHAPTER 5: THE SIGNAL ODYSSEY (End-to-End Workflow)                       */}
      {/* ========================================================================= */}
      <section id="chapter-journey" className="relative z-10 scroll-mt-20">
        <div className="text-center mb-4" data-scroll>
          <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full text-xs font-mono tracking-widest uppercase bg-rp-primary/10 text-rp-primary border border-rp-primary/25 mb-2">
            <TrendingUp className="w-3.5 h-3.5 text-rp-primary" />
            <span>Chapter V · The Signal Odyssey</span>
          </div>
        </div>
        <SignalJourney />
      </section>

      {/* Laser Horizon Divider */}
      <LaserHorizon glowColor="#BF89FF" />

      {/* ========================================================================= */}
      {/* CHAPTER 6: THE TRUST SHIELD (Verifiable Provenance)                       */}
      {/* ========================================================================= */}
      <section id="chapter-trust" className="relative z-10 scroll-mt-20 pb-16">
        <div className="text-center mb-4" data-scroll>
          <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full text-xs font-mono tracking-widest uppercase bg-rp-primary/10 text-rp-primary border border-rp-primary/25 mb-2">
            <ShieldCheck className="w-3.5 h-3.5 text-rp-primary" />
            <span>Chapter VI · The Trust Shield</span>
          </div>
        </div>
        <DataTrust />
      </section>
    </div>
  );
}
