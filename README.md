# 🦅 Talon — your executive assistant, inside your own WhatsApp

Talon is a personal AI executive assistant that lives in **your actual WhatsApp number** — not a separate bot account, not a new app. Pair once with a QR code and it appears in your **self-chat** ("message yourself"). From there it manages your day: commitments, reminders, scheduled messages, chat summaries, tone-matched drafts, a morning digest, your calendar, and auto-replies while you're away.

Everything runs **locally on your machine**: your message archive lives in a SQLite file you own, and the only external calls are to the LLM API *you* choose (and Google Calendar, if you connect it). No third-party server ever sees your chats.

**Bring your own LLM.** Talon is provider-agnostic — you pick both the API and the model. Anthropic (Claude) is the default, and any OpenAI-compatible endpoint works too: OpenAI, Groq, Ollama (fully local!), OpenRouter, Together, DeepSeek, Gemini's compatibility endpoint, LM Studio, vLLM…

## What it does

| Feature | How it works |
|---|---|
| 📌 **Commitment tracking** | A background pass over your conversations extracts every concrete promise — what you owe others and what they owe you — into a ledger you can review, complete, or dismiss. It nudges you in your self-chat when it spots new ones. |
| ⏰ **Reminders** | "Remind me to call Sara tomorrow at 4pm" — fires back into your self-chat at the right moment. |
| 📤 **Scheduled messages** | "Send 'happy birthday! 🎉' to Dad at midnight" — queued locally and delivered to any chat or group on time. |
| 📚 **Chat & group summaries** | "What did I miss in the Founders group?" — summarizes stored history for any chat, any time window. |
| ✍️ **Drafts in your voice** | Before drafting a reply, Talon studies how *you* write in that specific chat — length, formality, emoji, language — and matches it. |
| 🌅 **Morning digest** | Every morning (default 07:30): what happened overnight, today's calendar, reminders, and commitments due — under 200 words. |
| 📆 **Calendar** | Optional Google Calendar connection: check your day, create events, spot conflicts — from inside WhatsApp. |
| 🌙 **Away mode** | "I'm in meetings until 3, cover for me" — Talon answers incoming DMs in your tone, clearly marked as auto-replies, and never commits you to anything. |

## Quick start

Requires Node.js 20+ and an API key for the LLM provider of your choice.

```bash
git clone <this repo> && cd aiapp
npm install
cp .env.example .env       # set LLM_PROVIDER, LLM_API_KEY, LLM_MODEL
npm run build
npm start
```

A QR code appears in your terminal. On your phone: **WhatsApp → Settings → Linked Devices → Link a Device** and scan it. That's it — open the chat with yourself and say hi.

For development: `npm run dev` (runs from source with tsx).

**Going live?** See [DEPLOY.md](DEPLOY.md) — Docker on a VPS (recommended, `docker compose up -d` and scan the QR from the logs), bare Node + pm2, Railway/Fly worker, and how to present the product from a WordPress site (`wordpress-landing.html`).

## Talking to Talon

Just message yourself in plain language:

- *"remind me to renew the domain on the 1st"*
- *"summarize the Design team group since yesterday"*
- *"what do I owe people this week?"*
- *"draft a reply to Marco — tell him the deck slips to Thursday, keep it warm"*
- *"schedule 'running 10 min late' to Anna for 8:50 tomorrow"*
- *"what's on my calendar Friday?"*
- *"away mode on — back at 3pm"*

Talon always shows you the exact draft and recipient and waits for your **yes** before sending anything to anyone else. Reminders and nudges arrive in your self-chat.

## Configuration

All via `.env` (see `.env.example`):

| Variable | Default | Purpose |
|---|---|---|
| `LLM_PROVIDER` | `anthropic` | `anthropic`, or `openai` for any OpenAI-compatible endpoint |
| `LLM_API_KEY` | — | Required — key for your provider (`ANTHROPIC_API_KEY`/`OPENAI_API_KEY` work as fallbacks) |
| `LLM_MODEL` | per provider | Any model your provider serves (`claude-opus-4-8` / `gpt-4o` defaults) |
| `LLM_BASE_URL` | per provider | Point at Groq, Ollama, OpenRouter, a proxy, … |
| `TALON_NAME` | `Talon` | Assistant name |
| `TALON_TIMEZONE` | system | IANA timezone for times & digest |
| `TALON_DIGEST_TIME` | `07:30` | Daily digest time (24h local) |
| `TALON_COMMITMENT_SCAN_MIN` | `15` | Minutes between commitment scans |
| `TALON_DATA_DIR` | `./data` | Where SQLite DB + WhatsApp session live |
| `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` / `GOOGLE_REFRESH_TOKEN` | — | Optional Google Calendar |
| `GOOGLE_CALENDAR_ID` | `primary` | Which calendar to use |

## Architecture

```
WhatsApp (your number, multi-device Web protocol via Baileys)
      │  ingests every message → SQLite (local, yours)
      ▼
 self-chat message ──► Agent (your LLM, tool loop) ──► tools:
                                                     chats · history · send/schedule
                                                     reminders · commitments
                                                     away mode · calendar
 background (20s tick):
   due reminders → self-chat        scheduled messages → target chat
   morning digest (once daily)      commitment scanner (your LLM, structured output)
   away-mode auto-replies on incoming DMs
```

- `src/whatsapp.ts` — Baileys connection, QR pairing, message ingestion, send helpers
- `src/llm/` — provider abstraction: Anthropic SDK client + a zero-dependency OpenAI-compatible client (plain fetch); both API and model are user-configurable
- `src/agent/` — system prompt, tool definitions, provider-agnostic tool-use loop
- `src/features/` — scheduler heartbeat, commitment scanner, digest builder, away responder
- `src/db.ts` — SQLite schema and queries (messages, chats, reminders, scheduled messages, commitments, settings)
- `src/integrations/calendar.ts` — Google Calendar over raw REST (refresh-token OAuth), zero extra deps

## Privacy & safety

- **Local-first**: messages, ledger, and WhatsApp session credentials never leave your machine except as context in your own Claude API calls.
- **Confirmation gate**: outbound messages to anyone but yourself require your explicit approval of the exact text and recipient.
- **Honest auto-replies**: away-mode messages are signed `— Talon (auto-reply)` and never make decisions or commitments for you.

> ⚠️ Talon uses the WhatsApp Web multi-device protocol via the open-source Baileys library, the same class of unofficial API used by similar products. Automating a personal WhatsApp account is against WhatsApp's ToS in principle; use a number you're comfortable with and avoid spammy behavior.

## License

MIT

---

## Also in this repository

`index.html` + `pptxgen.bundle.js` are a separate mini-app: the **Skillopedia Curriculum Builder** (live at https://aihunter9892.github.io/aiapp/), an AI-powered, brand-styled curriculum generator with PPT/Word/PDF export. It shares this repo but is unrelated to Talon.
