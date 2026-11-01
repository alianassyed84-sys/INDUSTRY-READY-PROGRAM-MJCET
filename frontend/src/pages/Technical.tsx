import { PageContainer, PageHeader } from '@/components/layout/Page';
import { Card } from '@/components/ui/Card';
import { API_BASE_URL } from '@/lib/api';

export default function Technical() {
  return (
    <PageContainer>
      <PageHeader
        title="Technical Architecture & Details"
        subtitle="Internal system contract, integration routes, and local development specifications."
      />

      <div className="space-y-6 max-w-4xl">
        <Card className="p-6 space-y-3">
          <h2 className="font-heading text-lg font-bold text-rp-navy">Backend Integration URL</h2>
          <p className="text-sm text-rp-text">
            Configured API Base URL:{' '}
            <code className="rounded bg-rp-primary-light px-2 py-0.5 text-xs font-mono text-rp-primary">
              {API_BASE_URL}
            </code>
          </p>
        </Card>

        <Card className="p-6 space-y-3">
          <h2 className="font-heading text-lg font-bold text-rp-navy">Contract Verification Endpoints</h2>
          <pre className="overflow-x-auto rounded-xl border border-rp-border bg-rp-surface p-4 text-xs font-mono leading-relaxed text-rp-text">
{`GET  /api/v1/health                                 (Liveness)
GET  /api/v1/ready                                  (Readiness)
GET  /api/v1/harvester/products?limit=100           (All products)
GET  /api/v1/harvester/products/{id}                (Product detail)
GET  /api/v1/harvester/products/{id}/insights       (Product insights)
GET  /api/v1/harvester/reviews?product_id={id}      (Reviews)
GET  /api/v1/harvester/products/{id}/price-history  (Price observations)
POST /api/v1/harvester/products/{id}/check-price    (On-demand price poll)
POST /api/v1/harvester/analyze-url                  (Link inspection)
POST /api/v1/analysis/sentiment                     (Aspect sentiment)
POST /api/v1/analysis/language                      (Language detection)
POST /api/v1/analysis/topics                        (Topic extraction)
POST /api/v1/analysis/readability                   (Readability metrics)`}
          </pre>
        </Card>
      </div>
    </PageContainer>
  );
}
