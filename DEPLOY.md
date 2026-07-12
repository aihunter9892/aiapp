# Deploying Talon

Talon is a long-running Node.js process: it holds a live WebSocket connection to WhatsApp, ticks a scheduler every 20 seconds, and writes to a local SQLite database. That means it needs a machine that **stays on** — a small VPS, a home server, or a Raspberry Pi. It cannot run on serverless platforms or on shared WordPress/PHP hosting (see the WordPress section below for what *can* live there).

## Option A — Docker on any VPS (recommended)

Works on a $4–6/mo VPS (Hetzner, DigitalOcean, Lightsail, …) or any box with Docker.

```bash
git clone <this repo> talon && cd talon
cp .env.example .env        # set LLM_PROVIDER, LLM_API_KEY, LLM_MODEL
docker compose up -d --build
docker compose logs -f talon   # the WhatsApp QR code prints here — scan it
```

Scan the QR once (WhatsApp → Settings → Linked Devices → Link a Device). The session, message archive, and ledger persist in the `talon-data` volume, so restarts and updates don't need re-pairing:

```bash
git pull && docker compose up -d --build   # update
docker compose logs -f talon               # watch
```

## Option B — bare Node + pm2

```bash
git clone <this repo> talon && cd talon
npm install && cp .env.example .env && npm run build
npm start                    # first run in the foreground to scan the QR
# then keep it alive forever:
npm i -g pm2
pm2 start dist/index.js --name talon
pm2 save && pm2 startup      # survive reboots
```

## Option C — Railway / Fly.io / Render

Deploy as a **worker/background service** (not a web service — there's no HTTP port) using the Dockerfile. Two requirements:

1. Attach a **persistent volume** mounted at `/data` (the WhatsApp session and SQLite DB live there — without it you'd re-pair on every deploy).
2. Scan the QR from the service logs on first boot.

## What about WordPress?

WordPress hosting can't run a persistent Node process, so Talon itself can't live there — but WordPress is the right place for the **public face** of the product:

- If your WordPress runs on a **VPS you control**, run Talon on the same machine (Option A or B) alongside it.
- On your WordPress site, add a landing page for the product: paste the contents of `wordpress-landing.html` into a **Custom HTML** block on any page or post. It's self-contained (inline styles, no scripts) and matches the product branding.

## Notes

- **Timezone**: set `TALON_TIMEZONE` (e.g. `Asia/Kolkata`) so reminders and the digest fire at your local time — containers default to UTC.
- **Logged out?** If WhatsApp unlinks the device, delete the `auth/` folder inside the data volume and restart to re-pair.
- **Privacy**: the data volume contains your full message archive and session keys. Treat it like a password vault — encrypt backups, restrict access.
