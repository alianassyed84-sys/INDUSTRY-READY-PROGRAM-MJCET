import { Suspense, lazy, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, BookOpenCheck, Globe2, Hash, LineChart, SmilePlus, Tag, Link2, DownloadCloud, Cpu, Lightbulb, ShieldCheck, Database, FlaskConical } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { UrlAnalyzer } from '@/components/shared/UrlAnalyzer';
import { ROUTES } from '@/lib/routes';
import { gsap, prefersReducedMotion, scrollReveal } from '@/lib/motion';
import { demoInsights } from '@/data/demo';
import { pct } from '@/lib/utils';

const ThreeHero = lazy(() => import('@/components/three/ThreeHero'));

const FEATURES = [
  { icon: SmilePlus, title: 'Sentiment', text: 'See how positive, neutral and negative reviews split, with polarity where the backend provides it.' },
  { icon: Hash, title: 'Topics', text: 'TF-IDF keyphrase extraction surfaces the terms customers repeat most.' },
  { icon: Globe2, title: 'Language', text: 'Identify which languages reviews are written in and how well they were classified.' },
  { icon: BookOpenCheck, title: 'Readability', text: 'Flesch Reading Ease and grade-level estimates for review text.' },
  { icon: LineChart, title: 'Price monitoring', text: 'Track stored price observations over time once snapshots exist.' },
];

const STEPS = [
  { icon: Link2, title: 'URL', text: 'Paste an Amazon.in product link.' },
  { icon: DownloadCloud, title: 'Collection', text: 'Reviews are gathered by the backend harvester.' },
  { icon: Cpu, title: 'Analysis', text: 'Sentiment, topics, language and readability are computed.' },
  { icon: Lightbulb, title: 'Insights', text: 'Explore the results across ReviewPulse.' },
];

export default function Landing() {
  const root = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = root.current;
    if (!el) return;
    const stop = scrollReveal(el);
    let ctx: gsap.Context | undefined;
    if (!prefersReducedMotion()) {
      ctx = gsap.context(() => {
        gsap.from('[data-hero]', { opacity: 0, y: 16, duration: 0.55, ease: 'power2.out', stagger: 0.09, clearProps: 'opacity,transform' });
      }, el);
    }
    return () => { stop(); ctx?.revert(); };
  }, []);

  const d = demoInsights('demo-1');
  const s = d.sentiment!;
  const total = s.positive + s.neutral + s.negative;

  return (
    <div ref={root}>
      {/* 1. Hero */}
      <section className="rp-ambient relative overflow-hidden">
        <div className="mx-auto grid max-w-content items-center gap-8 px-4 py-12 md:px-6 lg:grid-cols-[1.05fr_.95fr] lg:px-10 lg:py-20">
          <div>
            <Badge tone="primary" data-hero className="mb-5">AI-powered review analytics</Badge>
            {/* 3. Headline + supporting text */}
            <h1 data-hero className="text-display font-extrabold">
              Understand what customers <span className="text-rp-primary">really</span> think.
            </h1>
            <p data-hero className="mt-5 max-w-xl text-lg text-rp-muted">
              Turn thousands of product reviews into clear signals: sentiment, recurring complaints, languages and readability, all in one place.
            </p>
            {/* 2 + 4. URL entry with primary CTA */}
            <div data-hero className="mt-8 max-w-2xl"><UrlAnalyzer cta="Analyze a Product" /></div>
            {/* 5. Secondary CTA */}
            <div data-hero className="mt-4 flex flex-wrap items-center gap-3">
              <Link to={ROUTES.dashboard}><Button variant="secondary" size="lg">Explore Dashboard <ArrowRight className="h-4 w-4" aria-hidden /></Button></Link>
              <span className="text-sm text-rp-muted">No sign-up needed to look around.</span>
            </div>
          </div>
          <div data-hero className="relative mx-auto h-[320px] w-full max-w-[560px] sm:h-[420px] lg:h-[520px]">
            <div aria-hidden className="absolute inset-6 rounded-full bg-rp-primary/10 blur-3xl" />
            <Suspense fallback={<div aria-hidden className="mx-auto mt-10 aspect-square w-2/3 rounded-full bg-gradient-to-br from-rp-primary-soft to-rp-primary/70" />}>
              <ThreeHero />
            </Suspense>
          </div>
        </div>
      </section>

      {/* 6. Feature cards */}
      <section id="features" className="mx-auto max-w-content scroll-mt-24 px-4 py-14 md:px-6 lg:px-10">
        <div data-scroll className="mb-8 max-w-2xl">
          <h2 className="text-[28px] font-extrabold md:text-[32px]">Five lenses on every product</h2>
          <p className="mt-2 text-rp-muted">Each analysis page works from the same product, so findings connect.</p>
        </div>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
          {FEATURES.map(({ icon: Icon, title, text }) => (
            <Card key={title} interactive data-scroll>
              <span className="mb-4 grid h-11 w-11 place-items-center rounded-2xl bg-rp-primary-light text-rp-primary"><Icon className="h-5 w-5" aria-hidden /></span>
              <h3 className="text-[17px] font-bold">{title}</h3>
              <p className="mt-1.5 text-sm text-rp-muted">{text}</p>
            </Card>
          ))}
        </div>
      </section>

      {/* 7. Product-analysis preview */}
      <section className="mx-auto max-w-content px-4 pb-14 md:px-6 lg:px-10">
        <Card tone="featured" data-scroll className="!p-6 md:!p-8">
          <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
            <div>
              <h2 className="text-[24px] font-extrabold">Product analysis preview</h2>
              <p className="mt-1 text-sm text-rp-muted">{d.product.title}</p>
            </div>
            <Badge tone="warning"><FlaskConical className="h-3.5 w-3.5" aria-hidden /> Demo data</Badge>
          </div>
          <div className="grid gap-4 md:grid-cols-3">
            {([['Positive', s.positive, 'bg-rp-success'], ['Neutral', s.neutral, 'bg-rp-muted'], ['Negative', s.negative, 'bg-rp-coral']] as const).map(([l, n, c]) => (
              <div key={l} className="rounded-2xl border border-rp-border bg-rp-surface p-4">
                <p className="text-[13px] font-semibold text-rp-muted">{l} reviews</p>
                <p className="tnum mt-1 font-heading text-3xl font-extrabold">{pct(n, total)}%</p>
                <div className="mt-3 h-2 overflow-hidden rounded-full bg-rp-primary-light"><div className={`h-full rounded-full ${c}`} style={{ width: `${pct(n, total)}%` }} /></div>
              </div>
            ))}
          </div>
          <div className="mt-5 flex flex-wrap gap-2">
            {d.topics!.slice(0, 5).map((t) => <Badge key={t.term} tone="primary"><Tag className="h-3 w-3" aria-hidden />{t.term}</Badge>)}
          </div>
        </Card>
      </section>

      {/* 8. Workflow */}
      <section id="workflow" className="mx-auto max-w-content scroll-mt-24 px-4 pb-14 md:px-6 lg:px-10">
        <h2 data-scroll className="mb-8 text-[28px] font-extrabold md:text-[32px]">From link to insight</h2>
        <ol className="grid gap-4 md:grid-cols-4">
          {STEPS.map(({ icon: Icon, title, text }, i) => (
            <li key={title} data-scroll className="relative">
              <Card className="h-full">
                <div className="mb-4 flex items-center justify-between">
                  <span className="grid h-11 w-11 place-items-center rounded-2xl bg-rp-primary text-white"><Icon className="h-5 w-5" aria-hidden /></span>
                  <span className="tnum font-heading text-2xl font-extrabold text-rp-primary-soft">0{i + 1}</span>
                </div>
                <h3 className="text-[17px] font-bold">{title}</h3>
                <p className="mt-1.5 text-sm text-rp-muted">{text}</p>
              </Card>
            </li>
          ))}
        </ol>
      </section>

      {/* 9. Trust and data source */}
      <section id="trust" className="mx-auto max-w-content scroll-mt-24 px-4 pb-16 md:px-6 lg:px-10">
        <div className="grid gap-4 lg:grid-cols-2">
          <Card data-scroll>
            <ShieldCheck className="mb-3 h-6 w-6 text-rp-primary" aria-hidden />
            <h2 className="text-xl font-extrabold">Honest about the data</h2>
            <p className="mt-2 text-sm text-rp-muted">Missing fields are shown as unavailable, never guessed. Any page showing sample content carries a visible “Demo data” label, and demo values are never blended with live results.</p>
          </Card>
          <Card data-scroll>
            <Database className="mb-3 h-6 w-6 text-rp-primary" aria-hidden />
            <h2 className="text-xl font-extrabold">Where reviews come from</h2>
            <p className="mt-2 text-sm text-rp-muted">Reviews are loaded by the project’s own backend harvester (currently CSV-based; direct Amazon.in retrieval is still in development). ReviewPulse is independent and not affiliated with Amazon.</p>
            <Link to={ROUTES.about} className="mt-3 inline-flex items-center gap-1 text-sm font-semibold text-rp-primary hover:text-rp-primary-hover">Read the documentation <ArrowRight className="h-4 w-4" aria-hidden /></Link>
          </Card>
        </div>
      </section>
    </div>
  );
}
