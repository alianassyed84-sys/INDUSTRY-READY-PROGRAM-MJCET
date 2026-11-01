GOAL: data enters in two ways (product link, or dataset file: Amazon/Flipkart
CSV or JSON). Users then explore it through charts and plain-language summaries.
Language: simple English, short sentences. Forbidden on screen: backend, API,
database, polarity, compound, TF-IDF, ASIN/PID, snapshot, endpoint, CSV job.
Every number has a plain-language meaning (tooltip "What does this mean?").

SITE MAP
/                    Landing (shows BOTH entry points: paste a link / upload a
                     dataset)
/dashboard           All-data overview (see below)
/products            All Products library: search, sort, filter by data source
/product/:id/:tab    Product workspace, tabs = overview | reviews | sentiment |
                     topics | languages | readability | price (deep-linkable;
                     tab and product kept in the URL)
/analyze?url=        The ONLY link entry (one shared <UrlAnalyzer>), 3-step
                     progress, then goes to /product/:id/overview
/data                Data Sources: upload file, preview, import, history
/text-lab            paste any text -> mood, language, topics, reading level
/help /settings /login /register /recover   keep; Settings only has controls that
                     really work
/technical           technical details, not in nav, not linked
LATER, only when their backend exists: /reports, Processing Center, Buyer/Seller
mode, /compare.
REDIRECTS: /reviews /analysis /topics /language /readability /analytics ->
/products (user opens a product tab); /harvester -> /analyze; /about -> /help.

SHELL: Lavender Luxe sidebar + slim top bar. Sidebar: Dashboard | All Products |
Analyze a Link | Data Sources | Text Lab | Help | Settings. Top bar: quick
product switcher (keeps the current tab), profile menu. Inside a product the
sticky product header + tab bar replace any per-page product picker. Mobile:
sidebar becomes a drawer.

PAGE TEMPLATE: PageHeader (title, one plain line, at most one primary action)
-> filter bar -> cards on a 12-column grid, max width 1280px. Product header
always shows name, brand (never a raw category), marketplace (taken from the
product link domain, never hardcoded), price, rating, "Based on N of M reviews",
and "Sample data, not live reviews" when true. Category shows as a path like
"Electronics > Phones".

DATA SOURCES /data: (1) Upload file: drag and drop, then PREVIEW (detected type,
first 10 rows, row count, problems), then Import with progress, then a result
summary (products added, reviews added, duplicates skipped, errors) taken from
the backend counts only. (2) Analyze-a-link shortcut. (3) Import history table.
Never claim success without backend counts. Failures are explained in plain
words.

CHARTS (recharts only, one shared ChartCard). Each chart: a takeaway title in
plain words ("Most reviews are positive"), labelled axes, tooltip, legend,
colour-blind-safe palette, "View as table" toggle, plain empty state. Never draw
a chart on too little data (a line needs 2+ points). Never invent points.
DASHBOARD (all data): KPI cards (reviews, products, average stars, happy share,
unhappy share); rating distribution (bar); mood mix (donut); biggest complaints
(horizontal bar); top topics (bar); language mix (donut); latest imports.
PRODUCT TABS:
 overview: summary cards + fixed-template written summary + 3 real quotes.
 reviews: search, stars, mood, feature, language filters, sort, pagination;
   translated reviews show "Translated from X" + "Show original".
 sentiment: mood donut, per-feature positive-vs-negative bars, feature radar,
   click a bar to see those reviews.
 topics: toggle words / 2-word / 3-word phrases; bar "How important"; chips.
 languages: language bar or donut; "N reviews could not be read".
 readability: histogram of reading levels, "Average reading level" in words,
   formulas only under "More detail".
 price: line chart with lowest/highest markers, discount bar; one plain sentence
   when under 2 price checks.
Partial workspaces: a tab whose analysis is missing says so in a sentence.

DATA LIMITS (do not invent): no review date exists yet, so NO "reviews over time"
chart and NO date filter until the backend adds review_date. Insights must say
"analysed N of M" until the backend analyses all reviews. Missing values are a
plain sentence, never 0 (the readability adapter currently turns missing into 0
and returns an empty distribution: fix, do not copy).

VISUAL SYSTEM: keep Lavender Luxe exactly: bg #FAF7F2, primary #7138F5, navy
#171B50, Manrope headings, Inter body, glass surfaces, 20px cards, soft shadows.
One primary button per screen. Status colours (green / amber / red) always with
an icon and a word. Mobile-first at 375px. WCAG AA, visible focus, keyboard use,
aria-live for progress.
RULES: reuse existing components (preserve the existing frontend, restructure
rather than rebuild); no new dependencies; never show fake data as real; update
tests, never delete them; each piece ends with screenshots at 375, 768 and
1440 px.
