import { useState } from 'react';
import { PageContainer, PageHeader } from '@/components/layout/Page';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { ErrorState, LoadingState } from '@/components/ui/states';
import { api } from '@/lib/api';
import { Sparkles, Globe2, Hash, BookOpenCheck } from 'lucide-react';

export default function TextLab() {
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [sentimentResult, setSentimentResult] = useState<any>(null);
  const [languageResult, setLanguageResult] = useState<any>(null);
  const [topicsResult, setTopicsResult] = useState<any>(null);
  const [readabilityResult, setReadabilityResult] = useState<any>(null);

  const handleAnalyze = async () => {
    if (!text.trim()) return;
    setLoading(true);
    setError(null);

    try {
      const [sentiment, lang, topics, read] = await Promise.allSettled([
        api.analyzeSentiment(text),
        api.detectLanguage(text),
        api.extractTopics([text]),
        api.readability(text),
      ]);

      if (sentiment.status === 'fulfilled') setSentimentResult(sentiment.value);
      if (lang.status === 'fulfilled') setLanguageResult(lang.value);
      if (topics.status === 'fulfilled') setTopicsResult(topics.value);
      if (read.status === 'fulfilled') setReadabilityResult(read.value);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Analysis failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <PageContainer>
      <PageHeader
        title="Text Lab"
        subtitle="Paste any customer review or feedback to evaluate mood, language, topics, and reading level."
      />

      <Card className="p-6 space-y-4">
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Paste customer review text here..."
          rows={5}
          className="w-full rounded-xl border border-rp-border bg-rp-surface p-3 text-sm text-rp-navy placeholder:text-rp-muted outline-none focus:border-rp-primary"
          aria-label="Text to analyze"
        />

        <div className="flex justify-end">
          <Button onClick={handleAnalyze} disabled={loading || !text.trim()}>
            {loading ? 'Evaluating...' : 'Analyze Text'}
          </Button>
        </div>

        {error && <ErrorState title="Analysis error" description={error} />}
      </Card>

      {loading && <LoadingState label="Running linguistic analysis..." />}

      {(sentimentResult || languageResult || topicsResult || readabilityResult) && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Mood / Sentiment */}
          <Card className="p-5 space-y-2">
            <h3 className="font-heading font-bold text-rp-navy flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-rp-primary" /> Mood & Tone
            </h3>
            {sentimentResult ? (
              <div className="text-xs space-y-1">
                <p>
                  <strong>Mood:</strong> {sentimentResult.label ?? 'Neutral'}
                </p>
                <p>
                  <strong>Confidence:</strong>{' '}
                  {sentimentResult.confidence != null ? `${(sentimentResult.confidence * 100).toFixed(0)}%` : 'Not available'}
                </p>
              </div>
            ) : (
              <p className="text-xs text-rp-muted">No mood output available.</p>
            )}
          </Card>

          {/* Language */}
          <Card className="p-5 space-y-2">
            <h3 className="font-heading font-bold text-rp-navy flex items-center gap-2">
              <Globe2 className="h-4 w-4 text-rp-primary" /> Language
            </h3>
            {languageResult ? (
              <div className="text-xs space-y-1">
                <p>
                  <strong>Detected:</strong>{' '}
                  {languageResult.detected_language_name ?? languageResult.detected_language ?? 'English'}
                </p>
                <p>
                  <strong>Confidence:</strong>{' '}
                  {languageResult.confidence != null ? `${(languageResult.confidence * 100).toFixed(0)}%` : 'Not available'}
                </p>
              </div>
            ) : (
              <p className="text-xs text-rp-muted">No language output available.</p>
            )}
          </Card>

          {/* Topics */}
          <Card className="p-5 space-y-2">
            <h3 className="font-heading font-bold text-rp-navy flex items-center gap-2">
              <Hash className="h-4 w-4 text-rp-primary" /> Recurring Topics
            </h3>
            {topicsResult?.documents?.[0]?.terms && topicsResult.documents[0].terms.length > 0 ? (
              <div className="flex flex-wrap gap-1.5 pt-1">
                {topicsResult.documents[0].terms.map((t: any, i: number) => (
                  <span
                    key={i}
                    className="rounded-lg bg-rp-primary-light px-2.5 py-1 text-xs font-semibold text-rp-primary"
                  >
                    {t.term ?? t}
                  </span>
                ))}
              </div>
            ) : (
              <p className="text-xs text-rp-muted">No topics extracted.</p>
            )}
          </Card>

          {/* Reading Level */}
          <Card className="p-5 space-y-2">
            <h3 className="font-heading font-bold text-rp-navy flex items-center gap-2">
              <BookOpenCheck className="h-4 w-4 text-rp-primary" /> Reading Level
            </h3>
            {readabilityResult ? (
              <div className="text-xs space-y-1">
                <p>
                  <strong>Ease Score:</strong>{' '}
                  {readabilityResult.flesch_reading_ease?.score != null
                    ? readabilityResult.flesch_reading_ease.score.toFixed(1)
                    : 'Not available'}
                </p>
                <p>
                  <strong>Consensus Grade:</strong>{' '}
                  {readabilityResult.consensus_grade_level != null
                    ? `Grade ${readabilityResult.consensus_grade_level.toFixed(1)}`
                    : 'Not available'}
                </p>
              </div>
            ) : (
              <p className="text-xs text-rp-muted">No readability score available.</p>
            )}
          </Card>
        </div>
      )}
    </PageContainer>
  );
}
