import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import App from '@/App';
import { ProductProvider } from '@/hooks/useProduct';
import { SessionProvider } from '@/hooks/useSession';
import { ROUTES } from '@/lib/routes';

function renderApp(path: string) {
  const qc = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });
  return render(
    <QueryClientProvider client={qc}>
      <SessionProvider>
        <ProductProvider>
          <MemoryRouter initialEntries={[path]}>
            <App />
          </MemoryRouter>
        </ProductProvider>
      </SessionProvider>
    </QueryClientProvider>,
  );
}

describe('Interactive On-Demand Tool Integrations', () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('ANAL-04: executes sentiment evaluation mutation and displays ABSA polarity chips', async () => {
    const user = userEvent.setup();
    const mockSentiment = {
      label: 'positive',
      confidence: 0.94,
      scores: { compound: 0.85, positive: 0.6, neutral: 0.35, negative: 0.05 },
      aspects: {
        battery: {
          aspect: 'battery',
          label: 'positive',
          mention_count: 1,
          average_polarity: 0.9,
          mentions: [{ sentence: 'Battery is great.', polarity: 0.9, label: 'positive' }],
        },
      },
      highlights: [{ token: 'great', adjusted_valence: 0.9, modifiers: [] }],
      model: 'rule-based-absa',
      processing_time_ms: 1.2,
    };

    vi.stubGlobal('fetch', vi.fn().mockImplementation((url: string) => {
      if (url.includes('/api/v1/analysis/sentiment')) {
        return Promise.resolve(new Response(JSON.stringify(mockSentiment), {
          status: 200,
          headers: { 'Content-Type': 'application/json', 'X-Request-ID': 'req-sent-01' },
        }));
      }
      return Promise.reject(new TypeError('offline'));
    }));

    renderApp(ROUTES.analysis);
    const textarea = await screen.findByPlaceholderText(/Type or paste a review to evaluate/i);
    await user.type(textarea, 'Battery is great.');
    const submitBtn = screen.getByRole('button', { name: /^Analyze Sentiment$/i });
    await user.click(submitBtn);

    expect(await screen.findByText('POSITIVE')).toBeInTheDocument();
    expect(screen.getByText('+0.85')).toBeInTheDocument();
    expect(screen.getByText('battery:')).toBeInTheDocument();
    expect(screen.getByText('+0.90')).toBeInTheDocument();
    expect(screen.getByText(/“great”/)).toBeInTheDocument();
  });

  it('LANG-04: executes language detection mutation and displays detection metrics', async () => {
    const user = userEvent.setup();
    const mockLanguage = {
      detected_language: 'en',
      detected_language_name: 'English',
      confidence: 0.99,
      confidence_level: 'high',
      script_fast_path: false,
      candidates: [{ language: 'en', language_name: 'English', confidence: 0.99, score: 0.99 }],
      is_reliable: true,
      text_length: 35,
    };

    vi.stubGlobal('fetch', vi.fn().mockImplementation((url: string) => {
      if (url.includes('/api/v1/analysis/language')) {
        return Promise.resolve(new Response(JSON.stringify(mockLanguage), {
          status: 200,
          headers: { 'Content-Type': 'application/json', 'X-Request-ID': 'req-lang-01' },
        }));
      }
      return Promise.reject(new TypeError('offline'));
    }));

    renderApp(ROUTES.language);
    const textarea = await screen.findByPlaceholderText(/Type or paste any text to detect its language/i);
    await user.type(textarea, 'This is a high quality phone case.');
    const submitBtn = screen.getByRole('button', { name: /^Identify Language$/i });
    await user.click(submitBtn);

    expect(await screen.findByText(/English \(en\)/)).toBeInTheDocument();
    expect(screen.getByText(/high \(99%\)/i)).toBeInTheDocument();
    expect(screen.getByText(/Full N-Gram Profiling/i)).toBeInTheDocument();
  });

  it('READ-03: executes readability complexity audit and displays linguistic metrics', async () => {
    const user = userEvent.setup();
    const mockReadability = {
      flesch_reading_ease: { score: 75.4, band: 'fairly_easy', interpretation: 'Fairly easy' },
      consensus_grade_level: 6.2,
      statistics: { word_count: 18, sentence_count: 2 },
      reading_time_seconds: 4.5,
    };

    vi.stubGlobal('fetch', vi.fn().mockImplementation((url: string) => {
      if (url.includes('/api/v1/analysis/readability')) {
        return Promise.resolve(new Response(JSON.stringify(mockReadability), {
          status: 200,
          headers: { 'Content-Type': 'application/json', 'X-Request-ID': 'req-read-01' },
        }));
      }
      return Promise.reject(new TypeError('offline'));
    }));

    renderApp(ROUTES.readability);
    const textarea = await screen.findByPlaceholderText(/Paste or type a customer review here/i);
    await user.type(textarea, 'The camera is crystal clear and very responsive.');
    const submitBtn = screen.getByRole('button', { name: /^Analyze Text Complexity$/i });
    await user.click(submitBtn);

    expect(await screen.findByText(/75.4 \(Fairly easy\)/)).toBeInTheDocument();
    expect(screen.getByText(/Grade 6.2/)).toBeInTheDocument();
    expect(screen.getByText(/18 words \/ 2 sentences/)).toBeInTheDocument();
    expect(screen.getByText(/4.5s/)).toBeInTheDocument();
  });

  it('TOPIC-05: executes TF-IDF topic extractor on user corpus', async () => {
    const user = userEvent.setup();
    const mockTopics = {
      corpus_size: 2,
      documents: [
        {
          keyphrases: [{ term: 'neural audio', score: 0.95 }],
        },
        {
          keyphrases: [{ term: 'hyper charging', score: 0.88 }],
        },
      ],
    };

    vi.stubGlobal('fetch', vi.fn().mockImplementation((url: string) => {
      if (url.includes('/api/v1/analysis/topics')) {
        return Promise.resolve(new Response(JSON.stringify(mockTopics), {
          status: 200,
          headers: { 'Content-Type': 'application/json', 'X-Request-ID': 'req-top-01' },
        }));
      }
      return Promise.reject(new TypeError('offline'));
    }));

    renderApp(ROUTES.topics);
    const submitBtn = await screen.findByRole('button', { name: /^Extract Live Keyphrases$/i });
    await user.click(submitBtn);

    expect(await screen.findByText(/Analyzed 2 document\(s\) in corpus:/i)).toBeInTheDocument();
    expect(screen.getByText('neural audio')).toBeInTheDocument();
    expect(screen.getByText('(0.95)')).toBeInTheDocument();
    expect(screen.getByText('hyper charging')).toBeInTheDocument();
  });

  it('PRIC-05: executes on-demand price polling and displays fresh snapshot notification', async () => {
    const user = userEvent.setup();
    const mockPriceHistory = {
      product_id: 'prod-1',
      observations_count: 5,
      latest_observed_price: 2499,
      snapshots: [
        { price: 2499, currency: 'INR', observed_at: '2026-10-22T12:00:00Z', source: 'provider' },
      ],
    };

    vi.stubGlobal('fetch', vi.fn().mockImplementation((url: string) => {
      if (url.includes('/check-price')) {
        return Promise.resolve(new Response(JSON.stringify(mockPriceHistory), {
          status: 200,
          headers: { 'Content-Type': 'application/json', 'X-Request-ID': 'req-price-01' },
        }));
      }
      return Promise.reject(new TypeError('offline'));
    }));

    renderApp(ROUTES.analytics);
    const pollBtn = await screen.findByRole('button', { name: /Poll Fresh Price/i });
    await user.click(pollBtn);

    expect(await screen.findByText(/Recorded new snapshot: ₹2,499 \(5 snapshots total\)/i)).toBeInTheDocument();
  });

  it('HARV-05: executes admin CSV import job and reports inserted items count', async () => {
    const user = userEvent.setup();
    const mockJob = {
      id: 42,
      status: 'completed',
      source: 'csv_amazon',
      products_inserted: 12,
      reviews_inserted: 350,
      warning_count: 0,
      created_at: '2026-10-22T10:00:00Z',
    };

    vi.stubGlobal('fetch', vi.fn().mockImplementation((url: string) => {
      if (url.includes('/api/v1/harvester/jobs')) {
        return Promise.resolve(new Response(JSON.stringify(mockJob), {
          status: 200,
          headers: { 'Content-Type': 'application/json', 'X-Request-ID': 'req-job-01' },
        }));
      }
      return Promise.reject(new TypeError('offline'));
    }));

    renderApp(ROUTES.harvester);
    const jobBtn = await screen.findByRole('button', { name: /Run CSV Import Job/i });
    await user.click(jobBtn);

    const confirmBtn = await screen.findByRole('button', { name: /Run Ingestion/i });
    await user.click(confirmBtn);

    expect(await screen.findByText(/Job #42 completed: 12 products, 350 reviews imported/i)).toBeInTheDocument();
  });

  it('NAV-02 & NAV-08: mobile drawer opens via hamburger and closes on backdrop click', async () => {
    const user = userEvent.setup();
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('offline')));

    renderApp(ROUTES.dashboard);
    const menuBtn = screen.getByRole('button', { name: 'Open navigation' });
    await user.click(menuBtn);

    const dialog = await screen.findByRole('dialog', { name: 'Navigation' });
    expect(dialog).toBeInTheDocument();

    const closeButtons = screen.getAllByRole('button', { name: 'Close navigation' });
    const backdrop = closeButtons[0];
    await user.click(backdrop);

    await waitFor(() => {
      expect(screen.queryByRole('dialog', { name: 'Navigation' })).not.toBeInTheDocument();
    });
  });
});
