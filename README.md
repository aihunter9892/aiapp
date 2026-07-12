# Skillopedia Curriculum Builder (Prototype)

An AI-powered curriculum builder for **Skillopedia**. Clients (or you, on a call) enter a
company name, target audience and workshop format — and instantly get a fully branded,
client-ready Skillopedia training curriculum, matching the format of Skillopedia's real
proposals: program overview, learning outcomes, time-slotted session plan with hands-on
activities, AI tools covered, participant takeaways, and the trainer / Skillopedia profile.

The whole prototype is **one file**: `index.html`. No build step, no server, no dependencies.

## Try it

Open `index.html` in any browser. That's it.

1. Enter the client's **company name** and **industry**
2. Pick the **target audience** (Managers, Sales/BD, IT, HR, Marketing, Finance, Operations, Leadership, All Employees)
3. Pick the **format** — 2-hour masterclass, half day, full day, or 2-day bootcamp
4. Pick the **delivery mode** and add any **special focus** notes
5. Hit **Generate curriculum**

The generated document is fully **click-to-edit** (tweak any line before sending) and
**Download PDF / Print** produces a clean, print-ready branded PDF via the browser's
print dialog.

## Engines

The header's **Engine** chip opens the AI settings:

| Engine | Needs a key? | Notes |
|---|---|---|
| Built-in demo (default) | No | Curated Skillopedia module library, assembled per audience + format. Instant, free, works offline. |
| Groq | Yes | `llama-3.3-70b-versatile` by default |
| Google Gemini | Yes | `gemini-2.0-flash` by default |
| OpenAI | Yes | `gpt-4o-mini` by default |
| Anthropic Claude | Yes | `claude-sonnet-5` by default |

All live engines are asked for the **same JSON structure**, and every engine renders
through the **same branded template** — so the branding, layout and format never change,
only the content generation gets smarter.

> **Prototype note:** live engines are called directly from the browser and the API key is
> stored in `localStorage`. That's fine for personal testing, but for a public site the
> call must move server-side (a tiny PHP endpoint / WordPress plugin / serverless function)
> so your key is never exposed to visitors.

## Using it with WordPress

Three options, easiest first:

1. **Iframe embed** — upload `index.html` anywhere (your hosting's `public_html`, Netlify,
   GitHub Pages…), then in any WordPress page add a *Custom HTML* block:
   ```html
   <iframe src="https://your-domain.com/curriculum-builder/index.html"
           style="width:100%;height:100vh;border:0"></iframe>
   ```
2. **Custom HTML block** — paste the contents of `index.html` (everything inside `<body>`,
   plus the `<style>` and `<script>`) straight into a *Custom HTML* block on a full-width
   page template.
3. **Next level (recommended for production)** — wrap it as a small WordPress plugin with a
   `[skillopedia_builder]` shortcode, and add a PHP endpoint that proxies the AI API call
   server-side with the key stored in `wp-config.php`. This also unlocks lead capture
   (email-gate the PDF download) and usage analytics.

## Roadmap ideas (next level)

- Server-side AI proxy + key management (WordPress plugin or serverless)
- Lead capture: visitor enters email → curriculum PDF emailed via your CRM
- True PDF export (server-rendered) with page headers/footers
- Curriculum history & shareable links
- Pricing/proposal section toggle, multi-language output (Hindi/Gujarati)
