import type { Config } from "../config.js";
import type { Store } from "../db.js";
import { textOf, type LlmClient } from "../llm/index.js";
import type { WhatsAppClient, IncomingMessage } from "../whatsapp.js";
import { awayReplyPrompt } from "../agent/prompts.js";
import { logger } from "../logger.js";

const MIN_SECONDS_BETWEEN_REPLIES = 120;

/**
 * Away mode: when enabled, answers incoming direct messages on the user's
 * behalf, in their tone for that chat, clearly marked as an auto-reply.
 */
export class AwayResponder {
  private lastReplyAt = new Map<string, number>();

  constructor(
    private cfg: Config,
    private llm: LlmClient,
    private store: Store,
    private wa: WhatsAppClient
  ) {}

  enabled(): boolean {
    return this.store.getSetting("away_mode") === "1";
  }

  async maybeReply(msg: IncomingMessage): Promise<void> {
    if (!this.enabled()) return;
    if (msg.fromMe || msg.isSelfChat || msg.isGroup) return;

    const now = Math.floor(Date.now() / 1000);
    const last = this.lastReplyAt.get(msg.chatJid) ?? 0;
    if (now - last < MIN_SECONDS_BETWEEN_REPLIES) return;

    const history = this.store
      .chatHistory(msg.chatJid, 40)
      .map((m) => `${m.from_me ? "me" : m.sender_name || "them"}: ${m.text}`)
      .join("\n");
    const note = this.store.getSetting("away_note") ?? "";

    try {
      const response = await this.llm.chat({
        maxTokens: 1024,
        system: awayReplyPrompt(this.cfg.assistantName),
        messages: [
          {
            role: "user",
            content: `${note ? `User's away note: ${note}\n\n` : ""}Recent conversation:\n${history}\n\nNew incoming message from ${msg.senderName || "them"}: ${msg.text}`,
          },
        ],
      });

      const reply = textOf(response);
      if (!reply || reply === "NO_REPLY") return;

      await this.wa.sendText(msg.chatJid, reply);
      this.lastReplyAt.set(msg.chatJid, now);
      logger.info({ chat: msg.chatJid }, "away-mode auto-reply sent");
    } catch (err) {
      logger.error({ err }, "away-mode reply failed");
    }
  }
}
