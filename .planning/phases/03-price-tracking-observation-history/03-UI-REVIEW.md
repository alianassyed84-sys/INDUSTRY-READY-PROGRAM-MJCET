# Phase 3 — UI Review

**Audited:** 2026-10-22
**Baseline:** Abstract 6-Pillar Standards (No UI-SPEC.md present)
**Screenshots:** Not captured (Headless CLI environment without Playwright browser binary; Dev server verified active at http://localhost:5173)

---

## Pillar Scores

| Pillar | Score | Key Finding |
|--------|-------|-------------|
| 1. Copywriting | 3/4 | Honest and domain-specific terminology, but empty and error states lack detailed troubleshooting descriptions and correlation IDs. |
| 2. Visuals | 3/4 | Strong focal points, charts, and 100% icon button ARIA label coverage; fixed chart heights risk truncation on small viewports. |
| 3. Color | 2/4 | Balanced 60/30/10 distribution, but heavy hardcoded hex code bleed in `Badge.tsx`, `states.tsx`, and `Analysis.tsx` bypasses theme tokens. |
| 4. Typography | 2/4 | Variable Manrope/Inter loaded, but severe scale fragmentation with 22+ arbitrary pixel font sizes (`text-[10px]` to `text-[44px]`). |
| 5. Spacing | 3/4 | Clean 4px grid adherence for margins, paddings, and gaps; minor off-token border radius and icon dimension outliers. |
| 6. Experience Design | 3/4 | Solid skeleton loading and accessibility, but no root React Error Boundary and destructive actions lack confirmation dialogs. |

**Overall: 16/24**

---

## Top 3 Priority Fixes

1. **Unify Arbitrary Typographic Scale across Components (Typography — Score: 2/4)**  
   - *User impact:* Inconsistent visual rhythm, uneven heading hierarchy, and fragmented text sizing degrade readability across screens.  
   - *Concrete fix:* Audit and replace 22+ arbitrary bracketed text sizes (`text-[10px]`, `text-[13px]`, `text-[15px]`, `text-[17px]`, `text-[22px]`, `text-[34px]`) in `About.tsx`, `Settings.tsx`, `Input.tsx`, and `Dashboard.tsx` with standard Tailwind scale classes (`text-xs`, `text-sm`, `text-base`, `text-lg`, `text-page`, `text-display`).

2. **Eliminate Hardcoded Hex Codes in Status and Badge Components (Color — Score: 2/4)**  
   - *User impact:* Inconsistent alert and badge colors across pages (e.g. neutral sentiment is `#9A9DB3` in `Analysis.tsx` but `text-rp-muted` in `Dashboard.tsx`), breaking theme consistency.  
   - *Concrete fix:* Migrate raw hex strings (`#FBF0DC`, `#FDE9E5`, `#8E2F20`, `#F1EEF4`, `#E3F4EC`, `#B8402E`) in `frontend/src/components/ui/states.tsx`, `frontend/src/components/ui/Badge.tsx`, and `frontend/src/components/shared/AnalysisProgress.tsx` to CSS variables and Tailwind tokens in `tailwind.config.js`.

3. **Implement Root Error Boundary & Rich Diagnostic Error States (Experience Design & Copywriting — Score: 3/4)**  
   - *User impact:* Uncaught component render errors or WebGL crashes produce an unrecoverable blank white screen. Failed queries display generic "Something went wrong" messages without actionable error descriptions or correlation IDs.  
   - *Concrete fix:* Wrap `<App />` in `frontend/src/main.tsx` with a React Error Boundary displaying a reset button, and pass `error.message` and `X-Request-ID` into `ErrorState` across `Analytics.tsx`, `Dashboard.tsx`, and `Topics.tsx`.

---

## Detailed Findings

### Pillar 1: Copywriting (3/4)
- **Strengths:**
  - Clear, active-voice CTAs throughout: `"Extract Live Keyphrases"`, `"Analyze Text Complexity"`, `"Identify Language"`, `"Poll Fresh Price"`, `"Run CSV Import Job"`.
  - Transparent data provenance badges distinguishing mock fixture data from live backend data (`DataSourceBadge` in `frontend/src/components/ui/states.tsx:52-60`).
  - Honest disclosure in `frontend/src/pages/Auth.tsx:25` and `Settings.tsx:29` stating that auth and password recovery operate in device-local prototype mode.
  - Comprehensive documentation in `frontend/src/pages/About.tsx` explaining linguistic algorithms (Flesch Reading Ease, TF-IDF, Cavnar & Trenkle) and system limitations.
- **Defects & Deviations:**
  - `frontend/src/pages/Analytics.tsx:54`: `<ErrorState onRetry={() => q.refetch()} />` passes no title or description, falling back to the generic string `"Something went wrong"`.
  - Missing descriptions in empty states:
    - `frontend/src/pages/Topics.tsx:55`: `<EmptyState title="No topics match your search" />` has no description or "Clear search" CTA.
    - `frontend/src/pages/Dashboard.tsx:110`: `<EmptyState title="No sentiment data" />` provides no guidance on how to trigger sentiment computation.
    - `frontend/src/pages/Analytics.tsx:140`: `<EmptyState title="Add another product to compare" />` lacks instructions.
    - `frontend/src/pages/Analysis.tsx:143`: `<EmptyState title="No topics extracted" />` has no description.
  - Generic error fallback in `frontend/src/pages/Dashboard.tsx:45` uses `"The request failed unexpectedly."` without displaying the HTTP status code or request correlation ID.

### Pillar 2: Visuals (3/4)
- **Strengths:**
  - Distinct focal points on `Landing.tsx` (ambient gradient hero, 3D interactive core) and `Dashboard.tsx` (URL Analyzer header and KPI cards).
  - 100% icon button accessibility compliance: every icon-only button across `Topbar.tsx`, `Dialog.tsx`, `Sidebar.tsx`, `UrlAnalyzer.tsx`, and `Auth.tsx` contains an explicit `aria-label` or `Tooltip`.
  - Diverse, domain-appropriate charting: Recharts Radar chart (`Dashboard.tsx`), Area/Line chart (`Analytics.tsx`), Donut/Pie chart (`Analysis.tsx`), Bar distribution charts (`Readability.tsx`, `Language.tsx`, `Topics.tsx`).
  - 3D hero visualization (`frontend/src/components/three/ThreeHero.tsx`) includes WebGL feature detection, canvas error fallbacks, and reduced motion adaptations.
- **Defects & Deviations:**
  - Chart containers use fixed pixel heights (`h-[320px]`, `h-[290px]`, `h-[300px]`) without aspect ratio constraints, causing axis clipping on narrow mobile viewports (<380px).
  - Sentiment pie chart in `frontend/src/pages/Analysis.tsx:75-90` lacks in-slice percentage callouts, requiring users to hover on tooltips to read exact distribution values.
  - When chart data is empty, the entire card collapses into an empty box rather than rendering a faint ghost/wireframe grid showing expected visual layout.

### Pillar 3: Color (2/4)
- **Strengths:**
  - Brand identity based on cohesive palette: `--rp-primary` (`#7138F5`), `--rp-navy` (`#171B50`), `--rp-bg` (`#FAF7F2`), `--rp-coral` (`#F36B57`), `--rp-success` (`#16865C`).
  - Adheres to the 60/30/10 rule: 60% warm ivory/white background, 30% navy text/card borders, 10% purple accent and semantic status colors.
- **Defects & Deviations:**
  - **Severe Hardcoded Hex Bleed**:
    - `frontend/src/components/ui/states.tsx:37`: `UnavailableState` uses hardcoded `bg-[#FBF0DC] text-rp-warning`.
    - `frontend/src/components/ui/states.tsx:41, 44, 45`: `ErrorState` hardcodes `bg-[#FDE9E5]`, `text-[#8E2F20]`, `text-[#8E2F20]/85` instead of theme tokens.
    - `frontend/src/components/ui/Badge.tsx:6-11`: All 5 variant tone styles use raw hex strings (`bg-[#F1EEF4]`, `bg-[#E3F4EC]`, `bg-[#FBF0DC]`, `bg-[#FDE9E5] text-[#B8402E]`, `bg-[#E4EEFB]`).
    - `frontend/src/components/shared/AnalysisProgress.tsx:12-13`: Uses raw hex codes `bg-[#F1EEF4]` and `bg-[#FBF0DC]`.
    - `frontend/src/pages/Readability.tsx:53`: Empty bar chart fill hardcodes `#E7E2EE`.
    - `frontend/src/pages/Auth.tsx:97`: Uses `bg-[#FBF0DC] text-rp-warning`.
  - **Semantic Color Inconsistency**:
    - `frontend/src/pages/Dashboard.tsx:103`: Neutral sentiment rendered as `bg-rp-muted` (`#666B85`).
    - `frontend/src/pages/Analysis.tsx:85, 92`: Neutral sentiment rendered as `bg-[#9A9DB3]` (`#9A9DB3`). Identical metric rendered with conflicting color values across views.

### Pillar 4: Typography (2/4)
- **Strengths:**
  - Dual variable font system (`Manrope Variable` for headings, `Inter Variable` for body copy) with tabular figures (`tnum`) for data metrics.
  - Base typography rules configured in `frontend/src/index.css:26-39`.
- **Defects & Deviations:**
  - **Scale Fragmentation (22+ distinct sizes)**:
    - Rather than adhering to the declared scale in `tailwind.config.js` (`display`, `page`, `section`, `kpi`), arbitrary pixel sizes are spread throughout the code:
      - `text-[10px]`, `text-[11px]`, `text-[13px]` (14 instances)
      - `text-[15px]` (7 instances), `text-[17px]` (6 instances), `text-[20px]`, `text-[22px]` (3 instances)
      - `text-[24px]`, `text-[28px]`, `text-[30px]`, `text-[32px]`, `text-[34px]`, `text-[44px]`
    - This competes with standard classes (`text-xs`, `text-sm`, `text-base`, `text-lg`, `text-xl`, `text-2xl`, `text-3xl`, `text-4xl`).
  - **Inconsistent Weight Hierarchy**:
    - Headings inconsistently oscillate between `font-bold` (20 instances) and `font-extrabold` (24 instances) without distinct semantic levels.

### Pillar 5: Spacing (3/4)
- **Strengths:**
  - **100% Standard Scale Compliance on Margins/Paddings/Gaps**: Zero arbitrary bracket values found for padding, margin, or flex gaps. Consistently adheres to the 4px baseline scale (`gap-1` [4px], `gap-2` [8px], `gap-3` [12px], `gap-4` [16px], `gap-6` [24px], `p-3`, `p-4`, `p-6`).
  - Standardized page padding across all routes via `PageContainer` (`px-4 md:px-6 lg:px-8`).
- **Defects & Deviations:**
  - Outlier border radii:
    - `frontend/src/pages/Dashboard.tsx:33`: Hero container uses `rounded-[24px]` (bypassing `rounded-card` [20px] and `rounded-3xl` [24px]).
    - `frontend/src/components/layout/Sidebar.tsx:19`: Nav links use `rounded-[13px]`, introducing an arbitrary 1px deviation from `rounded-btn` (14px).
  - Outlier icon dimensions:
    - `frontend/src/components/layout/Sidebar.tsx:25`: Hardcoded icon dimensions `h-[19px] w-[19px]` instead of standard `h-5 w-5` (20px).
    - `frontend/src/components/shared/KpiCard.tsx:13`: Uses `h-[18px] w-[18px]`.
  - Inline box shadow: `frontend/src/components/layout/Sidebar.tsx:21` hardcodes `shadow-[0_8px_18px_-8px_rgba(113,56,245,.65)]`.

### Pillar 6: Experience Design (3/4)
- **Strengths:**
  - Accessible loading states using animated skeletons with ARIA live announcements (`role="status" aria-live="polite"`).
  - Interactive API mutation buttons reflect `loading` state, display spinners, and disable duplicate submissions.
  - Skip-to-content keyboard accessibility shortcut in `frontend/src/components/layout/AppShell.tsx:18`.
  - Full respect for user motion preferences (`prefers-reduced-motion: reduce`) across CSS animations, GSAP tweens, and Three.js 3D rendering.
- **Defects & Deviations:**
  - **No Global React Error Boundary**:
    - Neither `frontend/src/main.tsx` nor `frontend/src/App.tsx` contains an Error Boundary. An unhandled exception during rendering crashes the client to a white screen.
  - **Destructive Actions Missing Confirmations**:
    - `frontend/src/pages/Settings.tsx:83`: Logout action immediately clears session without confirmation.
    - `frontend/src/pages/Harvester.tsx:201`: "Run CSV Import Job" triggers backend dataset ingestion synchronously without confirmation.
  - **Lack of Diagnostic Context in Query Errors**:
    - Query failure components in `Analytics.tsx`, `Topics.tsx`, and `Readability.tsx` do not display backend error messages, HTTP status codes, or `X-Request-ID` correlation identifiers.

---

## Files Audited

- `frontend/src/App.tsx`
- `frontend/src/main.tsx`
- `frontend/src/index.css`
- `frontend/tailwind.config.js`
- `frontend/src/pages/About.tsx`
- `frontend/src/pages/Analysis.tsx`
- `frontend/src/pages/Analytics.tsx`
- `frontend/src/pages/Auth.tsx`
- `frontend/src/pages/Dashboard.tsx`
- `frontend/src/pages/Harvester.tsx`
- `frontend/src/pages/Landing.tsx`
- `frontend/src/pages/Language.tsx`
- `frontend/src/pages/Readability.tsx`
- `frontend/src/pages/Reviews.tsx`
- `frontend/src/pages/Settings.tsx`
- `frontend/src/pages/Topics.tsx`
- `frontend/src/components/layout/AppShell.tsx`
- `frontend/src/components/layout/Logo.tsx`
- `frontend/src/components/layout/Page.tsx`
- `frontend/src/components/layout/Public.tsx`
- `frontend/src/components/layout/Sidebar.tsx`
- `frontend/src/components/layout/Topbar.tsx`
- `frontend/src/components/ui/Badge.tsx`
- `frontend/src/components/ui/Button.tsx`
- `frontend/src/components/ui/Card.tsx`
- `frontend/src/components/ui/Dialog.tsx`
- `frontend/src/components/ui/Dropdown.tsx`
- `frontend/src/components/ui/Input.tsx`
- `frontend/src/components/ui/Tooltip.tsx`
- `frontend/src/components/ui/states.tsx`
- `frontend/src/components/shared/AnalysisProgress.tsx`
- `frontend/src/components/shared/ChartCard.tsx`
- `frontend/src/components/shared/KpiCard.tsx`
- `frontend/src/components/shared/ProductCard.tsx`
- `frontend/src/components/shared/ProductSelect.tsx`
- `frontend/src/components/shared/ReviewCard.tsx`
- `frontend/src/components/shared/ReviewFilters.tsx`
- `frontend/src/components/shared/UrlAnalyzer.tsx`
- `frontend/src/components/shared/charts.ts`
- `frontend/src/components/three/ThreeHero.tsx`
