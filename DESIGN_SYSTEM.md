# ReviewPulse Design System

## 1. Purpose

This document defines the shared visual language and UI design standards for ReviewPulse, an AI-powered e-commerce product review intelligence platform.

All developers, designers, and AI coding agents must follow this design system when creating or modifying frontend components and pages.

The objective is to deliver a consistent, premium, accessible, responsive, and professional user experience across the entire application.

This document defines design requirements, not the implementation technology. The existing repository, framework, dependencies, and architecture remain authoritative for technical decisions.

## 2. Product Design Vision

ReviewPulse uses a premium, light-themed interactive workspace inspired by modern creative applications and analytical SaaS products.

The interface should combine:

- Spacious layouts and clear visual hierarchy.
- A clean light background with subtle mint and teal accents.
- Rounded cards and restrained shadows.
- Interactive charts and evidence-focused analytical views.
- Contextual floating controls and side panels.
- Smooth, purposeful animations.
- Readable data visualizations.
- Consistent navigation and reusable components.

The interface must prioritize analytical clarity and usability over decoration.

Do not copy unrelated reference websites literally. Adapt their visual qualities to the needs of a review intelligence platform.

## 3. Brand Identity

### Brand name

ReviewPulse

### Product description

AI-powered e-commerce review intelligence for understanding customer sentiment, discovering emerging complaints, evaluating product claims, and investigating evidence-backed insights.

### Brand personality

- Intelligent
- Trustworthy
- Analytical
- Modern
- Approachable
- Precise
- Professional

### Visual principles

1. Clarity before decoration.
2. Evidence before unsupported claims.
3. Consistency across every page.
4. Subtle motion rather than distracting animation.
5. Accessible contrast and readable typography.
6. Responsive layouts without loss of functionality.
7. Honest presentation of uncertainty, missing data, and unsupported features.

## 4. Color Palette

The following colors are the proposed default palette. They must be checked against the existing repository's documented branding before adoption. If an established project palette exists, preserve it or document an approved migration.

### Primary colors

| Token | HEX | Purpose |
|---|---|---|
| Primary | `#0F766E` | Primary actions and brand emphasis |
| Primary hover | `#115E59` | Hover and active states |
| Primary subtle | `#E8F7F2` | Selected backgrounds and subtle highlights |
| Accent | `#2DD4BF` | Decorative accents and selected visual emphasis |
| Accent subtle | `#CCFBF1` | Light accent backgrounds |

### Neutral colors

| Token | HEX | Purpose |
|---|---|---|
| Page background | `#F8FAFC` | Main application background |
| Surface | `#FFFFFF` | Cards, dialogs, and panels |
| Surface secondary | `#F1F5F9` | Secondary surfaces |
| Border | `#E2E8F0` | Dividers and component outlines |
| Text primary | `#172033` | Headings and primary content |
| Text secondary | `#64748B` | Supporting text |
| Text muted | `#94A3B8` | Nonessential metadata |

### Semantic colors

| Token | HEX | Purpose |
|---|---|---|
| Success | `#15803D` | Successful operations and positive states |
| Success subtle | `#DCFCE7` | Success backgrounds |
| Warning | `#D97706` | Caution and emerging-risk indicators |
| Warning subtle | `#FEF3C7` | Warning backgrounds |
| Error | `#DC2626` | Errors and critical states |
| Error subtle | `#FEE2E2` | Error backgrounds |
| Information | `#2563EB` | Informational messages |
| Information subtle | `#DBEAFE` | Informational backgrounds |

### Color usage rules

- Use the primary teal for primary actions, selected navigation, and brand accents.
- Use neutral surfaces for most of the interface.
- Reserve warning and error colors for meaningful statuses.
- Never communicate status using color alone.
- Use text, icons, labels, or other accessible indicators alongside semantic colors.
- Verify text and interface contrast against WCAG 2.2 AA requirements.
- Do not apply gradients to every card or button.
- Avoid excessive saturation and competing accent colors.

## 5. Typography

### Font family

Inspect the existing application and reuse its configured typography where appropriate.

If no suitable font exists, use Inter with a system sans-serif fallback, provided the font source and loading strategy are compatible with the project.

Do not assume a font file already exists. Use a verified local asset or an approved font source.

### Typography scale

| Element | Suggested size | Weight |
|---|---:|---:|
| Main page title | 28–32 px | 600–700 |
| Section heading | 20–24 px | 600 |
| Card heading | 16–18 px | 600 |
| Body text | 14–16 px | 400 |
| Supporting text | 12–14 px | 400 |
| Form labels | 13–14 px | 500 |
| Metric value | 28–36 px | 600–700 |
| Table text | 13–14 px | 400 |
| Metadata | 12 px minimum where practical | 400 |

### Typography rules

- Maintain a clear hierarchy between page titles, section headings, and body content.
- Use consistent line heights.
- Avoid excessively long line lengths.
- Use tabular numerals for aligned metrics where supported.
- Do not use very small text for important analytical evidence.
- Avoid excessive font-weight variation.
- Ensure text remains readable on mobile screens.

## 6. Spacing System

Use a consistent spacing scale throughout the application.

| Token | Value |
|---|---:|
| Space 1 | 4 px |
| Space 2 | 8 px |
| Space 3 | 12 px |
| Space 4 | 16 px |
| Space 5 | 20 px |
| Space 6 | 24 px |
| Space 8 | 32 px |
| Space 10 | 40 px |
| Space 12 | 48 px |
| Space 16 | 64 px |

### Spacing rules

- Use consistent spacing between headings, descriptions, and content sections.
- Keep sufficient internal padding inside cards.
- Separate unrelated content with whitespace or subtle dividers.
- Avoid cramped dashboards and unnecessarily large gaps.
- Use the same spacing tokens across related components.
- Adapt padding to smaller screens without sacrificing readability.

## 7. Border Radius, Borders, and Shadows

### Border radius

| Component | Suggested radius |
|---|---:|
| Small controls | 6–8 px |
| Buttons and inputs | 8–10 px |
| Cards | 12–16 px |
| Large workspace panels | 16–20 px |
| Dialogs and drawers | 16–20 px |
| Pills and status chips | Fully rounded |

### Borders

- Use subtle neutral borders for cards, inputs, tables, and panels.
- Use a clearly visible focus outline for keyboard navigation.
- Avoid thick decorative borders.
- Use semantic border colors for validation states where appropriate.

### Shadows

Use restrained shadows to communicate elevation.

Suggested starting values:

- Small control: `0 1px 2px rgba(15, 23, 42, 0.05)`
- Standard card: `0 4px 12px rgba(15, 23, 42, 0.04)`
- Floating panel: `0 12px 32px rgba(15, 23, 42, 0.10)`

Use shadows sparingly. Prefer borders and surface contrast for most components.

## 8. Application Layout

### General layout

ReviewPulse should use a sidebar-led workspace with a spacious central content area.

The application shell should support:

- Brand identity and navigation.
- Page title and contextual actions.
- Search and relevant global controls.
- Notification access when supported.
- Account controls using the existing authentication implementation.
- Main content area.
- Contextual side panels.
- Responsive navigation.

### Sidebar

The sidebar should provide navigation to the following planned areas:

1. Overview
2. Products
3. Review Explorer
4. Early-Warning Radar
5. Promise vs. Reality
6. AI Investigator
7. Rating–Reality Contradictions
8. Data Ingestion
9. Settings

Only display routes that are implemented or intentionally presented as unavailable.

Sidebar requirements:

- Clear active-page indicator.
- Consistent icons.
- Readable labels.
- Keyboard-accessible navigation.
- Collapsible desktop behavior.
- Appropriate tablet and mobile navigation.
- Tooltips for icon-only navigation where useful.
- No accidental loss of navigation state during routine interactions.

### Main workspace

- Keep content aligned to a consistent layout grid.
- Use a consistent page-header structure.
- Place important actions where users expect them.
- Prefer balanced card layouts rather than dense, unstructured dashboards.
- Keep analytical evidence easy to discover.
- Use contextual panels for secondary details when this avoids unnecessary navigation.

## 9. Responsive Design

Use the existing project's responsive conventions if documented. If none exist, establish and document appropriate breakpoints.

Suggested starting breakpoints:

| Name | Width |
|---|---|
| Small mobile | 360–479 px |
| Large mobile | 480–767 px |
| Tablet | 768–1023 px |
| Desktop | 1024–1439 px |
| Large desktop | 1440 px and above |

These values are design targets, not evidence of existing project configuration.

### Desktop

- Spacious workspace.
- Collapsible sidebar.
- Multi-column analytical cards.
- Interactive charts.
- Contextual evidence panel.
- Tables with appropriate column widths.

### Tablet

- Collapsible or compact navigation.
- Adaptive card grids.
- Responsive chart sizing.
- Side panels constrained to the available viewport.
- Touch-friendly controls.

### Mobile

- Single-column content layout.
- Compact navigation or an accessible navigation drawer.
- Stacked metric cards.
- Responsive charts with readable labels.
- Appropriately transformed or scrollable data tables.
- Full-width forms where useful.
- Touch-friendly controls.
- No unintended horizontal page overflow.

Do not simply scale down the desktop interface. Preserve core workflows on every supported screen size.

## 10. Core Component Standards

### Buttons

Support the following variants:

- Primary
- Secondary
- Tertiary or ghost
- Destructive
- Icon-only

Every button must have:

- A clear purpose.
- Visible hover and focus states.
- Disabled and loading states where applicable.
- Accessible labels.
- A sufficiently large interaction target.

Do not use decorative buttons that have no action.

### Inputs and forms

Use consistent styling for:

- Text inputs.
- Search fields.
- Select controls.
- Date-range selectors.
- File inputs.
- Checkboxes.
- Radio controls.
- Text areas.

Provide labels, validation feedback, helpful descriptions, and clear required-field indicators.

### Cards

Cards should have a consistent structure, spacing, and surface treatment.

Metric cards may contain:

- Metric label.
- Main value.
- Comparison period, where available.
- Trend indicator, where supported.
- Optional supporting description.

Never fabricate metric values or trend percentages.

### Tables

Tables must support appropriate alignment, readable column headings, and clear row separation.

Where implemented, include:

- Sorting.
- Filtering.
- Pagination.
- Empty states.
- Loading states.
- Error states.
- Responsive handling.
- Accessible row and column relationships.

### Status chips

Use status chips for meaningful states such as:

- Positive
- Negative
- Neutral
- Processing
- Completed
- Warning
- Error

Pair color with text or an accessible icon.

### Modals and drawers

- Use clear titles and descriptions.
- Provide a visible close action.
- Support keyboard interaction.
- Prevent background interaction when modal behavior requires it.
- Preserve user context when opening and closing contextual panels.
- Request confirmation for destructive actions.

## 11. Data Visualization Standards

Charts are central to ReviewPulse and must prioritize accuracy, clarity, and honest representation.

### Supported visualization types

Use the charting capabilities already available in the project. Depending on verified data and requirements, suitable visualizations may include:

- Line charts for trends over time.
- Bar charts for product or topic comparisons.
- Stacked bars for sentiment distributions.
- Donut charts for simple proportions.
- Tables for detailed evidence.
- Timeline visualizations for emerging complaints.
- Scatter plots when comparing numerical measures.

Do not introduce a chart type merely for visual variety.

### Chart requirements

Every chart should provide, as appropriate:

- Descriptive title.
- Axis labels.
- Legend.
- Units or percentages.
- Date range.
- Tooltips.
- Empty and error states.
- Accessible textual alternatives.
- Consistent semantic colors.
- Clear handling of missing values.

### Analytical integrity

- Do not invent data points.
- Do not imply statistical significance without supporting analysis.
- Distinguish observed historical data from predictions.
- Display sample size and time period when available.
- Avoid misleading axes and distorted proportions.
- Make uncertainty visible when supported by the analysis.

## 12. ReviewPulse Innovation Feature Styling

### Early-Warning Radar

Visualize emerging complaint patterns using time-based trends, severity indicators, topic breakdowns, and supporting review counts where available.

Use warning colors selectively.

An increasing complaint trend must not automatically be described as proof of a future rating decline.

### Promise vs. Reality

Use a clear comparison layout for product claims and customer experiences.

Distinguish:

- Verified product claims.
- Supporting customer evidence.
- Contradictory evidence.
- Missing information.
- Uncertainty.

Never fabricate a claim or customer quotation.

### Evidence-First AI Investigator

Present conclusions alongside their supporting review records.

Use contextual side panels, readable excerpts, source information, sample sizes, time periods, and uncertainty indicators where available.

The visual design must distinguish evidence from generated interpretation.

### Rating–Reality Contradiction Detector

Present rating-text mismatches neutrally.

Provide the review rating, review text, product context, and explanation of the detected mismatch where supported.

Do not visually label a contradiction as confirmed fraud.

## 13. Loading, Empty, Error, and Success States

Every data-dependent view must account for the full lifecycle of the interface.

### Loading

- Use skeleton placeholders for initial content loading.
- Preserve the expected layout to minimize visual shifts.
- Use progress indicators for longer-running operations when progress information is available.
- Do not invent precise completion percentages.

### Empty states

Provide clear explanations and relevant next steps when:

- No products exist.
- No reviews have been imported.
- Filters return no results.
- No emerging complaints are detected.
- No supporting evidence is available.
- An integration has not been configured.

Use a guided setup flow where appropriate.

Demo data must be explicitly identified and kept separate from real data.

### Error states

Explain what failed in plain language, preserve user input when possible, and offer a retry action when safe.

Do not conceal API failures by silently substituting sample data.

### Success states

Show success feedback only after the relevant operation has actually succeeded.

## 14. Animation and Motion

ReviewPulse uses smooth, contextual animation.

Suggested initial timing values:

| Interaction | Duration |
|---|---:|
| Hover and micro-interaction | 120–180 ms |
| Button transitions | 150–200 ms |
| Tooltip and dropdown | 160–220 ms |
| Drawer and evidence panel | 220–300 ms |
| Page-level transition | 200–300 ms |

Suggested easing:

`cubic-bezier(0.22, 1, 0.36, 1)`

Use animation for:

- Sidebar collapse and expansion.
- Evidence panel transitions.
- Dialog and dropdown appearance.
- Dashboard card entry.
- Chart updates.
- Filter and tab changes.
- Loading-state transitions.
- Button feedback.

Avoid excessive parallax, constant movement, distracting background animation, and unnecessary layout shifts.

Respect the user's reduced-motion preference. Essential content and interactions must never depend on animation.

Use the existing animation library or framework capabilities. Any additional dependency must be justified and compatible with the project.

## 15. Accessibility

Target WCAG 2.2 AA.

Required practices include:

- Keyboard-accessible controls and navigation.
- Visible focus indicators.
- Sufficient text and interface contrast.
- Semantic headings and page structure.
- Accessible labels and form errors.
- Meaningful button names.
- Accessible dialog and drawer behavior.
- Reduced-motion support.
- Textual alternatives for charts.
- Status communication that does not rely on color alone.
- Readable content at supported viewport sizes.
- Appropriate screen-reader announcements for important asynchronous updates.

Accessibility must be considered during component implementation rather than added only at the end.

## 16. Asset Management

Generated assets may be used when they improve the experience.

Target directories, subject to the existing framework's conventions:

- `/public/images/` — static imagery, illustrations, and backgrounds.
- `/public/icons/` — SVG or approved icon assets.
- `/public/videos/` — video content or sequences when genuinely required.

Do not assume any specific asset file already exists.

Prefer CSS, SVG, and real chart components over unnecessary decorative images. Optimize images, provide appropriate alternative text, and verify asset paths before referencing them.

Use consistent iconography from an existing project library where available.

## 17. Performance and Implementation Consistency

- Reuse shared components instead of recreating the same pattern on every page.
- Avoid unnecessary dependencies.
- Avoid repeated API requests when caching or request reuse is appropriate.
- Keep large tables and charts responsive.
- Optimize generated assets.
- Avoid excessive animations and expensive visual effects.
- Prevent unnecessary layout shifts.
- Follow the existing project's loading and error-handling conventions.
- Keep styles consistent with the established architecture.
- Do not introduce global styles that unexpectedly break existing pages.
- Do not overwrite teammate changes or unrelated application functionality.

## 18. Design System Change Policy

This document is the shared visual reference for ReviewPulse.

Before introducing a new design pattern, color, font, spacing value, or component variant:

1. Check whether an existing design token or component already covers the requirement.
2. Reuse the existing pattern where practical.
3. If a new pattern is necessary, keep it consistent with this system.
4. Update this document when an approved change affects shared design conventions.
5. Do not make unrelated or breaking architectural changes under the guise of visual refinement.

Existing repository documentation and implemented behavior must be inspected before changing established conventions.

## 19. Design Quality Checklist

Before completing a page or component, verify:

- [ ] The visual hierarchy is clear.
- [ ] Colors and typography follow the design system.
- [ ] Spacing and border radii are consistent.
- [ ] The component works at desktop, tablet, and mobile sizes.
- [ ] Hover, focus, active, disabled, and loading states are implemented where relevant.
- [ ] Loading, empty, error, and success states are handled.
- [ ] All interactive controls have meaningful behavior.
- [ ] Accessibility requirements have been considered.
- [ ] Animations are smooth and respect reduced-motion preferences.
- [ ] Charts and metrics use verified data.
- [ ] Evidence is not fabricated.
- [ ] No unintended horizontal overflow exists.
- [ ] Existing functionality and teammate changes remain intact.

## 20. Final Principle

Every ReviewPulse page should feel like part of one coherent product.

The design must combine the elegance of a premium interactive workspace with the clarity, reliability, accessibility, and analytical integrity required by an AI-powered review intelligence platform.

**This document defines how ReviewPulse should look and behave visually. It does not authorize changes to the backend, data models, API contracts, authentication, or deployment architecture.**