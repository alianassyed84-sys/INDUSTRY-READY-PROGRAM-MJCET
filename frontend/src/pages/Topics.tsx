import { useMemo, useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip as RTooltip, XAxis, YAxis } from 'recharts';
import { ChevronDown, Info, Search } from 'lucide-react';
import { PageContainer, PageHeader } from '@/components/layout/Page';
import { Card, CardHeader } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { DataSourceBadge, EmptyState, ErrorState, LoadingBlock } from '@/components/ui/states';
import { ChartCard } from '@/components/shared/ChartCard';
import { ProductSelect } from '@/components/shared/ProductSelect';
import { CHART } from '@/components/shared/charts';
import { useInsights } from '@/hooks/useProduct';
import { cn } from '@/lib/utils';
import { api, type ApiError } from '@/lib/api';

export default function Topics() {
  const q = useInsights();
  const [term, setTerm] = useState('');
  const [open, setOpen] = useState<string | null>(null);
  const [corpusText, setCorpusText] = useState(
    'The battery life is amazing and the camera is fantastic.\nPoor battery performance and the display is dull.\nGreat screen quality but charging takes too long.',
  );
  const topicsMutation = useMutation({
    mutationFn: (docs: string[]) => api.extractTopics(docs, 5),
  });
  const env = q.data;
  const topics = env?.data.topics ?? [];
  const shown = useMemo(() => topics.filter((t) => t.term.toLowerCase().includes(term.trim().toLowerCase())), [topics, term]);

  return (
    <PageContainer>
      <PageHeader title="Topic Extraction" description="The terms and phrases that stand out across a product's reviews." actions={<ProductSelect />} meta={env && <DataSourceBadge source={env.source} reason={env.fallbackReason} />} />
      {q.isLoading && <LoadingBlock label="Loading topics" />}
      {q.isError && (
        <ErrorState
          title="Could not load topics"
          description={(q.error as ApiError)?.message}
          requestId={(q.error as ApiError)?.requestId}
          onRetry={() => q.refetch()}
        />
      )}
      {env && topics.length === 0 && <EmptyState title="No topics available" description="Topics appear after reviews have been analyzed for this product." />}

      {topics.length > 0 && (
        <>
          <div className="grid gap-6 xl:grid-cols-[1.2fr_1fr]">
            <ChartCard title="Topic frequency" subtitle="How many times each term appears" summary={`Topic frequency: ${shown.map((t) => `${t.term} ${t.frequency}`).join(', ')}.`}>
              {shown.length ? (
                <div style={{ height: Math.max(220, shown.length * 44) }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={shown} layout="vertical" margin={{ left: 8, right: 16 }}>
                      <CartesianGrid stroke={CHART.grid} horizontal={false} />
                      <XAxis type="number" allowDecimals={false} tick={CHART.tick} axisLine={false} tickLine={false} />
                      <YAxis type="category" dataKey="term" width={128} tick={CHART.tick} axisLine={false} tickLine={false} />
                      <RTooltip {...CHART.tooltip} />
                      <Bar dataKey="frequency" name="Frequency" fill={CHART.primary} radius={[0, 8, 8, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <EmptyState
                  title="No topics match your search"
                  description={`No extracted topics contain "${term}". Try another keyword or reset the filter.`}
                  action={<Button variant="secondary" onClick={() => setTerm('')}>Clear search</Button>}
                />
              )}
            </ChartCard>

            <div className="space-y-6">
              <Card data-reveal>
                <CardHeader title="Top topics" subtitle="Frequency and TF-IDF relevance" />
                <Input aria-label="Search topics" placeholder="Search topics" leading={<Search className="h-4 w-4" />} value={term} onChange={(e) => setTerm(e.target.value)} />
                <ul className="mt-4 space-y-2.5">
                  {shown.map((t) => {
                    const isOpen = open === t.term;
                    return (
                      <li key={t.term} className={cn('rounded-2xl border bg-rp-surface', isOpen ? 'border-rp-primary-soft' : 'border-rp-border')}>
                        <button onClick={() => setOpen(isOpen ? null : t.term)} aria-expanded={isOpen} className="flex min-h-[52px] w-full items-center gap-3 px-4 text-left">
                          <span className="flex-1 font-semibold capitalize text-rp-navy">{t.term}</span>
                          <Badge tone="primary" className="tnum">{t.frequency}×</Badge>
                          <span className="tnum w-12 text-right text-sm text-rp-muted" title="Relevance score">{t.relevance.toFixed(2)}</span>
                          <ChevronDown className={cn('h-4 w-4 text-rp-muted transition-transform', isOpen && 'rotate-180')} aria-hidden />
                        </button>
                        {isOpen && (
                          <div className="border-t border-rp-border px-4 py-3">
                            <div className="mb-2 h-2 overflow-hidden rounded-full bg-rp-primary-light"><div className="h-full rounded-full bg-rp-primary" style={{ width: `${Math.min(100, t.relevance * 100)}%` }} /></div>
                            {t.snippets?.length ? <ul className="space-y-2">{t.snippets.map((s) => <li key={s} className="rounded-xl bg-rp-surface-soft px-3 py-2 text-sm text-rp-text">“{s}”</li>)}</ul> : <p className="text-sm text-rp-muted">No review snippets were supplied for this topic.</p>}
                          </div>
                        )}
                      </li>
                    );
                  })}
                  {shown.length === 0 && <li className="text-sm text-rp-muted">No matches.</li>}
                </ul>
              </Card>
            </div>
          </div>

          <Card data-reveal tone="featured">
            <div className="flex items-start gap-3">
              <Info className="mt-0.5 h-5 w-5 shrink-0 text-rp-primary" aria-hidden />
              <div>
                <h2 className="text-[17px] font-bold">How keyphrases are extracted</h2>
                <p className="mt-1.5 max-w-3xl text-sm text-rp-muted">Topics come from TF-IDF: terms are weighted higher when they appear often in this product’s reviews but are uncommon across the wider review set. The relevance value is that weighting, scaled by the backend. This is statistical keyphrase extraction; it does not use semantic embeddings, so different wordings of the same idea are counted separately.</p>
              </div>
            </div>
          </Card>
        </>
      )}

      <Card data-reveal className="mt-6">
        <CardHeader
          title="On-Demand TF-IDF Keyphrase Extractor"
          subtitle="Submit custom review texts (one review per line) to extract distinctive unigram and bigram keyphrases"
        />
        <div className="space-y-3">
          <textarea
            className="w-full rounded-2xl border border-rp-border bg-rp-surface p-3 font-mono text-xs focus:border-rp-primary focus:outline-none"
            rows={4}
            placeholder="Enter documents (one per line)..."
            value={corpusText}
            onChange={(e) => setCorpusText(e.target.value)}
          />
          <Button
            variant="primary"
            size="md"
            disabled={!corpusText.trim()}
            loading={topicsMutation.isPending}
            onClick={() => {
              const docs = corpusText
                .split('\n')
                .map((s) => s.trim())
                .filter(Boolean);
              if (docs.length) topicsMutation.mutate(docs);
            }}
          >
            Extract Live Keyphrases
          </Button>
          {topicsMutation.data && (
            <div className="mt-3 space-y-3 rounded-2xl bg-rp-surface-soft p-3.5 text-xs">
              <p className="font-semibold text-rp-navy">
                Analyzed {topicsMutation.data.corpus_size} document(s) in corpus:
              </p>
              {topicsMutation.data.documents.map((doc, idx) => (
                <div key={idx} className="rounded-xl border border-rp-border bg-rp-surface p-2.5">
                  <span className="font-bold text-rp-primary">Review #{idx + 1} Keyphrases: </span>
                  {doc.keyphrases.length ? (
                    <div className="mt-1 flex flex-wrap gap-1.5">
                      {doc.keyphrases.map((kp) => (
                        <span
                          key={kp.term}
                          className="inline-flex items-center gap-1 rounded-md bg-rp-primary-light px-2 py-0.5 font-semibold text-rp-navy"
                        >
                          {kp.term} <span className="text-[10px] text-rp-muted">({kp.score.toFixed(2)})</span>
                        </span>
                      ))}
                    </div>
                  ) : (
                    <span className="text-rp-muted">No distinctive keyphrases found.</span>
                  )}
                </div>
              ))}
            </div>
          )}
          {topicsMutation.isError && (
            <p className="text-xs font-semibold text-rp-coral">
              Extraction failed: {(topicsMutation.error as ApiError).message}
            </p>
          )}
        </div>
      </Card>
    </PageContainer>
  );
}
