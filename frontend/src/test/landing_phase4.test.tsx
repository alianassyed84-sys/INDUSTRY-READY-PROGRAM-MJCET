import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Landing from '@/pages/Landing';
import { MotionToggle } from '@/components/motion/MotionToggle';
import { MotionProvider } from '@/hooks/useMotion';

describe('Phase 4: Landing Page & Plain Language Verification', () => {
  const renderLanding = () => {
    const qc = new QueryClient();
    return render(
      <QueryClientProvider client={qc}>
        <MotionProvider>
          <MemoryRouter>
            <Landing />
          </MemoryRouter>
        </MotionProvider>
      </QueryClientProvider>,
    );
  };

  it('renders both entry points: product-link input and Upload a dataset button', () => {
    renderLanding();
    expect(screen.getByLabelText(/product URL/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Upload a dataset/i })).toBeInTheDocument();
  });

  it('contains zero instances of forbidden jargon on landing screen', () => {
    renderLanding();
    expect(screen.queryByText(/Average polarity/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Project harvester · CSV based/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Signal preview/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Friction signal/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Review health/i)).not.toBeInTheDocument();
  });

  it('renders Example preview label on sample analysis card', () => {
    renderLanding();
    expect(screen.getByText('Example preview')).toBeInTheDocument();
  });

  it('renders MotionToggle with proper accessibility labels for reduced motion', () => {
    render(
      <MotionProvider>
        <MotionToggle />
      </MotionProvider>,
    );
    expect(screen.getByRole('button', { name: /animations/i })).toBeInTheDocument();
  });
});
