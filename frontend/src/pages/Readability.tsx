import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip as RTooltip, XAxis, YAxis } from 'recharts';
import { PageContainer, PageHeader } from '@/components/layout/Page';
import { Card, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { DataSourceBadge, ErrorState, LoadingBlock, UnavailableState } from '@/components/ui/states';
import { KpiCard } from '@/components/shared/KpiCard';
import { ChartCard } from '@/components/shared/ChartCard';
import { ProductSelect } from '@/components/shared/ProductSelect';
import { CHART } from '@/components/shared/charts';
import { useInsights } from '@/hooks/useProduct';
import { api, type ApiError } from '@/lib/api';

/** Standard Flesch Reading Ease bands. */
const band = (s: number) =>
  s >= 90 ? 'Very easy (about 5th grade)' : s >= 80 ? 'Easy' : s >= 70 ? 'Fairly easy' : s >= 60 ? 'Plain English' : s >= 50 ? 'Fairly difficult' : s >= 30 ? 'Difficult' : 'Very difficult';

export default function Readability() {
  const q = useInsights();
  const env = q.data;
  const r = env?.data.readability;
  const [sampleText, setSampleText] = useState('');
  const sampleMutation = useMutation({
    mutationFn: (text: string) => api.readability(text),
  });

  return (
    <PageContainer>
      <PageHeader title="Readability Analysis" description="How easy customer reviews are to read, using the Flesch Reading Ease score." actions={<ProductSelect />} meta={env && <DataSourceBadge source={env.source} reason={env.fallbackReason} />} />
      {q.isLoading && <LoadingBlock label="Loading readability" />}
      {q.isError && (
        <ErrorState
          title="Could not load readability"
          description={(q.error as ApiError)?.message}
          requestId={(q.error as ApiError)?.requestId}
          onRetry={() => q.refetch()}
        />
      )}
      {env && !r && <UnavailableState title="Readability unavailable" description="The backend did not return readability results for this product. Nothing is estimated in the browser." />}

      {r && (
        <>
          <section aria-label="Readability summary" className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <KpiCard label="Flesch Reading Ease" value={r.fleschReadingEase.toFixed(1)} hint={band(r.fleschReadingEase)} />
            <KpiCard label="Grade level" value={r.gradeLevel.toFixed(1)} hint="Estimated US school grade" />
            <KpiCard label="Reviews analyzed" value={r.analyzed} hint="Included in the score" />
            <KpiCard label="Excluded" value={r.excluded} hint="Too short, blank or unsupported" />
          </section>

          <div className="grid gap-6 xl:grid-cols-[1.3fr_1fr]">
            <ChartCard title="Readability distribution" subtitle="Reviews per readability level" summary={`Readability levels: ${r.distribution.map((d) => `${d.label} ${d.count}`).join(', ')}.`}>
              <div className="h-[290px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={r.distribution} margin={{ left: -12, right: 8 }}>
                    <CartesianGrid stroke={CHART.grid} vertical={false} />
                    <XAxis dataKey="label" tick={CHART.tick} axisLine={false} tickLine={false} />
                    <YAxis allowDecimals={false} tick={CHART.tick} axisLine={false} tickLine={false} />
                    <RTooltip {...CHART.tooltip} />
                    <Bar dataKey="count" name="Reviews" radius={[8, 8, 0, 0]}>{r.distribution.map((d) => <Cell key={d.label} fill={d.count === 0 ? 'var(--rp-border)' : CHART.primary} />)}</Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
              <p className="mt-2 text-xs text-rp-muted">A level with 0 reviews means none were found at that level, not that data is missing.</p>
            </ChartCard>

            <div className="space-y-6">
              <Card data-reveal tone="featured">
                <CardHeader title="What the score means" />
                <p className="tnum font-heading text-4xl font-extrabold text-rp-primary">{r.fleschReadingEase.toFixed(1)}</p>
                <p className="mt-1 font-semibold text-rp-navy">{band(r.fleschReadingEase)}</p>
                <p className="mt-2 text-sm text-rp-muted">Higher scores mean easier text. Typical short consumer reviews score high because they use short sentences and common words.</p>
              </Card>
              <Card data-reveal>
                <CardHeader title="Coverage" />
                <p className="text-sm text-rp-muted"><b className="tnum text-rp-navy">{r.analyzed}</b> of <b className="tnum text-rp-navy">{r.analyzed + r.excluded}</b> reviews were scored; <b className="tnum text-rp-navy">{r.excluded}</b> were excluded.</p>
              </Card>
            </div>
          </div>

          <div className="grid gap-6 lg:grid-cols-2">
            <Card data-reveal>
              <CardHeader title="On-Demand Readability Auditor" subtitle="Evaluate any single review using the backend's classic readability algorithms" />
              <div className="space-y-3">
                <textarea
                  className="w-full rounded-2xl border border-rp-border bg-rp-surface p-3 text-sm focus:border-rp-primary focus:outline-none"
                  rows={3}
                  placeholder="Paste or type a customer review here to analyze its linguistic complexity..."
                  value={sampleText}
                  onChange={(e) => setSampleText(e.target.value)}
                />
                <Button
                  variant="primary"
                  size="md"
                  disabled={!sampleText.trim()}
                  loading={sampleMutation.isPending}
                  onClick={() => sampleMutation.mutate(sampleText.trim())}
                >
                  Analyze Text Complexity
                </Button>
                {sampleMutation.data && (
                  <div className="mt-3 space-y-2 rounded-2xl bg-rp-surface-soft p-3.5 text-xs">
                    <div className="flex justify-between">
                      <span className="font-semibold text-rp-navy">Flesch Reading Ease:</span>
                      <span className="font-bold text-rp-primary">
                        {sampleMutation.data.flesch_reading_ease.score?.toFixed(1) ?? 'N/A'} (
                        {sampleMutation.data.flesch_reading_ease.interpretation ?? 'Unclassified'})
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="font-semibold text-rp-navy">Consensus Grade Level:</span>
                      <span>Grade {sampleMutation.data.consensus_grade_level?.toFixed(1) ?? 'N/A'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="font-semibold text-rp-navy">Word & Sentence Count:</span>
                      <span>
                        {sampleMutation.data.statistics.word_count} words /{' '}
                        {sampleMutation.data.statistics.sentence_count} sentences
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="font-semibold text-rp-navy">Est. Reading Time:</span>
                      <span>{sampleMutation.data.reading_time_seconds.toFixed(1)}s</span>
                    </div>
                  </div>
                )}
                {sampleMutation.isError && (
                  <p className="text-xs font-semibold text-rp-coral">
                    Analysis failed: {(sampleMutation.error as ApiError).message}
                  </p>
                )}
              </div>
            </Card>
            <Card data-reveal>
              <CardHeader title="Limitations" />
              <ul className="list-disc space-y-2 pl-5 text-sm text-rp-muted">
                <li>The Flesch formula was designed for English. Scores for other languages, or mixed-language reviews, are not reliable.</li>
                <li>Very short or blank reviews give unstable scores and are excluded.</li>
                <li>Readability measures sentence and word length, not whether a review is clear, helpful or accurate.</li>
              </ul>
            </Card>
          </div>
        </>
      )}
    </PageContainer>
  );
}
