import { Link } from 'react-router-dom';
import { PageContainer, PageHeader } from '@/components/layout/Page';
import { Card } from '@/components/ui/Card';
import { ROUTES } from '@/lib/routes';
import { API_BASE_URL } from '@/lib/api';

const SECTIONS = [
  ['mission', 'Mission'], ['workflows', 'Workflows'], ['sentiment', 'Sentiment'], ['tfidf', 'TF-IDF topics'], ['language', 'Language ID'],
  ['readability', 'Readability'], ['provenance', 'Data & limits'], ['setup', 'Setup'], ['api', 'API overview'], ['troubleshooting', 'Troubleshooting'], ['version', 'Version'],
] as const;

const Code = ({ children }: { children: string }) => <pre className="overflow-x-auto rounded-2xl bg-rp-navy p-4 text-[13px] leading-relaxed text-[#E5D8FF]"><code>{children}</code></pre>;
const Sec = ({ id, title, children }: { id: string; title: string; children: React.ReactNode }) => (
  <Card id={id} data-reveal className="scroll-mt-28"><h2 className="mb-3 text-[22px] font-extrabold">{title}</h2><div className="space-y-3 text-[15px] leading-relaxed text-rp-text">{children}</div></Card>
);

export default function About() {
  return (
    <PageContainer>
      <PageHeader title="About & Documentation" description="What ReviewPulse does, how its analyses work, and how to run it." />
      <div className="grid gap-6 lg:grid-cols-[220px_1fr]">
        <nav aria-label="On this page" className="lg:sticky lg:top-24 lg:self-start">
          <ul className="flex gap-2 overflow-x-auto pb-2 lg:flex-col lg:gap-1 lg:overflow-visible">
            {SECTIONS.map(([id, label]) => <li key={id} className="shrink-0"><a href={`#${id}`} className="flex min-h-[40px] items-center rounded-xl px-3 text-sm font-semibold text-rp-muted hover:bg-rp-primary-light hover:text-rp-primary-hover">{label}</a></li>)}
          </ul>
        </nav>
        <div className="space-y-6">
          <Sec id="mission" title="Product mission"><p>ReviewPulse helps people understand what customers say about a product by turning large sets of reviews into structured, checkable signals. It is an independent project and is not affiliated with, endorsed by, or sponsored by Amazon.</p></Sec>
          <Sec id="workflows" title="Supported workflows">
            <ul className="list-disc space-y-1.5 pl-5"><li>Browse and filter collected reviews (<Link className="font-semibold text-rp-primary" to={ROUTES.reviews}>Product Reviews</Link>).</li><li>Inspect a product’s analysis (<Link className="font-semibold text-rp-primary" to={ROUTES.analysis}>Review Analysis</Link>), language mix, topics and readability.</li><li>Check price observations and comparisons (<Link className="font-semibold text-rp-primary" to={ROUTES.analytics}>Analytics</Link>).</li><li>Validate an Amazon.in URL in the <Link className="font-semibold text-rp-primary" to={ROUTES.harvester}>Review Harvester</Link>. Live retrieval is still in development.</li></ul>
          </Sec>
          <Sec id="sentiment" title="Sentiment analysis"><p>Each review is classified as positive, neutral or negative, and a polarity score between −1 and +1 summarises overall tone. The computation happens in the backend; the frontend only displays what it returns. Sarcasm, mixed opinions and short text are common sources of error.</p></Sec>
          <Sec id="tfidf" title="TF-IDF topic and keyphrase extraction"><p>TF-IDF weights a term higher when it is frequent in this product’s reviews but rare across the wider collection. The highest-weighted terms become topics, with their frequency and a relevance score. It is a statistical method, not semantic clustering, so synonyms are counted separately.</p></Sec>
          <Sec id="language" title="Language identification"><p>Each review is labelled with its most likely language. Short or mixed-language reviews (for example Hindi written in Latin script) can be misclassified or left unclassified, which is why the Language page reports coverage separately from the distribution.</p></Sec>
          <Sec id="readability" title="Readability analysis"><p>Flesch Reading Ease rates text from very difficult to very easy using sentence and word length. It was designed for English and says nothing about whether a review is useful. See the <Link className="font-semibold text-rp-primary" to={ROUTES.readability}>Readability page</Link> for results.</p></Sec>
          <Sec id="provenance" title="Data provenance and known limitations">
            <ul className="list-disc space-y-1.5 pl-5"><li>Reviews currently load through a CSV-based harvester in the backend. Direct Amazon.in retrieval is not yet available.</li><li>When the backend is unreachable, the UI shows labelled demo fixtures. They are fictional.</li><li>Price history requires multiple stored snapshots; a single lookup cannot show a trend or an all-time high.</li><li>Authentication, report export and job history are not connected to backend endpoints yet.</li></ul>
          </Sec>
          <Sec id="setup" title="Backend setup and frontend startup">
            <p>Start the FastAPI backend following its own README so it serves on the URL below, then run the frontend:</p>
            <Code>{`cp .env.example .env     # sets VITE_API_BASE_URL
npm install
npm run dev              # development server
npm run build            # typecheck + production build
npm test                 # unit and component tests`}</Code>
            <p>Configured API base URL: <code className="rounded bg-rp-primary-light px-1.5 py-0.5 text-[13px]">{API_BASE_URL}</code></p>
          </Sec>
          <Sec id="api" title="API integration overview">
            <p>All requests go through one centralized client in <code className="rounded bg-rp-primary-light px-1.5 py-0.5 text-[13px]">src/lib/api.ts</code> with TanStack Query for caching and cancellation. Verified backend endpoints:</p>
            <Code>{`GET  /api/v1/health                                (Process liveness)
GET  /api/v1/ready                                 (Database readiness check)
GET  /api/v1/harvester/products                    (Paginated product catalog)
GET  /api/v1/harvester/products/{id}               (Detailed product view)
GET  /api/v1/harvester/products/{id}/insights      (NLP sentiment, ratings, topics)
GET  /api/v1/harvester/products/{id}/price-history (Recorded price snapshots)
POST /api/v1/harvester/products/{id}/check-price   (Admin price observation poll)
GET  /api/v1/harvester/reviews                     (Paginated review catalog)
POST /api/v1/harvester/analyze-url                 (On-demand Amazon URL analysis)
POST /api/v1/harvester/jobs                        (Admin CSV dataset import)
POST /api/v1/analysis/readability                  (Linguistic readability metrics)
POST /api/v1/analysis/language                     (Statistical language detection)
POST /api/v1/analysis/sentiment                    (Polarity & aspect sentiment)
POST /api/v1/analysis/topics                       (TF-IDF keyphrase extraction)`}</Code>
            <p>All endpoints run with structured request tracking (<code className="rounded bg-rp-primary-light px-1.5 py-0.5 text-[13px]">X-Request-ID</code>) and cryptographic token validation.</p>
          </Sec>
          <Sec id="troubleshooting" title="Troubleshooting">
            <ul className="list-disc space-y-1.5 pl-5"><li><b>“Demo data” badge shows:</b> the backend could not be reached. Check it is running and that <code>VITE_API_BASE_URL</code> is correct.</li><li><b>Browser CORS errors:</b> allow the frontend origin in the backend’s CORS settings.</li><li><b>Empty charts:</b> the backend did not return that metric; the page shows an unavailable state rather than guessing.</li></ul>
          </Sec>
          <Sec id="version" title="Version and build"><p>Frontend version <b className="tnum">{__APP_VERSION__}</b>. No license or service-level guarantee is stated by this application.</p></Sec>
        </div>
      </div>
    </PageContainer>
  );
}
