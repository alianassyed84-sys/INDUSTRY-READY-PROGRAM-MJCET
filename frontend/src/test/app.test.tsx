import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import App from '@/App';
import { ProductProvider } from '@/hooks/useProduct';
import { SessionProvider } from '@/hooks/useSession';
import { ROUTES } from '@/lib/routes';

function renderAt(path: string) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={qc}><SessionProvider><ProductProvider><MemoryRouter initialEntries={[path]}><App /></MemoryRouter></ProductProvider></SessionProvider></QueryClientProvider>,
  );
}

beforeEach(() => {
  // No backend in tests: every request fails, so pages must fall back to labelled demo data.
  vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('offline')));
});

describe('routes', () => {
  const app: [string, RegExp][] = [
    [ROUTES.dashboard, /Explore the pulse of products/],
    [ROUTES.reviews, /^Product Reviews$/],
    [ROUTES.analysis, /^Review Analysis$/],
    [ROUTES.language, /^Language Detection$/],
    [ROUTES.topics, /^Topic Extraction$/],
    [ROUTES.readability, /^Readability Analysis$/],
    [ROUTES.harvester, /^Review Harvester$/],
    [ROUTES.analytics, /^Analytics & Reports$/],
    [ROUTES.settings, /^Settings & Account$/],
    [ROUTES.about, /^About & Documentation$/],
  ];
  it.each(app)('%s renders inside the shared shell', async (path, heading) => {
    renderAt(path);
    expect(await screen.findByRole('heading', { level: 1, name: heading })).toBeInTheDocument();
    expect(screen.getByRole('navigation', { name: 'Primary' })).toBeInTheDocument();
  });

  it.each([ROUTES.login, ROUTES.register, ROUTES.recover])('%s renders auth screen with prototype notice', async (path) => {
    renderAt(path);
    expect(await screen.findByText(/Prototype: no auth backend connected/)).toBeInTheDocument();
  });

  it('landing page renders headline and both CTAs', async () => {
    renderAt(ROUTES.landing);
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent(/really think/);
    expect(screen.getByRole('button', { name: /Analyze a Product/ })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Explore Dashboard/ })).toBeInTheDocument();
  });
});

describe('data honesty', () => {
  it('labels fallback fixtures as demo data when the backend is unreachable', async () => {
    renderAt(ROUTES.analysis);
    await waitFor(() => expect(screen.getAllByText('Demo data').length).toBeGreaterThan(0));
  });

  it('review search filters the list', async () => {
    const user = userEvent.setup();
    renderAt(ROUTES.reviews);
    await screen.findByText(/matching reviews/);
    await user.type(screen.getByLabelText('Search within reviews'), 'zzzz-no-match');
    expect(await screen.findByText(/No reviews match your filters/)).toBeInTheDocument();
  });

  it('harvester rejects an incomplete URL and never claims retrieval succeeded', async () => {
    const user = userEvent.setup();
    renderAt(ROUTES.harvester);
    await user.type(screen.getByLabelText('Amazon.in product URL'), 'https://www.amazon.in/dp/');
    await user.click(screen.getByRole('button', { name: /^Analyze$/ }));
    expect((await screen.findAllByText(/No ASIN found/)).length).toBeGreaterThan(0);
    expect(screen.queryByText(/retrieval succeeded/i)).not.toBeInTheDocument();
  });

  it('analytics refuses to draw a price trend from fewer than two snapshots', async () => {
    const user = userEvent.setup();
    renderAt(ROUTES.analytics);
    await screen.findByText('Price history');
    await user.type(screen.getByLabelText('From'), '2026-10-09');
    expect(await screen.findByText(/Not enough price observations/)).toBeInTheDocument();
  });

  it('reviews view automatically filters when URL search query parameter is present', async () => {
    renderAt(`${ROUTES.reviews}?q=zzzz-no-match`);
    expect(await screen.findByText(/No reviews match your filters/)).toBeInTheDocument();
  });

  it('settings view prompts user with confirmation dialog before logout', async () => {
    sessionStorage.setItem('rp.prototype.session', JSON.stringify({ name: 'Jane Doe', email: 'jane@example.com' }));
    const user = userEvent.setup();
    renderAt(ROUTES.settings);
    expect(await screen.findByDisplayValue('Jane Doe')).toBeInTheDocument();
    const logoutBtn = screen.getByRole('button', { name: /Log out/i });
    expect(logoutBtn).not.toBeDisabled();
    await user.click(logoutBtn);
    expect(await screen.findByRole('dialog')).toBeInTheDocument();
    expect(screen.getByText(/Are you sure you want to end your session/i)).toBeInTheDocument();
  });
});

describe('error boundary', () => {
  it('catches render errors and renders the recovery UI', async () => {
    const spy = vi.spyOn(console, 'error').mockImplementation(() => {});
    const Broken = () => {
      throw new Error('Test component crash');
    };
    const { ErrorBoundary } = await import('@/components/shared/ErrorBoundary');
    render(
      <ErrorBoundary>
        <Broken />
      </ErrorBoundary>,
    );
    expect(screen.getByRole('alert')).toHaveTextContent(/unexpected error/i);
    expect(screen.getByText('Test component crash')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Reload Application/i })).toBeInTheDocument();
    spy.mockRestore();
  });
});

