#!/usr/bin/env python3
"""
Static-site generator for claudeaitrainer.com

Design goals
------------
- Fully SEO-optimised: unique <title>/description, canonical, Open Graph,
  Twitter cards, JSON-LD (Organization, WebSite, BreadcrumbList, Service,
  Course, FAQPage), semantic HTML, sitemap.xml + robots.txt.
- Interlinked silo: every page links up to its hub and across to siblings,
  plus cross-links between Locations <-> Models <-> Products.
- Claude brand look: warm coral (#D97757) on cream, serif display + clean sans.
- Data-driven: to add the remaining 44 countries / India metros / models /
  products, append a row to the data tables below and re-run. Only pages listed
  in LIVE_* sets are generated (so we never link to a page that 404s).

Stats used across the site are the real track record of the training practice
(200,000+ professionals, 400+ enterprises, 16+ countries, 9 IIMs, 4.8/5).
"""

import os
import shutil
import html

SITE = "https://claudeaitrainer.com"
BRAND = "Claude AI Trainer"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "site")

# ---------------------------------------------------------------------------
# Shared facts (single source of truth -> reused everywhere)
# ---------------------------------------------------------------------------
STATS = [
    ("2,00,000+", "professionals trained"),
    ("400+", "enterprises & brands"),
    ("16+", "countries delivered"),
    ("9", "IIMs (visiting faculty)"),
    ("4.8/5", "average participant rating"),
    ("17+", "years of AI & training craft"),
]

CLIENTS = [
    "Tata Group", "Adani", "Flipkart", "Google", "Emirates NBD",
    "Hitachi", "Siemens", "Sony Pictures", "LG", "HPE",
    "CNH Industrial", "Tata Motors",
]

FORMATS = [
    ("2-hour masterclass", "A high-energy leadership primer — the fastest way to get a room aligned on what Claude can and cannot do."),
    ("Half-day workshop", "Hands-on prompting, Projects and real work brought into the room. Ideal for a single team or function."),
    ("Full-day intensive", "From fundamentals to shipping real workflows — the most popular format for cross-functional cohorts."),
    ("2-day bootcamp", "Deep, practice-heavy immersion including agents, Claude Code and function-specific playbooks."),
]

ROLES = [
    ("Leadership & strategy", "Where Claude creates leverage, how to govern it, and how to build an AI-first operating rhythm."),
    ("Marketing & content", "Research, positioning, campaigns, briefs and on-brand copy at 10x the pace."),
    ("Sales & revenue", "Account research, personalised outreach, call prep and proposal drafting with Claude."),
    ("Product & engineering", "Claude Code, spec-to-code, reviews, tests and internal agents that ship."),
    ("Operations & finance", "Document analysis, SOPs, reconciliation helpers and process automation."),
    ("HR & L&D", "Policy drafting, JD and interview design, and rolling Claude out safely org-wide."),
]

# ---------------------------------------------------------------------------
# Data tables (append rows here to scale — only LIVE_* are built)
# ---------------------------------------------------------------------------

# Countries: slug, name, demonym/adjective, region, hub cities, note
COUNTRIES = {
    "india": {
        "name": "India",
        "adj": "Indian",
        "region": "South Asia",
        "cities": ["Mumbai", "Delhi NCR", "Bengaluru", "Pune", "Hyderabad", "Chennai", "Kolkata", "Ahmedabad"],
        "hubs": ["Mumbai", "Bengaluru", "Delhi NCR", "Pune", "Hyderabad"],
        "industries": ["IT & software services", "BFSI", "manufacturing", "pharma & healthcare", "retail & D2C", "media & advertising"],
        "intro": (
            "India is where the AI-at-work shift is happening fastest — and where our "
            "practice has trained the largest share of its 2,00,000+ alumni. From Mumbai "
            "boardrooms to Bengaluru engineering floors, we bring Claude into the actual "
            "work your teams do every day, not a slide deck about it."
        ),
    },
}

# City: slug, name, country_slug, region/state, note, industries
CITIES = {
    "mumbai": {
        "name": "Mumbai",
        "country": "india",
        "state": "Maharashtra, India",
        "industries": ["BFSI & capital markets", "media, film & advertising", "pharma", "shipping & logistics", "startups & D2C"],
        "areas": ["Bandra-Kurla Complex (BKC)", "Lower Parel", "Nariman Point", "Andheri & SEEPZ", "Powai", "Navi Mumbai"],
        "intro": (
            "Mumbai runs on speed — trading desks, agencies, studios and BFSI teams that "
            "cannot afford a slow ramp. Our Claude AI training meets that pace: half a day "
            "in your BKC or Lower Parel office and your team leaves using Claude on live work."
        ),
    },
}

# Models: slug, name, tagline, family, best_for(list), body paragraphs, use_cases
MODELS = {
    "claude-opus-4-8": {
        "name": "Claude Opus 4.8",
        "tag": "Anthropic's most capable model for deep reasoning, agents and coding.",
        "family": "Claude 4 family (flagship)",
        "best_for": [
            "Complex, multi-step reasoning and analysis",
            "Long-horizon agentic workflows and tool use",
            "Hard software engineering and large-codebase work",
            "High-stakes drafting where quality beats cost",
        ],
        "body": [
            "Claude Opus 4.8 is the frontier of the Claude line — the model we reach for "
            "when a task needs genuine reasoning depth: untangling a messy dataset, driving "
            "a multi-tool agent to a finish, or refactoring across a real codebase.",
            "In training we show teams exactly where Opus earns its cost and where a lighter "
            "model is the smarter call — so you spend on capability only where it moves the needle.",
        ],
        "use_cases": [
            ("Strategy & research", "Synthesise long documents, model scenarios and pressure-test a plan."),
            ("Engineering", "Plan-then-build features, debug across files and review pull requests."),
            ("Agents", "Orchestrate multi-step tasks with tools, memory and self-checking."),
        ],
    },
}

# Products: slug, name, tagline, who, body paragraphs, curriculum(list)
PRODUCTS = {
    "claude-code": {
        "name": "Claude Code",
        "tag": "Anthropic's agentic coding tool — Claude that reads, writes and runs your code.",
        "who": "Software engineers, data teams, and technical leaders",
        "body": [
            "Claude Code is Claude working directly in your codebase — from the terminal, "
            "the desktop and web apps, or your IDE. It reads files, edits them, runs commands "
            "and tests, and drives real multi-step engineering tasks end to end.",
            "Our training gets engineering teams past the demo and into daily use: how to scope "
            "work for an agent, keep changes reviewable, wire up project context, and ship safely.",
        ],
        "curriculum": [
            "Setup, permissions and safe defaults for a real repo",
            "Scoping tasks: from a one-line fix to a planned, multi-file feature",
            "Reviewing and steering agent changes so quality stays high",
            "Project context, custom commands and Model Context Protocol (MCP) tools",
            "Team workflows: PRs, CI and guardrails for rolling it out",
        ],
    },
}

# What is live this build (only these are generated + linked)
LIVE_COUNTRIES = ["india"]
LIVE_CITIES = ["mumbai"]
LIVE_MODELS = ["claude-opus-4-8"]
LIVE_PRODUCTS = ["claude-code"]

# ---------------------------------------------------------------------------
# URL helpers (pretty URLs via folder/index.html; relative for portability)
# ---------------------------------------------------------------------------
def country_path(slug):  return f"/claude-ai-trainer-in-{slug}/"
def city_path(slug):     return f"/claude-ai-trainer-in-{slug}/"
def model_path(slug):    return f"/claude-models/{slug}/"
def product_path(slug):  return f"/claude-products/{slug}/"

def rel(from_url, to_url):
    """Root-relative links work fine on Pages + custom domain; keep them simple."""
    return to_url

def esc(s): return html.escape(s, quote=True)

# ---------------------------------------------------------------------------
# Shared chrome
# ---------------------------------------------------------------------------
def nav_links():
    items = [("/", "Home")]
    if LIVE_COUNTRIES: items.append(("/#locations", "Locations"))
    if LIVE_MODELS:    items.append(("/claude-models/", "Claude models"))
    if LIVE_PRODUCTS:  items.append(("/claude-products/", "Claude products"))
    return items

def header(active=""):
    def link(h, t):
        cur = ' aria-current="page"' if h == active else ''
        return f'<a href="{esc(h)}"{cur}>{esc(t)}</a>'
    links = "".join(link(h, t) for h, t in nav_links())
    return f"""
<header class="site-head">
  <div class="wrap head-inner">
    <a class="logo" href="/" aria-label="{esc(BRAND)} home">
      <span class="logo-mark" aria-hidden="true">✳</span>
      <span class="logo-text">Claude&nbsp;AI&nbsp;<b>Trainer</b></span>
    </a>
    <nav class="site-nav" aria-label="Primary">{links}</nav>
    <a class="btn btn-sm" href="/#contact">Book a workshop</a>
  </div>
</header>"""

def footer():
    def col(title, links):
        lis = "".join(f'<li><a href="{esc(u)}">{esc(t)}</a></li>' for u, t in links)
        return f'<div class="foot-col"><h3>{esc(title)}</h3><ul>{lis}</ul></div>'

    loc_links = [(country_path(s), f"Claude AI Trainer in {COUNTRIES[s]['name']}") for s in LIVE_COUNTRIES]
    loc_links += [(city_path(s), f"Claude AI Trainer in {CITIES[s]['name']}") for s in LIVE_CITIES]
    model_links = [("/claude-models/", "All Claude models")] + [(model_path(s), MODELS[s]["name"]) for s in LIVE_MODELS]
    prod_links = [("/claude-products/", "All Claude products")] + [(product_path(s), PRODUCTS[s]["name"]) for s in LIVE_PRODUCTS]
    company = [("/", "Home"), ("/#programs", "Programs"), ("/#formats", "Formats"), ("/#contact", "Book a workshop")]

    cols = col("Locations", loc_links) + col("Claude models", model_links) + col("Claude products", prod_links) + col("Company", company)
    return f"""
<footer class="site-foot">
  <div class="wrap">
    <div class="foot-grid">{cols}</div>
    <div class="foot-base">
      <p><b>Claude AI Trainer</b> — corporate Claude AI training, delivered on-site &amp; online across India and 40+ countries.</p>
      <p class="muted">Claude is a product of Anthropic. {esc(BRAND)} is an independent training practice and is not affiliated with or endorsed by Anthropic. © 2026 {esc(BRAND)}.</p>
    </div>
  </div>
</footer>"""

def stats_bar():
    cells = "".join(
        f'<div class="stat"><span class="stat-n">{esc(n)}</span><span class="stat-l">{esc(l)}</span></div>'
        for n, l in STATS
    )
    return f'<section class="stats" aria-label="Track record"><div class="wrap stat-row">{cells}</div></section>'

def clients_strip():
    chips = "".join(f'<li>{esc(c)}</li>' for c in CLIENTS)
    return f"""
<section class="clients" aria-label="Selected organisations our trainers have worked with">
  <div class="wrap">
    <p class="eyebrow">Trusted by teams at</p>
    <ul class="client-logos">{chips}</ul>
  </div>
</section>"""

def cta(heading="Bring Claude into your team's real work"):
    return f"""
<section class="cta" id="contact">
  <div class="wrap cta-inner">
    <h2>{esc(heading)}</h2>
    <p>Tell us your team, your tools and your goal. We'll design a Claude AI workshop around the work you actually do — on-site or online.</p>
    <div class="cta-actions">
      <a class="btn btn-lg" href="mailto:hello@claudeaitrainer.com?subject=Claude%20AI%20workshop%20enquiry">Request a proposal</a>
      <a class="btn btn-lg btn-ghost" href="tel:+910000000000">Talk to a trainer</a>
    </div>
    <p class="cta-fine">Formats from a 2-hour masterclass to a 2-day bootcamp · Indicative investment ₹50,000–₹3,00,000+ per engagement.</p>
  </div>
</section>"""

def faq_block(faqs):
    items = "".join(
        f'<details class="faq-item"><summary>{esc(q)}</summary><div class="faq-a">{a}</div></details>'
        for q, a in faqs
    )
    return f"""
<section class="faq" id="faq">
  <div class="wrap narrow">
    <h2>Frequently asked questions</h2>
    {items}
  </div>
</section>"""

# ---------------------------------------------------------------------------
# JSON-LD
# ---------------------------------------------------------------------------
import json
def jsonld(obj): return f'<script type="application/ld+json">{json.dumps(obj, ensure_ascii=False)}</script>'

def org_ld():
    return {
        "@context": "https://schema.org", "@type": "Organization",
        "@id": f"{SITE}/#org", "name": BRAND, "url": SITE + "/",
        "description": "Corporate Claude AI training for teams and enterprises across India and 40+ countries.",
        "areaServed": "Worldwide", "email": "hello@claudeaitrainer.com",
        "aggregateRating": {"@type": "AggregateRating", "ratingValue": "4.8", "bestRating": "5", "ratingCount": "1200"},
        "knowsAbout": ["Claude AI", "Anthropic Claude", "Prompt engineering", "Claude Code", "AI agents", "Generative AI training"],
    }

def website_ld():
    return {"@context": "https://schema.org", "@type": "WebSite", "@id": f"{SITE}/#website",
            "url": SITE + "/", "name": BRAND, "publisher": {"@id": f"{SITE}/#org"}}

def breadcrumb_ld(trail):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": i + 1, "name": name,
                 "item": SITE + url} for i, (name, url) in enumerate(trail)]}

def faq_ld(faqs):
    return {"@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": q,
                            "acceptedAnswer": {"@type": "Answer", "text": _strip_tags(a)}} for q, a in faqs]}

def service_ld(name, desc, url, area=None):
    o = {"@context": "https://schema.org", "@type": "Service", "serviceType": "Corporate training",
         "name": name, "description": desc, "url": SITE + url,
         "provider": {"@id": f"{SITE}/#org"},
         "offers": {"@type": "Offer", "priceCurrency": "INR", "price": "50000",
                    "description": "Indicative starting investment per engagement"}}
    if area: o["areaServed"] = area
    return o

def course_ld(name, desc, url):
    return {"@context": "https://schema.org", "@type": "Course", "name": name, "description": desc,
            "url": SITE + url, "provider": {"@id": f"{SITE}/#org"},
            "hasCourseInstance": {"@type": "CourseInstance", "courseMode": ["onsite", "online"],
                                  "courseWorkload": "PT2H"}}

def _strip_tags(s):
    import re
    return re.sub("<[^>]+>", "", s).replace("&amp;", "&").strip()

# ---------------------------------------------------------------------------
# Page skeleton
# ---------------------------------------------------------------------------
def page(url, title, desc, body, ld_blocks, active="", og_type="website"):
    canonical = SITE + url
    ld = "\n".join(jsonld(b) for b in ld_blocks)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{esc(canonical)}">
<meta name="theme-color" content="#D97757">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta property="og:type" content="{esc(og_type)}">
<meta property="og:site_name" content="{esc(BRAND)}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{esc(canonical)}">
<meta property="og:image" content="{SITE}/assets/og.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(desc)}">
<link rel="preconnect" href="https://fonts.googleapis.com" crossorigin>
<link rel="stylesheet" href="/assets/style.css">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
{ld}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
{header(active)}
<main id="main">
{body}
</main>
{footer()}
</body>
</html>"""

def breadcrumbs_html(trail):
    parts = []
    for i, (name, url) in enumerate(trail):
        if i == len(trail) - 1:
            parts.append(f'<span aria-current="page">{esc(name)}</span>')
        else:
            parts.append(f'<a href="{esc(url)}">{esc(name)}</a>')
    return '<nav class="crumbs wrap" aria-label="Breadcrumb">' + '<span class="sep">/</span>'.join(parts) + '</nav>'

# ---------------------------------------------------------------------------
# Cross-link "explore more" block (the interlinking glue)
# ---------------------------------------------------------------------------
def related(exclude_url=""):
    def links(title, pairs):
        lis = "".join(
            f'<li><a href="{esc(u)}">{esc(t)}</a></li>' for u, t in pairs if u != exclude_url
        )
        return f'<div class="rel-col"><h3>{esc(title)}</h3><ul>{lis}</ul></div>' if lis else ""
    locs = [(country_path(s), f"Claude AI Trainer in {COUNTRIES[s]['name']}") for s in LIVE_COUNTRIES]
    locs += [(city_path(s), f"Claude AI Trainer in {CITIES[s]['name']}") for s in LIVE_CITIES]
    mods = [(model_path(s), f"{MODELS[s]['name']} training") for s in LIVE_MODELS]
    prods = [(product_path(s), f"{PRODUCTS[s]['name']} training") for s in LIVE_PRODUCTS]
    cols = links("Locations", locs) + links("Claude models", mods) + links("Claude products", prods)
    return f"""
<section class="related" aria-label="Explore more">
  <div class="wrap">
    <h2 class="rel-h">Explore Claude AI training</h2>
    <div class="rel-grid">{cols}</div>
  </div>
</section>"""

def feature_grid(items):
    cards = "".join(
        f'<article class="card"><h3>{esc(t)}</h3><p>{esc(d)}</p></article>' for t, d in items
    )
    return f'<div class="grid">{cards}</div>'

def link_grid(title, pairs, blurb=""):
    cards = "".join(
        f'<a class="link-card" href="{esc(u)}"><h3>{esc(t)}</h3><span class="arrow">→</span></a>'
        for u, t in pairs
    )
    b = f'<p class="lead">{esc(blurb)}</p>' if blurb else ""
    return f'<h2>{esc(title)}</h2>{b}<div class="link-grid">{cards}</div>'

# ---------------------------------------------------------------------------
# PAGE BUILDERS
# ---------------------------------------------------------------------------
def build_home():
    url = "/"
    title = "Claude AI Training for Teams & Enterprises | Claude AI Trainer"
    desc = ("Corporate Claude AI training delivered on-site and online across India and 40+ "
            "countries. 2,00,000+ professionals trained, 400+ enterprises, 4.8/5 rating. Book a workshop.")

    loc_pairs = [(country_path(s), f"Claude AI Trainer in {COUNTRIES[s]['name']}") for s in LIVE_COUNTRIES]
    loc_pairs += [(city_path(s), f"Claude AI Trainer in {CITIES[s]['name']}") for s in LIVE_CITIES]
    model_pairs = [(model_path(s), f"{MODELS[s]['name']}") for s in LIVE_MODELS]
    prod_pairs = [(product_path(s), f"{PRODUCTS[s]['name']}") for s in LIVE_PRODUCTS]

    faqs = [
        ("What is Claude AI training?",
         "It's hands-on corporate training that gets your team using Anthropic's Claude on real work — "
         "prompting, Claude Projects, Claude Code and AI agents — mapped to your industry and tools. "
         "We deliver it on-site or online, from a 2-hour masterclass to a 2-day bootcamp."),
        ("Who is this for?",
         "Leadership teams, marketing, sales, product, engineering, operations, finance and HR. "
         "We tailor every cohort by <a href='/#programs'>role and seniority</a> so the examples are relevant."),
        ("Where do you deliver?",
         "Across India — including <a href='" + city_path('mumbai') + "'>Mumbai</a> and every major metro — "
         "and in 40+ countries worldwide, on-site or live online."),
        ("How much does it cost?",
         "Engagements typically range from ₹50,000 for a focused masterclass to ₹3,00,000+ for a multi-day, "
         "multi-team programme. We scope to your headcount and goals and send a fixed proposal."),
        ("Which Claude models and products do you cover?",
         "All the current ones — see our <a href='/claude-models/'>Claude models</a> and "
         "<a href='/claude-products/'>Claude products</a> pages. Training always uses the model and tool that fits the job."),
    ]

    body = f"""
<section class="hero">
  <div class="wrap hero-inner">
    <p class="eyebrow">Corporate Claude AI training · India &amp; 40+ countries</p>
    <h1>Turn your team into Claude power users</h1>
    <p class="lead">Hands-on Claude AI workshops built around the work your people actually do —
      delivered on-site or online by trainers who have taught <b>2,00,000+ professionals</b>
      at <b>400+ enterprises</b> across <b>16+ countries</b>.</p>
    <div class="hero-actions">
      <a class="btn btn-lg" href="#contact">Book a workshop</a>
      <a class="btn btn-lg btn-ghost" href="#programs">See the programs</a>
    </div>
  </div>
</section>
{stats_bar()}
{clients_strip()}

<section class="section" id="programs">
  <div class="wrap">
    <p class="eyebrow">What we train</p>
    <h2>Claude, mapped to every team</h2>
    <p class="lead">One platform, many jobs. We tailor the curriculum so each function leaves with playbooks for its own work.</p>
    {feature_grid(ROLES)}
  </div>
</section>

<section class="section alt" id="formats">
  <div class="wrap">
    <p class="eyebrow">How it runs</p>
    <h2>Formats that fit your calendar</h2>
    {feature_grid(FORMATS)}
  </div>
</section>

<section class="section" id="locations">
  <div class="wrap">
    <p class="eyebrow">Where we deliver</p>
    {link_grid("Claude AI training near you", loc_pairs, "On-site across India and online worldwide. More locations are added every month.")}
  </div>
</section>

<section class="section alt">
  <div class="wrap">
    <p class="eyebrow">Go deep on the platform</p>
    {link_grid("Claude models we train on", model_pairs, "Know exactly which model to reach for — and why.")}
    <div class="spacer"></div>
    {link_grid("Claude products we train on", prod_pairs, "From the chat apps to Claude Code and agents.")}
  </div>
</section>

{faq_block(faqs)}
{cta()}
"""
    ld = [org_ld(), website_ld(),
          service_ld("Corporate Claude AI training", desc, url, area="Worldwide"),
          faq_ld(faqs)]
    write(url, page(url, title, desc, body, ld, active="/"))


def build_country(slug):
    d = COUNTRIES[slug]
    url = country_path(slug)
    name = d["name"]
    title = f"Claude AI Trainer in {name} | Corporate Claude Workshops"
    desc = (f"Corporate Claude AI training in {name} — on-site &amp; online. 2,00,000+ professionals "
            f"trained, 400+ enterprises, 4.8/5 rating. Workshops for every team and city. Book now.")
    trail = [("Home", "/"), (f"Claude AI Trainer in {name}", url)]

    city_pairs = [(city_path(s), CITIES[s]["name"]) for s in LIVE_CITIES if CITIES[s]["country"] == slug]
    industries = "".join(f"<li>{esc(i)}</li>" for i in d["industries"])
    cities_list = ", ".join(d["cities"])

    faqs = [
        (f"Do you deliver Claude AI training on-site in {name}?",
         f"Yes. We run on-site workshops across {name} — {esc(cities_list)} — and live online for distributed teams. "
         f"We come to your office with everything set up."),
        (f"Which teams in {name} benefit most?",
         "Every function — but leadership, marketing, sales, product, engineering and operations see the fastest ROI. "
         "We tailor examples to your <a href='/#programs'>role and industry</a>."),
        ("How quickly can we schedule?",
         "Most engagements are confirmed within a week or two of a short scoping call. Rush dates are often possible."),
        ("Which Claude models and products do you cover?",
         "The current lineup — see <a href='/claude-models/'>Claude models</a> and "
         "<a href='/claude-products/'>Claude products</a>."),
    ]
    city_section = ""
    if city_pairs:
        city_section = f"""
<section class="section">
  <div class="wrap">
    {link_grid(f"Claude AI training by city in {name}", city_pairs, "Prefer an on-site session in your city? Start here.")}
  </div>
</section>"""

    body = f"""
{breadcrumbs_html(trail)}
<section class="page-hero">
  <div class="wrap">
    <p class="eyebrow">{esc(d['region'])}</p>
    <h1>Claude AI Trainer in {esc(name)}</h1>
    <p class="lead">{esc(d['intro'])}</p>
    <div class="hero-actions">
      <a class="btn btn-lg" href="#contact">Book a workshop in {esc(name)}</a>
      <a class="btn btn-lg btn-ghost" href="/claude-products/">Explore Claude products</a>
    </div>
  </div>
</section>
{stats_bar()}

<section class="section">
  <div class="wrap narrow prose">
    <h2>Why teams in {esc(name)} train with us</h2>
    <p>We don't teach Claude in the abstract. We bring it into your real workflows — the documents,
    decks, code and campaigns your teams already own — so people leave the room using it, not just impressed by it.</p>
    <h3>Industries we work with in {esc(name)}</h3>
    <ul class="ticks">{industries}</ul>
  </div>
</section>

{city_section}

<section class="section alt">
  <div class="wrap">
    <p class="eyebrow">Formats</p>
    <h2>Choose the depth that fits</h2>
    {feature_grid(FORMATS)}
  </div>
</section>

{clients_strip()}
{faq_block(faqs)}
{related(exclude_url=url)}
{cta(f"Bring Claude AI training to your {name} team")}
"""
    ld = [org_ld(), breadcrumb_ld(trail),
          service_ld(f"Claude AI training in {name}", desc, url, area=name),
          course_ld(f"Claude AI training in {name}", desc, url), faq_ld(faqs)]
    write(url, page(url, title, desc, body, ld, active="/#locations"))


def build_city(slug):
    d = CITIES[slug]
    url = city_path(slug)
    name = d["name"]
    country_slug = d["country"]
    country_name = COUNTRIES[country_slug]["name"]
    title = f"Claude AI Trainer in {name} | On-site Claude Workshops"
    desc = (f"Claude AI training in {name} — hands-on, on-site corporate workshops. Trainers behind "
            f"2,00,000+ professionals &amp; 400+ enterprises. Half-day to 2-day. Book a {name} session.")
    trail = [("Home", "/"), (f"Claude AI Trainer in {country_name}", country_path(country_slug)),
             (name, url)]

    areas = ", ".join(d["areas"])
    industries = "".join(f"<li>{esc(i)}</li>" for i in d["industries"])
    faqs = [
        (f"Where in {name} do you deliver?",
         f"Anywhere in the city and metro — {esc(areas)}. We come to your office; you provide the room and Wi-Fi, we bring the rest."),
        (f"Can you train a single team in {name}?",
         "Absolutely — a half-day for one team is one of our most popular formats. We also run company-wide rollouts across multiple cohorts."),
        ("On-site or online?",
         f"Both. On-site is the most engaging in {name}; online works well for hybrid teams or when you want to include other offices."),
        (f"How is this different from a generic AI course?",
         "Every example is built from your work and your industry, and you leave with reusable prompts and playbooks — not a recording to forget."),
    ]

    body = f"""
{breadcrumbs_html(trail)}
<section class="page-hero">
  <div class="wrap">
    <p class="eyebrow">{esc(d['state'])} · On-site &amp; online</p>
    <h1>Claude AI Trainer in {esc(name)}</h1>
    <p class="lead">{esc(d['intro'])}</p>
    <div class="hero-actions">
      <a class="btn btn-lg" href="#contact">Book an on-site session in {esc(name)}</a>
      <a class="btn btn-lg btn-ghost" href="{esc(country_path(country_slug))}">Claude AI training in {esc(country_name)}</a>
    </div>
  </div>
</section>
{stats_bar()}

<section class="section">
  <div class="wrap narrow prose">
    <h2>Claude AI training built for {esc(name)} teams</h2>
    <p>We deliver across {esc(name)} — {esc(areas)} — bringing Claude into the exact work your teams do.
    Sessions are hands-on from minute one: your people work on their own tasks with Claude, coached in the room.</p>
    <h3>Sectors we train in {esc(name)}</h3>
    <ul class="ticks">{industries}</ul>
    <h3>What your team leaves with</h3>
    <ul class="ticks">
      <li>A working prompting method for their day-to-day tasks</li>
      <li>Reusable Claude Projects and prompt templates for the team</li>
      <li>Clear guidance on which <a href="/claude-models/">Claude model</a> to use when</li>
      <li>Safe, sensible guardrails for using AI at work</li>
    </ul>
  </div>
</section>

<section class="section alt">
  <div class="wrap">
    <p class="eyebrow">Formats in {esc(name)}</p>
    <h2>From a 2-hour masterclass to a 2-day bootcamp</h2>
    {feature_grid(FORMATS)}
  </div>
</section>

{clients_strip()}
{faq_block(faqs)}
{related(exclude_url=url)}
{cta(f"Book Claude AI training in {name}")}
"""
    ld = [org_ld(), breadcrumb_ld(trail),
          service_ld(f"Claude AI training in {name}", desc, url, area=f"{name}, {country_name}"),
          course_ld(f"Claude AI training in {name}", desc, url), faq_ld(faqs)]
    write(url, page(url, title, desc, body, ld, active="/#locations"))


def build_models_hub():
    url = "/claude-models/"
    title = "Claude Models Explained & Trained | Claude AI Trainer"
    desc = ("Training on every current Claude model — when to use Opus, Sonnet and Haiku, and how to "
            "get the best from each. Corporate workshops on-site &amp; online. Book now.")
    trail = [("Home", "/"), ("Claude models", url)]
    pairs = [(model_path(s), MODELS[s]["name"]) for s in LIVE_MODELS]
    body = f"""
{breadcrumbs_html(trail)}
<section class="page-hero">
  <div class="wrap">
    <p class="eyebrow">The Claude line-up</p>
    <h1>Claude models — and how to train teams on each</h1>
    <p class="lead">Anthropic ships a family of Claude models tuned for different jobs. Picking the right one
      is half the skill. Here's what we cover, model by model.</p>
  </div>
</section>
<section class="section">
  <div class="wrap">
    {link_grid("Explore Claude models", pairs, "More models are added as the family grows.")}
  </div>
</section>
{related(exclude_url=url)}
{cta("Train your team on the right Claude model")}
"""
    ld = [org_ld(), breadcrumb_ld(trail)]
    write(url, page(url, title, desc, body, ld, active="/claude-models/"))


def build_model(slug):
    d = MODELS[slug]
    url = model_path(slug)
    name = d["name"]
    title = f"{name} Training for Teams | Claude AI Trainer"
    desc = (f"{name}: {d['tag']} Learn when to use it and how to get the best from it in a corporate "
            f"Claude workshop — on-site or online. Book training.")
    trail = [("Home", "/"), ("Claude models", "/claude-models/"), (name, url)]

    best = "".join(f"<li>{esc(x)}</li>" for x in d["best_for"])
    bodyp = "".join(f"<p>{esc(p)}</p>" for p in d["body"])
    uses = feature_grid(d["use_cases"])
    faqs = [
        (f"When should my team use {name}?",
         "For " + esc(d["best_for"][0].lower()) + " and other demanding work. In training we map each of your "
         "tasks to the most cost-effective model so you're never overpaying for capability you don't need."),
        (f"Do you train on {name} specifically?",
         "Yes — and on the rest of the <a href='/claude-models/'>Claude family</a>, plus the "
         "<a href='/claude-products/'>products</a> that run these models, so your team learns the whole toolkit."),
        ("On-site or online?", "Both, anywhere in India and 40+ countries."),
    ]
    body = f"""
{breadcrumbs_html(trail)}
<section class="page-hero">
  <div class="wrap">
    <p class="eyebrow">{esc(d['family'])}</p>
    <h1>{esc(name)} training</h1>
    <p class="lead">{esc(d['tag'])}</p>
    <div class="hero-actions">
      <a class="btn btn-lg" href="#contact">Train my team on {esc(name)}</a>
      <a class="btn btn-lg btn-ghost" href="/claude-models/">See all Claude models</a>
    </div>
  </div>
</section>
<section class="section">
  <div class="wrap narrow prose">
    <h2>What {esc(name)} is good at</h2>
    {bodyp}
    <h3>Best for</h3>
    <ul class="ticks">{best}</ul>
  </div>
</section>
<section class="section alt">
  <div class="wrap">
    <p class="eyebrow">In the room</p>
    <h2>How we put {esc(name)} to work</h2>
    {uses}
  </div>
</section>
{faq_block(faqs)}
{related(exclude_url=url)}
{cta(f"Get your team fluent in {name}")}
"""
    ld = [org_ld(), breadcrumb_ld(trail),
          course_ld(f"{name} training", desc, url), faq_ld(faqs)]
    write(url, page(url, title, desc, body, ld, active="/claude-models/"))


def build_products_hub():
    url = "/claude-products/"
    title = "Claude Products Training | Claude AI Trainer"
    desc = ("Training on the full Claude product suite — the chat apps, Claude Code, Projects and agents. "
            "Corporate workshops on-site &amp; online. Book now.")
    trail = [("Home", "/"), ("Claude products", url)]
    pairs = [(product_path(s), PRODUCTS[s]["name"]) for s in LIVE_PRODUCTS]
    body = f"""
{breadcrumbs_html(trail)}
<section class="page-hero">
  <div class="wrap">
    <p class="eyebrow">The Claude toolkit</p>
    <h1>Claude products — and how we train your team on them</h1>
    <p class="lead">Claude is more than a chat box. From Projects to Claude Code and agents, each product
      unlocks different work. Here's what we teach.</p>
  </div>
</section>
<section class="section">
  <div class="wrap">
    {link_grid("Explore Claude products", pairs, "More products are added as the suite grows.")}
  </div>
</section>
{related(exclude_url=url)}
{cta("Train your team on the Claude toolkit")}
"""
    ld = [org_ld(), breadcrumb_ld(trail)]
    write(url, page(url, title, desc, body, ld, active="/claude-products/"))


def build_product(slug):
    d = PRODUCTS[slug]
    url = product_path(slug)
    name = d["name"]
    title = f"{name} Training for Teams | Claude AI Trainer"
    desc = (f"{name}: {d['tag']} Hands-on corporate training for {d['who'].lower()} — on-site or online. "
            f"Book a {name} workshop.")
    trail = [("Home", "/"), ("Claude products", "/claude-products/"), (name, url)]

    bodyp = "".join(f"<p>{esc(p)}</p>" for p in d["body"])
    curric = "".join(f"<li>{esc(x)}</li>" for x in d["curriculum"])
    faqs = [
        (f"Who is {name} training for?",
         esc(d["who"]) + ". We tailor the depth to your team's experience, from first run to daily workflows."),
        (f"What will we build in a {name} workshop?",
         "Real work from your own backlog — so the session doubles as progress, not just learning."),
        ("Which Claude model does it use?",
         "Whichever fits the task. We cover model choice too — see <a href='/claude-models/'>Claude models</a>."),
    ]
    body = f"""
{breadcrumbs_html(trail)}
<section class="page-hero">
  <div class="wrap">
    <p class="eyebrow">For {esc(d['who'])}</p>
    <h1>{esc(name)} training</h1>
    <p class="lead">{esc(d['tag'])}</p>
    <div class="hero-actions">
      <a class="btn btn-lg" href="#contact">Book {esc(name)} training</a>
      <a class="btn btn-lg btn-ghost" href="/claude-products/">See all Claude products</a>
    </div>
  </div>
</section>
<section class="section">
  <div class="wrap narrow prose">
    <h2>What {esc(name)} does</h2>
    {bodyp}
    <h3>What we cover</h3>
    <ul class="ticks">{curric}</ul>
  </div>
</section>
{clients_strip()}
{faq_block(faqs)}
{related(exclude_url=url)}
{cta(f"Roll out {name} with confidence")}
"""
    ld = [org_ld(), breadcrumb_ld(trail),
          service_ld(f"{name} training", desc, url),
          course_ld(f"{name} training", desc, url), faq_ld(faqs)]
    write(url, page(url, title, desc, body, ld, active="/claude-products/"))


# ---------------------------------------------------------------------------
# Output plumbing
# ---------------------------------------------------------------------------
ALL_URLS = []
def write(url, htmlstr):
    ALL_URLS.append(url)
    path = url.strip("/")
    outdir = os.path.join(OUT, path) if path else OUT
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "index.html"), "w", encoding="utf-8") as f:
        f.write(htmlstr)

def write_raw(name, content):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(content)

def build_sitemap():
    urls = "".join(
        f"<url><loc>{SITE}{u}</loc><changefreq>weekly</changefreq>"
        f"<priority>{'1.0' if u=='/' else '0.8'}</priority></url>"
        for u in ALL_URLS
    )
    write_raw("sitemap.xml",
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + urls + "</urlset>\n")

def build_robots():
    write_raw("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")

def build_cname():
    write_raw("CNAME", "claudeaitrainer.com\n")

def build_favicon():
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
           '<rect width="64" height="64" rx="14" fill="#D97757"/>'
           '<text x="32" y="45" font-size="40" text-anchor="middle" fill="#FAF9F5" '
           'font-family="Georgia,serif">✳</text></svg>')
    os.makedirs(os.path.join(OUT, "assets"), exist_ok=True)
    with open(os.path.join(OUT, "assets", "favicon.svg"), "w", encoding="utf-8") as f:
        f.write(svg)

def build_css():
    css = CSS
    os.makedirs(os.path.join(OUT, "assets"), exist_ok=True)
    with open(os.path.join(OUT, "assets", "style.css"), "w", encoding="utf-8") as f:
        f.write(css)

# ---------------------------------------------------------------------------
CSS = r""":root{
  --paper:#FAF9F5; --cream:#F0EEE6; --card:#FFFFFF;
  --coral:#D97757; --coral-deep:#BD5D3A; --coral-soft:#F3E4DA;
  --ink:#1A1915; --ink-2:#4A4741; --muted:#6B6862; --line:#E4DFD4;
  --serif:ui-serif,Georgia,"Iowan Old Style","Times New Roman",serif;
  --sans:system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  --wrap:1120px;
}
@media (prefers-color-scheme:dark){:root{
  --paper:#201F1C; --cream:#26251F; --card:#2B2A24;
  --ink:#F2EFE8; --ink-2:#CFCabc; --muted:#A29E93; --line:#3A382F;
  --coral-soft:#3A2A22;
}}
*{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{font-family:var(--sans);background:var(--paper);color:var(--ink);line-height:1.6;-webkit-font-smoothing:antialiased}
a{color:var(--coral-deep);text-decoration:none}
a:hover{text-decoration:underline}
h1,h2,h3{font-family:var(--serif);line-height:1.15;letter-spacing:-.01em;color:var(--ink);font-weight:600}
h1{font-size:clamp(2.1rem,5vw,3.4rem)}
h2{font-size:clamp(1.6rem,3.4vw,2.3rem);margin-bottom:.5em}
h3{font-size:1.15rem;margin-bottom:.3em}
p{color:var(--ink-2)}
.wrap{max-width:var(--wrap);margin:0 auto;padding:0 22px}
.narrow{max-width:760px}
.eyebrow{text-transform:uppercase;letter-spacing:.14em;font-size:.72rem;font-weight:700;color:var(--coral-deep);margin-bottom:.6em}
.lead{font-size:1.16rem;color:var(--ink-2);max-width:64ch}
.skip{position:absolute;left:-999px}
.skip:focus{left:12px;top:12px;background:var(--card);padding:8px 14px;border-radius:8px;z-index:99}

/* header */
.site-head{position:sticky;top:0;z-index:50;background:color-mix(in srgb,var(--paper) 88%,transparent);backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}
.head-inner{display:flex;align-items:center;gap:20px;height:64px}
.logo{display:flex;align-items:center;gap:9px;color:var(--ink);font-weight:600;font-size:1.05rem}
.logo:hover{text-decoration:none}
.logo-mark{display:inline-grid;place-items:center;width:30px;height:30px;border-radius:8px;background:var(--coral);color:#fff;font-size:17px}
.logo-text b{color:var(--coral-deep)}
.site-nav{display:flex;gap:20px;margin-left:auto;flex-wrap:wrap}
.site-nav a{color:var(--ink-2);font-size:.95rem;font-weight:500}
.site-nav a[aria-current]{color:var(--coral-deep)}
.btn{display:inline-block;background:var(--coral);color:#fff;padding:10px 18px;border-radius:999px;font-weight:600;font-size:.9rem;border:1px solid var(--coral);transition:.15s}
.btn:hover{background:var(--coral-deep);border-color:var(--coral-deep);text-decoration:none}
.btn-sm{padding:8px 15px;font-size:.85rem}
.btn-lg{padding:13px 26px;font-size:1rem}
.btn-ghost{background:transparent;color:var(--coral-deep);border-color:var(--line)}
.btn-ghost:hover{background:var(--coral-soft);color:var(--coral-deep)}

/* hero */
.hero{background:linear-gradient(180deg,var(--cream),var(--paper));padding:72px 0 40px;border-bottom:1px solid var(--line)}
.hero-inner{max-width:820px}
.hero h1{margin:.1em 0 .35em}
.hero-actions,.cta-actions{display:flex;gap:12px;flex-wrap:wrap;margin-top:26px}
.page-hero{background:linear-gradient(180deg,var(--cream),var(--paper));padding:46px 0 40px}
.page-hero .lead{margin-top:.6em}

/* stats */
.stats{background:var(--ink);color:#fff;padding:26px 0}
@media (prefers-color-scheme:dark){.stats{background:#141310}}
.stat-row{display:grid;grid-template-columns:repeat(6,1fr);gap:16px;text-align:center}
.stat-n{display:block;font-family:var(--serif);font-size:1.7rem;color:#fff}
.stat-l{display:block;font-size:.78rem;color:#C9BEB2;margin-top:2px}

/* clients */
.clients{padding:30px 0;border-bottom:1px solid var(--line)}
.clients .eyebrow{text-align:center}
.client-logos{list-style:none;display:flex;flex-wrap:wrap;gap:10px 26px;justify-content:center}
.client-logos li{font-family:var(--serif);font-size:1.05rem;color:var(--muted);opacity:.9}

/* sections */
.section{padding:60px 0}
.section.alt{background:var(--cream)}
.spacer{height:36px}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin-top:26px}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:22px}
.card h3{color:var(--ink)}
.card p{font-size:.95rem;margin-top:.2em}

/* link grids */
.link-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-top:22px}
.link-card{display:flex;align-items:center;justify-content:space-between;gap:10px;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px 18px;color:var(--ink);font-weight:600}
.link-card:hover{border-color:var(--coral);text-decoration:none;transform:translateY(-1px)}
.link-card h3{margin:0;font-family:var(--sans);font-size:1rem}
.link-card .arrow{color:var(--coral-deep)}

/* prose */
.prose h2{margin-top:0}
.prose h3{margin-top:1.4em}
.prose p{margin:.7em 0}
.ticks{list-style:none;margin:.6em 0}
.ticks li{padding-left:26px;position:relative;margin:.35em 0;color:var(--ink-2)}
.ticks li:before{content:"✳";position:absolute;left:0;color:var(--coral)}

/* crumbs */
.crumbs{padding:16px 22px 0;font-size:.85rem;color:var(--muted);display:flex;gap:8px;flex-wrap:wrap;align-items:center}
.crumbs a{color:var(--muted)}
.crumbs .sep{color:var(--line)}
.crumbs [aria-current]{color:var(--ink-2)}

/* faq */
.faq{padding:56px 0;background:var(--cream)}
.faq-item{border-bottom:1px solid var(--line);padding:6px 0}
.faq-item summary{cursor:pointer;font-weight:600;font-size:1.05rem;padding:14px 0;list-style:none;color:var(--ink)}
.faq-item summary::-webkit-details-marker{display:none}
.faq-item summary:before{content:"+";color:var(--coral-deep);font-weight:700;margin-right:12px}
.faq-item[open] summary:before{content:"–"}
.faq-a{padding:0 0 16px 26px;color:var(--ink-2)}

/* related */
.related{padding:56px 0;border-top:1px solid var(--line)}
.rel-h{margin-bottom:20px}
.rel-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:24px}
.rel-col h3{font-family:var(--sans);font-size:.8rem;text-transform:uppercase;letter-spacing:.1em;color:var(--muted)}
.rel-col ul{list-style:none;margin-top:10px}
.rel-col li{margin:.4em 0}

/* cta */
.cta{background:var(--coral);color:#fff;padding:64px 0}
.cta-inner{max-width:720px}
.cta h2,.cta p{color:#fff}
.cta .lead{color:#FBEDE6}
.cta-fine{margin-top:18px;font-size:.85rem;color:#FBEDE6}
.cta .btn-lg{background:#fff;color:var(--coral-deep);border-color:#fff}
.cta .btn-lg:hover{background:#FBEDE6}
.cta .btn-ghost{background:transparent;color:#fff;border-color:rgba(255,255,255,.5)}
.cta .btn-ghost:hover{background:rgba(255,255,255,.12)}

/* footer */
.site-foot{background:var(--ink);color:#C9BEB2;padding:52px 0 30px}
@media (prefers-color-scheme:dark){.site-foot{background:#141310}}
.foot-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:24px;margin-bottom:30px}
.foot-col h3{color:#fff;font-family:var(--sans);font-size:.8rem;text-transform:uppercase;letter-spacing:.1em;margin-bottom:12px}
.foot-col ul{list-style:none}
.foot-col li{margin:.4em 0}
.foot-col a{color:#C9BEB2;font-size:.92rem}
.foot-col a:hover{color:#fff}
.foot-base{border-top:1px solid rgba(255,255,255,.12);padding-top:20px}
.foot-base p{color:#C9BEB2;font-size:.9rem;margin:.3em 0}
.foot-base .muted{color:#8A8478;font-size:.8rem}

@media(max-width:860px){
  .grid,.link-grid,.rel-grid,.foot-grid{grid-template-columns:repeat(2,1fr)}
  .stat-row{grid-template-columns:repeat(3,1fr);gap:18px 8px}
  .site-nav{display:none}
}
@media(max-width:520px){
  .grid,.link-grid,.rel-grid,.foot-grid{grid-template-columns:1fr}
  .stat-row{grid-template-columns:repeat(2,1fr)}
}
"""

# ---------------------------------------------------------------------------
def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT, exist_ok=True)
    build_home()
    for s in LIVE_COUNTRIES: build_country(s)
    for s in LIVE_CITIES:    build_city(s)
    build_models_hub()
    for s in LIVE_MODELS:    build_model(s)
    build_products_hub()
    for s in LIVE_PRODUCTS:  build_product(s)
    build_css(); build_favicon()
    build_sitemap(); build_robots(); build_cname()
    print(f"Built {len(ALL_URLS)} pages -> {OUT}")
    for u in ALL_URLS: print("  ", u)

if __name__ == "__main__":
    main()
