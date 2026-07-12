import type { Config } from "../config.js";
import type { Store } from "../db.js";
import { textOf, type LlmClient } from "../llm/index.js";
import { COMMITMENT_SCAN_PROMPT } from "../agent/prompts.js";
import { logger } from "../logger.js";

interface ExtractedCommitment {
  direction: "owed_by_me" | "owed_to_me";
  counterparty: string;
  description: string;
  due_at: string | null;
  source_excerpt: string;
}

const SCHEMA = {
  type: "object",
  properties: {
    commitments: {
      type: "array",
      items: {
        type: "object",
        properties: {
          direction: { type: "string", enum: ["owed_by_me", "owed_to_me"] },
          counterparty: { type: "string" },
          description: { type: "string" },
          due_at: { type: ["string", "null"] },
          source_excerpt: { type: "string" },
        },
        required: ["direction", "counterparty", "description", "due_at", "source_excerpt"],
        additionalProperties: false,
      },
    },
  },
  required: ["commitments"],
  additionalProperties: false,
} as const;

/**
 * Background pass over new messages: extracts commitments (what the user
 * owes others, what others owe the user) and records them in the ledger.
 */
export class CommitmentScanner {
  constructor(
    private cfg: Config,
    private llm: LlmClient,
    private store: Store,
    private selfJid: () => string
  ) {}

  async scan(): Promise<number> {
    const now = Math.floor(Date.now() / 1000);
    const lastScan = Number(this.store.getSetting("commitment_scan_ts") ?? now - 3600);

    const messages = this.store.messagesSince(lastScan, this.selfJid() || undefined, 400);
    if (messages.length === 0) {
      this.store.setSetting("commitment_scan_ts", String(now));
      return 0;
    }

    // group by chat so the model sees coherent conversations
    const byChat = new Map<string, typeof messages>();
    for (const m of messages) {
      if (!byChat.has(m.chat_jid)) byChat.set(m.chat_jid, []);
      byChat.get(m.chat_jid)!.push(m);
    }

    let added = 0;
    for (const [chatJid, msgs] of byChat) {
      const chat = this.store.getChat(chatJid);
      const transcript = msgs
        .map((m) => `${m.from_me ? "me" : m.sender_name || "them"}: ${m.text}`)
        .join("\n");

      try {
        const response = await this.llm.chat({
          system: COMMITMENT_SCAN_PROMPT,
          maxTokens: 2048,
          jsonSchema: SCHEMA as unknown as Record<string, unknown>,
          messages: [
            {
              role: "user",
              content: `Current time: ${new Date().toISOString()} (${this.cfg.timezone})\nChat: ${chat?.name || chatJid}\n\n${transcript}`,
            },
          ],
        });

        const text = textOf(response);
        if (!text) continue;
        const parsed = JSON.parse(text) as { commitments: ExtractedCommitment[] };

        for (const c of parsed.commitments) {
          if (this.store.hasSimilarCommitment(chatJid, c.description)) continue;
          this.store.addCommitment({
            chat_jid: chatJid,
            direction: c.direction,
            counterparty: c.counterparty,
            description: c.description,
            due_at: c.due_at ? Math.floor(Date.parse(c.due_at) / 1000) || null : null,
            source_excerpt: c.source_excerpt.slice(0, 300),
          });
          added++;
        }
      } catch (err) {
        logger.error({ err, chatJid }, "commitment scan failed for chat");
      }
    }

    this.store.setSetting("commitment_scan_ts", String(now));
    if (added > 0) logger.info({ added }, "commitments extracted");
    return added;
  }
}
