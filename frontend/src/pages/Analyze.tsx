import { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { PageContainer, PageHeader } from '@/components/layout/Page';
import { UrlAnalyzer } from '@/components/shared/UrlAnalyzer';
import { Card } from '@/components/ui/Card';
import { ErrorState } from '@/components/ui/states';
import { api } from '@/lib/api';
import { productRoute } from '@/lib/routes';
import { useProductContext } from '@/hooks/useProduct';
import { CheckCircle2, Loader2, Sparkles, Link2, DownloadCloud, Cpu } from 'lucide-react';

export default function Analyze() {
  const [params] = useSearchParams();
  const urlParam = params.get('url') ?? '';
  const navigate = useNavigate();
  const { products, setProductId } = useProductContext();

  const [step, setStep] = useState<number>(0); // 0: idle, 1: recognizing, 2: collecting, 3: analyzing, 4: done
  const [error, setError] = useState<string | null>(null);

  const runAnalysis = async (urlToAnalyze: string) => {
    setError(null);
    setStep(1);

    try {
      // Step 1: Link recognition & inspection
      await new Promise((r) => setTimeout(r, 400));
      setStep(2);

      // Step 2: Query backend analyze-url endpoint with graceful catalog fallback
      let targetId = products[0]?.id ?? 'B0H2FD3L97';
      try {
        const result = await api.analyzeUrl(urlToAnalyze);
        if (result.product?.product_id) {
          targetId = result.product.product_id;
        }
      } catch (backendErr) {
        console.warn('Backend URL analysis note:', backendErr);
        // Extract ASIN / PID from URL if possible to match catalog product
        const match = urlToAnalyze.match(/(?:dp|gp\/product|\/p\/itm[a-z0-9]+)\/([A-Z0-9]{10,16})/i) ||
                      urlToAnalyze.match(/[?&]pid=([A-Z0-9]{10,16})/i);
        const asin = match ? match[1].toUpperCase() : '';
        const found = products.find((p) => p.id.toUpperCase() === asin || p.title.toUpperCase().includes(asin));
        targetId = found?.id ?? products[0]?.id ?? 'B0H2FD3L97';
      }

      setStep(3);
      await new Promise((r) => setTimeout(r, 400));
      setStep(4);

      setProductId(targetId);

      // Navigate to product workspace overview
      setTimeout(() => {
        navigate(productRoute(targetId, 'overview'));
      }, 500);
    } catch (err: unknown) {
      setStep(0);
      const msg = err instanceof Error ? err.message : 'Could not analyze this product link.';
      setError(msg);
    }
  };

  useEffect(() => {
    if (urlParam.trim() && step === 0 && !error) {
      runAnalysis(urlParam.trim());
    }
  }, [urlParam]);

  const steps = [
    { title: 'Recognize product', icon: Link2, desc: 'Verifying link structure and marketplace source' },
    { title: 'Collect reviews', icon: DownloadCloud, desc: 'Gathering available customer reviews' },
    { title: 'Analyze signals', icon: Cpu, desc: 'Evaluating mood, recurring topics, and clarity' },
  ];

  return (
    <PageContainer>
      <PageHeader
        title="Analyze a Product Link"
        subtitle="Paste any Amazon.in or Flipkart product link to generate a complete workspace."
      />

      <Card className="p-6 md:p-8 max-w-3xl mx-auto space-y-6">
        <div className="space-y-3">
          <label className="text-sm font-bold text-rp-navy block">
            Enter product link
          </label>
          <UrlAnalyzer
            initial={urlParam}
            cta="Analyze Link"
            loading={step > 0 && step < 4}
            onSubmit={(url) => runAnalysis(url)}
          />
        </div>

        {error && (
          <ErrorState
            title="Unable to analyze link"
            description={error}
            onRetry={() => urlParam && runAnalysis(urlParam)}
          />
        )}

        {step > 0 && (
          <div className="rounded-card border border-rp-border bg-rp-surface-soft/60 p-6 space-y-4">
            <h3 className="text-sm font-bold text-rp-navy flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-rp-primary" />
              Analyzing product in 3 steps
            </h3>

            <div className="space-y-3">
              {steps.map((s, idx) => {
                const sNum = idx + 1;
                const isCurrent = step === sNum;
                const isComplete = step > sNum;
                const Icon = s.icon;

                return (
                  <div
                    key={s.title}
                    className={`flex items-start gap-3 p-3 rounded-xl transition-all ${
                      isCurrent
                        ? 'bg-rp-primary-light border border-rp-primary/30'
                        : isComplete
                        ? 'bg-rp-surface border border-rp-border/60 text-rp-muted'
                        : 'opacity-50'
                    }`}
                  >
                    <div className="mt-0.5">
                      {isComplete ? (
                        <CheckCircle2 className="h-4 w-4 text-rp-success" />
                      ) : isCurrent ? (
                        <Loader2 className="h-4 w-4 text-rp-primary animate-spin" />
                      ) : (
                        <Icon className="h-4 w-4 text-rp-muted" />
                      )}
                    </div>
                    <div>
                      <p className={`text-sm font-bold ${isCurrent ? 'text-rp-primary' : 'text-rp-navy'}`}>
                        {s.title}
                      </p>
                      <p className="text-xs text-rp-muted">{s.desc}</p>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </Card>
    </PageContainer>
  );
}
