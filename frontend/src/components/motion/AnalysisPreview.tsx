import { useEffect, useRef, useState, type CSSProperties } from 'react';
import { Link } from 'react-router-dom';
import { Activity, ArrowRight, CircleMinus, FlaskConical, Radio, Tag, TrendingDown, TrendingUp } from 'lucide-react';
import { useMotion } from '@/hooks/useMotion';
import { pct } from '@/lib/utils';
import { ROUTES } from '@/lib/routes';
import type { Insights, Topic } from '@/lib/types';
import './analysis-preview.css';

interface AnalysisPreviewProps {
  productTitle: string;
  sentiment: NonNullable<Insights['sentiment']>;
  topics: Topic[];
}

function useAnimatedValue(value: number, active: boolean) {
  const [display, setDisplay] = useState(active ? 0 : value);

  useEffect(() => {
    if (!active) {
      setDisplay(value);
      return;
    }
    let frame = 0;
    const started = performance.now();
    const update = (now: number) => {
      const progress = Math.min((now - started) / 900, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setDisplay(value * eased);
      if (progress < 1) frame = requestAnimationFrame(update);
    };
    frame = requestAnimationFrame(update);
    return () => cancelAnimationFrame(frame);
  }, [active, value]);

  return display;
}

function Percent({ value, active }: { value: number; active: boolean }) {
  const display = useAnimatedValue(value, active);
  return <>{display.toFixed(value % 1 ? 1 : 0)}%</>;
}

export default function AnalysisPreview({ productTitle, sentiment, topics }: AnalysisPreviewProps) {
  const root = useRef<HTMLElement>(null);
  const [entered, setEntered] = useState(false);
  const { enabled } = useMotion();
  const total = sentiment.positive + sentiment.neutral + sentiment.negative;
  const positive = pct(sentiment.positive, total);
  const neutral = pct(sentiment.neutral, total);
  const negative = pct(sentiment.negative, total);
  const animate = entered && enabled;

  useEffect(() => {
    const node = root.current;
    if (!node) return;
    const observer = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) {
        setEntered(true);
        observer.disconnect();
      }
    }, { threshold: .2 });
    observer.observe(node);
    return () => observer.disconnect();
  }, []);

  return (
    <section
      ref={root}
      className="analysis-preview"
      aria-labelledby="analysis-preview-heading"
      data-visible={entered || !enabled}
      data-animate={animate}
    >
      <header className="analysis-preview-heading" data-scroll>
        <div>
          <span className="analysis-preview-kicker"><Activity size={14} aria-hidden /> Overview</span>
          <h2 id="analysis-preview-heading">Product analysis, <span>at a glance.</span></h2>
          <p>{productTitle} · A connected view of customer sentiment and recurring themes.</p>
        </div>
        <div role="status" aria-label="Example notice: The analysis shown below is simulated sample data." className="analysis-demo-badge">
          <FlaskConical size={14} aria-hidden />
          <span>Example preview</span>
        </div>
      </header>

      <div className="analysis-console">
        <article className="analysis-panel analysis-positive">
          <div className="analysis-panel-head">
            <div>
              <span className="analysis-panel-label"><span className="analysis-live-dot" /> Positive momentum</span>
              <p>Customers are leaning favorable</p>
            </div>
            <span className="analysis-panel-icon"><TrendingUp size={18} aria-hidden /></span>
          </div>

          <div className="analysis-primary-value">
            <strong className="tnum"><Percent value={positive} active={animate} /></strong>
            <span>{sentiment.positive} of {total} reviews</span>
          </div>

          <div className="analysis-chart analysis-chart-positive" aria-hidden="true">
            <svg viewBox="0 0 560 170" preserveAspectRatio="none">
              <defs>
                <linearGradient id="analysis-positive-fill" x1="0" y1="0" x2="0" y2="1">
                  <stop stopColor="#53e0c0" stopOpacity=".28" />
                  <stop offset="1" stopColor="#53e0c0" stopOpacity="0" />
                </linearGradient>
              </defs>
              <g className="analysis-chart-grid"><path d="M0 38H560M0 86H560M0 134H560" /></g>
              <path className="analysis-chart-area" d="M0 142 48 126 93 133 142 102 190 111 238 72 286 89 333 55 382 66 430 39 478 54 520 25 560 31V170H0Z" fill="url(#analysis-positive-fill)" />
              <path className="analysis-chart-line" pathLength="1" d="M0 142 48 126 93 133 142 102 190 111 238 72 286 89 333 55 382 66 430 39 478 54 520 25 560 31" />
              <g className="analysis-chart-points"><circle cx="142" cy="102" r="4" /><circle cx="333" cy="55" r="4" /><circle cx="520" cy="25" r="4" /></g>
            </svg>
          </div>

          <div className="analysis-card-footer">
            <span>Average mood</span>
            <strong className="tnum">+{(sentiment.avgPolarity ?? 0).toFixed(2)}</strong>
            <span className="analysis-divider" />
            <span>Tone</span>
            <strong>Favorable</strong>
          </div>
        </article>

        <article className="analysis-panel analysis-negative">
          <div className="analysis-panel-head">
            <div>
              <span className="analysis-panel-label">Top complaints</span>
              <p>Concerns worth investigating</p>
            </div>
            <span className="analysis-panel-icon"><TrendingDown size={18} aria-hidden /></span>
          </div>
          <div className="analysis-secondary-value">
            <strong className="tnum"><Percent value={negative} active={animate} /></strong>
            <span>{sentiment.negative} critical voices</span>
          </div>
          <div className="analysis-mini-chart" aria-hidden="true">
            <svg viewBox="0 0 340 88" preserveAspectRatio="none">
              <path className="analysis-mini-area" d="M0 74 35 66 69 30 103 41 137 70 171 58 205 45 239 51 273 29 307 37 340 17V88H0Z" />
              <path className="analysis-mini-line" pathLength="1" d="M0 74 35 66 69 30 103 41 137 70 171 58 205 45 239 51 273 29 307 37 340 17" />
            </svg>
          </div>
          <div className="analysis-risk-note"><Radio size={13} aria-hidden /> Monitor connection, microphone, and case feedback</div>
        </article>

        <article className="analysis-panel analysis-neutral">
          <div className="analysis-neutral-ring" role="meter" aria-label="Neutral reviews proportion" aria-valuemin={0} aria-valuemax={100} aria-valuenow={neutral} style={{ '--neutral': `${neutral * 3.6}deg` } as CSSProperties}>
            <div><CircleMinus size={17} aria-hidden /><strong className="tnum"><Percent value={neutral} active={animate} /></strong></div>
          </div>
          <div className="analysis-neutral-copy">
            <span className="analysis-panel-label">Balanced voices</span>
            <h3>Neutral reviews</h3>
            <p>{sentiment.neutral} reviews sit between praise and concern.</p>
          </div>
        </article>
      </div>

      <div className="analysis-topic-rail">
        <div className="analysis-topic-intro">
          <span><Tag size={15} aria-hidden /> Recurring themes</span>
          <p>What customers mention most</p>
        </div>
        <div className="analysis-topic-list">
          {topics.slice(0, 5).map((topic, index) => (
            <span key={topic.term} className="analysis-topic" style={{ '--topic-index': index, '--relevance': topic.relevance } as CSSProperties}>
              <i aria-hidden />
              <span>{topic.term}</span>
              <small className="tnum">{Math.round(topic.relevance * 100)}</small>
            </span>
          ))}
        </div>
        <Link to={ROUTES.analysis} className="analysis-open-link">Open full analysis <ArrowRight size={16} aria-hidden /></Link>
      </div>
    </section>
  );
}
