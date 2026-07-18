#!/usr/bin/env python3
"""
Generate a native Elementor page-template JSON for the claudeaitrainer.com
home page. Every element is a real Elementor widget (heading / text-editor /
counter / icon-list / button / accordion / shortcode) so the whole page is
editable inside Elementor. Global content (model names, form, contact) is
placed via shortcodes from the claude-ai-trainer-globals plugin, so it can
be changed in one place.

Run:  python3 build_elementor.py   ->  claude-ai-trainer-home.json
Import in WP:  Templates -> Saved Templates -> Import Templates
"""

import json, os, sys, itertools

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from build import (CLAUDE_INTRO, PRODUCTS_OVERVIEW, CAPABILITIES, WHY_TRAIN,
                   METHODOLOGY, ROLES, FORMATS, PROGRAMS, PROGRAM_ORDER,
                   COUNTRIES, COUNTRY_ORDER, CITIES, CITY_ORDER, CLIENTS)

# ---------------------------------------------------------------- primitives
_ids = itertools.count(1)
def nid(): return "cat" + format(next(_ids), "04x")

INK = "#1A1915"; INK2 = "#4A4741"; CORAL = "#D97757"; CORAL_D = "#BD5D3A"
CREAM = "#F0EEE6"; PAPER = "#FAF9F5"; DARK = "#171512"; LINE = "#E4DFD4"
FONT_H = "Space Grotesk"; FONT_B = "Roboto"

def widget(wtype, settings, anim=True, delay=0):
    s = dict(settings)
    if anim:
        s.setdefault("_animation", "fadeInUp")
        if delay: s["_animation_delay"] = delay
    return {"id": nid(), "elType": "widget", "widgetType": wtype,
            "settings": s, "elements": []}

def column(size, elements, settings=None):
    s = {"_column_size": size, "_inline_size": None}
    if settings: s.update(settings)
    return {"id": nid(), "elType": "column", "settings": s,
            "elements": elements, "isInner": False}

def section(columns, settings=None, inner=False):
    s = {"layout": "boxed", "gap": "extended"}
    if settings: s.update(settings)
    for c in columns: c["isInner"] = inner
    return {"id": nid(), "elType": "section", "settings": s,
            "elements": columns, "isInner": inner}

def pad(top, bottom, left=0, right=0):
    return {"unit": "px", "top": str(top), "right": str(right),
            "bottom": str(bottom), "left": str(left), "isLinked": False}

def heading(text, size="h2", color=INK, px=38, weight="600", align="left",
            family=FONT_H, delay=0):
    return widget("heading", {
        "title": text, "header_size": size, "align": align,
        "title_color": color,
        "typography_typography": "custom",
        "typography_font_family": family,
        "typography_font_weight": weight,
        "typography_font_size": {"unit": "px", "size": px, "sizes": []},
    }, delay=delay)

def eyebrow(text, color=CORAL_D, delay=0):
    return widget("heading", {
        "title": text.upper(), "header_size": "h6", "align": "left",
        "title_color": color,
        "typography_typography": "custom",
        "typography_font_family": FONT_B, "typography_font_weight": "700",
        "typography_font_size": {"unit": "px", "size": 12, "sizes": []},
        "typography_letter_spacing": {"unit": "px", "size": 2, "sizes": []},
    }, delay=delay)

def text(html, color=INK2, px=16, delay=0):
    return widget("text-editor", {
        "editor": html, "text_color": color,
        "typography_typography": "custom",
        "typography_font_family": FONT_B,
        "typography_font_size": {"unit": "px", "size": px, "sizes": []},
    }, delay=delay)

def button(label, url, filled=True, delay=0):
    s = {
        "text": label, "link": {"url": url, "is_external": "", "nofollow": ""},
        "align": "left", "size": "lg",
        "border_radius": {"unit": "px", "size": 999, "sizes": []},
        "typography_typography": "custom",
        "typography_font_family": FONT_B, "typography_font_weight": "700",
    }
    if filled:
        s.update({"background_color": CORAL, "button_text_color": "#FFFFFF",
                  "hover_color": "#FFFFFF", "button_background_hover_color": CORAL_D})
    else:
        s.update({"background_color": "rgba(0,0,0,0)", "button_text_color": CORAL_D,
                  "border_border": "solid", "border_width": {"unit": "px", "top": "1", "right": "1", "bottom": "1", "left": "1", "isLinked": True},
                  "border_color": LINE, "button_background_hover_color": "#F3E4DA",
                  "hover_color": CORAL_D})
    return widget("button", s, delay=delay)

def icon_list(items, color=INK2, delay=0):
    return widget("icon-list", {
        "icon_list": [{"_id": nid(), "text": t,
                       "selected_icon": {"value": "fas fa-check", "library": "fa-solid"}}
                      for t in items],
        "text_color": color, "icon_color": CORAL,
        "typography_typography": "custom",
        "typography_font_family": FONT_B,
        "typography_font_size": {"unit": "px", "size": 15, "sizes": []},
        "space_between": {"unit": "px", "size": 8, "sizes": []},
    }, delay=delay)

def counter(end, suffix, title, delay=0):
    return widget("counter", {
        "starting_number": 0, "ending_number": end, "suffix": suffix,
        "duration": 2000, "thousand_separator": "yes",
        "title": title, "number_color": "#FFFFFF", "title_color": "#C9BEB2",
        "typography_number_typography": "custom",
        "typography_number_font_family": FONT_H,
        "typography_number_font_size": {"unit": "px", "size": 34, "sizes": []},
        "typography_title_typography": "custom",
        "typography_title_font_family": FONT_B,
        "typography_title_font_size": {"unit": "px", "size": 13, "sizes": []},
    }, delay=delay)

def shortcode(code, delay=0):
    return widget("shortcode", {"shortcode": code}, delay=delay)

def anchor(slug):
    return widget("menu-anchor", {"anchor": slug}, anim=False)

def card_col(size, elements, dark=False, delay=0):
    s = {
        "background_background": "classic",
        "background_color": DARK if dark else "#FFFFFF",
        "border_border": "solid",
        "border_width": {"unit": "px", "top": "1", "right": "1", "bottom": "1", "left": "1", "isLinked": True},
        "border_color": "#3A342C" if dark else LINE,
        "border_radius": {"unit": "px", "size": 14, "sizes": []},
        "padding": {"unit": "px", "top": "24", "right": "22", "bottom": "24", "left": "22", "isLinked": False},
        "margin": {"unit": "px", "top": "0", "right": "8", "bottom": "16", "left": "8", "isLinked": False},
        "animation": "fadeInUp", "animation_delay": delay,
    }
    return column(size, elements, s)

def rows_of(cards, per_row, settings=None):
    """Chunk card-columns into full-width inner rows."""
    out = []
    for i in range(0, len(cards), per_row):
        out.append(section(cards[i:i+per_row], settings, inner=True))
    return out

def section_shell(inner_elements, bg=PAPER, top=70, bottom=70):
    """A full-width section whose single column stacks headers + card rows."""
    return section(
        [column(100, inner_elements)],
        {"background_background": "classic", "background_color": bg,
         "padding": pad(top, bottom)})

# ---------------------------------------------------------------- sections
content = []

# 1 ▸ HERO (dark)
content.append(section(
    [column(100, [
        eyebrow("Corporate Claude AI training · India & 40+ countries", color="#E8B29A"),
        heading('Everything your team needs to <span style="color:#D97757">master Claude AI</span>',
                size="h1", color="#FFFFFF", px=52),
        text("<p>Claude is the AI assistant from Anthropic that writes, reasons, analyses and codes at a "
             "professional level. We turn your people into confident Claude power users — hands-on, on real "
             "work, delivered by a global bench of <b>[cat_trainers] trainers</b> who have taught "
             "<b>2,00,000+ professionals</b> at <b>400+ enterprises</b> — on-site in 44 countries or live "
             "online.</p>", color="#CFC8BE", px=18, delay=150),
        section([column(50, [button("Book a workshop", "#enquire", delay=300)]),
                 column(50, [button("Explore programs", "#offerings", filled=False, delay=350)])],
                inner=True),
    ])],
    {"background_background": "gradient",
     "background_color": DARK, "background_color_b": "#2B1F18",
     "background_gradient_angle": {"unit": "deg", "size": 160},
     "padding": pad(110, 90)}))

# 2 ▸ STATS (dark, native counters)
stat_cols = [
    counter(200000, "+", "Professionals trained"),
    counter(300, "+", "Trainers worldwide", delay=100),
    counter(400, "+", "Enterprises & brands", delay=200),
    counter(44, "", "Countries served", delay=300),
    counter(17, "+", "Years of training craft", delay=400),
]
rating = [heading("4.8/5", size="h3", color="#FFFFFF", px=34, delay=500),
          text("<p>Average participant rating</p>", color="#C9BEB2", px=13, delay=500)]
content.append(section(
    [column(16, [c]) for c in stat_cols] + [column(16, rating)],
    {"background_background": "classic", "background_color": "#1A1915",
     "padding": pad(40, 36)}))

# 3 ▸ CLIENTS
content.append(section_shell([
    eyebrow("Trusted by teams at"),
    text("<p style='font-size:17px;letter-spacing:.3px'>" +
         " &nbsp;·&nbsp; ".join(CLIENTS) + "</p>", color="#6B6862", delay=100),
], bg=PAPER, top=34, bottom=30))

# 4 ▸ WHAT IS CLAUDE
content.append(section_shell([
    anchor("what-is-claude"),
    eyebrow("The basics"),
    heading("What is Claude?"),
    text("".join(f"<p>{p}</p>" for p in CLAUDE_INTRO), delay=150),
]))

# 5 ▸ MODELS — names via global shortcodes
model_cards = []
model_specs = [
    ("flagship", "The new frontier — first of the Claude 5 family.",
     ["Most intelligent generally available model", "A tier above Opus in capability", "Frontier reasoning, agents & coding"]),
    ("advanced", "The proven flagship of the Claude 4 line.",
     ["Deep reasoning and analysis", "Hard coding & long agentic tasks", "High-stakes, quality-first work"]),
    ("balanced", "The balanced workhorse.",
     ["Fast and highly capable", "The default for day-to-day work", "Great coding & writing economics"]),
    ("fast", "The fast, economical model.",
     ["Lowest latency and cost", "High-volume, real-time tasks", "Classification, extraction, support"]),
]
for i, (key, tag, points) in enumerate(model_specs):
    model_cards.append(card_col(25, [
        text(f'<h3 style="margin:0;font-size:21px">[cat_model key="{key}"]</h3>', color=INK),
        text(f"<p><b style='color:{CORAL_D}'>{tag}</b></p>", px=15),
        icon_list(points),
    ], delay=i * 100))
content.append(section_shell([
    anchor("models"),
    eyebrow("The model family"),
    heading("Meet the Claude models"),
    text("<p>Anthropic ships a family of Claude models tuned for different jobs — today that's [cat_models]. "
         "Knowing which to reach for is half the skill.</p>", delay=100),
    *rows_of(model_cards, 4),
    text("<p><i>Model names update automatically from Settings → Claude AI Trainer.</i></p>", px=13, delay=200),
], bg=CREAM))

# 6 ▸ PRODUCTS
prod_cards = []
for i, (name, tag, points) in enumerate(PRODUCTS_OVERVIEW):
    prod_cards.append(card_col(33, [
        heading(name, size="h3", px=21),
        text(f"<p><b style='color:{CORAL_D}'>{tag}</b></p>", px=15),
        icon_list(points),
    ], delay=(i % 3) * 100))
content.append(section_shell([
    anchor("products"),
    eyebrow("The product suite"),
    heading("Claude is more than a chat box"),
    text("<p>From the everyday apps to Projects, Artifacts, Claude Code and the developer platform — "
         "each product unlocks a different kind of work.</p>", delay=100),
    *rows_of(prod_cards, 3),
]))

# 7 ▸ CAPABILITIES
cap_cards = [card_col(33, [heading(t, size="h3", px=19), text(f"<p>{d}</p>", px=15)],
                      delay=(i % 3) * 100)
             for i, (t, d) in enumerate(CAPABILITIES)]
content.append(section_shell([
    anchor("capabilities"),
    eyebrow("What Claude can do"),
    heading("Six things your team will put to work on day one"),
    *rows_of(cap_cards, 3),
], bg=CREAM))

# 8 ▸ OFFERINGS
offer_cards = []
for i, slug in enumerate(PROGRAM_ORDER):
    p = PROGRAMS[slug]
    dark = p["flagship"]
    fg = "#F2EFE8" if dark else INK
    offer_cards.append(card_col(33, [
        eyebrow(p["badge"], color="#E8926B" if dark else CORAL_D),
        heading(p["name"], size="h3", px=22, color=fg),
        text(f"<p>{p['tag']}</p>", color="#BFB8AD" if dark else INK2, px=15),
        icon_list(p["includes"][:3], color="#BFB8AD" if dark else INK2),
        button("Enquire →", "#enquire", filled=not dark),
    ], dark=dark, delay=(i % 3) * 100))
content.append(section_shell([
    anchor("offerings"),
    eyebrow("Our offerings"),
    heading("Pick your program"),
    text("<p>From a single masterclass to a company-wide capability build — six ways to bring Claude into "
         "your organisation.</p>", delay=100),
    *rows_of(offer_cards, 3),
]))

# 9 ▸ WHY US + METHOD
why_cards = [card_col(33, [heading(t, size="h3", px=19), text(f"<p>{d}</p>", px=15)],
                      delay=(i % 3) * 100)
             for i, (t, d) in enumerate(WHY_TRAIN)]
content.append(section_shell([
    anchor("why-us"),
    eyebrow("Why train with us"),
    heading("Owning Claude is a skill — we teach it"),
    text("<p>Buying licences is easy. Getting real, safe, everyday value out of them is the hard part. "
         "That's the gap we close — with [cat_trainers] certified trainers across the globe.</p>", delay=100),
    *rows_of(why_cards, 3),
    heading("How our workshops work", px=30, delay=150),
    icon_list([f"{t} — {d}" for t, d in METHODOLOGY], delay=200),
], bg=CREAM))

# 10 ▸ TEAMS
team_cards = [card_col(33, [heading(t, size="h3", px=19), text(f"<p>{d}</p>", px=15)],
                       delay=(i % 3) * 100)
              for i, (t, d) in enumerate(ROLES)]
content.append(section_shell([
    anchor("teams"), eyebrow("Tailored by team"),
    heading("Claude, mapped to every function"),
    *rows_of(team_cards, 3),
]))

# 11 ▸ FORMATS
fmt_cards = [card_col(25, [heading(t, size="h3", px=18), text(f"<p>{d}</p>", px=14)],
                      delay=i * 100)
             for i, (t, d) in enumerate(FORMATS)]
content.append(section_shell([
    anchor("formats"), eyebrow("How it runs"),
    heading("Formats that fit your calendar"),
    *rows_of(fmt_cards, 4),
], bg=CREAM))

# 12 ▸ LOCATIONS (chips as editable rich text)
chip_css = ("display:inline-block;margin:4px 6px 4px 0;padding:8px 16px;border:1px solid #E4DFD4;"
            "border-radius:999px;background:#fff;color:#4A4741;text-decoration:none;font-size:14px")
def chips(names):
    return "".join(f'<a href="#enquire" style="{chip_css}">{n}</a>' for n in names)
metro_names = [CITIES[s]["name"] for s in CITY_ORDER]
country_names = [COUNTRIES[s]["name"] for s in COUNTRY_ORDER]
content.append(section_shell([
    anchor("locations"), eyebrow("Where we deliver"),
    heading("Claude AI training, worldwide"),
    text("<p>On-site in 44 countries and online everywhere — delivered by 300+ trainers worldwide. "
         "Tap your location to enquire.</p>", delay=100),
    heading("India — major cities", size="h4", px=19, delay=150),
    text(f"<p>{chips(metro_names)}</p>", delay=200),
    heading("Countries we serve", size="h4", px=19, delay=250),
    text(f"<p>{chips(country_names)}</p>", delay=300),
]))

# 13 ▸ FAQ (native accordion)
faqs = [
    ("What is Claude?", "Claude is Anthropic's AI assistant — a family of large language models "
     "([cat_models]) that write, research, analyse data, code and use tools to get real work done."),
    ("What is Claude AI training?", "Hands-on corporate training that gets your team using Claude on real "
     "work — prompting, Projects, Claude Code and agents — mapped to your industry and tools."),
    ("Which Claude model should we use?", "It depends on the task — [cat_model key=\"flagship\"] for the "
     "frontier, [cat_model key=\"balanced\"] as the daily default, [cat_model key=\"fast\"] for speed. "
     "Choosing well is part of what we teach."),
    ("Who delivers the training?", "A global bench of [cat_trainers] certified trainers who have taught "
     "2,00,000+ professionals at 400+ enterprises, with a 4.8/5 average rating."),
    ("Where do you deliver?", "Across India and 44 countries — on-site or live online."),
    ("How much does it cost?", "Engagements typically range from ₹50,000 for a focused masterclass to "
     "₹3,00,000+ for a multi-day programme. We send a fixed proposal after a short scoping call."),
]
content.append(section_shell([
    anchor("faq"),
    heading("Frequently asked questions"),
    widget("accordion", {
        "tabs": [{"_id": nid(), "tab_title": q, "tab_content": f"<p>{a}</p>"} for q, a in faqs],
        "title_color": INK, "icon_color": CORAL_D,
    }, delay=100),
], bg=CREAM))

# 14 ▸ CTA + GLOBAL FORM
content.append(section(
    [column(55, [
        heading("Bring Claude into your team's real work", color="#FFFFFF", px=34),
        text("<p>Tell us your team, your tools and your goal. We'll design a Claude AI workshop around the "
             "work you actually do — on-site or online.</p><p><b>Email:</b> [cat_email] &nbsp; "
             "<b>Phone:</b> [cat_phone]</p>", color="#FBEDE6", delay=100),
     ]),
     column(45, [shortcode("[cat_form]", delay=150)],
            {"background_background": "classic", "background_color": "#FFFFFF",
             "border_radius": {"unit": "px", "size": 16, "sizes": []},
             "padding": {"unit": "px", "top": "28", "right": "26", "bottom": "28", "left": "26", "isLinked": False}})],
    {"background_background": "classic", "background_color": CORAL,
     "padding": pad(80, 80)}))

# ---------------------------------------------------------------- emit
tpl = {
    "version": "0.4",
    "title": "Claude AI Trainer — Home",
    "type": "page",
    "page_settings": {"hide_title": "yes"},
    "content": content,
}
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "claude-ai-trainer-home.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(tpl, f, ensure_ascii=False)
print(f"Wrote {out} ({os.path.getsize(out)//1024} KB)")

def _count(els):
    n = 0
    for e in els:
        n += 1 + _count(e.get("elements", []))
    return n
print("Elementor elements:", _count(content))
