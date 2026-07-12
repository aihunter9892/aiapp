import Anthropic from "@anthropic-ai/sdk";
import type { Config } from "../config.js";
import type { Store } from "../db.js";
import type { GoogleCalendar } from "../integrations/calendar.js";
import { logger } from "../logger.js";

/**
 * Builds the morning digest: what happened overnight, what's due today
 * (reminders + commitments), and today's calendar.
 */
export class DigestBuilder {
  private client: Anthropic;

  constructor(
    private cfg: Config,
    private store: Store,
    private selfJid: () => string,
    private calendar?: GoogleCalendar
  ) {
    this.client = new Anthropic({ apiKey: cfg.anthropicApiKey });
  }

  async build(): Promise<string> {
    const now = new Date();
    const nowSec = Math.floor(now.getTime() / 1000);
    const since = nowSec - 16 * 3600; // roughly "since yesterday evening"

    const overnight = this.store.messagesSince(since, this.selfJid() || undefined, 600);
    const endOfDay = nowSec + 24 * 3600;

    const remindersToday = this.store
      .openReminders()
      .filter((r) => r.due_at <= endOfDay)
      .map((r) => `- ${r.text} (${new Date(r.due_at * 1000).toLocaleTimeString("en-GB", { timeZone: this.cfg.timezone, hour: "2-digit", minute: "2-digit" })})`)
      .join("\n");

    const commitments = this.store
      .openCommitments()
      .slice(0, 15)
      .map(
        (c) =>
          `- [${c.direction === "owed_by_me" ? "I owe" : "owed to me"}] ${c.counterparty}: ${c.description}${c.due_at ? ` (due ${new Date(c.due_at * 1000).toLocaleDateString("en-GB", { timeZone: this.cfg.timezone })})` : ""}`
      )
      .join("\n");

    let calendarBlock = "";
    if (this.calendar) {
      try {
        const startOfDay = new Date(now);
        startOfDay.setHours(0, 0, 0, 0);
        const endDay = new Date(startOfDay.getTime() + 24 * 3600 * 1000);
        const events = await this.calendar.listEvents(
          startOfDay.toISOString(),
          endDay.toISOString()
        );
        calendarBlock = events
          .map((e) => `- ${e.start.slice(11, 16) || "all day"} ${e.summary}`)
          .join("\n");
      } catch (err) {
        logger.error({ err }, "digest calendar fetch failed");
        calendarBlock = "(calendar unavailable)";
      }
    }

    const transcript = overnight
      .slice(-400)
      .map((m) => {
        const chat = this.store.getChat(m.chat_jid);
        return `[${chat?.name || m.chat_jid}] ${m.from_me ? "me" : m.sender_name || "them"}: ${m.text}`;
      })
      .join("\n");

    const response = await this.client.messages.create({
      model: this.cfg.model,
      max_tokens: 2048,
      system: `You write a concise WhatsApp morning digest for your user. WhatsApp formatting only (*bold*, _italics_, "-" lists — no markdown headers). Structure: greeting with today's date; "*Overnight*" — 1-line-per-chat summary of anything that matters from the transcript (skip noise; if nothing matters say "Quiet night."); "*Today*" — calendar events, reminders, and commitments due, merged into one prioritized list; a closing one-liner if something urgently needs attention. Keep the whole digest under 200 words.`,
      messages: [
        {
          role: "user",
          content: `Today: ${now.toLocaleDateString("en-GB", { timeZone: this.cfg.timezone, weekday: "long", day: "numeric", month: "long" })}

Overnight messages:
${transcript || "(none)"}

Reminders due today:
${remindersToday || "(none)"}

Open commitments:
${commitments || "(none)"}

Calendar today:
${calendarBlock || "(no calendar connected)"}`,
        },
      ],
    });

    const text = response.content.find((b) => b.type === "text");
    return text && text.type === "text" ? text.text : "Good morning! (digest unavailable)";
  }
}
