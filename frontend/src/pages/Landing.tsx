import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { UploadCloud, Sparkles, MessageSquare, TrendingUp } from 'lucide-react';
import { useMotion } from '@/hooks/useMotion';
import PulseHero from '@/components/motion/PulseHero';
import FeatureGallery from '@/components/motion/FeatureGallery';
import AnalysisPreview from '@/components/motion/AnalysisPreview';
import SignalJourney from '@/components/motion/SignalJourney';
import DataTrust from '@/components/motion/DataTrust';
import { UrlAnalyzer } from '@/components/shared/UrlAnalyzer';
import { Button } from '@/components/ui/Button';
import { scrollReveal } from '@/lib/motion';
import { demoInsights } from '@/data/demo';
import { ROUTES } from '@/lib/routes';

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
  const { enabled } = useMotion();
  const nav = useNavigate();

  const [sampleUrl, setSampleUrl] = useState('');
  const [activeMood, setActiveMood] = useState<'positive' | 'neutral' | 'negative'>('positive');

  useEffect(() => {
    const el = root.current;
    if (!el || !enabled) return;
    const stop = scrollReveal(el);
    return stop;
  }, [enabled]);

  const d = demoInsights('demo-1');
  const s = d.sentiment!;
  const currentMoodData = MOOD_SNIPPETS[activeMood];

  return (
    <div ref={root}>
      {/* 1. Hero */}
      <section className="rp-cinematic-hero rp-ambient relative overflow-hidden border-b border-rp-border/50">
        <div className="rp-cinematic-stage mx-auto max-w-content px-3 sm:px-5 lg:px-10">
          <div className="rp-cinematic-canvas relative z-10 min-w-0">
            <PulseHero />
          </div>

          {/* Interactive Dual Entry Points: Product Link Box & Dataset Upload */}
          <div className="relative z-20 mx-auto -mt-4 mb-10 max-w-2xl rounded-2xl border border-rp-border bg-rp-surface/95 p-6 shadow-xl backdrop-blur-md transition-all">
            <div className="flex items-center justify-between gap-2 mb-1">
              <h2 className="font-heading text-lg font-bold text-rp-navy flex items-center gap-2">
                <Sparkles className="h-4 w-4 text-rp-primary" />
                Analyze Reviews
              </h2>
              <span className="text-[11px] font-semibold text-rp-primary bg-rp-primary-light px-2.5 py-0.5 rounded-full border border-rp-primary/20">
                Interactive preview
              </span>
            </div>
            <p className="text-sm text-rp-muted">Paste any Amazon.in or Flipkart link, or try a sample product below.</p>

            {/* Interactive Quick Sample Chips */}
            <div className="mt-4 flex flex-wrap items-center gap-1.5">
              <span className="text-xs font-semibold text-rp-navy">Quick test:</span>
              {DEMO_SAMPLES.map((sample) => (
                <button
                  key={sample.label}
                  type="button"
                  onClick={() => setSampleUrl(sample.url)}
                  className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-semibold transition-all duration-200 border ${
                    sampleUrl === sample.url
                      ? 'bg-rp-primary text-white border-rp-primary shadow-soft scale-105'
                      : 'bg-rp-surface-soft text-rp-text border-rp-border hover:bg-rp-primary-light hover:border-rp-primary/40'
                  }`}
                >
                  <span aria-hidden>{sample.icon}</span>
                  <span>{sample.label}</span>
                </button>
              ))}
            </div>

            <div className="mt-4">
              <UrlAnalyzer
                value={sampleUrl || undefined}
                onChange={setSampleUrl}
                cta="Analyze link"
              />
            </div>

            {/* Live Interactive Mood Pulse Simulator */}
            <div className="mt-5 rounded-xl border border-rp-border/80 bg-rp-surface-soft/60 p-4 transition-all">
              <div className="flex flex-wrap items-center justify-between gap-2 border-b border-rp-border/50 pb-2.5">
                <span className="text-xs font-bold uppercase tracking-wider text-rp-muted flex items-center gap-1.5">
                  <TrendingUp className="h-3.5 w-3.5 text-rp-primary" /> Live Customer Signal
                </span>
                <div className="flex items-center gap-1" role="tablist" aria-label="Customer mood preview">
                  {(['positive', 'neutral', 'negative'] as const).map((m) => (
                    <button
                      key={m}
                      type="button"
                      role="tab"
                      aria-selected={activeMood === m}
                      onClick={() => setActiveMood(m)}
                      className={`px-2.5 py-1 rounded-md text-xs font-bold transition-all duration-200 ${
                        activeMood === m
                          ? 'bg-rp-surface text-rp-navy shadow-sm border border-rp-border'
                          : 'text-rp-muted hover:text-rp-navy'
                      }`}
                    >
                      {MOOD_SNIPPETS[m].label} ({MOOD_SNIPPETS[m].pct})
                    </button>
                  ))}
                </div>
              </div>

              {/* Animated Quote & Aspects */}
              <div className="mt-3 space-y-2">
                <div className="flex items-start gap-2.5 text-xs">
                  <MessageSquare className="h-4 w-4 text-rp-primary shrink-0 mt-0.5" />
                  <p className="italic text-rp-text leading-relaxed">
                    &ldquo;{currentMoodData.quote}&rdquo;
                  </p>
                </div>

                <div className="flex flex-wrap items-center gap-1.5 pt-1">
                  {currentMoodData.aspects.map((aspect) => (
                    <span
                      key={aspect}
                      className={`px-2 py-0.5 rounded text-[11px] font-semibold border ${currentMoodData.tone}`}
                    >
                      {aspect}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            <div className="mt-4 flex flex-wrap items-center justify-between gap-3 border-t border-rp-border/60 pt-4">
              <span className="text-xs text-rp-muted">Have a dataset file? Amazon/Flipkart CSV or JSON supported.</span>
              <Button
                type="button"
                variant="secondary"
                onClick={() => nav(ROUTES.data)}
                className="shrink-0 text-xs py-2 px-3"
              >
                <UploadCloud className="mr-1.5 h-4 w-4" />
                Upload a dataset
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* 6. Feature cards */}
      <FeatureGallery />

      {/* 7. Product-analysis preview */}
      <AnalysisPreview productTitle={d.product.title} sentiment={s} topics={d.topics ?? []} />

      {/* 8. Workflow */}
      <SignalJourney />

      {/* 9. Trust and data source */}
      <DataTrust />
    </div>
  );
}
