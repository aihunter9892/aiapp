#!/usr/bin/env python3
"""Daily scan for LinkedIn posts from the last 24 hours that ask for an AI trainer,
corporate AI trainer, or generative AI workshop.

LinkedIn has no public post-search API and its ToS forbids scraping, so this does
not touch linkedin.com. It asks a search API (Brave Search) for public LinkedIn post
pages indexed in the past day (freshness=pd), then keeps only posts that look like
*requests* and drops posts that look like *offers* from trainers.

Environment variables:
  BRAVE_API_KEY       required. Brave Search API subscription token.
  TELEGRAM_BOT_TOKEN  optional. With TELEGRAM_CHAT_ID, the digest is sent there.
  TELEGRAM_CHAT_ID    optional.
  OUTPUT_DIR          optional. Digest is written to OUTPUT_DIR/digest-YYYY-MM-DD.md (default: out).
"""

import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

BRAVE_URL = "https://api.search.brave.com/res/v1/web/search"
TELEGRAM_URL = "https://api.telegram.org/bot{token}/sendMessage"
TELEGRAM_LIMIT = 4000  # Telegram caps messages at 4096 characters

TOPICS = [
    "AI trainer",
    "corporate AI trainer",
    "generative AI workshop",
    "GenAI training",
    "ChatGPT training",
    "AI upskilling",
]

INTENT_TERMS = [
    "looking for", "we're looking", "we are looking", "seeking", "hiring",
    "need", "needs", "recommend", "recommendations", "suggestions",
    "anyone know", "know any", "can you suggest", "any leads", "who can",
    "who does", "is there",
]

AI_TERM = r"(?:ai|a\.i\.|gen\s?ai|generative ai|chatgpt|llms?|copilot)"
TRAIN_TERM = r"(?:trainers?|training|workshops?|upskilling|enablement|bootcamps?|masterclass(?:es)?)"
TOPIC_RE = re.compile(
    rf"\b{AI_TERM}\b(?:\W+\w+){{0,4}}?\W+{TRAIN_TERM}\b"
    rf"|\b{TRAIN_TERM}\b(?:\W+\w+){{0,4}}?\W+{AI_TERM}\b",
    re.IGNORECASE,
)
INTENT_RE = re.compile(
    r"\b(?:" + "|".join(re.escape(term) for term in INTENT_TERMS) + r")\b",
    re.IGNORECASE,
)
# Phrases trainers use when selling their own services. A request rarely contains these.
OFFER_RE = re.compile(
    r"\b(?:i (?:offer|run|conduct|deliver|provide)|we (?:offer|run|deliver|provide)"
    r"|my (?:workshops?|trainings?|courses?|programs?|cohorts?)"
    r"|our (?:workshops?|trainings?|courses?|programs?|cohorts?)"
    r"|i'?m (?:a|an|available)|i am (?:a|an|available)|available for"
    r"|book (?:a|your|me)|sign ?up|enrol+|register (?:now|today|here)"
    r"|join (?:my|our)|check out my|link in (?:the )?comments)\b",
    re.IGNORECASE,
)


def clean(text):
    """Strip the <strong> tags Brave adds to highlighted words, and unescape entities."""
    return html.unescape(re.sub(r"<[^>]+>", "", text or "")).strip()


def is_linkedin_post(url):
    parsed = urllib.parse.urlparse(url)
    return parsed.netloc.endswith("linkedin.com") and parsed.path.startswith(
        ("/posts/", "/feed/update/")
    )


def classify(title, description, url):
    """Return a match dict if the result is a request for AI training, else None."""
    if not is_linkedin_post(url):
        return None
    text = f"{title}. {description}"
    if not TOPIC_RE.search(text) or not INTENT_RE.search(text) or OFFER_RE.search(text):
        return None
    return {"title": title, "url": url, "snippet": description}


def search(query, api_key, count=20):
    params = urllib.parse.urlencode({"q": query, "freshness": "pd", "count": count})
    request = urllib.request.Request(
        f"{BRAVE_URL}?{params}",
        headers={"Accept": "application/json", "X-Subscription-Token": api_key},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        data = json.load(response)
    return data.get("web", {}).get("results", [])


def scan(api_key):
    matches = {}
    failures = 0
    for index, topic in enumerate(TOPICS):
        if index:
            time.sleep(1.1)  # Brave free tier allows about one request per second
        query = f'site:linkedin.com/posts "{topic}" ("looking for" OR hiring OR need OR recommend)'
        try:
            results = search(query, api_key)
        except (urllib.error.URLError, json.JSONDecodeError) as exc:
            failures += 1
            print(f"warning: search failed for {topic!r}: {exc}", file=sys.stderr)
            continue
        for result in results:
            url = result.get("url", "")
            if url in matches:
                continue
            match = classify(
                clean(result.get("title")), clean(result.get("description")), url
            )
            if match:
                matches[url] = match
    if failures == len(TOPICS):
        raise SystemExit("every search failed; check BRAVE_API_KEY and quota")
    return list(matches.values())


def render(matches, today):
    lines = [f"LinkedIn AI-training requests, last 24 hours ({today})", ""]
    if not matches:
        lines.append("No new requests found.")
    for match in matches:
        snippet = match["snippet"]
        if len(snippet) > 300:
            snippet = snippet[:297] + "..."
        lines += [f"- {match['title']}", f"  {match['url']}", f"  {snippet}", ""]
    return "\n".join(lines).rstrip() + "\n"


def send_telegram(token, chat_id, text):
    chunks, current = [], ""
    for line in text.splitlines(keepends=True):
        if len(current) + len(line) > TELEGRAM_LIMIT:
            chunks.append(current)
            current = ""
        current += line
    chunks.append(current)
    for chunk in chunks:
        body = urllib.parse.urlencode(
            {"chat_id": chat_id, "text": chunk, "disable_web_page_preview": "true"}
        ).encode()
        request = urllib.request.Request(TELEGRAM_URL.format(token=token), data=body)
        with urllib.request.urlopen(request, timeout=30):
            pass


def main():
    api_key = os.environ.get("BRAVE_API_KEY")
    if not api_key:
        sys.exit("BRAVE_API_KEY is not set")

    today = date.today().isoformat()
    text = render(scan(api_key), today)

    out_dir = Path(os.environ.get("OUTPUT_DIR", "out"))
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"digest-{today}.md").write_text(text, encoding="utf-8")
    print(text)

    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if token and chat_id:
        send_telegram(token, chat_id, text)


if __name__ == "__main__":
    main()
