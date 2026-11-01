import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import App from '@/App';
import { ProductProvider } from '@/hooks/useProduct';
import { SessionProvider } from '@/hooks/useSession';
import { productRoute } from '@/lib/routes';

function renderOverview(productId = 'demo-1') {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={qc}>
      <SessionProvider>
        <ProductProvider>
          <MemoryRouter initialEntries={[productRoute(productId, 'overview')]}>
            <App />
          </MemoryRouter>
        </ProductProvider>
      </SessionProvider>
    </QueryClientProvider>,
  );
}

describe('Product Workspace: Overview Tab (Amazon-Style Customer Reviews Intelligence)', () => {
  it('renders Customer reviews section with star distribution bars', async () => {
    renderOverview();

    // Customer reviews heading
    expect(await screen.findByRole('heading', { name: /^Customer reviews$/i })).toBeInTheDocument();

    // 5-star distribution labels
    expect(screen.getByText('5 star')).toBeInTheDocument();
    expect(screen.getByText('4 star')).toBeInTheDocument();
    expect(screen.getByText('3 star')).toBeInTheDocument();
    expect(screen.getByText('2 star')).toBeInTheDocument();
    expect(screen.getByText('1 star')).toBeInTheDocument();
  });

  it('renders Customers say section with synthesis and topic chips', async () => {
    renderOverview();

    // Customers say heading and generator badge
    expect(await screen.findByRole('heading', { name: /^Customers say$/i })).toBeInTheDocument();
    expect(screen.getByText(/Generated from customer review text/i)).toBeInTheDocument();

    // Select to learn more chips section
    expect(screen.getByText(/Select to learn more/i)).toBeInTheDocument();
  });

  it('renders authentic customer quotes section', async () => {
    renderOverview();

    // Customer quotes header
    expect(await screen.findByRole('heading', { name: /^Customer quotes$/i })).toBeInTheDocument();

    // Link to view all reviews
    expect(screen.getByRole('link', { name: /View all reviews/i })).toBeInTheDocument();
  });

  it('renders product photo thumbnail and Reviews with images gallery', async () => {
    renderOverview();

    // Header image thumbnail
    const headerImg = await screen.findByAltText('Sample Wireless Earbuds');
    expect(headerImg).toBeInTheDocument();
    expect(headerImg).toHaveAttribute('src', '/products/AMZN-AIRPODS-PRO2.jpg');

    // Reviews with images section
    expect(screen.getByRole('heading', { name: /^Reviews with images$/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /See all photos/i })).toBeInTheDocument();
  });
});
