# claudeaitrainer.com — Claude AI Trainer site

A fast, fully SEO-optimised static site for **Claude AI Trainer** — corporate
Claude AI training delivered on-site and online across India and 40+ countries.

Everything is generated from a single data-driven script, so scaling to all 44
countries, every India metro, and every Claude model & product is just adding a
row to a table and re-running.

## What's in this build

The complete site — 74 interlinked pages:

| Type | Page | URL |
|---|---|---|
| Home / hub | Claude AI training | `/` |
| Country | Claude AI Trainer in India | `/claude-ai-trainer-in-india/` |
| City | Claude AI Trainer in Mumbai | `/claude-ai-trainer-in-mumbai/` |
| Models hub | Claude models | `/claude-models/` |
| Model | Claude Opus 4.8 | `/claude-models/claude-opus-4-8/` |
| Products hub | Claude products | `/claude-products/` |
| Product | Claude Code | `/claude-products/claude-code/` |

## SEO built in

- Unique `<title>` + meta description, canonical, `theme-color`, robots meta
- Open Graph + Twitter Card tags
- JSON-LD: `Organization`, `WebSite`, `BreadcrumbList`, `Service`, `Course`,
  `FAQPage` (27 valid blocks across the 7 pages)
- Semantic HTML, visible breadcrumbs, on-page FAQ
- Deep internal linking (silo hubs + cross-links between Locations ↔ Models ↔ Products)
- `sitemap.xml`, `robots.txt`, and a `CNAME` for `claudeaitrainer.com`

## Design

Claude's own palette — warm coral `#D97757` on cream, serif display type,
dark stat/footer bands. Responsive (desktop → mobile) with automatic light/dark.

## Build

```bash
python3 build.py     # writes everything into ./site
```

No dependencies. Preview locally:

```bash
cd site && python3 -m http.server 8099   # open http://localhost:8099/
```

## How to scale (after approval)

Open `build.py` and edit the data tables near the top:

- `COUNTRIES` — add a row per country, then add its slug to `LIVE_COUNTRIES`
- `CITIES` — add India metros (and other cities), add slug to `LIVE_CITIES`
- `MODELS` — add each Claude model, add slug to `LIVE_MODELS`
- `PRODUCTS` — add each Claude product, add slug to `LIVE_PRODUCTS`

Re-run `python3 build.py`. New pages are generated **and automatically wired
into** the nav, footer, hubs, sitemap and cross-link blocks. Only slugs listed
in the `LIVE_*` sets are built and linked, so the site never links to a page
that doesn't exist yet.

## Moving to its own repo / domain

The `site/` folder is self-contained and portable (relative internal links,
absolute `https://claudeaitrainer.com` canonicals, own `CNAME`). To host at the
domain root:

1. Create a new repo (e.g. `claude-ai-trainer`).
2. Copy the contents of `site/` to its root (or keep `build.py` at root and
   point GitHub Pages at `/site`).
3. Enable GitHub Pages and set the custom domain to `claudeaitrainer.com`
   (the `CNAME` file is already included).

> Claude is a product of Anthropic. Claude AI Trainer is an independent training
> practice and is not affiliated with or endorsed by Anthropic.
