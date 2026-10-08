# COMPONENT_SPECIFICATIONS.md

## 1. Purpose

This document defines the reusable UI component specifications for ReviewPulse, an AI-powered e-commerce product review intelligence platform.

It establishes consistent component behavior, visual styling, interaction patterns, accessibility requirements, and implementation rules across all application pages.

This document is the reference for implementing shared frontend components. It is not a website-generation prompt or a backend architecture specification.

### Core principles

- Reuse shared components instead of creating page-specific duplicates.
- Maintain a premium, clean, light-theme SaaS interface.
- Present complex review intelligence in a clear, evidence-first format.
- Support individual sellers, small businesses, and larger product teams.
- Ensure consistent responsive behavior across desktop, tablet, and mobile.
- Use real backend data and verified API capabilities wherever available.
- Preserve the existing project's framework, conventions, and architecture unless a change is approved.

---

## 2. Global Component Rules

### 2.1 Design tokens

Components must use centralized design tokens rather than independently defined colors, spacing, shadows, and typography.

The following values are proposed defaults. Before implementation, check `DESIGN_SYSTEM.md` and the existing theme. If established project tokens differ, use the existing approved values or document the proposed change.

| Token | Proposed value |
|---|---|
| Primary | `#0F766E` |
| Primary hover | `#115E59` |
| Primary subtle | `#E8F7F2` |
| Accent | `#2DD4BF` |
| Page background | `#F8FAFC` |
| Surface | `#FFFFFF` |
| Border | `#E2E8F0` |
| Primary text | `#172033` |
| Secondary text | `#64748B` |
| Success | `#15803D` |
| Warning | `#D97706` |
| Error | `#DC2626` |
| Information | `#2563EB` |

Do not introduce new colors for individual pages without a design-system justification.

### 2.2 Component states

Every applicable interactive component must support the relevant states:

- Default
- Hover
- Keyboard focus
- Active or pressed
- Disabled
- Loading
- Success
- Error

Components must not communicate state through color alone. Use text, icons, labels, or other visual indicators where appropriate.

### 2.3 Implementation requirements

- Use the existing component framework and styling approach.
- Follow established naming, file organization, and import conventions.
- Use semantic HTML and accessible interaction patterns.
- Avoid unnecessary dependencies.
- Keep components small, reusable, and easy to test.
- Keep business logic and API access out of purely presentational components.
- Avoid hardcoded business data, fake API responses, and fabricated AI findings.
- Do not replace working components without reviewing their existing usage.
- Do not overwrite teammates' changes or unrelated files.

---

## 3. Application Shell Components

### 3.1 App Layout

**Purpose:** Provide the consistent application structure for authenticated ReviewPulse workspaces.

**Required structure:**
- Sidebar navigation
- Top application header
- Main content region
- Optional contextual side panel
- Toast or notification presentation area where supported

**Behavior:**
- Maintain consistent alignment across application pages.
- Allow the main content to scroll independently when compatible with the existing layout.
- Prevent horizontal overflow at supported viewport sizes.
- Preserve the current route and page state when opening or closing contextual panels where feasible.
- Support responsive navigation on smaller screens.

**Acceptance criteria:**
- Shared shell is reused across the main product pages.
- Page-specific content does not duplicate the global sidebar or header.
- Layout works with long tables, charts, and contextual panels.

### 3.2 Sidebar Navigation

**Purpose:** Provide access to the major ReviewPulse product areas.

**Navigation items:**
1. Overview
2. Products
3. Reviews
4. Early-Warning Radar
5. AI Investigator
6. Promise vs. Reality
7. Rating–Reality Contradiction Detector
8. Ingestion
9. Settings

**Behavior:**
- Display an icon and readable label for each primary navigation item.
- Clearly indicate the active route.
- Support keyboard navigation and visible focus.
- Collapse or adapt for tablet and mobile layouts.
- Provide accessible names for icon-only controls.
- Keep the navigation order consistent across the application.

**Acceptance criteria:**
- Each item navigates to its corresponding implemented route.
- Active state reflects the actual route.
- Unavailable or unimplemented destinations are not represented as fully functional features.
- Navigation does not discard unsaved user work without an appropriate warning.

### 3.3 Top Header

**Purpose:** Provide global workspace context and frequently used actions.

**Potential contents, depending on existing functionality:**
- Current page title or breadcrumb
- Workspace or account context
- Global search
- Notification center
- User profile menu

**Behavior:**
- Maintain consistent height, spacing, and alignment.
- Adapt to narrow screens without overlapping controls.
- Use existing authentication and account APIs for user information.
- Do not invent notification counts, account details, or search results.

### 3.4 Page Header

**Purpose:** Establish the context of each page.

**Required elements:**
- Page title
- Short descriptive subtitle where useful
- Optional breadcrumb
- Optional primary action
- Optional secondary actions

**Behavior:**
- Use a consistent heading hierarchy.
- Keep action placement predictable.
- Allow titles and action groups to wrap on smaller screens.
- Avoid excessive introductory text on data-dense pages.

---

## 4. Buttons and Action Controls

### 4.1 Button Variants

Support these variants where appropriate:

- **Primary:** Main action, such as starting an available analysis.
- **Secondary:** Supporting action, such as opening filters.
- **Outline:** Lower-emphasis actions.
- **Ghost:** Compact actions with minimal visual emphasis.
- **Destructive:** Deletion or other irreversible operations.
- **Icon button:** Compact action represented by an icon.

### 4.2 Button Specifications

- Use consistent height, padding, radius, typography, and icon spacing.
- Include visible hover, focus, active, and disabled states.
- Prevent duplicate submissions while an operation is in progress.
- Use clear action labels such as “Upload reviews,” “Export report,” or “Save insight.”
- Use tooltips for icon-only controls when the action is not self-evident.
- Do not use a destructive style for ordinary navigation.

### 4.3 Loading behavior

When a button triggers an asynchronous operation:
- Indicate that the operation is in progress.
- Disable repeated submission where appropriate.
- Preserve the button's contextual meaning.
- Restore an actionable state after success or failure.
- Show a clear error if the operation fails.

### 4.4 Acceptance criteria

- Buttons are keyboard accessible.
- All visible buttons perform their stated action.
- Disabled buttons cannot trigger their action.
- Destructive actions require confirmation when the operation is irreversible or consequential.

---

## 5. Form Components

### 5.1 Text Input

**Use for:** Search queries, product identifiers, names, and short text values.

**Requirements:**
- Visible label or equivalent accessible name.
- Optional helper text.
- Clear error message when invalid.
- Appropriate input type and autocomplete behavior.
- Clear focus indicator.
- Support for disabled and read-only states when needed.

Do not use placeholder text as the only label.

### 5.2 Search Input

**Use for:** Searching products, reviews, and available records.

**Behavior:**
- Provide a clear accessible label.
- Support a clear action when a query is entered.
- Debounce requests only when appropriate for the existing search API.
- Distinguish an empty query from a query with no results.
- Avoid inventing search results or silently changing user input.

### 5.3 Select and Dropdown

**Use for:** Sorting, date-range selection, product selection, and other constrained choices.

**Requirements:**
- Clearly identify the current selection.
- Support keyboard operation.
- Include an explicit empty or default choice where appropriate.
- Preserve the selected value when compatible with route and filter state.
- Ensure menus remain usable on small screens.

### 5.4 Checkbox and Toggle

**Use for:** Multi-select filters and binary settings.

**Requirements:**
- Provide a visible label.
- Use checkboxes for independent selections.
- Use switches for immediate on/off settings when that interaction is appropriate.
- Clearly indicate whether a change takes effect immediately or requires saving.
- Do not use toggles to imply capabilities the backend does not support.

### 5.5 Date Range Picker

**Use for:** Filtering review trends, complaint patterns, and analysis periods.

**Behavior:**
- Support available predefined ranges and custom dates if supported.
- Validate the start and end dates.
- Display the selected range clearly.
- Apply the range consistently to the relevant data and charts.
- Communicate when no data exists for the chosen period.

Do not assume a backend supports arbitrary historical date ranges without checking its API contract.

### 5.6 Form Validation

- Validate required fields and supported formats.
- Show errors near the relevant field.
- Preserve valid user input when submission fails.
- Avoid clearing the entire form after an error.
- Announce validation feedback accessibly.
- Distinguish client-side validation from server-side errors.

---

## 6. Cards and Summary Components

### 6.1 Standard Card

**Purpose:** Group related content into a visually distinct surface.

**Required characteristics:**
- Consistent internal padding
- White or approved surface background
- Subtle border
- Consistent corner radius
- Clear content hierarchy

Avoid unnecessary shadows, decorative gradients, and excessive nested cards.

### 6.2 KPI Card

**Purpose:** Summarize a meaningful business metric.

**Possible metrics, only when supported by real data:**
- Total products analyzed
- Reviews processed
- Emerging complaint clusters
- High-priority issues
- Analysis coverage

**Structure:**
- Metric label
- Main value
- Optional comparison or trend
- Optional supporting context
- Optional link to relevant details

**Behavior:**
- Display formatted values consistently.
- Show a loading skeleton while the metric loads.
- Distinguish unavailable data from a genuine zero.
- Include the comparison period for percentage changes.
- Do not show a trend indicator without a valid comparison baseline.

**Acceptance criteria:**
- Each metric can be traced to its data source or calculation.
- Missing values are not replaced with invented numbers.
- Trends are not presented as causal explanations.

### 6.3 Insight Card

**Purpose:** Summarize an actionable finding from review analysis.

**Recommended content:**
- Insight title
- Concise explanation
- Relevant product or category
- Severity or priority when supported
- Evidence count
- Relevant time period
- Confidence or uncertainty information when available
- Link to supporting evidence
- Available actions

**Behavior:**
- Distinguish observed evidence from AI-generated interpretation.
- Avoid unsupported certainty.
- Do not label an issue as confirmed solely because an AI model flagged it.
- Provide a path to inspect the underlying evidence.

### 6.4 Product Card

**Purpose:** Present a concise summary of an analyzed product.

**Potential content:**
- Product name
- Product image when available
- Product identifier
- Review count
- Rating
- Latest review activity
- Relevant insight summary

**Rules:**
- Use actual product data.
- Provide an appropriate fallback when no image exists.
- Avoid fabricated product names, ratings, or review counts.
- Keep the layout usable when names are long.

---

## 7. Data Table Components

### 7.1 Standard Data Table

**Use for:**
- Products
- Reviews
- Review clusters
- Investigation evidence
- Ingestion history

**Requirements:**
- Clear column headings.
- Consistent cell alignment.
- Readable row spacing.
- Responsive overflow behavior.
- Visible row-hover state where useful.
- Accessible sort controls when sorting is supported.
- Clear loading, empty, and error states.

### 7.2 Sorting and Filtering

- Indicate the active sort field and direction.
- Make filter state visible.
- Keep filter behavior consistent across relevant data views.
- Do not claim a sort or filter is active unless it changes the displayed results.
- Preserve filter state when navigating back where practical.

### 7.3 Pagination

Use pagination or an established incremental-loading pattern according to backend capabilities.

When server-side pagination is available:
- Use the actual total or continuation information returned by the API.
- Avoid requesting every record just to populate the initial view.
- Preserve active filters and sort order when changing pages.

Do not fabricate total record counts.

### 7.4 Row Actions

- Place row-level actions consistently.
- Provide accessible labels for icon-only actions.
- Prevent accidental row navigation when an action button is clicked.
- Confirm consequential destructive operations.
- Respect the current user's permissions where the application exposes them.

### 7.5 Empty Table State

Explain why the table has no visible records when that information is available.

Examples:
- “No products have been added yet.”
- “No reviews match these filters.”
- “No analysis results are available for this period.”

Provide a relevant next step without implying data exists when it does not.

---

## 8. Filter Bar and Active Filter Chips

### 8.1 Purpose

Provide a consistent filtering experience across Products, Reviews, Radar, and other data-driven pages.

### 8.2 Components

- Search field
- Date-range control
- Product or category selector where supported
- Sentiment or issue-type filters where supported
- Additional filters appropriate to the page
- Apply or clear controls when the filter model requires them
- Active filter chips

### 8.3 Behavior

- Show which filters are active.
- Allow an individual filter to be removed through its chip.
- Provide a clear-all action.
- Keep filters synchronized with displayed records and charts.
- Avoid showing irrelevant filter controls on pages that do not support them.
- Preserve state when appropriate and compatible with the existing routing approach.

### 8.4 Acceptance criteria

- Removing a chip removes its corresponding filter.
- Clearing filters restores the default filter state.
- Filter controls work with keyboard and assistive technology.
- Filter changes do not create misleading counts or stale charts.

---

## 9. Status Badges and Labels

### 9.1 Supported status categories

Use badges for meaningful states such as:
- Success
- Warning
- Error
- Informational
- Processing
- Neutral or unknown

### 9.2 Usage rules

- Use short, understandable labels.
- Pair color with readable text or an accessible icon.
- Apply status colors consistently.
- Avoid decorative badges without semantic value.
- Do not treat a model prediction as a confirmed fact.

For AI-related results, prefer carefully qualified terms such as “Potential issue,” “Emerging pattern,” or “Needs review” when they accurately reflect the system's output.

Do not introduce a confidence category unless the backend or model output defines a meaningful basis for it.

---

## 10. Charts and Data Visualization

### 10.1 General requirements

Charts must support meaningful interpretation of review data rather than serve as decoration.

**Required where applicable:**
- Descriptive title
- Clear axes and units
- Legible labels
- Useful hover details
- Loading and empty states
- Responsive resizing
- Accessible textual summaries or equivalent data access

### 10.2 Supported chart patterns

Use chart types appropriate to the question and the available data:

- Line chart for change over time
- Bar chart for category comparisons
- Stacked bar chart for composition over time
- Distribution chart for rating or sentiment breakdowns
- Scatter plot for exploring relationships between measurable variables

Use only chart types the existing charting library supports.

### 10.3 Chart interactions

Where the underlying data supports it:
- Hover to reveal exact values and context.
- Select date ranges.
- Filter by product or category.
- Drill into the records represented by a chart element.
- Update relevant charts when shared filters change.

### 10.4 Data integrity

- Use real values returned by the backend or computed from verified records.
- Clearly label aggregated data.
- Make date ranges and denominators visible where relevant.
- Do not imply causation from correlation.
- Do not smooth or transform data in ways that misrepresent the source.
- Do not show fabricated chart values in production views.

### 10.5 Chart failure states

If data cannot be loaded, display an informative error and a retry option when retrying is supported.

Do not replace a failed real-data chart with fabricated values.

---

## 11. Review Evidence Components

### 11.1 Review Snippet

**Purpose:** Display a review or relevant excerpt supporting a finding.

**Recommended content:**
- Review text or relevant excerpt
- Rating when available
- Product association
- Review date when available
- Source or platform when available
- Verified status only when provided by a trustworthy source field

**Behavior:**
- Preserve the meaning of the original review.
- Clearly indicate when text is truncated.
- Allow the full review to be inspected when available.
- Do not fabricate missing review metadata.
- Handle missing, malformed, or unusually long text safely.

### 11.2 Evidence Count

Display the number of supporting records only when the count is derived from the relevant dataset and filters.

Where appropriate, distinguish:
- Total reviews examined
- Reviews supporting the finding
- Reviews contradicting the finding
- Reviews excluded from analysis

Only display distinctions the underlying analysis can substantiate.

### 11.3 Evidence Drawer or Side Panel

**Purpose:** Allow users to investigate a finding without losing their current context.

**Behavior:**
- Open from an insight, chart selection, table row, or evidence link.
- Display the selected finding and its supporting records.
- Show relevant dates and product context when available.
- Provide clear close and back behavior.
- Preserve the underlying page's filter and scroll state where practical.
- Support keyboard focus management.
- On mobile, adapt to a full-height panel or suitable dialog layout.

**Acceptance criteria:**
- The user can close the panel using a visible control and the Escape key when appropriate.
- Keyboard focus remains managed within modal interactions.
- Opening evidence does not silently reset the underlying page.
- Each displayed finding links to the evidence that actually supports it.

---

## 12. ReviewPulse Innovation Components

### 12.1 Early-Warning Radar Components

**Purpose:** Highlight emerging complaint patterns that may deserve investigation.

**Components:**
- Emerging pattern summary
- Complaint cluster card
- Trend chart
- Severity or priority indicator, if supported
- Evidence count
- Detection period
- Evidence side panel
- Investigation action

**Behavior:**
- Show the period over which a pattern was detected.
- Display available comparison information.
- Explain why a pattern is surfaced when the analysis supports an explanation.
- Distinguish an emerging signal from a confirmed business problem.
- Allow users to inspect representative supporting reviews.

**Acceptance criteria:**
- Every actionable pattern links to relevant evidence.
- Trend comparisons use consistent time windows and denominators.
- No alert is presented as a prediction of certainty.

### 12.2 Promise vs. Reality Components

**Purpose:** Compare product claims with customer review evidence.

**Components:**
- Product or claim selector
- Claim summary
- Supporting evidence section
- Contradicting evidence section
- Evidence coverage summary
- Time-period context
- Investigation action

**Behavior:**
- Distinguish a product claim from an inferred interpretation of that claim.
- Show evidence that supports and challenges the claim when available.
- Make the number and coverage of reviewed records clear.
- Identify missing or insufficient evidence.
- Avoid declaring a claim false solely because some reviews disagree with it.

**Acceptance criteria:**
- Claim and review evidence are visibly distinct.
- Conclusions can be traced to the displayed records.
- Insufficient evidence is communicated explicitly.

### 12.3 Evidence-First AI Investigator Components

**Purpose:** Present analysis conclusions alongside inspectable evidence.

**Components:**
- Investigation question or subject
- Findings list
- Evidence references
- Supporting and contradicting evidence
- Analysis status
- Relevant uncertainty or limitations
- Save or export actions where supported
- Feedback action where supported

**Behavior:**
- Separate observed facts, model interpretations, and recommendations.
- Link each substantive finding to relevant evidence.
- Indicate when a finding has limited support.
- Do not fabricate citations, review excerpts, or evidence references.
- Preserve the distinction between an AI-generated explanation and a verified business fact.

**Acceptance criteria:**
- Users can inspect the evidence behind a finding.
- Findings without sufficient evidence are qualified appropriately.
- Failed or incomplete analyses are not displayed as successful.

### 12.4 Rating–Reality Contradiction Detector Components

**Purpose:** Surface potential mismatches between numerical ratings and the content of reviews.

**Components:**
- Mismatch summary
- Rating indicator
- Text sentiment or issue summary
- Review excerpt
- Detection rationale, if available
- Evidence inspection action

**Behavior:**
- Explain the type of mismatch identified.
- Show the original rating and relevant review text when available.
- Present the result as a potential contradiction, not proof of fraud or manipulation.
- Allow inspection of the underlying review.
- Clearly indicate when the classification is uncertain.

**Acceptance criteria:**
- The original rating and review evidence remain accessible.
- No person, seller, or reviewer is labeled fraudulent solely because of a detected mismatch.
- Model classifications are not presented as confirmed intent.

---

## 13. File Upload and Ingestion Components

### 13.1 Upload Dropzone

**Purpose:** Support the file-upload formats accepted by the existing ingestion implementation.

**Behavior:**
- Support drag-and-drop and file selection when compatible with the current stack.
- Show accepted file types and size limits based on verified backend constraints.
- Validate file type and size before upload where possible.
- Display the selected filename and file size.
- Provide a way to remove or replace a file before submission.
- Communicate upload failures clearly.

Do not claim support for a file format until it is implemented and verified.

### 13.2 Upload Progress

For long-running ingestion tasks, display actual progress when available.

Possible stages:
1. File selected
2. Uploading
3. Processing
4. Validating
5. Importing
6. Completed
7. Failed

Use only stages that correspond to real operations in the backend.

If the backend does not expose progress, show a truthful indeterminate loading state rather than inventing percentages.

### 13.3 Ingestion Result Summary

**Potential content:**
- Source filename or integration
- Processing status
- Records imported
- Records rejected
- Validation warnings
- Error summary
- Next action

All counts and statuses must come from actual ingestion results.

### 13.4 Integration Connection Card

For supported integrations:
- Display the integration name and connection status.
- Provide the relevant connection or configuration action.
- Show the latest successful sync when available.
- Clearly identify permission or configuration issues.
- Use the existing integration and authentication flow.

Do not display an integration as connected when its actual status is unknown.

---

## 14. Dialogs and Confirmation Components

### 14.1 Dialog

**Use for:** Short focused tasks requiring user attention.

**Requirements:**
- Clear title
- Concise description
- Explicit action buttons
- Keyboard-accessible focus handling
- Suitable mobile layout

### 14.2 Confirmation Dialog

Use before consequential or irreversible actions.

Examples:
- Deleting a saved item
- Removing a configured connection
- Discarding unsaved changes

**Behavior:**
- Explain what will happen.
- Identify the affected resource when possible.
- Use an explicit confirm action.
- Make cancellation easy.
- Do not describe an action as irreversible unless that is accurate.

### 14.3 Drawer

Use for contextual detail such as review evidence or insight investigation.

Prefer a drawer when users need to inspect details while retaining their current page context. Use a dialog for a short, focused task.

---

## 15. Toasts and Notifications

### 15.1 Toast Variants

- Success
- Error
- Warning
- Information

### 15.2 Behavior

- Communicate the result of a real action.
- Use concise, actionable language.
- Avoid displaying sensitive review content unnecessarily.
- Provide sufficient display time for reading.
- Do not make important error information available only in a toast.
- Avoid duplicate notifications for the same event.

For long-running operations, use a persistent status area or task panel when a short-lived toast is insufficient.

### 15.3 Notification Center

If supported by the existing product:
- Group notifications logically.
- Indicate read and unread states.
- Link notifications to relevant pages or evidence.
- Use actual notification data.
- Provide an understandable empty state.

Email alerts are optional and must only be exposed if the backend supports the relevant configuration and delivery flow.

---

## 16. Loading, Empty, Error, and Success States

Every data-driven component must handle its relevant states.

### 16.1 Loading

- Use skeletons that resemble the final content layout.
- Avoid sudden layout shifts.
- Keep long-running task status visible.
- Respect reduced-motion preferences.
- Do not display fabricated placeholder metrics that could be mistaken for real data.

### 16.2 Empty

An empty state should include:
- A clear explanation
- A relevant next step where possible
- A primary action when a genuine action is available

Distinguish an empty account from an empty filtered result.

### 16.3 Error

An error state should:
- Explain what failed in understandable language.
- Preserve user input when possible.
- Offer retry when retry is supported.
- Avoid exposing internal stack traces or secrets.
- Distinguish validation, network, permission, and processing errors when the information is available.

### 16.4 Success

- Confirm the completed action.
- Reflect the updated data or status.
- Offer a relevant next step when useful.
- Avoid reporting success before the operation actually completes.

---

## 17. Export and Saved Insight Components

### 17.1 Export Menu

Potential export formats:
- CSV
- PDF
- XLSX
- PNG

Only enable formats that the current application and backend actually support.

**Behavior:**
- Make the export scope clear.
- Respect current filters when applicable.
- Show progress for long-running exports when available.
- Display success only after a file is successfully generated or returned.
- Communicate failures without losing the user's current view.

### 17.2 Save Insight Control

If supported:
- Allow users to save and unsave an insight.
- Reflect the actual saved state.
- Prevent duplicate saves where relevant.
- Show success or error feedback.
- Preserve saved items according to the existing persistence model.

### 17.3 Compare Control

If comparison is supported:
- Allow the user to select comparable products, periods, or findings.
- Validate that the selected items can meaningfully be compared.
- Clearly label each comparison dimension.
- Use consistent periods and metrics.
- Avoid implying comparability when data coverage differs substantially.

---

## 18. Accessibility Requirements

Target **WCAG 2.2 Level AA** for the component system.

Required practices:
- Use semantic elements and appropriate accessible names.
- Ensure all interactive elements work by keyboard.
- Provide visible focus indicators.
- Maintain sufficient text and interface contrast.
- Do not rely on color alone to communicate information.
- Associate form fields with labels and errors.
- Manage focus in dialogs and drawers.
- Provide accessible names for icon-only buttons.
- Respect reduced-motion preferences.
- Ensure charts have accessible descriptions or equivalent data representations.
- Keep touch controls practical for mobile use.
- Avoid interactions that require hover as the only way to access essential information.

Accessibility checks must be performed against the implemented components, not inferred from their appearance.

---

## 19. Responsive Behavior

### Desktop
- Use the full application shell and sidebar.
- Keep data tables and charts readable.
- Allow contextual evidence panels beside the main content when space permits.

### Tablet
- Allow the sidebar to collapse.
- Adapt multi-column layouts.
- Prevent chart labels, filter controls, and action groups from overlapping.

### Mobile
- Use an appropriate compact navigation pattern.
- Stack content into a single primary column where appropriate.
- Convert contextual drawers to a mobile-friendly full-height view when needed.
- Make tables horizontally navigable or present a suitable alternative layout.
- Keep primary actions visible and reachable.
- Prevent fixed elements from covering content or keyboard focus.

Use the project's established breakpoints. If no breakpoints exist, propose and document them in `DESIGN_SYSTEM.md` before establishing new values across components.

---

## 20. Motion and Interaction

Motion should communicate state changes and improve orientation rather than decorate the interface.

**Suitable uses:**
- Drawer and dialog transitions
- Button and chip feedback
- Chart entrance or update transitions
- Staggered appearance of grouped insights
- Navigation state changes
- Upload progress transitions

**Requirements:**
- Use consistent timing and easing from the design system.
- Keep motion brief and non-disruptive.
- Avoid unnecessary bouncing, flashing, or continuous decorative movement.
- Respect reduced-motion preferences.
- Do not delay important user actions for animation.
- Ensure motion does not obscure content or make controls difficult to use.

---

## 21. Component Ownership and File Organization

Follow the repository's existing structure first. The following is a conceptual organization, not a mandate to move or duplicate existing files.

```text
src/
  components/
    layout/
      AppLayout
      Sidebar
      Header
      PageHeader
    ui/
      Button
      Input
      Select
      Dialog
      Drawer
      Badge
      Card
      Skeleton
      Toast
    data-display/
      DataTable
      FilterBar
      FilterChip
      KpiCard
      InsightCard
      ReviewSnippet
      ChartContainer
    evidence/
      EvidenceDrawer
      EvidenceList
      EvidenceCount
    ingestion/
      UploadDropzone
      UploadProgress
      IngestionSummary
    features/
      radar/
      investigator/
      promise-reality/
      contradiction-detector/
```

Adapt filenames and extensions to the existing framework and repository conventions.

### Ownership rules

- Shared UI components should have one authoritative implementation.
- Feature-specific components should remain close to the feature they serve.
- Shared components should not contain page-specific business logic.
- API calls should use the project's established service or API-client layer.
- Avoid creating duplicate components that differ only in minor styling.
- Before creating a new shared component, search the repository for an existing equivalent.
- Coordinate changes to shared components with teammates using the agreed branch and pull-request workflow.

---

## 22. Testing and Acceptance Criteria

Each reusable component must be tested according to its complexity and risk.

### Minimum checks

- Renders correctly with valid data.
- Handles missing or optional fields safely.
- Handles loading, empty, and error states where relevant.
- Supports keyboard interaction.
- Displays visible focus states.
- Works at desktop, tablet, and mobile widths.
- Does not overflow its container.
- Uses approved design tokens.
- Performs its stated action correctly.
- Does not fabricate backend results.
- Does not cause regressions in existing pages.

### Additional checks for data-driven components

- Values match the actual data source.
- Filters and sorting produce correct results.
- Pagination preserves the query state.
- Evidence links open the correct supporting records.
- Charts use the correct data range and labels.
- Export actions reflect the actual exported scope.
- Errors are handled without losing important user input.

### Quality gates

Before merging component changes:
1. Run the repository's available lint checks.
2. Run type checking when configured.
3. Run relevant component and integration tests.
4. Run the production build when practical.
5. Verify responsive layouts.
6. Check accessibility with available automated and manual methods.
7. Review the diff for unrelated changes and accidental overwrites.
8. Document checks that could not be executed.

Do not claim a check passed unless it was actually run.

---

## 23. Change Management

- Treat this document as the shared component contract.
- Update it when a component's behavior or interface changes materially.
- Review changes to shared tokens or shared component APIs before broad adoption.
- Do not make unilateral changes that break another teammate's feature.
- Prefer backward-compatible changes when feasible.
- Document any temporary exceptions and their intended resolution.
- Do not modify backend architecture, authentication, API contracts, or deployment configuration as part of a component-only change without explicit approval.

---

## 24. Definition of Done

A component is ready for reuse when:

- Its purpose and intended usage are clear.
- Its visual styling follows the approved design system.
- Its behavior is consistent and predictable.
- Its relevant loading, empty, error, and success states are implemented.
- Its accessibility and responsive requirements are met.
- Its data comes from verified sources or explicitly defined inputs.
- Its interactions work as documented.
- Its tests and applicable quality checks have been completed.
- Its implementation does not duplicate existing functionality or overwrite unrelated work.

**Final principle:** Every ReviewPulse component must make review intelligence easier to understand, inspect, and act upon while preserving evidence integrity, accessibility, visual consistency, and team-wide code ownership.
