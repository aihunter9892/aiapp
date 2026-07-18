# Claude AI Trainer — WordPress / Elementor package

Two files put the complete home page into your WordPress at claudeaitrainer.com,
fully editable in Elementor:

| File | What it is |
|---|---|
| `claude-ai-trainer-globals.zip` | WordPress plugin — global model names, trainer count, contact details and the enquiry form (shortcodes + settings page) |
| `claude-ai-trainer-home.json` | Elementor page template — the entire home page as 251 native Elementor elements (14 sections) |

## Install (5 minutes)

1. **Plugin first:** WP Admin → Plugins → Add New → **Upload Plugin** →
   `claude-ai-trainer-globals.zip` → Install → **Activate**.
2. **Set your globals:** Settings → **Claude AI Trainer** → check the model
   names, set your real **email/phone**, and where form submissions should go
   → Save.
3. **Import the template:** Templates → Saved Templates → **Import Templates**
   → `claude-ai-trainer-home.json`.
4. **Create the page:** Pages → Add New → title "Home" → **Edit with
   Elementor** → click the grey **folder icon** in the editor canvas →
   **My Templates** tab → Insert "Claude AI Trainer — Home".
5. **Make it the front page:** Settings → Reading → "Your homepage displays"
   → A static page → select Home.
6. In Elementor: Site Settings → Layout → set **Page Title = hidden** for this
   page if your theme still shows a title, and set content width ~1140px.

## How the "global" pieces work

Everything global lives in **Settings → Claude AI Trainer** — change once,
updates everywhere the shortcode appears:

| Shortcode | Renders |
|---|---|
| `[cat_model key="flagship"]` | Claude Fable 5 |
| `[cat_model key="advanced"]` | Claude Opus 4.8 |
| `[cat_model key="balanced"]` | Claude Sonnet 5 |
| `[cat_model key="fast"]` | Claude Haiku 4.5 |
| `[cat_models]` | the full list in a sentence |
| `[cat_trainers]` | 300+ |
| `[cat_email]` / `[cat_phone]` | linked contact details |
| `[cat_form]` | the enquiry form (name, email, company, phone, location, program, message → emailed to you) |

When Anthropic ships a new model, change one field and every mention across
the site updates — model cards, FAQ answers, running copy.

The template uses these shortcodes inside native Elementor Text Editor and
Shortcode widgets, so they're visible and movable in the editor like any
other element. If you have **Elementor Pro**, you can additionally right-click
any section → Save as Global for reuse across pages.

## Editing

Every heading, paragraph, card, counter, chip row, accordion item and button
is a native Elementor element — click and edit. Entrance animations
(fade-in-up with stagger) and the counter count-ups are Elementor-native
settings under Advanced → Motion Effects / the Counter widget.

Location chips currently link to `#enquire` (the form). As you add country/
city pages in WordPress, edit the chip links in the two Text Editor widgets
in the Locations section.

## Form notes

Submissions are emailed to the address in Settings → Claude AI Trainer
(falls back to the site admin email), with the visitor's email as Reply-To,
plus honeypot + nonce spam protection. If your host's mail is unreliable,
install any SMTP plugin (e.g. WP Mail SMTP) — `[cat_form]` uses `wp_mail()`
so it benefits automatically. Prefer WPForms/CF7? Replace the Shortcode
widget's content with that plugin's shortcode — same one-place-to-edit
behaviour.
