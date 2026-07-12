import type { Config } from "../config.js";
import type { Store } from "../db.js";
import type { WhatsAppClient } from "../whatsapp.js";
import type { CommitmentScanner } from "./commitments.js";
import type { DigestBuilder } from "./digest.js";
import { logger } from "../logger.js";

const TICK_MS = 20_000;

/**
 * The heartbeat: fires due reminders into the self-chat, sends scheduled
 * messages, triggers the morning digest once a day, and runs the
 * commitment scanner on its interval.
 */
export class Scheduler {
  private timer: NodeJS.Timeout | null = null;
  private ticking = false;

  constructor(
    private cfg: Config,
    private store: Store,
    private wa: WhatsAppClient,
    private digest: DigestBuilder,
    private commitments: CommitmentScanner
  ) {}

  start() {
    this.timer = setInterval(() => void this.tick(), TICK_MS);
    logger.info("scheduler started");
  }

  stop() {
    if (this.timer) clearInterval(this.timer);
  }

  private async tick() {
    if (this.ticking || !this.wa.ownJid) return;
    this.ticking = true;
    try {
      await this.fireReminders();
      await this.sendScheduledMessages();
      await this.maybeSendDigest();
      await this.maybeScanCommitments();
    } catch (err) {
      logger.error({ err }, "scheduler tick failed");
    } finally {
      this.ticking = false;
    }
  }

  private async fireReminders() {
    const now = Math.floor(Date.now() / 1000);
    for (const r of this.store.dueReminders(now)) {
      await this.wa.sendToSelf(`⏰ *Reminder:* ${r.text}`);
      this.store.completeReminder(r.id);
    }
  }

  private async sendScheduledMessages() {
    const now = Math.floor(Date.now() / 1000);
    for (const s of this.store.dueScheduledMessages(now)) {
      try {
        await this.wa.sendText(s.chat_jid, s.text);
        this.store.markScheduledSent(s.id);
        const chat = this.store.getChat(s.chat_jid);
        await this.wa.sendToSelf(`📤 Sent your scheduled message to ${chat?.name || s.chat_jid}.`);
      } catch (err) {
        logger.error({ err, id: s.id }, "scheduled message send failed");
      }
    }
  }

  private async maybeSendDigest() {
    const now = new Date();
    const local = now.toLocaleTimeString("en-GB", {
      timeZone: this.cfg.timezone,
      hour: "2-digit",
      minute: "2-digit",
      hour12: false,
    });
    if (local < this.cfg.digestTime) return;

    const today = now.toLocaleDateString("en-CA", { timeZone: this.cfg.timezone }); // YYYY-MM-DD
    if (this.store.getSetting("last_digest_date") === today) return;
    this.store.setSetting("last_digest_date", today);

    try {
      const text = await this.digest.build();
      await this.wa.sendToSelf(text);
      logger.info("morning digest sent");
    } catch (err) {
      logger.error({ err }, "digest failed");
    }
  }

  private async maybeScanCommitments() {
    const now = Math.floor(Date.now() / 1000);
    const last = Number(this.store.getSetting("commitment_scan_last_run") ?? 0);
    if (now - last < this.cfg.commitmentScanIntervalMin * 60) return;
    this.store.setSetting("commitment_scan_last_run", String(now));

    const added = await this.commitments.scan();
    if (added > 0) {
      await this.wa.sendToSelf(
        `📌 I spotted ${added} new commitment${added === 1 ? "" : "s"} in your chats. Say "show commitments" to review.`
      );
    }
  }
}
