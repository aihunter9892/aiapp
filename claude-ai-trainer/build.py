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
# BASE_PATH lets us serve the same build under a sub-path (e.g. GitHub Pages
# preview at /aiapp/claude-ai-trainer). Canonical/OG URLs always stay absolute
# to the real domain; only on-page internal links/assets are prefixed.
BASE_PATH = os.environ.get("BASE_PATH", "").rstrip("/")
OUT = os.environ.get("OUT_DIR") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "site")

# ---------------------------------------------------------------------------
# Shared facts (single source of truth -> reused everywhere)
# ---------------------------------------------------------------------------
# (display, label, number, decimals, suffix, locale) — number/decimals drive the count-up animation
STATS = [
    ("2,00,000+", "professionals trained", 200000, 0, "+", "en-IN"),
    ("400+", "enterprises & brands", 400, 0, "+", "en-US"),
    ("16+", "countries delivered", 16, 0, "+", "en-US"),
    ("9", "IIMs (visiting faculty)", 9, 0, "", "en-US"),
    ("4.8/5", "average participant rating", 4.8, 1, "/5", "en-US"),
    ("17+", "years of AI & training craft", 17, 0, "+", "en-US"),
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

# Countries: (slug, name, region, business hubs, industries, intro)
_COUNTRY_ROWS = [
    ("india", "India", "South Asia",
     ["Mumbai", "Delhi NCR", "Bengaluru", "Pune", "Hyderabad", "Chennai", "Kolkata", "Ahmedabad", "Gurgaon", "Noida"],
     ["IT & software services", "BFSI", "manufacturing", "pharma & healthcare", "retail & D2C", "media & advertising"],
     "India is where the AI-at-work shift is happening fastest — and where our practice has trained the "
     "largest share of its 2,00,000+ alumni. From Mumbai boardrooms to Bengaluru engineering floors, we bring "
     "Claude into the actual work your teams do every day, not a slide deck about it."),
    ("uae", "UAE", "Middle East",
     ["Dubai", "Abu Dhabi", "Sharjah"],
     ["banking & finance", "government & free zones", "real estate & construction", "aviation & logistics", "retail & tourism", "energy"],
     "From DIFC trading floors to Abu Dhabi's sovereign institutions, the Emirates is building an AI-first "
     "economy at national-strategy speed. We bring Claude into that ambition — hands-on workshops for banks, "
     "government entities and family conglomerates across Dubai, Abu Dhabi and Sharjah."),
    ("usa", "USA", "North America",
     ["New York", "San Francisco", "Chicago", "Austin", "Seattle"],
     ["technology & SaaS", "financial services", "healthcare", "retail & e-commerce", "media", "professional services"],
     "American teams don't need convincing about AI — they need fluency that outpaces the market. From New York "
     "financial services to Bay Area product orgs, our workshops turn Claude seats into shipped work, "
     "delivered on-site or live online across US time zones."),
    ("uk", "UK", "Europe",
     ["London", "Manchester", "Birmingham", "Edinburgh"],
     ["financial services", "professional services", "media & creative", "life sciences", "retail", "public sector"],
     "From the City's trading desks to Soho's creative agencies, UK organisations are past the AI pilot phase "
     "and into the productivity race. We train London and regional teams to make Claude a daily instrument — "
     "safely, and in line with your governance."),
    ("singapore", "Singapore", "Southeast Asia",
     ["Raffles Place & Marina Bay", "Changi Business Park", "one-north"],
     ["banking & wealth", "commodities & trading", "logistics & maritime", "technology & startups", "pharma manufacturing", "government"],
     "Singapore runs on being two steps ahead — and its Smart Nation agenda has made AI fluency a baseline "
     "skill. We deliver Claude workshops for banks, trading houses, agencies and regional HQs across the "
     "island, on-site or online."),
    ("canada", "Canada", "North America",
     ["Toronto", "Vancouver", "Montreal", "Calgary"],
     ["banking & insurance", "technology", "energy", "healthcare", "mining", "public sector"],
     "From Bay Street banks to Vancouver and Montreal tech hubs, Canadian teams are adopting AI with "
     "characteristic care — governance first, value fast. Our Claude training fits that culture: practical, "
     "safe and measurable."),
    ("germany", "Germany", "Europe",
     ["Berlin", "Munich", "Frankfurt", "Hamburg", "Stuttgart"],
     ["automotive", "engineering & Mittelstand", "banking", "chemicals & pharma", "logistics", "software"],
     "German engineering excellence deserves AI tooling used with the same rigour. From Frankfurt finance to "
     "Bavarian manufacturers and the Mittelstand backbone, we train teams to put Claude to work on "
     "documentation, analysis, code and process — properly."),
    ("france", "France", "Europe",
     ["Paris", "Lyon", "Toulouse", "Marseille"],
     ["luxury & retail", "banking & insurance", "aerospace", "energy", "consulting", "pharma"],
     "From La Défense towers to the ateliers of luxury houses, French enterprises are industrialising AI. "
     "Our Claude workshops give Paris and regional teams a working method — prompting, Projects and agents — "
     "applied to their own métier."),
    ("switzerland", "Switzerland", "Europe",
     ["Zurich", "Geneva", "Basel", "Zug"],
     ["banking & wealth management", "pharma", "insurance & reinsurance", "commodities trading", "precision manufacturing"],
     "Swiss organisations hold themselves to a different standard of precision and discretion — and their AI "
     "adoption is no different. We train banking, pharma and trading teams in Zurich, Geneva and Basel to use "
     "Claude with exactly that rigour."),
    ("japan", "Japan", "East Asia",
     ["Tokyo", "Osaka", "Nagoya", "Fukuoka"],
     ["automotive", "electronics & manufacturing", "banking & insurance", "trading houses", "pharma"],
     "Japan's enterprises are moving from AI curiosity to disciplined deployment — kaizen applied to knowledge "
     "work. Our Claude workshops for Tokyo and Osaka teams are hands-on, structured and built around your "
     "own gemba: the real work."),
    ("saudi-arabia", "Saudi Arabia", "Middle East",
     ["Riyadh", "Jeddah", "Dammam", "NEOM"],
     ["energy", "government & Vision 2030 programs", "banking", "construction & giga-projects", "retail"],
     "Vision 2030 has made the Kingdom one of the world's most ambitious AI adopters. From Riyadh ministries "
     "to giga-project teams, we deliver Claude training that matches that scale — bilingual-friendly, "
     "hands-on and tied to real deliverables."),
    ("hong-kong", "Hong Kong", "East Asia",
     ["Central", "Kowloon East", "Cyberport & Science Park"],
     ["banking & capital markets", "insurance", "trading & logistics", "professional services", "real estate"],
     "Hong Kong's finance and trading floors run on speed and precision — the exact conditions where Claude "
     "compounds. We train banks, insurers and professional firms across Central and Kowloon to fold AI into "
     "deal work, research and client service."),
    ("china", "China", "East Asia",
     ["Shanghai", "Beijing", "Shenzhen", "Guangzhou"],
     ["manufacturing & supply chain", "e-commerce", "automotive & EV", "electronics", "finance"],
     "For multinationals and export-facing teams operating in China, global AI fluency is now table stakes. "
     "We train Shanghai, Beijing and Shenzhen teams — in-person or online — with enterprise-appropriate "
     "setups for international AI tools."),
    ("taiwan", "Taiwan", "East Asia",
     ["Taipei", "Hsinchu", "Taichung", "Kaohsiung"],
     ["semiconductors", "electronics manufacturing", "ICT", "precision machinery", "finance"],
     "The island that powers the world's compute is putting AI to work on its own operations. From Hsinchu "
     "fabs to Taipei HQs, we train engineering and business teams to make Claude part of the daily toolchain."),
    ("indonesia", "Indonesia", "Southeast Asia",
     ["Jakarta", "Surabaya", "Bandung", "Bali"],
     ["banking", "e-commerce & digital", "consumer goods", "energy & mining", "telecom"],
     "Indonesia's digital economy is scaling faster than teams can hire — which makes AI leverage the "
     "obvious answer. We train Jakarta's banks, unicorns and conglomerates to put Claude to work across "
     "operations, marketing and engineering."),
    ("vietnam", "Vietnam", "Southeast Asia",
     ["Ho Chi Minh City", "Hanoi", "Da Nang"],
     ["manufacturing & exports", "software outsourcing", "banking", "e-commerce", "logistics"],
     "Vietnam is the rising factory and software floor of Asia — and its teams are hungry for leverage. "
     "From HCMC to Hanoi, our Claude workshops give manufacturers, banks and dev shops a faster way to "
     "compete globally."),
    ("philippines", "Philippines", "Southeast Asia",
     ["Metro Manila", "Cebu", "Davao"],
     ["BPO & shared services", "banking", "real estate", "retail", "telecom"],
     "The Philippines runs the world's back office — and AI is rewriting what that work looks like. We help "
     "BPOs, shared-service centres and banks across Manila and Cebu move up the value chain with Claude, "
     "not get displaced by it."),
    ("sri-lanka", "Sri Lanka", "South Asia",
     ["Colombo", "Kandy", "Galle"],
     ["IT & BPM", "apparel & manufacturing", "banking", "tea & agri-exports", "tourism & hospitality"],
     "Colombo's IT-BPM sector and export houses are rebuilding for a digital decade, and AI skills are the "
     "multiplier. Our Claude workshops give Sri Lankan teams world-class capability at practical, "
     "local-friendly formats."),
    ("nepal", "Nepal", "South Asia",
     ["Kathmandu", "Lalitpur", "Pokhara"],
     ["banking & microfinance", "IT services", "development sector", "tourism", "fintech & remittances"],
     "Nepal's young IT workforce and banking sector are leapfrogging straight into the AI era. We train "
     "Kathmandu teams — banks, dev shops and development organisations — to use Claude as a daily "
     "productivity engine."),
    ("uzbekistan", "Uzbekistan", "Central Asia",
     ["Tashkent", "Samarkand", "Bukhara"],
     ["banking & fintech", "government digitalisation", "IT park startups", "textiles", "mining"],
     "Uzbekistan's reform-driven economy is digitalising at remarkable pace, with Tashkent's IT Park at the "
     "centre. We bring Claude training to banks, ministries and startups building the region's next "
     "digital chapter."),
    ("italy", "Italy", "Europe",
     ["Milan", "Rome", "Turin", "Bologna"],
     ["fashion & luxury", "banking", "manufacturing & machinery", "food & beverage", "automotive"],
     "From Milan's fashion houses to the manufacturing districts of the north, Italian excellence is "
     "artisanal — and AI is its newest tool. We train teams to use Claude with taste: on brand, on brief "
     "and on their own work."),
    ("spain", "Spain", "Europe",
     ["Madrid", "Barcelona", "Valencia", "Bilbao"],
     ["banking", "tourism & hospitality", "retail & fashion", "energy", "telecom"],
     "Spanish enterprises — from Madrid's banks to Barcelona's tech scene — are scaling AI beyond pilots. "
     "Our Claude workshops land in Spanish or English, built around each team's real workflows."),
    ("sweden", "Sweden", "Europe",
     ["Stockholm", "Gothenburg", "Malmö"],
     ["engineering & automotive", "fintech", "telecom", "gaming & tech", "retail"],
     "Sweden ships world-class products with famously lean teams — exactly the environment where Claude "
     "multiplies output. We train Stockholm and Gothenburg orgs to fold AI into design, code and operations."),
    ("denmark", "Denmark", "Europe",
     ["Copenhagen", "Aarhus", "Odense"],
     ["pharma", "shipping & logistics", "renewable energy", "design & consumer", "fintech"],
     "Danish organisations pair pragmatism with design sense, and their AI adoption reflects it. From "
     "Copenhagen pharma to global shipping lines, we train teams to make Claude part of an elegant, "
     "efficient workflow."),
    ("finland", "Finland", "Europe",
     ["Helsinki", "Espoo", "Tampere"],
     ["telecom & tech", "engineering", "gaming", "forestry & materials", "energy"],
     "Finland's engineering culture takes new tools seriously — once proven, they're everywhere. We give "
     "Helsinki and Espoo teams the proof and the practice: Claude applied to real code, documents and "
     "decisions."),
    ("austria", "Austria", "Europe",
     ["Vienna", "Graz", "Linz", "Salzburg"],
     ["banking", "industrial manufacturing", "energy", "logistics", "tourism"],
     "Vienna's banks and Austria's industrial champions are quietly building serious AI capability. Our "
     "Claude workshops match that style — substantive, well-organised and immediately useful."),
    ("poland", "Poland", "Europe",
     ["Warsaw", "Kraków", "Wrocław", "Gdańsk"],
     ["shared services & IT", "banking", "manufacturing", "logistics", "gaming"],
     "Poland is Europe's engine room for shared services and software — and AI is redefining both. We train "
     "Warsaw and Kraków centres to move up the value curve with Claude across finance, HR, IT and delivery."),
    ("romania", "Romania", "Europe",
     ["Bucharest", "Cluj-Napoca", "Timișoara", "Iași"],
     ["IT & outsourcing", "banking", "automotive components", "energy", "telecom"],
     "Romania's tech talent already builds for the world; Claude makes those teams dramatically faster. "
     "From Bucharest to Cluj, we train engineering and business teams to work AI-first."),
    ("greece", "Greece", "Europe",
     ["Athens", "Thessaloniki", "Patras"],
     ["shipping", "tourism & hospitality", "banking", "energy", "food & agri"],
     "From Piraeus shipping offices to a fast-growing Athens tech scene, Greek enterprises are modernising "
     "at speed. Our Claude workshops give commercial and operations teams practical AI leverage from day one."),
    ("turkey", "Turkey", "Eurasia",
     ["Istanbul", "Ankara", "Izmir"],
     ["banking", "manufacturing & exports", "e-commerce", "construction", "logistics"],
     "Istanbul's banks, exporters and e-commerce giants compete across three continents — and AI is the "
     "new edge. We deliver Claude training that works in Turkish business culture: fast, relationship-driven "
     "and results-first."),
    ("russia", "Russia", "Eurasia",
     ["Moscow", "St Petersburg", "Kazan"],
     ["energy", "banking", "metals & mining", "telecom", "retail"],
     "For internationally connected teams in Russia, we deliver Claude training online — the same hands-on "
     "method, adapted to remote delivery and your compliance context."),
    ("egypt", "Egypt", "Africa",
     ["Cairo", "Alexandria", "Giza"],
     ["banking", "telecom", "outsourcing & shared services", "construction", "tourism"],
     "Cairo is one of the region's great talent pools, and its banks, telcos and shared-service centres are "
     "embracing AI fast. Our Claude workshops give Egyptian teams world-class skills in practical formats."),
    ("morocco", "Morocco", "Africa",
     ["Casablanca", "Rabat", "Tangier", "Marrakech"],
     ["banking", "automotive & aerospace manufacturing", "offshoring", "agriculture", "tourism"],
     "From Casablanca's finance district to Tangier's factories serving Europe, Morocco is Africa's "
     "industrial bridge. We train teams in French or English to put Claude to work across operations "
     "and services."),
    ("tunisia", "Tunisia", "Africa",
     ["Tunis", "Sfax", "Sousse"],
     ["IT & outsourcing", "textiles & manufacturing", "banking", "agri-exports", "tourism"],
     "Tunisia's engineers serve clients across Europe — and Claude makes those teams sharper and faster. "
     "We deliver hands-on workshops in Tunis for IT firms, banks and exporters, in French or English."),
    ("kenya", "Kenya", "Africa",
     ["Nairobi", "Mombasa", "Kisumu"],
     ["banking & mobile money", "telecom", "development sector", "agriculture & exports", "logistics"],
     "Nairobi leapfrogged the world on mobile money; AI is its next leap. We train Kenya's banks, telcos "
     "and development organisations to make Claude a daily working tool — practical, safe and local-context "
     "aware."),
    ("brazil", "Brazil", "South America",
     ["São Paulo", "Rio de Janeiro", "Belo Horizonte", "Brasília"],
     ["banking & fintech", "agribusiness", "retail & e-commerce", "energy", "manufacturing", "media"],
     "São Paulo is Latin America's business capital and its fintech scene rivals anywhere on earth. We "
     "train Brazilian enterprises — banks, retailers, agrobusiness — to turn Claude into everyday "
     "productivity, delivered in English or with Portuguese-friendly materials."),
    ("argentina", "Argentina", "South America",
     ["Buenos Aires", "Córdoba", "Rosario"],
     ["software & IT exports", "agribusiness", "banking", "energy", "e-commerce"],
     "Argentina exports world-class software talent — and that talent multiplied by Claude is formidable. "
     "We train Buenos Aires teams across tech, banking and agro to work AI-first."),
    ("mexico", "Mexico", "North America",
     ["Mexico City", "Monterrey", "Guadalajara"],
     ["manufacturing & nearshoring", "banking", "retail", "automotive", "fintech"],
     "Nearshoring has put Mexican operations at the centre of North American supply chains — and AI keeps "
     "them there. We train CDMX, Monterrey and Guadalajara teams to fold Claude into manufacturing, finance "
     "and commercial work."),
    ("colombia", "Colombia", "South America",
     ["Bogotá", "Medellín", "Cali", "Barranquilla"],
     ["banking", "BPO & software", "energy", "retail", "logistics"],
     "Bogotá and Medellín have become serious tech and services hubs, and Colombian teams adopt new tools "
     "with real energy. Our Claude workshops channel that energy into skills that show up in the P&L."),
    ("peru", "Peru", "South America",
     ["Lima", "Arequipa", "Cusco"],
     ["mining", "banking", "retail", "agri-exports", "logistics"],
     "Lima's banks, miners and retailers run lean — which is exactly where Claude's leverage lands hardest. "
     "We deliver practical AI workshops for Peruvian teams, on-site or online."),
    ("ecuador", "Ecuador", "South America",
     ["Quito", "Guayaquil", "Cuenca"],
     ["banking", "agri-exports", "energy", "retail", "logistics"],
     "From Quito's banks to Guayaquil's exporters, Ecuadorian enterprises are modernising fast. Our Claude "
     "training gives commercial and operations teams immediate, practical AI capability."),
    ("bolivia", "Bolivia", "South America",
     ["La Paz", "Santa Cruz", "Cochabamba"],
     ["banking", "mining & energy", "agribusiness", "telecom", "commerce"],
     "Santa Cruz and La Paz businesses are joining the region's AI wave, and early movers will set the "
     "pace. We bring hands-on Claude training to Bolivian banks, agro firms and operators — online or "
     "on-site."),
    ("costa-rica", "Costa Rica", "North America",
     ["San José", "Heredia", "Cartago"],
     ["shared services & BPO", "medtech manufacturing", "software", "tourism", "agri-exports"],
     "Costa Rica hosts some of the hemisphere's best shared-service and medtech operations. We train those "
     "centres to move up the value chain with Claude — analysis, automation and better client work."),
    ("new-zealand", "New Zealand", "Oceania",
     ["Auckland", "Wellington", "Christchurch"],
     ["agri & dairy exports", "banking", "government", "tech & SaaS", "tourism"],
     "Kiwi organisations punch far above their weight, and lean teams are exactly where Claude shines. From "
     "Auckland enterprises to Wellington agencies, we make AI a practical daily tool."),
]

COUNTRIES = {
    slug: {"name": name, "region": region, "cities": cities, "industries": inds, "intro": intro}
    for slug, name, region, cities, inds, intro in _COUNTRY_ROWS
}
COUNTRY_ORDER = [r[0] for r in _COUNTRY_ROWS]

# City: (slug, name, state, areas, industries, intro) — all in India
_CITY_ROWS = [
    ("mumbai", "Mumbai", "Maharashtra, India",
     ["Bandra-Kurla Complex (BKC)", "Lower Parel", "Nariman Point", "Andheri & SEEPZ", "Powai", "Navi Mumbai"],
     ["BFSI & capital markets", "media, film & advertising", "pharma", "shipping & logistics", "startups & D2C"],
     "Mumbai runs on speed — trading desks, agencies, studios and BFSI teams that cannot afford a slow ramp. "
     "Our Claude AI training meets that pace: half a day in your BKC or Lower Parel office and your team "
     "leaves using Claude on live work."),
    ("delhi-ncr", "Delhi NCR", "National Capital Region, India",
     ["Connaught Place", "Nehru Place", "Aerocity", "Okhla & Mohan Estate", "Dwarka", "Saket"],
     ["government & PSUs", "IT & consulting", "BFSI", "media & communications", "startups", "manufacturing"],
     "Delhi is where policy, capital and enterprise meet — and its organisations are adopting AI with "
     "national-mission urgency. From Connaught Place headquarters to Aerocity offices, we train leadership "
     "and delivery teams to make Claude their daily edge."),
    ("bengaluru", "Bengaluru", "Karnataka, India",
     ["MG Road & CBD", "Koramangala", "Whitefield", "Electronic City", "Outer Ring Road", "HSR Layout"],
     ["IT services & GCCs", "startups & SaaS", "e-commerce", "biotech", "aerospace & defence"],
     "India's tech capital doesn't need an AI introduction — it needs mastery. We train Bengaluru's GCCs, "
     "SaaS teams and startups on the deep end of Claude: agentic coding, Projects at team scale and "
     "workflows that actually ship."),
    ("pune", "Pune", "Maharashtra, India",
     ["Hinjawadi", "Kharadi & EON IT Park", "Magarpatta", "Baner-Balewadi", "Senapati Bapat Road"],
     ["IT & GCCs", "automotive & manufacturing", "engineering R&D", "fintech", "education"],
     "Pune pairs engineering depth with a young, fast-learning workforce — ideal conditions for Claude "
     "adoption. From Hinjawadi campuses to auto R&D centres, our workshops turn that talent into an "
     "AI-first operation."),
    ("hyderabad", "Hyderabad", "Telangana, India",
     ["HITEC City", "Gachibowli", "Financial District", "Madhapur", "Banjara Hills"],
     ["IT services & GCCs", "pharma & life sciences", "aerospace", "startups", "real estate"],
     "Hyderabad's HITEC City hosts some of the world's largest capability centres, and its pharma corridor "
     "leads the globe. We train both — engineering floors and lab-adjacent business teams — to put Claude "
     "to work on their real pipelines."),
    ("chennai", "Chennai", "Tamil Nadu, India",
     ["OMR IT Corridor", "Tidel Park", "Guindy", "T. Nagar", "Ambattur"],
     ["automotive & manufacturing", "IT services & SaaS", "healthcare", "banking back-offices", "port & logistics"],
     "Chennai builds things that last — cars, software, SaaS companies — with discipline that rewards good "
     "tooling. Our Claude workshops give OMR tech teams and manufacturing leaders a rigorous, hands-on "
     "path to AI fluency."),
    ("kolkata", "Kolkata", "West Bengal, India",
     ["Salt Lake Sector V", "New Town & Rajarhat", "Park Street & CBD"],
     ["IT services", "BFSI", "manufacturing & steel", "FMCG", "education"],
     "Kolkata's enterprises combine institutional depth with a new wave of tech energy in Sector V and New "
     "Town. We train banks, manufacturers and IT teams to bring Claude into everyday work — practically "
     "and confidently."),
    ("ahmedabad", "Ahmedabad", "Gujarat, India",
     ["SG Highway", "GIFT City (Gandhinagar)", "Prahlad Nagar", "Ashram Road"],
     ["pharma", "chemicals & manufacturing", "textiles", "fintech & GIFT City", "infrastructure"],
     "Gujarat's commercial capital moves with famous speed, and GIFT City is pulling global finance next "
     "door. We train Ahmedabad's pharma, manufacturing and finance teams to convert Claude into throughput."),
    ("gurgaon", "Gurgaon", "Haryana, India",
     ["Cyber City", "Golf Course Road", "Udyog Vihar", "Sohna Road"],
     ["GCCs & consulting", "fintech", "e-commerce", "automotive (Manesar)", "media & ad tech"],
     "Gurgaon is corporate India's fastest lane — Cyber City towers full of GCCs, consultancies and "
     "unicorns. Our Claude workshops match that intensity: high-tempo, hands-on and aimed straight at "
     "billable output."),
    ("noida", "Noida", "Uttar Pradesh, India",
     ["Sector 62", "Noida Expressway (Sector 125–142)", "Film City", "Greater Noida"],
     ["IT & BPO", "media & broadcasting", "electronics manufacturing", "edtech", "startups"],
     "Noida's mix of IT campuses, newsrooms and electronics plants makes it one of NCR's most versatile "
     "talent bases. We train those teams — from broadcasters to BPOs — to make Claude a daily instrument."),
]

CITIES = {
    slug: {"name": name, "country": "india", "state": state, "areas": areas, "industries": inds, "intro": intro}
    for slug, name, state, areas, inds, intro in _CITY_ROWS
}
CITY_ORDER = [r[0] for r in _CITY_ROWS]

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
    "claude-sonnet-5": {
        "name": "Claude Sonnet 5",
        "tag": "The balanced workhorse — frontier intelligence at everyday speed and cost.",
        "family": "Claude family (balanced tier)",
        "best_for": [
            "The default for most day-to-day knowledge work",
            "Strong coding, writing and analysis at scale",
            "Team-wide rollouts where cost and speed both matter",
            "Production workloads on the Claude API",
        ],
        "body": [
            "Claude Sonnet 5 is the model most teams should live in: near-flagship intelligence with the "
            "speed and economics that make all-day, every-day use sensible. Drafting, analysis, coding, "
            "customer work — Sonnet handles the bulk of real business tasks brilliantly.",
            "In training we make Sonnet the home base and teach the escalation path: when a task deserves "
            "Opus-level depth, and when Haiku's speed wins. That judgement is what separates power users "
            "from passengers.",
        ],
        "use_cases": [
            ("Everyday drafting", "Emails, briefs, reports and content — fast and consistently good."),
            ("Coding", "Feature work, refactors and reviews at excellent speed-to-quality."),
            ("Analysis", "Spreadsheets, documents and dashboards explained and interrogated."),
        ],
    },
    "claude-haiku-4-5": {
        "name": "Claude Haiku 4.5",
        "tag": "The fast, economical model — near-frontier quality at real-time speed.",
        "family": "Claude family (speed tier)",
        "best_for": [
            "High-volume and real-time workloads",
            "Classification, extraction and routing",
            "Customer-facing assistants where latency matters",
            "Cost-sensitive API deployments at scale",
        ],
        "body": [
            "Claude Haiku 4.5 delivers a remarkable share of frontier capability at a fraction of the cost "
            "and latency. For high-volume work — support triage, document extraction, real-time assistance — "
            "it is often the smartest choice, not the compromise.",
            "In training we show teams where Haiku genuinely suffices (more often than most expect) and how "
            "pairing it with Sonnet and Opus builds workflows that are both excellent and economical.",
        ],
        "use_cases": [
            ("Support & service", "Fast, on-brand responses and intelligent triage at volume."),
            ("Data extraction", "Pull structure out of documents, forms and messages at scale."),
            ("Real-time apps", "Low-latency assistants and in-product AI features."),
        ],
    },
}
MODEL_ORDER = ["claude-opus-4-8", "claude-sonnet-5", "claude-haiku-4-5"]

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
    "claude-apps": {
        "name": "Claude Apps",
        "tag": "Claude on web, desktop and mobile — the everyday home for AI-powered work.",
        "who": "Every professional, from first-time users to daily power users",
        "body": [
            "The Claude apps at claude.ai (plus desktop and mobile) are where most people meet Claude: chat "
            "with files, images and voice; search-connected answers; and the full model family in one place.",
            "Our training turns casual chatting into a working method — how to brief Claude like a brilliant "
            "colleague, structure multi-step tasks, use files well, and build personal workflows that save "
            "hours every week.",
        ],
        "curriculum": [
            "The prompting method: context, task, format, iteration",
            "Working with documents, spreadsheets and images",
            "Long conversations, memory and when to start fresh",
            "Choosing the right model for the task at hand",
            "Personal workflow design: your top 10 tasks, systematised",
        ],
    },
    "claude-projects": {
        "name": "Claude Projects",
        "tag": "Shared context for a team's recurring work — knowledge, instructions and files in one place.",
        "who": "Teams and functions with recurring, standardisable work",
        "body": [
            "Projects give Claude durable context: brand guidelines, SOPs, product docs, tone of voice — set "
            "once, used by everyone. The result is consistent, on-standard output across an entire team.",
            "We train teams to design Projects properly: what knowledge to load, how to write project "
            "instructions that hold, and how to turn one team's best prompts into everyone's baseline.",
        ],
        "curriculum": [
            "Project architecture: knowledge, instructions, conversations",
            "Writing instructions that keep output on-standard",
            "Building a team prompt library that compounds",
            "Projects for functions: marketing, sales, ops, HR patterns",
            "Governance: what belongs in a Project and what doesn't",
        ],
    },
    "artifacts": {
        "name": "Artifacts",
        "tag": "Claude builds documents, apps and visuals in a live side panel — see work take shape.",
        "who": "Anyone who produces documents, decks, tools or prototypes",
        "body": [
            "Artifacts turn Claude from a chat into a workbench: documents, interactive apps, diagrams and "
            "dashboards built live beside the conversation, edited in place, shared in a click.",
            "We train teams to think in artifacts — briefs that become documents, ideas that become working "
            "prototypes, data that becomes an interactive view — collapsing the gap between asking and having.",
        ],
        "curriculum": [
            "From prompt to polished document in one thread",
            "Interactive artifacts: calculators, mini-apps and visualisations",
            "Iterating in place: targeted edits without starting over",
            "Sharing and reusing artifacts across the team",
            "When to use Artifacts vs Projects vs Claude Code",
        ],
    },
    "claude-for-work": {
        "name": "Claude for Work",
        "tag": "Team and Enterprise plans — admin, security and collaboration for org-wide rollout.",
        "who": "IT, L&D and leadership teams rolling Claude out across an organisation",
        "body": [
            "Claude for Work brings the capability under organisational control: central billing, admin and "
            "user management, enterprise-grade security, and shared Projects that make good practice the "
            "default.",
            "Our training pairs the rollout with capability: we help IT and L&D design the deployment — "
            "seats, guardrails, champions — and then train the workforce so the licences actually get used.",
        ],
        "curriculum": [
            "Plan design: Team vs Enterprise, seats and structure",
            "Security, data handling and admin controls",
            "Governance: acceptable-use guardrails people actually follow",
            "Shared Projects as your org's operating layer",
            "Adoption programme: champions, cohorts and measurement",
        ],
    },
    "developer-platform": {
        "name": "Claude API & MCP",
        "tag": "The developer platform — build Claude into your own products, tools and agents.",
        "who": "Engineering and product teams building with the Claude API",
        "body": [
            "The Claude Developer Platform is how Claude becomes part of your product: the API and SDKs, "
            "tool use, structured outputs, and the Model Context Protocol (MCP) — the open standard that "
            "connects AI to your systems and data.",
            "We train engineering teams from first API call to production agents: prompt design as "
            "engineering, tool-calling patterns, MCP servers for your internal systems, evaluation and cost "
            "control.",
        ],
        "curriculum": [
            "Claude API fundamentals: messages, models, streaming",
            "Tool use and structured outputs that hold in production",
            "MCP: connecting Claude to your tools, data and services",
            "Agent patterns: planning, memory, guardrails, evaluation",
            "Cost, latency and model-mix engineering",
        ],
    },
}
PRODUCT_ORDER = ["claude-apps", "claude-projects", "artifacts", "claude-code", "claude-for-work", "developer-platform"]

# What is live this build (only these are generated + linked)
LIVE_COUNTRIES = COUNTRY_ORDER
LIVE_CITIES = CITY_ORDER
LIVE_MODELS = MODEL_ORDER
LIVE_PRODUCTS = PRODUCT_ORDER

# ---------------------------------------------------------------------------
# URL helpers (pretty URLs via folder/index.html; relative for portability)
# ---------------------------------------------------------------------------
def country_path(slug):  return f"/claude-ai-trainer-in-{slug}/"
def city_path(slug):     return f"/claude-ai-trainer-in-{slug}/"
def model_path(slug):    return f"/claude-models/{slug}/"
def product_path(slug):  return f"/claude-products/{slug}/"
def program_path(slug):  return f"/programs/{slug}/"

def rel(from_url, to_url):
    """Root-relative links work fine on Pages + custom domain; keep them simple."""
    return to_url

def esc(s): return html.escape(s, quote=True)

# ---------------------------------------------------------------------------
# Shared chrome
# ---------------------------------------------------------------------------
def nav_links():
    return [
        ("/", "Home"),
        ("/programs/", "Programs"),
        ("/claude-models/", "Models"),
        ("/claude-products/", "Products"),
        ("/locations/", "Locations"),
    ]

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

    prog_links = [("/programs/", "All programs")] + [(program_path(s), PROGRAMS[s]["name"]) for s in PROGRAM_ORDER]
    model_links = [("/claude-models/", "All Claude models")] + [(model_path(s), MODELS[s]["name"]) for s in LIVE_MODELS]
    prod_links = [("/claude-products/", "All Claude products")] + [(product_path(s), PRODUCTS[s]["name"]) for s in LIVE_PRODUCTS]
    loc_links = [("/locations/", "All locations")]
    loc_links += [(country_path(s), COUNTRIES[s]["name"]) for s in ["india", "uae", "usa", "uk", "singapore"]]
    loc_links += [(city_path(s), CITIES[s]["name"]) for s in ["mumbai", "delhi-ncr", "bengaluru"]]
    company = [("/", "Home"), ("/#what-is-claude", "What is Claude"), ("/#formats", "Formats"), ("/#contact", "Book a workshop")]

    cols = (col("Programs", prog_links) + col("Claude models", model_links) +
            col("Claude products", prod_links) + col("Locations", loc_links) + col("Company", company))
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
        f'<div class="stat"><span class="stat-n" data-num="{num}" data-dec="{dec}" '
        f'data-suffix="{esc(suf)}" data-locale="{loc}">{esc(disp)}</span>'
        f'<span class="stat-l">{esc(label)}</span></div>'
        for disp, label, num, dec, suf, loc in STATS
    )
    return f'<section class="stats" aria-label="Track record"><div class="wrap stat-row">{cells}</div></section>'

def clients_strip():
    chips = "".join(f'<li>{esc(c)}</li>' for c in CLIENTS)
    return f"""
<section class="clients" aria-label="Selected organisations our trainers have worked with">
  <p class="eyebrow">Trusted by teams at</p>
  <div class="marquee">
    <ul class="client-logos">{chips}</ul>
    <ul class="client-logos" aria-hidden="true">{chips}</ul>
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
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&family=Space+Grotesk:wght@500;600;700&display=swap">
<link rel="stylesheet" href="/assets/style.css">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<script src="/assets/app.js" defer></script>
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
    locs = [("/locations/", "All locations")]
    locs += [(country_path(s), f"Claude AI Trainer in {COUNTRIES[s]['name']}")
             for s in ["india", "uae", "usa", "uk", "singapore"]]
    locs += [(city_path(s), f"Claude AI Trainer in {CITIES[s]['name']}") for s in ["mumbai", "bengaluru"]]
    progs = [(program_path(s), PROGRAMS[s]["name"]) for s in PROGRAM_ORDER]
    mods = [(model_path(s), f"{MODELS[s]['name']} training") for s in LIVE_MODELS]
    prods = [(product_path(s), f"{PRODUCTS[s]['name']} training") for s in LIVE_PRODUCTS]
    cols = (links("Programs", progs) + links("Claude models", mods) +
            links("Claude products", prods) + links("Locations", locs))
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

def rich_grid(items):
    """items: (title, tag, [points]) -> cards with a heading, sub-line and bullets."""
    out = []
    for title, tag, points in items:
        lis = "".join(f"<li>{esc(p)}</li>" for p in points)
        out.append(
            f'<article class="rich-card"><h3>{esc(title)}</h3>'
            f'<p class="rich-tag">{esc(tag)}</p><ul class="ticks">{lis}</ul></article>'
        )
    return f'<div class="rich-grid">{"".join(out)}</div>'

def steps_html(steps):
    out = []
    for i, (t, d) in enumerate(steps, 1):
        out.append(
            f'<li class="step"><span class="step-n">{i}</span>'
            f'<div><h3>{esc(t)}</h3><p>{esc(d)}</p></div></li>'
        )
    return f'<ol class="steps">{"".join(out)}</ol>'

def offerings_html():
    cards = []
    for slug in PROGRAM_ORDER:
        p = PROGRAMS[slug]
        lis = "".join(f"<li>{esc(x)}</li>" for x in p["includes"][:3])
        cls = "offer-card flagship" if p["flagship"] else "offer-card"
        cards.append(
            f'<article class="{cls}">'
            f'<span class="offer-badge">{esc(p["badge"])}</span>'
            f'<h3><a href="{esc(program_path(slug))}">{esc(p["name"])}</a></h3><p>{esc(p["tag"])}</p>'
            f'<ul class="ticks">{lis}</ul>'
            f'<a class="offer-link" href="{esc(program_path(slug))}">Explore program →</a>'
            f'</article>'
        )
    return f'<div class="offer-grid">{"".join(cards)}</div>'

def chips_html(names, live_map=None, highlight=()):
    """Render location chips. live_map: name -> url for chips that have real pages."""
    live_map = live_map or {}
    out = []
    for n in names:
        if n in live_map:
            cls = "chip live" if n in highlight else "chip"
            out.append(f'<a class="{cls}" href="{esc(live_map[n])}">{esc(n)}</a>')
        else:
            out.append(f'<a class="chip" href="#contact" title="Enquire about {esc(n)}">{esc(n)}</a>')
    return f'<div class="chip-grid">{"".join(out)}</div>'

# ---------------------------------------------------------------------------
# Educational content — "everything about Claude" (home page)
# ---------------------------------------------------------------------------
CLAUDE_INTRO = [
    "Claude is the AI assistant built by Anthropic — a family of large language models designed to be genuinely "
    "helpful at real work while staying safe, steerable and honest. It reads and writes long documents, reasons "
    "through hard problems, analyses data, writes and ships code, understands images and diagrams, and can use "
    "tools to take action on your behalf.",
    "Teams reach for Claude because it is strong where knowledge work actually lives: a large context window for "
    "whole reports and codebases, careful reasoning you can trust on nuanced tasks, and a calm, professional voice. "
    "But a tool is only as good as the hands using it — which is exactly what our training fixes.",
]

# Model family overview (capability-focused, current lineup)
MODELS_OVERVIEW = [
    ("Claude Opus 4.8", "The flagship — maximum capability.",
     ["Deepest reasoning and analysis", "Best for hard coding and long agentic tasks",
      "The model for high-stakes, quality-first work"]),
    ("Claude Sonnet 5", "The balanced workhorse.",
     ["Fast and highly capable", "The sensible default for most day-to-day work",
      "Strong coding and writing at lower cost than Opus"]),
    ("Claude Haiku 4.5", "The fast, economical model.",
     ["Lowest latency and cost", "Ideal for high-volume, real-time tasks",
      "Great for classification, extraction and support"]),
]

# Product suite overview
PRODUCTS_OVERVIEW = [
    ("Claude apps", "Web, desktop and mobile at claude.ai — chat, files, voice and more.",
     ["The everyday home for Claude", "Upload docs, images and spreadsheets", "Available on every device"]),
    ("Claude Projects", "Give Claude shared context for a team's recurring work.",
     ["Keep knowledge, instructions and files in one place", "Consistent answers across a team",
      "Perfect for playbooks and SOPs"]),
    ("Artifacts", "Claude builds documents, apps and visuals in a live side panel.",
     ["See work take shape as you go", "Edit and iterate in place", "Share the result in a click"]),
    ("Claude Code", "Agentic coding across the terminal, IDE, desktop and web.",
     ["Reads, writes and runs your code", "Plans and ships multi-file features", "For engineering and data teams"]),
    ("Claude for Work", "Team and Enterprise plans with admin, security and collaboration.",
     ["Central billing and controls", "Enterprise-grade security", "Roll Claude out across the org"]),
    ("Developer Platform", "The Claude API plus agents and Model Context Protocol (MCP).",
     ["Build Claude into your own products", "Connect Claude to your tools and data", "Automate real workflows"]),
]

# What Claude can do — capabilities
CAPABILITIES = [
    ("Write & edit", "Drafts, rewrites, briefs, emails and on-brand copy — in your voice."),
    ("Research & summarise", "Digest long PDFs, reports and threads into clear, cited answers."),
    ("Analyse data", "Explore spreadsheets, spot patterns and explain the numbers."),
    ("Code & build", "From a quick script to shipping features with Claude Code."),
    ("See & interpret", "Read screenshots, charts, diagrams and documents."),
    ("Automate with agents", "Chain steps and tools together to finish real tasks."),
]

# Why train — benefits
WHY_TRAIN = [
    ("A faster ramp", "Skip months of trial and error. Your team gets to confident daily use in days, not quarters."),
    ("Real ROI on AI spend", "Licences are only worth it if people use them well. We turn seats into productivity."),
    ("Safe, governed adoption", "Clear guardrails on what to share, what to check, and where AI does and doesn't belong."),
    ("Consistent practice", "Everyone learns the same methods and templates, so quality is even across the team."),
    ("Function-specific playbooks", "Marketing, sales, engineering, ops and HR each leave with prompts for their own work."),
    ("Change that sticks", "Reusable Projects, prompt libraries and follow-up so the habit outlasts the workshop."),
]

# Programs — the productised offerings (each gets its own page)
PROGRAMS = {
    "corporate-training": {
        "name": "Corporate Training", "badge": "Flagship", "flagship": True,
        "duration": "Half-day to 2-day · on-site or online",
        "tag": "Fully customised Claude workshops for your teams — on-site or online, built from your real work, tools and industry.",
        "who": "Teams and departments at enterprises and growing companies",
        "body": [
            "Our flagship engagement: a Claude workshop designed around your organisation — your industry, "
            "your tools, your actual documents and workflows. No generic demos; from the first exercise, "
            "your people work on their own tasks with Claude, coached live.",
            "We scope the cohort by function and seniority, build the examples from your world, and leave "
            "behind the infrastructure of adoption: shared Projects, prompt libraries and guardrails.",
        ],
        "includes": [
            "Pre-workshop scoping call and curriculum tailoring",
            "Hands-on delivery for up to multiple cohorts",
            "Function-specific playbooks and prompt libraries",
            "Shared Claude Projects set up for your teams",
            "Rollout guardrails and post-workshop support",
        ],
        "outcomes": [
            "Teams using Claude on real work from day one",
            "A common prompting method across the organisation",
            "Documented playbooks per function",
            "Clear, safe usage guardrails",
        ],
    },
    "claude-masterclass": {
        "name": "Claude Masterclass", "badge": "2 hours", "flagship": False,
        "duration": "2 hours · in-person or live online",
        "tag": "A high-energy, live masterclass that takes a room from curious to confident — the fastest introduction to Claude done right.",
        "who": "All-hands audiences, offsites, leadership town halls, conferences",
        "body": [
            "Two hours that change how a room thinks about AI. The Claude Masterclass is a live, demo-driven "
            "session that shows exactly what Claude can do on real business tasks — and hands the audience a "
            "prompting method they can use the same afternoon.",
            "It's the ideal opener: energising for an offsite or town hall, and the proven first step before "
            "a deeper corporate programme.",
        ],
        "includes": [
            "Live demos on tasks from your industry",
            "The TAGS-style contextual prompting method, taught simply",
            "Interactive audience exercises",
            "Q&A tuned to your organisation's questions",
            "Take-home quick-reference prompt guide",
        ],
        "outcomes": [
            "A shared, accurate mental model of Claude",
            "Immediate hands-on confidence",
            "Energy and pull for deeper adoption",
            "A clear next-step roadmap",
        ],
    },
    "claude-for-cxos": {
        "name": "Claude for CXOs", "badge": "Executive", "flagship": False,
        "duration": "90 minutes or half-day · boardroom or virtual",
        "tag": "A focused briefing for CEOs, CXOs and boards: where Claude creates leverage, what to govern, and how to lead an AI-first org.",
        "who": "CEOs, CXOs, boards and senior leadership teams",
        "body": [
            "Leaders don't need to become prompt engineers — they need judgement: where AI creates real "
            "leverage in their business, what to govern, what to fund and what to ignore. This briefing "
            "delivers exactly that, drawn from work with 400+ enterprises.",
            "It's candid, hype-free and hands-on enough that every leader leaves having used Claude on a "
            "real leadership task — strategy, review, communication — themselves.",
        ],
        "includes": [
            "Executive-level view of the Claude platform and model family",
            "Where AI is creating P&L impact — peer examples",
            "Governance, risk and data framework for AI at work",
            "Hands-on: each leader works a real task with Claude",
            "An adoption roadmap for the organisation",
        ],
        "outcomes": [
            "Aligned leadership view of AI opportunity and risk",
            "A governance posture you can defend",
            "Personal fluency at the top",
            "A funded, sequenced adoption plan",
        ],
    },
    "open-batches": {
        "name": "Open Batches", "badge": "Individuals", "flagship": False,
        "duration": "Live online cohorts · new batches monthly",
        "tag": "Public cohorts for professionals and small teams — join the next live online batch and learn alongside peers.",
        "who": "Individual professionals, freelancers and small teams",
        "body": [
            "Not every learner comes with an enterprise behind them. Open Batches bring the same hands-on "
            "Claude curriculum to public cohorts — live online sessions where you learn alongside peers from "
            "across industries and geographies.",
            "Expect the same method as our corporate work: real tasks, live coaching, and a personal workflow "
            "you leave actually using.",
        ],
        "includes": [
            "Live online, hands-on sessions (not recordings)",
            "The complete prompting and Projects curriculum",
            "Personal workflow design for your own role",
            "Certificate of completion",
            "Alumni community and resources",
        ],
        "outcomes": [
            "Daily, confident Claude use in your own work",
            "A portfolio of reusable prompts and Projects",
            "A certificate that signals real capability",
            "Peers to keep learning with",
        ],
    },
    "claude-code-bootcamp": {
        "name": "Claude Code Bootcamp", "badge": "Engineering", "flagship": False,
        "duration": "1–2 day intensive · on-site or online",
        "tag": "A deep, practice-heavy immersion for engineering and data teams — from first agentic task to shipping with Claude Code daily.",
        "who": "Software engineers, data teams and technical leaders",
        "body": [
            "This is the deep end: a practice-heavy bootcamp where engineering teams work in their own "
            "repositories with Claude Code — scoping agent tasks, steering multi-file changes, wiring up "
            "MCP tools and keeping quality high under review.",
            "Teams leave with working conventions — how to brief the agent, when to plan vs act, how to keep "
            "changes reviewable — and the confidence to make agentic coding the default, not the demo.",
        ],
        "includes": [
            "Setup, permissions and safe defaults on a real repo",
            "Agentic workflows: scoping, planning, steering, review",
            "Project context, custom commands and MCP integration",
            "Team conventions for PRs, CI and quality gates",
            "Real tickets shipped during the bootcamp",
        ],
        "outcomes": [
            "Engineers shipping with Claude Code daily",
            "Team conventions that keep quality high",
            "Measurable cycle-time improvement",
            "An internal playbook for agentic development",
        ],
    },
    "ai-champions-program": {
        "name": "AI Champions Program", "badge": "Train-the-trainer", "flagship": False,
        "duration": "Multi-week program · cohort-based",
        "tag": "We train your internal champions to keep the adoption compounding — curriculum, coaching and certification included.",
        "who": "L&D teams and organisations building durable in-house AI capability",
        "body": [
            "External training starts the fire; internal champions keep it burning. This program selects and "
            "develops your own people into certified Claude champions — equipped with our curriculum, "
            "coaching techniques and refresh cadence.",
            "It's how adoption survives attrition, reorgs and the next model release: capability that lives "
            "inside your organisation, not in a vendor's calendar.",
        ],
        "includes": [
            "Champion selection framework and cohort design",
            "Deep-dive training beyond the standard curriculum",
            "Teach-back practice with live coaching",
            "Ready-to-run internal workshop materials",
            "Certification and quarterly refreshers",
        ],
        "outcomes": [
            "A certified internal training bench",
            "Self-sustaining adoption rhythm",
            "Lower long-run enablement cost",
            "A durable AI-first culture",
        ],
    },
}
PROGRAM_ORDER = ["corporate-training", "claude-masterclass", "claude-for-cxos",
                 "open-batches", "claude-code-bootcamp", "ai-champions-program"]

# How we train — methodology
METHODOLOGY = [
    ("Scope", "A short call to understand your teams, tools, data and goals."),
    ("Tailor", "We build every example from your real work and industry — no generic demos."),
    ("Train", "Hands-on from minute one: your people do their own tasks with Claude, coached live."),
    ("Embed", "They leave with Projects, prompt templates and guardrails ready to use tomorrow."),
    ("Support", "Follow-up resources and office hours so the adoption keeps compounding."),
]

# ---------------------------------------------------------------------------
# PAGE BUILDERS
# ---------------------------------------------------------------------------
def build_home():
    url = "/"
    title = "Claude AI Training for Teams & Enterprises | Claude AI Trainer"
    desc = ("Corporate Claude AI training delivered on-site and online across India and 40+ "
            "countries. 2,00,000+ professionals trained, 400+ enterprises, 4.8/5 rating. Book a workshop.")

    deep_pairs = [("/programs/", "All training programs"),
                  ("/claude-models/", "All Claude models"),
                  ("/claude-products/", "All Claude products"),
                  ("/locations/", "All locations")]

    intro_html = "".join(f"<p>{esc(p)}</p>" for p in CLAUDE_INTRO)

    faqs = [
        ("What is Claude?",
         "Claude is Anthropic's AI assistant — a family of large language models that can write, research, analyse "
         "data, code, read images and use tools to get real work done, with a strong focus on safety and reliability. "
         "See the <a href='#what-is-claude'>overview</a> above."),
        ("What is Claude AI training?",
         "Hands-on corporate training that gets your team using Claude on real work — prompting, Claude Projects, "
         "Claude Code and AI agents — mapped to your industry and tools. Delivered on-site or online, from a "
         "2-hour masterclass to a 2-day bootcamp."),
        ("Which Claude model should we use?",
         "It depends on the task: <b>Opus</b> for the hardest reasoning and coding, <b>Sonnet</b> as the balanced "
         "default, <b>Haiku</b> for fast, high-volume work. Choosing well is part of what we teach — see "
         "<a href='#models'>Claude models</a>."),
        ("Who is this for?",
         "Leadership, marketing, sales, product, engineering, operations, finance and HR. We tailor every cohort by "
         "<a href='#programs'>role and seniority</a> so the examples are relevant."),
        ("Where do you deliver?",
         "Across India — including <a href='" + city_path('mumbai') + "'>Mumbai</a> and every major metro — "
         "and in 40+ countries worldwide, on-site or live online."),
        ("How much does it cost?",
         "Engagements typically range from ₹50,000 for a focused masterclass to ₹3,00,000+ for a multi-day, "
         "multi-team programme. We scope to your headcount and goals and send a fixed proposal."),
        ("Is our data safe?",
         "Yes — a core part of every workshop is safe, governed use: what to share, what to verify, and where AI "
         "does and doesn't belong. We help you set sensible guardrails for the whole organisation."),
    ]

    # in-page section nav
    section_nav = """
<nav class="page-jump" aria-label="On this page">
  <div class="wrap jump-inner">
    <a href="#what-is-claude">What is Claude</a>
    <a href="#models">Models</a>
    <a href="#products">Products</a>
    <a href="#capabilities">What it does</a>
    <a href="#offerings">Offerings</a>
    <a href="#training">Why us</a>
    <a href="#programs">By team</a>
    <a href="#locations">Locations</a>
    <a href="#faq">FAQ</a>
  </div>
</nav>"""

    live_loc = {COUNTRIES[s]["name"]: country_path(s) for s in LIVE_COUNTRIES}
    live_loc.update({CITIES[s]["name"]: city_path(s) for s in LIVE_CITIES})
    metro_names = [CITIES[s]["name"] for s in CITY_ORDER]
    country_names = [COUNTRIES[s]["name"] for s in COUNTRY_ORDER]

    body = f"""
<section class="hero">
  <div class="hero-bg" aria-hidden="true">
    <span class="orb orb-1"></span><span class="orb orb-2"></span><span class="orb orb-3"></span>
    <span class="hero-grid"></span>
  </div>
  <div class="wrap hero-inner">
    <p class="hero-kicker"><span class="pulse-dot"></span>Corporate Claude AI training · India &amp; 40+ countries</p>
    <h1>Everything your team needs to <span class="grad-text">master Claude AI</span></h1>
    <p class="lead">Claude is the AI assistant from Anthropic that writes, reasons, analyses and codes at a
      professional level. We turn your people into confident Claude power users — hands-on, on real work,
      delivered on-site or online by trainers who have taught <b>2,00,000+ professionals</b> at
      <b>400+ enterprises</b> across <b>16+ countries</b>.</p>
    <div class="hero-actions">
      <a class="btn btn-lg btn-glow" href="#contact">Book a workshop</a>
      <a class="btn btn-lg btn-ghost" href="#what-is-claude">Learn about Claude</a>
    </div>
  </div>
</section>
{stats_bar()}
{clients_strip()}
{section_nav}

<section class="section" id="what-is-claude">
  <div class="wrap narrow prose">
    <p class="eyebrow">The basics</p>
    <h2>What is Claude?</h2>
    {intro_html}
  </div>
</section>

<section class="section alt" id="models">
  <div class="wrap">
    <p class="eyebrow">The model family</p>
    <h2>Meet the Claude models</h2>
    <p class="lead">Anthropic ships a family of Claude models tuned for different jobs. Knowing which to reach
      for — and why — is half the skill. Here's the current line-up.</p>
    {rich_grid(MODELS_OVERVIEW)}
    <p class="note">New models join the Claude family over time; our training always covers the current line-up
      and how to pick the right one for each task.</p>
  </div>
</section>

<section class="section" id="products">
  <div class="wrap">
    <p class="eyebrow">The product suite</p>
    <h2>Claude is more than a chat box</h2>
    <p class="lead">From the everyday apps to Projects, Artifacts, Claude Code and the developer platform —
      each product unlocks a different kind of work.</p>
    {rich_grid(PRODUCTS_OVERVIEW)}
  </div>
</section>

<section class="section alt" id="capabilities">
  <div class="wrap">
    <p class="eyebrow">What Claude can do</p>
    <h2>Six things your team will put to work on day one</h2>
    {feature_grid(CAPABILITIES)}
  </div>
</section>

<section class="section" id="offerings">
  <div class="wrap">
    <p class="eyebrow">Our offerings</p>
    <h2>Pick your program</h2>
    <p class="lead">From a single masterclass to a company-wide capability build — six ways to bring Claude
      into your organisation.</p>
    {offerings_html()}
  </div>
</section>

<section class="section alt" id="training">
  <div class="wrap">
    <p class="eyebrow">Why train with us</p>
    <h2>Owning Claude is a skill — we teach it</h2>
    <p class="lead">Buying licences is easy. Getting real, safe, everyday value out of them is the hard part.
      That's the gap we close.</p>
    {feature_grid(WHY_TRAIN)}
    <div class="spacer"></div>
    <h2 id="how">How our workshops work</h2>
    {steps_html(METHODOLOGY)}
  </div>
</section>

<section class="section" id="programs">
  <div class="wrap">
    <p class="eyebrow">Tailored by team</p>
    <h2>Claude, mapped to every function</h2>
    <p class="lead">One platform, many jobs. Each function leaves with playbooks for its own work.</p>
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
    <h2>Claude AI training, worldwide</h2>
    <p class="lead">On-site in 44 countries and online everywhere. Pick your location for a dedicated
      page on Claude AI training there.</p>
    <h3 class="chip-h">India — major cities</h3>
    {chips_html(metro_names, live_loc)}
    <h3 class="chip-h">Countries we serve</h3>
    {chips_html(country_names, live_loc)}
    <div class="spacer"></div>
    {link_grid("Go deeper", deep_pairs, "Sample deep-dive pages — many more locations, models and products are on the way.")}
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

    siblings = [s for s in COUNTRY_ORDER if COUNTRIES[s]["region"] == d["region"] and s != slug]
    sibling_section = ""
    if siblings:
        sib_map = {COUNTRIES[s]["name"]: country_path(s) for s in siblings}
        sibling_section = f"""
<section class="section">
  <div class="wrap">
    <h2>Also in {esc(d['region'])}</h2>
    {chips_html([COUNTRIES[s]['name'] for s in siblings], sib_map)}
    <p class="note"><a href="/locations/">See all 44 countries and India metros →</a></p>
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
{sibling_section}

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


def build_programs_hub():
    url = "/programs/"
    title = "Claude AI Training Programs | Claude AI Trainer"
    desc = ("Six ways to bring Claude into your organisation — corporate training, masterclass, CXO "
            "briefings, open batches, Claude Code bootcamp and AI champions. Compare programs and book.")
    trail = [("Home", "/"), ("Programs", url)]
    body = f"""
{breadcrumbs_html(trail)}
<section class="page-hero">
  <div class="wrap">
    <p class="eyebrow">Our offerings</p>
    <h1>Claude AI training programs</h1>
    <p class="lead">From a two-hour masterclass to a company-wide capability build — pick the program that
      fits where your organisation is on the AI curve.</p>
  </div>
</section>
<section class="section">
  <div class="wrap">
    {offerings_html()}
  </div>
</section>
{clients_strip()}
{related(exclude_url=url)}
{cta("Not sure which program fits? Ask us")}
"""
    ld = [org_ld(), breadcrumb_ld(trail)]
    write(url, page(url, title, desc, body, ld, active="/programs/"))


def build_program(slug):
    d = PROGRAMS[slug]
    url = program_path(slug)
    name = d["name"]
    title = f"{name} — Claude AI Training | Claude AI Trainer"
    desc = f"{d['tag']} {d['duration']}. Delivered by trainers behind 2,00,000+ professionals. Book now."
    trail = [("Home", "/"), ("Programs", "/programs/"), (name, url)]

    bodyp = "".join(f"<p>{esc(p)}</p>" for p in d["body"])
    includes = "".join(f"<li>{esc(x)}</li>" for x in d["includes"])
    outcomes = "".join(f"<li>{esc(x)}</li>" for x in d["outcomes"])
    faqs = [
        (f"Who is {name} for?", esc(d["who"]) + "."),
        ("How long does it take?", esc(d["duration"]) + "."),
        ("Is it customised to us?",
         "Yes — every engagement starts with a scoping call, and examples are built from your industry and "
         "workflows. See <a href='/#how'>how our workshops work</a>."),
        ("What does it cost?",
         "Engagements are scoped to your headcount and goals; indicative range ₹50,000–₹3,00,000+ per "
         "engagement. We send a fixed proposal after a short call."),
    ]
    body = f"""
{breadcrumbs_html(trail)}
<section class="page-hero">
  <div class="wrap">
    <p class="eyebrow">{esc(d['badge'])} · {esc(d['duration'])}</p>
    <h1>{esc(name)}</h1>
    <p class="lead">{esc(d['tag'])}</p>
    <div class="hero-actions">
      <a class="btn btn-lg btn-glow" href="#contact">Book {esc(name)}</a>
      <a class="btn btn-lg btn-ghost" href="/programs/">Compare all programs</a>
    </div>
  </div>
</section>
{stats_bar()}
<section class="section">
  <div class="wrap narrow prose">
    <h2>About this program</h2>
    {bodyp}
    <h3>What's included</h3>
    <ul class="ticks">{includes}</ul>
    <h3>Outcomes you can expect</h3>
    <ul class="ticks">{outcomes}</ul>
    <p><b>Who it's for:</b> {esc(d['who'])}.</p>
  </div>
</section>
{clients_strip()}
{faq_block(faqs)}
{related(exclude_url=url)}
{cta(f"Bring {name} to your organisation")}
"""
    ld = [org_ld(), breadcrumb_ld(trail),
          service_ld(name, desc, url), course_ld(name, desc, url), faq_ld(faqs)]
    write(url, page(url, title, desc, body, ld, active="/programs/"))


def build_locations_hub():
    url = "/locations/"
    title = "Claude AI Training Locations — 44 Countries & India Metros | Claude AI Trainer"
    desc = ("Find Claude AI training near you: dedicated pages for 44 countries and every major Indian "
            "metro. On-site and online corporate workshops. Pick your location.")
    trail = [("Home", "/"), ("Locations", url)]
    live_loc = {COUNTRIES[s]["name"]: country_path(s) for s in LIVE_COUNTRIES}
    live_loc.update({CITIES[s]["name"]: city_path(s) for s in LIVE_CITIES})
    metro_names = [CITIES[s]["name"] for s in CITY_ORDER]

    # group countries by region for a structured hub
    regions = {}
    for s in COUNTRY_ORDER:
        regions.setdefault(COUNTRIES[s]["region"], []).append(COUNTRIES[s]["name"])
    region_blocks = "".join(
        f'<h3 class="chip-h">{esc(region)}</h3>{chips_html(names, live_loc)}'
        for region, names in regions.items()
    )
    body = f"""
{breadcrumbs_html(trail)}
<section class="page-hero">
  <div class="wrap">
    <p class="eyebrow">Where we deliver</p>
    <h1>Claude AI training locations</h1>
    <p class="lead">On-site workshops in 44 countries and across every major Indian metro — and live online
      everywhere. Every location below has a dedicated page.</p>
  </div>
</section>
<section class="section">
  <div class="wrap">
    <h2>India — major cities</h2>
    {chips_html(metro_names, live_loc)}
    <div class="spacer"></div>
    <h2>Countries</h2>
    {region_blocks}
  </div>
</section>
{stats_bar()}
{related(exclude_url=url)}
{cta("Book Claude AI training in your city")}
"""
    ld = [org_ld(), breadcrumb_ld(trail)]
    write(url, page(url, title, desc, body, ld, active="/locations/"))


# ---------------------------------------------------------------------------
# Output plumbing
# ---------------------------------------------------------------------------
ALL_URLS = []
def apply_base(htmlstr):
    """Prefix root-relative internal links/assets with BASE_PATH (no-op if empty)."""
    if not BASE_PATH:
        return htmlstr
    for attr in ('href', 'src'):
        htmlstr = htmlstr.replace(f'{attr}="/', f'{attr}="{BASE_PATH}/')
        htmlstr = htmlstr.replace(f"{attr}='/", f"{attr}='{BASE_PATH}/")
    return htmlstr

def write(url, htmlstr):
    ALL_URLS.append(url)
    htmlstr = apply_base(htmlstr)
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

def build_js():
    os.makedirs(os.path.join(OUT, "assets"), exist_ok=True)
    with open(os.path.join(OUT, "assets", "app.js"), "w", encoding="utf-8") as f:
        f.write(APP_JS)

# ---------------------------------------------------------------------------
CSS = r""":root{
  --paper:#FAF9F5; --cream:#F0EEE6; --card:#FFFFFF;
  --coral:#D97757; --coral-deep:#BD5D3A; --coral-soft:#F3E4DA;
  --ink:#1A1915; --ink-2:#4A4741; --muted:#6B6862; --line:#E4DFD4;
  --serif:'Space Grotesk',system-ui,-apple-system,"Segoe UI",sans-serif;
  --sans:'Roboto',system-ui,-apple-system,"Segoe UI",Helvetica,Arial,sans-serif;
  --grad:linear-gradient(100deg,#E8926B,#D97757 45%,#C25B36);
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
h1,h2,h3{font-family:var(--serif);line-height:1.12;letter-spacing:-.02em;color:var(--ink);font-weight:600}
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

/* hero — dark, animated */
.hero{position:relative;overflow:hidden;background:#171512;color:#fff;padding:96px 0 72px}
.hero-bg{position:absolute;inset:0;pointer-events:none}
.orb{position:absolute;border-radius:50%;filter:blur(70px);opacity:.5;animation:drift 14s ease-in-out infinite alternate}
.orb-1{width:480px;height:480px;background:#D97757;top:-160px;right:-80px}
.orb-2{width:360px;height:360px;background:#8A4B2F;bottom:-140px;left:-100px;animation-duration:18s;animation-delay:-6s}
.orb-3{width:220px;height:220px;background:#E8926B;top:40%;left:55%;opacity:.28;animation-duration:11s;animation-delay:-3s}
@keyframes drift{from{transform:translate(0,0) scale(1)}to{transform:translate(-40px,30px) scale(1.12)}}
.hero-grid{position:absolute;inset:0;
  background-image:linear-gradient(rgba(255,255,255,.045) 1px,transparent 1px),
                   linear-gradient(90deg,rgba(255,255,255,.045) 1px,transparent 1px);
  background-size:56px 56px;
  -webkit-mask-image:radial-gradient(ellipse 90% 80% at 50% 0%,#000 30%,transparent 75%);
  mask-image:radial-gradient(ellipse 90% 80% at 50% 0%,#000 30%,transparent 75%)}
.hero-inner{position:relative;max-width:860px}
.hero h1{margin:.25em 0 .4em;color:#fff;font-size:clamp(2.4rem,5.6vw,4rem)}
.hero .lead{color:#CFC8BE}
.hero .lead b{color:#fff}
.hero-kicker{display:inline-flex;align-items:center;gap:9px;font-size:.8rem;font-weight:500;letter-spacing:.08em;text-transform:uppercase;color:#E8B29A;border:1px solid rgba(232,146,107,.35);background:rgba(217,119,87,.12);padding:8px 16px;border-radius:999px}
.pulse-dot{width:8px;height:8px;border-radius:50%;background:#E8926B;animation:pulse 2s ease-out infinite}
@keyframes pulse{0%{box-shadow:0 0 0 0 rgba(232,146,107,.6)}70%{box-shadow:0 0 0 10px rgba(232,146,107,0)}100%{box-shadow:0 0 0 0 rgba(232,146,107,0)}}
.grad-text{background:var(--grad);-webkit-background-clip:text;background-clip:text;color:transparent;background-size:200% 100%;animation:gradShift 6s ease infinite}
@keyframes gradShift{0%,100%{background-position:0% 50%}50%{background-position:100% 50%}}
.hero-actions,.cta-actions{display:flex;gap:12px;flex-wrap:wrap;margin-top:30px}
.hero .btn-ghost{color:#F2EFE8;border-color:rgba(255,255,255,.25)}
.hero .btn-ghost:hover{background:rgba(255,255,255,.08);color:#fff}
.btn-glow{background:var(--grad);border:none;box-shadow:0 8px 30px rgba(217,119,87,.45)}
.btn-glow:hover{transform:translateY(-2px);box-shadow:0 12px 40px rgba(217,119,87,.6)}
.page-hero{background:linear-gradient(180deg,var(--cream),var(--paper));padding:46px 0 40px}
.page-hero .lead{margin-top:.6em}

/* scroll reveal */
.reveal{opacity:0;transform:translateY(26px);transition:opacity .7s ease,transform .7s cubic-bezier(.16,1,.3,1);transition-delay:var(--d,0s)}
.reveal.in{opacity:1;transform:none}

/* offerings */
.offer-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin-top:28px}
.offer-card{position:relative;display:flex;flex-direction:column;background:var(--card);border:1px solid var(--line);border-radius:16px;padding:26px 24px;transition:transform .3s ease,box-shadow .3s ease,border-color .3s ease}
.offer-card:hover{transform:translateY(-5px);border-color:var(--coral);box-shadow:0 16px 40px rgba(23,21,18,.10)}
.offer-badge{align-self:flex-start;font-size:.7rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--coral-deep);background:var(--coral-soft);padding:5px 11px;border-radius:999px;margin-bottom:14px}
.offer-card h3{font-size:1.25rem}
.offer-card p{font-size:.95rem;margin:.5em 0 .8em}
.offer-card .ticks{margin-bottom:14px}
.offer-card .ticks li{font-size:.9rem}
.offer-link{margin-top:auto;font-weight:700;font-size:.95rem}
.offer-card.flagship{background:#171512;border-color:#3A342C}
.offer-card.flagship h3,.offer-card.flagship .ticks li{color:#F2EFE8}
.offer-card.flagship p{color:#BFB8AD}
.offer-card.flagship .offer-badge{background:rgba(217,119,87,.18);color:#E8926B}
.offer-card.flagship .offer-link{color:#E8926B}
.offer-card.flagship:hover{box-shadow:0 16px 44px rgba(217,119,87,.28)}

/* location chips */
.chip-h{margin:26px 0 4px;font-size:1.05rem;color:var(--ink-2)}
.chip-grid{display:flex;flex-wrap:wrap;gap:9px;margin-top:12px}
.chip{display:inline-block;padding:9px 17px;border:1px solid var(--line);border-radius:999px;background:var(--card);color:var(--ink-2);font-size:.9rem;font-weight:500;transition:all .25s ease}
.chip:hover{border-color:var(--coral);color:var(--coral-deep);text-decoration:none;transform:translateY(-2px);box-shadow:0 6px 16px rgba(217,119,87,.18)}
.chip.live{border-color:var(--coral);color:var(--coral-deep);background:var(--coral-soft);font-weight:700}

/* marquee */
.clients{padding:26px 0 30px;border-bottom:1px solid var(--line);overflow:hidden}
.clients .eyebrow{text-align:center;margin-bottom:14px}
.marquee{display:flex;gap:48px;width:max-content;animation:scrollX 30s linear infinite}
.marquee:hover{animation-play-state:paused}
.marquee .client-logos{list-style:none;display:flex;gap:48px;align-items:center;flex:none}
.marquee .client-logos li{font-family:var(--serif);font-weight:600;font-size:1.05rem;color:var(--muted);white-space:nowrap}
@keyframes scrollX{from{transform:translateX(0)}to{transform:translateX(calc(-50% - 24px))}}

@media (prefers-reduced-motion:reduce){
  .orb,.grad-text,.pulse-dot,.marquee{animation:none}
  .reveal{opacity:1;transform:none;transition:none}
  *{scroll-behavior:auto}
}

/* stats */
.stats{background:var(--ink);color:#fff;padding:26px 0}
@media (prefers-color-scheme:dark){.stats{background:#141310}}
.stat-row{display:grid;grid-template-columns:repeat(6,1fr);gap:16px;text-align:center}
.stat-n{display:block;font-family:var(--serif);font-size:1.7rem;color:#fff}
.stat-l{display:block;font-size:.78rem;color:#C9BEB2;margin-top:2px}

/* sections */
.section{padding:60px 0}
.section.alt{background:var(--cream)}
.spacer{height:36px}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin-top:26px}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:22px;transition:transform .3s ease,box-shadow .3s ease,border-color .3s ease}
.card:hover{transform:translateY(-4px);border-color:var(--coral);box-shadow:0 12px 32px rgba(23,21,18,.08)}
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
.note{margin-top:20px;font-size:.9rem;color:var(--muted);font-style:italic}

/* in-page jump nav */
.page-jump{position:sticky;top:64px;z-index:40;background:color-mix(in srgb,var(--paper) 92%,transparent);backdrop-filter:blur(8px);border-bottom:1px solid var(--line)}
.jump-inner{display:flex;gap:6px;overflow-x:auto;padding:10px 22px}
.page-jump a{white-space:nowrap;font-size:.85rem;font-weight:600;color:var(--ink-2);padding:6px 12px;border-radius:999px}
.page-jump a:hover{background:var(--coral-soft);color:var(--coral-deep);text-decoration:none}

/* rich cards (models / products) */
.rich-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin-top:26px}
.rich-card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:22px}
.rich-card h3{color:var(--ink)}
.rich-tag{font-size:.95rem;color:var(--coral-deep);font-weight:600;margin:.15em 0 .7em}
.rich-card .ticks li{font-size:.92rem}

/* methodology steps */
.steps{list-style:none;counter-reset:none;margin-top:24px;display:grid;gap:14px}
.step{display:flex;gap:16px;align-items:flex-start;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px 20px}
.step-n{flex:none;width:34px;height:34px;border-radius:50%;background:var(--coral);color:#fff;display:grid;place-items:center;font-family:var(--serif);font-size:1.05rem}
.step h3{margin:.1em 0 .1em}
.step p{font-size:.95rem}

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
.rel-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:24px}
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
.foot-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:24px;margin-bottom:30px}
.foot-col h3{color:#fff;font-family:var(--sans);font-size:.8rem;text-transform:uppercase;letter-spacing:.1em;margin-bottom:12px}
.foot-col ul{list-style:none}
.foot-col li{margin:.4em 0}
.foot-col a{color:#C9BEB2;font-size:.92rem}
.foot-col a:hover{color:#fff}
.foot-base{border-top:1px solid rgba(255,255,255,.12);padding-top:20px}
.foot-base p{color:#C9BEB2;font-size:.9rem;margin:.3em 0}
.foot-base .muted{color:#8A8478;font-size:.8rem}

@media(max-width:860px){
  .grid,.link-grid,.rel-grid,.foot-grid,.rich-grid,.offer-grid{grid-template-columns:repeat(2,1fr)}
  .stat-row{grid-template-columns:repeat(3,1fr);gap:18px 8px}
  .site-nav{display:none}
  .page-jump{top:64px}
}
@media(max-width:520px){
  .grid,.link-grid,.rel-grid,.foot-grid,.rich-grid,.offer-grid{grid-template-columns:1fr}
  .stat-row{grid-template-columns:repeat(2,1fr)}
}
"""

APP_JS = r"""(function () {
  'use strict';
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduced || !('IntersectionObserver' in window)) return;

  /* ---- scroll reveal with per-group stagger ---- */
  var targets = document.querySelectorAll(
    '.section .card, .section .rich-card, .section .offer-card, .section .link-card, ' +
    '.section .step, .section .chip, .faq-item, .section h2, .section .lead, .section .eyebrow, .prose p'
  );
  var groups = new Map();
  targets.forEach(function (el) {
    el.classList.add('reveal');
    var parent = el.parentElement;
    var idx = groups.get(parent) || 0;
    groups.set(parent, idx + 1);
    el.style.setProperty('--d', Math.min(idx * 0.06, 0.5) + 's');
  });
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
  targets.forEach(function (el) { io.observe(el); });

  /* ---- count-up stats ---- */
  function animateStat(el) {
    var num = parseFloat(el.dataset.num || '0');
    var dec = parseInt(el.dataset.dec || '0', 10);
    var suffix = el.dataset.suffix || '';
    var locale = el.dataset.locale || 'en-US';
    var dur = 1600, start = null;
    function frame(ts) {
      if (!start) start = ts;
      var p = Math.min((ts - start) / dur, 1);
      var eased = 1 - Math.pow(1 - p, 3);
      var val = num * eased;
      el.textContent = val.toLocaleString(locale, {
        minimumFractionDigits: dec, maximumFractionDigits: dec
      }) + (p === 1 ? suffix : '');
      if (p < 1) requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  }
  var statIO = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (e.isIntersecting) { animateStat(e.target); statIO.unobserve(e.target); }
    });
  }, { threshold: 0.6 });
  document.querySelectorAll('.stat-n[data-num]').forEach(function (el) { statIO.observe(el); });
})();
"""

# ---------------------------------------------------------------------------
def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT, exist_ok=True)
    build_home()
    build_locations_hub()
    for s in LIVE_COUNTRIES: build_country(s)
    for s in LIVE_CITIES:    build_city(s)
    build_models_hub()
    for s in LIVE_MODELS:    build_model(s)
    build_products_hub()
    for s in LIVE_PRODUCTS:  build_product(s)
    build_programs_hub()
    for s in PROGRAM_ORDER:  build_program(s)
    build_css(); build_js(); build_favicon()
    build_sitemap(); build_robots(); build_cname()
    print(f"Built {len(ALL_URLS)} pages -> {OUT}")
    for u in ALL_URLS: print("  ", u)

if __name__ == "__main__":
    main()
