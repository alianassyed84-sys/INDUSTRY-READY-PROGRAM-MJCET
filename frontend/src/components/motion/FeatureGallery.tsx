import { useEffect, useRef, useState, type CSSProperties } from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, ArrowRight, BookOpenCheck, Globe2, Hash, LineChart, Pause, Play, SmilePlus } from 'lucide-react';
import { useMotion } from '@/hooks/useMotion';
import { ROUTES } from '@/lib/routes';
import './feature-gallery.css';

const LENSES = [
  { title: 'Sentiment', eyebrow: 'Read the feeling', text: 'See the positive, neutral, and negative signals behind every customer opinion.', icon: SmilePlus, color: '191 137 255', to: ROUTES.products },
  { title: 'Topics', eyebrow: 'Find the patterns', text: 'Discover the recurring themes, standout features, and complaints worth your attention.', icon: Hash, color: '224 139 204', to: ROUTES.products },
  { title: 'Language', eyebrow: 'Hear every voice', text: 'Explore the languages your customers use and the confidence behind each classification.', icon: Globe2, color: '96 214 203', to: ROUTES.products },
  { title: 'Readability', eyebrow: 'Bring clarity', text: 'Understand how easy reviews are to read with reading ease and grade-level insights.', icon: BookOpenCheck, color: '147 175 255', to: ROUTES.products },
  { title: 'Price monitoring', eyebrow: 'Follow the changes', text: 'Connect the story over time with stored price observations as snapshots become available.', icon: LineChart, color: '240 197 106', to: ROUTES.products },
];

function LensArt({ index }: { index: number }) {
  return (
    <div className={`lens-art lens-art-${index}`} aria-hidden="true">
      <div className="lens-art-grid" />
      {index === 0 && (
        <svg viewBox="0 0 300 180">
          <circle cx="150" cy="90" r="56" fill="none" stroke="currentColor" strokeOpacity=".12" strokeWidth="16" />
          <circle cx="150" cy="90" r="56" fill="none" stroke="currentColor" strokeWidth="16" strokeDasharray="245 352" strokeLinecap="round" transform="rotate(-90 150 90)" />
          <path d="M128 98q22 24 44 0" fill="none" stroke="currentColor" strokeWidth="4" strokeLinecap="round" />
          <circle cx="132" cy="78" r="3" fill="currentColor" />
          <circle cx="168" cy="78" r="3" fill="currentColor" />
        </svg>
      )}
      {index === 1 && (
        <div className="lens-topic-cloud">
          <span>Build quality</span>
          <span>Battery life</span>
          <span>Sound quality</span>
          <span>Comfort</span>
          <span>Value</span>
        </div>
      )}
      {index === 2 && (
        <svg viewBox="0 0 300 180">
          <g fill="none" stroke="currentColor">
            <circle cx="150" cy="90" r="65" strokeOpacity=".6" />
            <ellipse cx="150" cy="90" rx="28" ry="65" />
            <ellipse cx="150" cy="90" rx="65" ry="24" />
            <path d="M85 90h130M150 25v130" strokeOpacity=".5" />
          </g>
          <g fill="currentColor">
            <circle cx="114" cy="70" r="5" />
            <circle cx="174" cy="104" r="5" />
            <circle cx="155" cy="42" r="4" />
          </g>
        </svg>
      )}
      {index === 3 && (
        <div className="lens-document">
          <div className="lens-document-title">Clear words.<br />Better understanding.</div>
          <i /><i /><i />
          <div className="lens-document-line"><span /> <span /> <span /></div>
        </div>
      )}
      {index === 4 && (
        <svg viewBox="0 0 300 180">
          <path d="M28 145H272M28 100H272M28 55H272" fill="none" stroke="currentColor" strokeOpacity=".13" />
          <path d="M28 130 70 112 113 121 155 73 198 88 240 42 272 52" fill="none" stroke="currentColor" strokeWidth="3" strokeLinejoin="round" strokeLinecap="round" />
          {[[28, 130], [70, 112], [113, 121], [155, 73], [198, 88], [240, 42], [272, 52]].map(([x, y]) => (
            <circle key={x} cx={x} cy={y} r="4" fill="currentColor" />
          ))}
        </svg>
      )}
      <span className="lens-art-caption">Illustrative preview</span>
    </div>
  );
}

export default function FeatureGallery() {
  const [active, setActive] = useState(0);
  const [paused, setPaused] = useState(false);
  const touchStart = useRef<number | null>(null);
  const { enabled } = useMotion();

  // Continuous smooth auto-rotation
  const rotating = !paused;

  const choose = (index: number) => {
    setActive((index + LENSES.length) % LENSES.length);
  };

  // Continuous loop transition every 2.4 seconds
  useEffect(() => {
    if (!rotating) return;
    const timer = window.setInterval(() => {
      setActive((value) => (value + 1) % LENSES.length);
    }, 2400);
    return () => window.clearInterval(timer);
  }, [rotating]);

  return (
    <section
      id="features"
      className="lens-section scroll-mt-24"
      aria-labelledby="lens-heading"
      aria-roledescription="carousel"
      onKeyDown={(event) => {
        if (event.key === 'ArrowRight' || event.key === 'ArrowLeft') {
          event.preventDefault();
          choose(active + (event.key === 'ArrowRight' ? 1 : -1));
        }
      }}
    >
      <div className="lens-heading" data-scroll>
        <span className="lens-kicker">One product. A fuller picture.</span>
        <h2 id="lens-heading">Five lenses on <span>every product.</span></h2>
        <p>Different perspectives. Connected insights. Explore what every review can tell you.</p>
      </div>

      <div
        className="lens-stage"
        data-rotating={rotating}
        onTouchStart={(event) => {
          touchStart.current = event.touches[0].clientX;
        }}
        onTouchEnd={(event) => {
          if (touchStart.current !== null) {
            const delta = event.changedTouches[0].clientX - touchStart.current;
            if (Math.abs(delta) > 45) choose(active + (delta < 0 ? 1 : -1));
          }
          touchStart.current = null;
        }}
      >
        {LENSES.map(({ title, eyebrow, text, icon: Icon, color }, index) => {
          const offset = ((index - active + 7) % 5) - 2;
          return (
            <button
              type="button"
              key={title}
              className="lens-card"
              data-active={index === active}
              aria-label={`Show ${title} lens`}
              aria-pressed={index === active}
              tabIndex={index === active ? 0 : -1}
              onClick={() => choose(index)}
              style={{
                '--lens-color': color,
                '--offset': offset,
                '--distance': Math.abs(offset),
                zIndex: 5 - Math.abs(offset),
              } as CSSProperties}
            >
              <div className="lens-card-inner">
                <div className="lens-card-top">
                  <span><Icon size={18} /></span>
                  <span>0{index + 1} / 05</span>
                </div>
                <LensArt index={index} />
                <div className="lens-card-copy">
                  <span className="lens-eyebrow">{eyebrow}</span>
                  <h3>{title}</h3>
                  <p>{text}</p>
                  <span className="lens-card-footer">
                    Explore the perspective <ArrowRight size={16} />
                  </span>
                </div>
              </div>
            </button>
          );
        })}
      </div>

      <div className="lens-controls">
        <button
          type="button"
          className="lens-control"
          aria-label="Previous lens"
          onClick={() => choose(active - 1)}
        >
          <ArrowLeft size={18} />
        </button>
        <div className="lens-dots" aria-label="Choose a lens">
          {LENSES.map(({ title }, index) => (
            <button
              type="button"
              key={title}
              aria-label={`Select ${title}`}
              aria-pressed={index === active}
              onClick={() => choose(index)}
            >
              <span />
            </button>
          ))}
        </div>
        <button
          type="button"
          className="lens-control"
          aria-label="Next lens"
          onClick={() => choose(active + 1)}
        >
          <ArrowRight size={18} />
        </button>
        <button
          type="button"
          className="lens-control lens-play"
          disabled={!enabled}
          aria-label={paused || !enabled ? 'Start continuous card motion' : 'Pause continuous card motion'}
          onClick={() => setPaused((value) => !value)}
        >
          {paused || !enabled ? <Play size={15} /> : <Pause size={15} />}
        </button>
      </div>

      <div className="lens-destination" aria-live={rotating ? 'off' : 'polite'}>
        <Link to={LENSES[active].to}>
          Open {LENSES[active].title.toLowerCase()} <ArrowRight size={15} />
        </Link>
      </div>
    </section>
  );
}
