import { useEffect, useRef, useState, type CSSProperties, type ReactNode } from 'react';
import { Link } from 'react-router-dom';
import {
  ArrowRight,
  BookOpenCheck,
  Check,
  Cpu,
  DownloadCloud,
  Hash,
  Languages,
  Lightbulb,
  Link2,
  MessageSquareText,
  ScanSearch,
  Sparkles,
} from 'lucide-react';
import { useMotion } from '@/hooks/useMotion';
import { ROUTES } from '@/lib/routes';
import { demoInsights } from '@/data/demo';
import './signal-journey.css';

const STEPS = [
  {
    icon: Link2,
    eyebrow: 'Start with the source',
    title: 'Share one product link',
    text: 'Paste an Amazon.in product URL. ReviewPulse identifies the product and prepares it for collection.',
  },
  {
    icon: DownloadCloud,
    eyebrow: 'Bring every voice together',
    title: 'Collect the review signal',
    text: 'The project’s harvester gathers available review text into one consistent, analysis-ready stream.',
  },
  {
    icon: Cpu,
    eyebrow: 'Turn volume into structure',
    title: 'Analyze what customers mean',
    text: 'Sentiment, topics, language, and readability run together so every result keeps its context.',
  },
  {
    icon: Lightbulb,
    eyebrow: 'Move from data to direction',
    title: 'Explore the clearest insights',
    text: 'See the strongest signals, recurring friction, and the themes worth acting on in one workspace.',
  },
];

function StepPreview({ index }: { index: number }) {
  if (index === 0) {
    return (
      <div className="journey-url-preview" aria-hidden="true">
        <span className="journey-url-lock"><Link2 size={14} /></span>
        <span className="journey-url-copy"><small>amazon.in</small><strong>/dp/B0D7...</strong></span>
        <span className="journey-url-status"><Check size={13} /> Recognized</span>
      </div>
    );
  }

  if (index === 1) {
    return (
      <div className="journey-review-stream" aria-hidden="true">
        {[78, 56, 68].map((width, item) => (
          <span key={width} style={{ '--review-width': `${width}%`, '--review-index': item } as CSSProperties}>
            <i />
            <b><em /><em /></b>
            <small>captured</small>
          </span>
        ))}
        <div><MessageSquareText size={15} /> Reviews entering the signal</div>
      </div>
    );
  }

  if (index === 2) {
    return (
      <div className="journey-engine-grid" aria-hidden="true">
        <span><Sparkles size={15} /><b>Sentiment</b><small>mood</small></span>
        <span><Hash size={15} /><b>Topics</b><small>patterns</small></span>
        <span><Languages size={15} /><b>Language</b><small>context</small></span>
        <span><BookOpenCheck size={15} /><b>Readability</b><small>clarity</small></span>
      </div>
    );
  }

  const sample = demoInsights('demo-1');
  const total = (sample.sentiment?.positive ?? 0) + (sample.sentiment?.neutral ?? 0) + (sample.sentiment?.negative ?? 0);
  const positivePct = total > 0 ? ((sample.sentiment!.positive / total) * 100).toFixed(1) : '68.0';
  const themeCount = sample.topics?.length ?? 5;

  return (
    <div className="journey-insight-preview" aria-hidden="true">
      <div className="journey-insight-head"><span><ScanSearch size={14} /> Leading signal</span><b>Example</b></div>
      <strong>Customers value the sound quality.</strong>
      <div className="journey-insight-meter"><span /></div>
      <div className="journey-insight-meta"><span>{positivePct}% positive</span><span>{themeCount} themes found</span></div>
    </div>
  );
}

function StepCard({ index, children }: { index: number; children: ReactNode }) {
  const { icon: Icon, eyebrow, title, text } = STEPS[index];

  return (
    <article className="journey-card">
      <div className="journey-card-top">
        <span className="journey-card-icon"><Icon size={19} aria-hidden="true" /></span>
        <span className="journey-card-number tnum">0{index + 1}</span>
      </div>
      <span className="journey-card-eyebrow">{eyebrow}</span>
      <h3>{title}</h3>
      <p>{text}</p>
      {children}
      {index === 3 && (
        <Link to={ROUTES.dashboard} className="journey-cta">
          Explore the dashboard <ArrowRight size={16} aria-hidden="true" />
        </Link>
      )}
    </article>
  );
}

export default function SignalJourney() {
  const root = useRef<HTMLElement>(null);
  const [entered, setEntered] = useState(false);
  const { enabled } = useMotion();

  useEffect(() => {
    const node = root.current;
    if (!node) return;
    const observer = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) {
        setEntered(true);
        observer.disconnect();
      }
    }, { threshold: 0.08 });
    observer.observe(node);
    return () => observer.disconnect();
  }, []);

  return (
    <section
      ref={root}
      id="workflow"
      className="signal-journey"
      aria-labelledby="signal-journey-heading"
      data-visible={entered || !enabled}
      data-animate={entered && enabled}
    >
      <header className="journey-heading" data-scroll>
        <span className="journey-kicker"><Sparkles size={14} aria-hidden="true" /> How it works</span>
        <h2 id="signal-journey-heading">From one link to a <span>clearer decision.</span></h2>
        <p>Watch a product page become a connected view of what customers praise, question, and repeat.</p>
      </header>

      <div className="journey-map">
        <div className="journey-rail" aria-hidden="true"><span /><i /></div>
        <ol className="journey-list">
          {STEPS.map((step, index) => (
            <li key={step.title} className="journey-step" style={{ '--step-index': index } as CSSProperties}>
              <span className="journey-node" aria-hidden="true"><i /></span>
              <StepCard index={index}><StepPreview index={index} /></StepCard>
            </li>
          ))}
        </ol>
      </div>
    </section>
  );
}
