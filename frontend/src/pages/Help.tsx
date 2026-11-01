import { Link } from 'react-router-dom';
import { PageContainer, PageHeader } from '@/components/layout/Page';
import { Card } from '@/components/ui/Card';
import { ROUTES } from '@/lib/routes';

export default function Help() {
  return (
    <PageContainer>
      <PageHeader
        title="Help & User Guide"
        subtitle="Learn how to import customer reviews and explore product insights in ReviewPulse."
      />

      <div className="space-y-6 max-w-4xl">
        <Card className="p-6 space-y-3">
          <h2 className="font-heading text-lg font-bold text-rp-navy">1. Getting Data In</h2>
          <p className="text-sm text-rp-text leading-relaxed">
            Data enters ReviewPulse in two ways:
          </p>
          <ul className="list-disc pl-5 text-sm space-y-1.5 text-rp-text">
            <li>
              <strong>Analyze a Link:</strong> Go to{' '}
              <Link to={ROUTES.analyze} className="font-semibold text-rp-primary hover:underline">
                Analyze a Link
              </Link>{' '}
              and paste an Amazon.in or Flipkart product URL.
            </li>
            <li>
              <strong>Import a Dataset:</strong> Go to{' '}
              <Link to={ROUTES.data} className="font-semibold text-rp-primary hover:underline">
                Data Sources
              </Link>{' '}
              to upload an Amazon or Flipkart CSV or JSON dataset with live preview before import.
            </li>
          </ul>
        </Card>

        <Card className="p-6 space-y-3">
          <h2 className="font-heading text-lg font-bold text-rp-navy">2. Exploring Product Workspaces</h2>
          <p className="text-sm text-rp-text leading-relaxed">
            From{' '}
            <Link to={ROUTES.products} className="font-semibold text-rp-primary hover:underline">
              All Products
            </Link>
            , choose any product to open its workspace. Each product workspace includes seven deep-linked tabs:
          </p>
          <ol className="list-decimal pl-5 text-sm space-y-1 text-rp-text">
            <li><strong>Overview:</strong> Key summary metrics, plain-language takeaway, and representative quotes.</li>
            <li><strong>Reviews:</strong> Filterable and searchable customer review list with sentiment tags.</li>
            <li><strong>Sentiment:</strong> Customer mood breakdown and tone across key features.</li>
            <li><strong>Topics:</strong> Recurring themes and phrases mentioned by customers.</li>
            <li><strong>Languages:</strong> Distribution of review languages and readability counts.</li>
            <li><strong>Readability:</strong> Reading clarity and grade levels in plain words.</li>
            <li><strong>Price:</strong> Verified price observations and discount benchmarks.</li>
          </ol>
        </Card>

        <Card className="p-6 space-y-3">
          <h2 className="font-heading text-lg font-bold text-rp-navy">3. Plain Language & Data Honesty</h2>
          <p className="text-sm text-rp-text leading-relaxed">
            ReviewPulse presents every metric in clear, plain words. Missing numbers are shown as &ldquo;Not available&rdquo; rather than artificial zeros, and sample data is always clearly marked.
          </p>
        </Card>
      </div>
    </PageContainer>
  );
}
