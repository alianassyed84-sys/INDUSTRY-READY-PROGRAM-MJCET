import { useEffect, useRef, useState, type CSSProperties } from 'react';
import { Link } from 'react-router-dom';
import { ArrowUpRight, Check, Database, Eye, ShieldCheck } from 'lucide-react';
import { useMotion } from '@/hooks/useMotion';
import { ROUTES } from '@/lib/routes';
import './data-trust.css';

const COMMITMENTS = [
  {
    icon: Eye,
    label: 'Clearly labeled',
    title: 'Demo stays demo',
    text: 'Sample content is always identified and remains separate from live results.',
  },
  {
    icon: Check,
    label: 'Never invented',
    title: 'Missing stays missing',
    text: 'Unavailable fields remain unavailable instead of being filled with guesses.',
  },
  {
    icon: Database,
    label: 'Source visible',
    title: 'Provenance stays attached',
    text: 'The collection method and origin remain clear wherever review data appears.',
  },
];

export default function DataTrust() {
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
    }, { threshold: 0.18 });
    observer.observe(node);
    return () => observer.disconnect();
  }, []);

  return (
    <section
      ref={root}
      id="trust"
      className="data-trust"
      aria-labelledby="data-trust-heading"
      data-visible={entered || !enabled}
    >
      <div className="data-trust-panel">
        <div className="data-trust-scan" aria-hidden="true" />
        <div className="data-trust-intro">
          <span className="data-trust-kicker"><ShieldCheck size={14} aria-hidden="true" /> Data trust</span>
          <h2 id="data-trust-heading">Evidence you can <span>trace.</span></h2>
          <p>ReviewPulse keeps the boundary between observed data, sample data, and unavailable data visible.</p>
          <div className="data-trust-source">
            <span><i /> Current source</span>
            <strong>Data sources · File and link imports</strong>
          </div>
          <Link to={ROUTES.about} className="data-trust-link">
            Read the data policy <ArrowUpRight size={16} aria-hidden="true" />
          </Link>
        </div>

        <ol className="data-trust-list">
          {COMMITMENTS.map(({ icon: Icon, label, title, text }, index) => (
            <li key={title} style={{ '--trust-index': index } as CSSProperties}>
              <span className="data-trust-icon"><Icon size={17} aria-hidden="true" /></span>
              <div>
                <span className="data-trust-label">{label}</span>
                <h3>{title}</h3>
                <p>{text}</p>
              </div>
              <span className="data-trust-number tnum">0{index + 1}</span>
            </li>
          ))}
        </ol>
      </div>

      <p className="data-trust-disclaimer">ReviewPulse is an independent project and is not affiliated with Amazon.</p>
    </section>
  );
}
