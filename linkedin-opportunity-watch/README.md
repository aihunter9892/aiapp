# LinkedIn AI-training opportunity digest

Once a day, this scans LinkedIn posts from the **last 24 hours** for people asking for an
**AI trainer**, a **corporate AI trainer**, or a **generative AI workshop**, and sends you the
post links on Telegram so you can reply.

## How it works

1. **Source.** LinkedIn has no public post-search API, and its terms forbid scraping, so the
   script never requests linkedin.com. It asks the [Brave Search API](https://brave.com/search/api/)
   for `site:linkedin.com/posts` pages indexed in the past day (`freshness=pd`).
2. **Request vs. offer.** Each result must mention an AI term and a training term, contain a
   request phrase ("looking for", "hiring", "recommend", ...), and must not read like a trainer
   selling ("I offer", "my workshop", "book a call", ...).
3. **Delivery.** A Markdown digest is written to `out/digest-YYYY-MM-DD.md` and sent to a
   Telegram chat. GitHub Actions runs it every day at 09:00 IST.

## Limits to know about

- **Coverage is partial.** A search index sees only some public posts, and usually with a delay.
  Also run LinkedIn's own search (Posts → Sort by *Latest* → Date posted *Past 24 hours*) with the
  same keywords, or save those searches as alerts.
- **Rules are heuristics.** Expect some false positives and a few misses. Tune `TOPICS`,
  `INTENT_TERMS` and `OFFER_RE` in `watch.py` after a week of digests.
- **Not truly real-time.** The daily schedule matches your "once a day" option. For hourly checks,
  change the cron. Repeat posts can then appear again, so you would need to persist the URLs
  already sent (for example with `actions/cache`).
- **You send the replies.** The script does not message anyone on LinkedIn. Automating DMs or
  connection requests would break LinkedIn's terms and risk your account.

## Setup (about 10 minutes)

1. **Brave Search API key.** Sign up at https://brave.com/search/api/, create a key, and
   copy it. Its free tier is limited, and the script makes 6 queries per run.
2. **Telegram bot.**
   - In Telegram, message `@BotFather`, send `/newbot`, and copy the token.
   - Send any message to your new bot.
   - Open `https://api.telegram.org/bot<TOKEN>/getUpdates` and copy `chat.id` from the result.
3. **GitHub secrets.** In the repo go to *Settings → Secrets and variables → Actions* and add:
   - `BRAVE_API_KEY`
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
4. **Test it.** Run the *LinkedIn AI-training opportunity digest* workflow manually
   (*Actions → … → Run workflow*), or locally:

   ```bash
   cd linkedin-opportunity-watch
   python3 -m unittest -v test_watch
   BRAVE_API_KEY=... python3 watch.py
   ```

## Files

| File | Purpose |
|---|---|
| `watch.py` | Search, classify, render the digest, send to Telegram. Standard library only. |
| `test_watch.py` | Unit tests for the request/offer rules. |
| `../.github/workflows/linkedin-opportunity-watch.yml` | Daily schedule, tests, and digest artifact. |
