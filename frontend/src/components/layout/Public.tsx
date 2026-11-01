import { Link, Outlet } from 'react-router-dom';
import { ROUTES } from '@/lib/routes';
import { Button } from '@/components/ui/Button';
import { MotionToggle } from '@/components/motion/MotionToggle';
import { Logo } from './Logo';

export function PublicHeader() {
  return (
    <header className="rp-topbar sticky top-0 z-30 border-b border-rp-border/70 bg-rp-bg/85 backdrop-blur-md">
      <div className="mx-auto flex h-[76px] max-w-content items-center justify-between px-2 sm:px-4 md:px-6 lg:px-10">
        <Logo />
        <nav aria-label="Landing" className="hidden items-center gap-7 text-sm font-semibold text-rp-text md:flex">
          <a href="/#features" className="hover:text-rp-primary transition-colors">Superpowers</a>
          <a href="/#workflow" className="hover:text-rp-primary transition-colors">Neural Pipeline</a>
          <a href="/#trust" className="hover:text-rp-primary transition-colors">Data Honesty</a>
          <Link to={ROUTES.about} className="hover:text-rp-primary transition-colors">Architecture</Link>
        </nav>
        <div className="flex items-center gap-1 sm:gap-2">
          <MotionToggle />
          <Link to={ROUTES.login} className="hidden min-h-[44px] items-center rounded-btn px-4 text-sm font-semibold hover:bg-rp-primary-light sm:inline-flex">Log in</Link>
          <Link to={ROUTES.dashboard}><Button className="shadow-lift">Launch App →</Button></Link>
        </div>
      </div>
    </header>
  );
}

export function Footer() {
  const col = (title: string, links: [string, string][]) => (
    <div>
      <h2 className="mb-3 font-heading text-sm font-extrabold text-rp-navy">{title}</h2>
      <ul className="space-y-2 text-sm text-rp-muted">
        {links.map(([l, to]) => <li key={l}><Link to={to} className="hover:text-rp-primary">{l}</Link></li>)}
      </ul>
    </div>
  );
  return (
    <footer className="border-t border-rp-border bg-rp-surface">
      <div className="mx-auto grid max-w-content gap-10 px-4 py-12 md:grid-cols-[1.4fr_1fr_1fr_1fr] md:px-6 lg:px-10">
        <div>
          <Logo />
          <p className="mt-4 max-w-xs text-sm text-rp-muted">Review analytics for online products. ReviewPulse is an independent project and is not affiliated with Amazon.</p>
        </div>
        {col('Product', [['Dashboard', ROUTES.dashboard], ['Product Reviews', ROUTES.reviews], ['Review Analysis', ROUTES.analysis], ['Analytics & Reports', ROUTES.analytics]])}
        {col('Analysis', [['Language Detection', ROUTES.language], ['Topic Extraction', ROUTES.topics], ['Readability', ROUTES.readability], ['Review Harvester', ROUTES.harvester]])}
        {col('Resources', [['Documentation', ROUTES.about], ['Settings', ROUTES.settings], ['Log in', ROUTES.login], ['Create account', ROUTES.register]])}
      </div>
      <div className="border-t border-rp-border py-5 text-center text-xs text-rp-muted">© 2026 ReviewPulse</div>
    </footer>
  );
}

export function PublicLayout() {
  return (
    <div className="min-h-screen bg-rp-bg">
      <PublicHeader />
      <Outlet />
      <Footer />
    </div>
  );
}
