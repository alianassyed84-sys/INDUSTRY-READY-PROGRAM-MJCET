# ReviewPulse Frontend

React 18 + TypeScript (strict) + Vite 5 + Tailwind 3.4 + React Router 6 + TanStack Query 5 + GSAP 3.12 + Recharts + React Hook Form/Zod.

## Run

```bash
cp .env.example .env     # VITE_API_BASE_URL=http://localhost:8000
npm install
npm run dev
npm run build            # tsc --noEmit && vite build
npm test                 # vitest
```

Start the FastAPI backend per its own README so it serves on `VITE_API_BASE_URL`. If it is unreachable, pages fall back to **clearly labelled, fictional demo fixtures** (`src/data/demo.ts`). Demo and live data are never merged.

## Routes (`src/lib/routes.ts`)

| # | Page | Route | Layout |
|---|------|-------|--------|
| 1 | Landing | `/` | Public |
| 2 | Dashboard | `/dashboard` | AppShell |
| 3 | Product Reviews | `/reviews` | AppShell |
| 4 | Review Analysis | `/analysis` | AppShell |
| 5 | Language Detection | `/language` | AppShell |
| 6 | Topic Extraction | `/topics` | AppShell |
| 7 | Readability | `/readability` | AppShell |
| 8 | Login / Register / Recover | `/login` `/register` `/recover` | Public |
| 9 | Review Harvester | `/harvester` | AppShell |
| 10 | Analytics & Reports | `/analytics` | AppShell |
| 11 | Settings & Account | `/settings` | AppShell |
| 12 | About & Docs | `/about` | AppShell |

## Design system handoff (Midnight Pulse)

- **Tokens:** CSS variables in `src/index.css` (`--rp-bg`, `--rp-surface`, `--rp-surface-soft`, `--rp-primary`, `--rp-primary-hover`, `--rp-primary-light`, `--rp-primary-soft`, `--rp-navy`, `--rp-text`, `--rp-muted`, `--rp-border`, `--rp-coral`, `--rp-success`, `--rp-warning`, `--rp-info`, `--rp-chart-grid`, `--rp-action`, `--rp-action-hover`, `--rp-overlay`, `--rp-magenta`), mapped in `tailwind.config.js` as `rp-*` colors.
- **Theme:** Dark plum canvas, layered violet surfaces, lavender text accents, and teal positive signals. Tokens store RGB channels for opacity-aware Tailwind utilities. `rp-primary` is for text and chart accents; `rp-action` provides accessible white-on-violet buttons. `rp-navy` is the legacy heading color token, now soft white. Glows stay in hero sections and primary actions; data panels use quiet surfaces.
- **Type:** Manrope Variable (`font-heading`), Inter Variable (`font-body`). `.tnum` for tabular numerals.
- **Dimensions:** sidebar 252px / 76px collapsed (`w-sidebar`, `w-sidebar-collapsed`), topbar 80px (`h-topbar`), content max 1440px (`max-w-content`), card radius 20px, button radius 12px, inputs >= 48px, buttons >= 44px.
- **Breakpoints:** sm 640, md 768, lg 1024, xl 1280, 2xl 1536. Below `lg` the sidebar becomes a drawer.
- **Shared components:** `components/ui` (Button, Input, Card, Badge, Tooltip, Dialog, Dropdown, states: Skeleton/LoadingBlock/EmptyState/UnavailableState/ErrorState/DataSourceBadge), `components/layout` (AppShell, Sidebar, Topbar, PageContainer, PageHeader, Public layout), `components/shared` (KpiCard, ChartCard, ProductCard, ProductSelect, ReviewCard, ReviewFilters, AnalysisProgress, UrlAnalyzer, `charts.ts` chart theme).
- **Motion:** `src/lib/motion.ts` provides scoped, intersection-based page and scroll reveals. `MotionProvider` respects the device’s reduced-motion preference, persists the pause control locally, and pauses ambient motion while the tab is hidden. The landing SVG scene in `components/motion/PulseHero.tsx` uses a scrubbed GSAP ScrollTrigger sequence, with a short desktop hero pin and a shorter unpinned mobile sequence. Reduced motion shows the complete scene immediately. It uses no video or WebGL runtime.
- **API:** `src/lib/api.ts`: a single `request()` helper plus `api.*` services returning `{ data, source, fallbackReason }`. Types in `src/lib/types.ts`. Hooks in `src/hooks/useProduct.tsx`.

## What is real vs. not connected

- **Known endpoint used:** `GET /api/v1/harvester/products/{id}/insights`. The `Insights` response shape is an assumption to verify against the FastAPI schema. The `products`, `reviews` and `/health` paths are also **unverified**.
- **Prototype auth:** no verified auth endpoints. Login/Register start a device-local session (name and email in `sessionStorage`; passwords are discarded). Recovery sends nothing and says so. Routes are not gated.
- **Harvester:** validates URL format and extracts the ASIN only. Provider retrieval, job status and history are shown as unavailable; nothing is simulated.
- **Analytics:** a price trend requires at least 2 stored snapshots. Topic trends and report export are shown as unavailable.
- **Settings:** profile is read-only; password and notification settings are unavailable.
- **Landing hero order:** headline, supporting text, URL entry (with the "Analyze a Product" CTA), then the "Explore Dashboard" CTA.

## Tests

`npm test` runs URL validation tests and route/shell/data-honesty component tests (jsdom).
Not covered: Playwright end-to-end suites, automated visual regression, live-backend integration.
