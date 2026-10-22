import { Component, type ErrorInfo, type ReactNode } from 'react';
import { AlertTriangle, RotateCcw } from 'lucide-react';
import { Button } from '@/components/ui/Button';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
  public override state: State = { hasError: false };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public override componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Unhandled UI exception in ErrorBoundary:', error, errorInfo);
  }

  public override render() {
    if (this.state.hasError) {
      return (
        <div role="alert" className="grid min-h-screen place-items-center bg-rp-bg p-6 text-center">
          <div className="max-w-md space-y-4 rounded-card border border-rp-coral/30 bg-rp-surface p-8 shadow-card">
            <span className="mx-auto grid h-12 w-12 place-items-center rounded-2xl bg-rp-coral/15 text-rp-coral">
              <AlertTriangle className="h-6 w-6" aria-hidden />
            </span>
            <h1 className="text-xl font-extrabold text-rp-navy">An unexpected error occurred</h1>
            <p className="text-sm text-rp-muted">
              {this.state.error?.message || 'A client-side error prevented this page from rendering correctly.'}
            </p>
            <Button
              variant="primary"
              className="mt-2"
              onClick={() => {
                this.setState({ hasError: false, error: undefined });
                window.location.reload();
              }}
            >
              <RotateCcw className="h-4 w-4" aria-hidden />
              Reload Application
            </Button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
