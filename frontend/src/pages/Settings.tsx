import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { LogOut, Palette } from 'lucide-react';
import { PageContainer, PageHeader } from '@/components/layout/Page';
import { Card, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Input } from '@/components/ui/Input';
import { Dialog } from '@/components/ui/Dialog';
import { EmptyState, UnavailableState } from '@/components/ui/states';
import { useSession } from '@/hooks/useSession';
import { useProductContext } from '@/hooks/useProduct';
import { api, API_BASE_URL } from '@/lib/api';
import { ROUTES } from '@/lib/routes';

const SWATCHES = [['Primary', '#7138F5'], ['Navy', '#171B50'], ['Ivory', '#FAF7F2'], ['Coral', '#F36B57']] as const;

export default function Settings() {
  const { user, signOut } = useSession();
  const nav = useNavigate();
  const [confirmLogout, setConfirmLogout] = useState(false);
  const { source, fallbackReason } = useProductContext();
  const health = useQuery({ queryKey: ['health'], queryFn: ({ signal }) => api.health(signal), retry: false, staleTime: 15_000 });
  const ready = useQuery({ queryKey: ['ready'], queryFn: ({ signal }) => api.ready(signal), retry: false, staleTime: 15_000 });

  return (
    <PageContainer>
      <PageHeader title="Settings & Account" description="Your profile, session and development status." />
      <div className="grid gap-6 xl:grid-cols-2">
        <Card data-reveal>
          <CardHeader title="Profile information" action={<Badge tone="warning">Prototype session</Badge>} />
          {user ? (
            <div className="space-y-4">
              <Input label="Full name" value={user.name} readOnly />
              <Input label="Email" value={user.email} readOnly hint="Read-only: no backend is connected to save profile changes." />
            </div>
          ) : (
            <EmptyState title="You are not logged in" description="Log in to see profile details." action={<Button onClick={() => nav(ROUTES.login)}>Log in</Button>} />
          )}
        </Card>

        <Card data-reveal>
          <CardHeader title="Account details" />
          <dl className="space-y-3 text-sm">
            <div className="flex justify-between gap-3"><dt className="text-rp-muted">Session type</dt><dd className="font-semibold">Device-local prototype</dd></div>
            <div className="flex justify-between gap-3"><dt className="text-rp-muted">Storage</dt><dd className="font-semibold">Browser session (cleared on close)</dd></div>
            <div className="flex justify-between gap-3"><dt className="text-rp-muted">Authentication mode</dt><dd className="font-semibold">Clerk JWT compatible (dev bypass enabled)</dd></div>
          </dl>
        </Card>

        <Card data-reveal>
          <CardHeader title="Password and notifications" />
          <UnavailableState title="Not supported by the backend yet" description="Password changes and notification preferences need account endpoints that are not available in this milestone." />
        </Card>

        <Card data-reveal>
          <CardHeader title="Theme" action={<Palette className="h-5 w-5 text-rp-primary" aria-hidden />} />
          <p className="text-sm text-rp-muted">ReviewPulse uses the <b className="text-rp-navy">Lavender Luxe</b> light theme. There is no theme switcher.</p>
          <ul className="mt-4 flex flex-wrap gap-3">
            {SWATCHES.map(([n, c]) => <li key={n} className="flex items-center gap-2 text-sm"><span className="h-6 w-6 rounded-lg border border-rp-border" style={{ background: c }} aria-hidden />{n}</li>)}
          </ul>
        </Card>

        <Card data-reveal>
          <CardHeader title="Backend status" subtitle="Development & infrastructure information" />
          <dl className="space-y-3 text-sm">
            <div className="flex justify-between gap-3"><dt className="text-rp-muted">API base URL</dt><dd className="break-all font-mono text-[13px] font-semibold">{API_BASE_URL}</dd></div>
            <div className="flex justify-between gap-3"><dt className="text-rp-muted">Service name</dt><dd className="font-mono text-[13px] font-semibold">{health.data?.service ?? 'reviewpulse-api'}</dd></div>
            <div className="flex justify-between gap-3"><dt className="text-rp-muted">Process liveness</dt><dd>{health.isLoading ? <Badge>Checking</Badge> : health.isError ? <Badge tone="danger">Unreachable</Badge> : <Badge tone="success">Active (HTTP 200)</Badge>}</dd></div>
            <div className="flex justify-between gap-3"><dt className="text-rp-muted">Database connectivity</dt><dd>{ready.isLoading ? <Badge>Checking</Badge> : ready.isError ? <Badge tone="danger">Unavailable</Badge> : ready.data?.database === 'ok' ? <Badge tone="success">Connected</Badge> : <Badge tone="warning">{ready.data?.database ?? 'Not ready'}</Badge>}</dd></div>
            <div className="flex justify-between gap-3"><dt className="text-rp-muted">Data in use</dt><dd>{source === 'demo' ? <Badge tone="warning">Demo data</Badge> : <Badge tone="success">Live database</Badge>}</dd></div>
          </dl>
          <Button variant="secondary" className="mt-4" onClick={() => { void health.refetch(); void ready.refetch(); }} loading={health.isFetching || ready.isFetching}>Re-check</Button>
          {source === 'demo' && fallbackReason && <p className="mt-3 text-xs text-rp-muted">Showing fixtures because: {fallbackReason}.</p>}
        </Card>

        <Card data-reveal>
          <CardHeader title="Data sources" />
          <p className="text-sm text-rp-muted">Review data comes from the backend harvester (CSV-based today). When the backend is unreachable, clearly labelled demo fixtures are shown instead; they are never blended with live results.</p>
        </Card>
      </div>

      <Card data-reveal className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-[17px] font-bold">Log out</h2>
          <p className="text-sm text-rp-muted">Ends the prototype session on this device.</p>
        </div>
        <Button variant="danger" disabled={!user} onClick={() => setConfirmLogout(true)}>
          <LogOut className="h-4 w-4" aria-hidden />
          Log out
        </Button>
      </Card>

      <Dialog open={confirmLogout} onClose={() => setConfirmLogout(false)} title="Confirm Logout">
        <div className="space-y-4">
          <p className="text-sm text-rp-muted">
            Are you sure you want to end your session on this device?
          </p>
          <div className="flex justify-end gap-3 pt-2">
            <Button variant="secondary" onClick={() => setConfirmLogout(false)}>
              Cancel
            </Button>
            <Button
              variant="danger"
              onClick={() => {
                setConfirmLogout(false);
                signOut();
                nav(ROUTES.login);
              }}
            >
              Log out
            </Button>
          </div>
        </div>
      </Dialog>
    </PageContainer>
  );
}
