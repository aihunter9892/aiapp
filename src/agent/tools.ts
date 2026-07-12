import type { ToolDefinition } from "../llm/index.js";
import type { Store } from "../db.js";
import type { WhatsAppClient } from "../whatsapp.js";
import type { GoogleCalendar } from "../integrations/calendar.js";
import { logger } from "../logger.js";

export interface ToolContext {
  store: Store;
  wa: WhatsAppClient;
  calendar?: GoogleCalendar;
}

function fmtTs(ts: number, timezone?: string): string {
  return new Date(ts * 1000).toLocaleString("en-GB", { timeZone: timezone });
}

function parseISO(iso: string): number {
  const ms = Date.parse(iso);
  if (Number.isNaN(ms)) throw new Error(`Invalid ISO timestamp: ${iso}`);
  return Math.floor(ms / 1000);
}

export function buildTools(calendarEnabled: boolean): ToolDefinition[] {
  const tools: ToolDefinition[] = [
    {
      name: "list_chats",
      description:
        "Search the user's WhatsApp chats by name (contacts and groups). With no query, returns the most recently active chats. Use this to resolve a chat name to its chat_jid before any other chat operation.",
      input_schema: {
        type: "object",
        properties: {
          query: { type: "string", description: "Substring of the chat or contact name. Omit to list recent chats." },
        },
        required: [],
      },
    },
    {
      name: "get_chat_history",
      description:
        "Read stored message history for a chat. Use it to summarize conversations, study the user's writing tone before drafting a reply, or answer questions about what was said.",
      input_schema: {
        type: "object",
        properties: {
          chat_jid: { type: "string", description: "The chat JID from list_chats" },
          limit: { type: "integer", description: "Max messages to return (default 100)" },
          hours: { type: "integer", description: "Only messages from the last N hours" },
        },
        required: ["chat_jid"],
      },
    },
    {
      name: "send_message",
      description:
        "Send a WhatsApp message right now. Requires prior explicit user confirmation of the exact text and recipient when the target is not the self-chat.",
      input_schema: {
        type: "object",
        properties: {
          chat_jid: { type: "string" },
          text: { type: "string" },
        },
        required: ["chat_jid", "text"],
      },
    },
    {
      name: "schedule_message",
      description:
        "Schedule a WhatsApp message to be sent to a chat at a future time. Requires prior explicit user confirmation of text, recipient and time when the target is not the self-chat.",
      input_schema: {
        type: "object",
        properties: {
          chat_jid: { type: "string" },
          text: { type: "string" },
          send_at: { type: "string", description: "ISO 8601 with timezone offset" },
        },
        required: ["chat_jid", "text", "send_at"],
      },
    },
    {
      name: "list_scheduled_messages",
      description: "List messages scheduled for future delivery.",
      input_schema: { type: "object", properties: {}, required: [] },
    },
    {
      name: "cancel_scheduled_message",
      description: "Cancel a pending scheduled message by id.",
      input_schema: {
        type: "object",
        properties: { id: { type: "integer" } },
        required: ["id"],
      },
    },
    {
      name: "create_reminder",
      description: "Create a reminder that fires into the user's self-chat at the given time.",
      input_schema: {
        type: "object",
        properties: {
          text: { type: "string" },
          due_at: { type: "string", description: "ISO 8601 with timezone offset" },
        },
        required: ["text", "due_at"],
      },
    },
    {
      name: "list_reminders",
      description: "List open reminders.",
      input_schema: { type: "object", properties: {}, required: [] },
    },
    {
      name: "complete_reminder",
      description: "Mark a reminder done / cancel it by id.",
      input_schema: {
        type: "object",
        properties: { id: { type: "integer" } },
        required: ["id"],
      },
    },
    {
      name: "list_commitments",
      description:
        "List open commitments — things the user owes others (owed_by_me) and things others owe the user (owed_to_me). These are auto-extracted from conversations and can also be added manually.",
      input_schema: { type: "object", properties: {}, required: [] },
    },
    {
      name: "add_commitment",
      description: "Manually record a commitment.",
      input_schema: {
        type: "object",
        properties: {
          direction: { type: "string", enum: ["owed_by_me", "owed_to_me"] },
          counterparty: { type: "string", description: "Who the commitment is with" },
          description: { type: "string" },
          due_at: { type: "string", description: "ISO 8601 with timezone offset; omit if unknown" },
          chat_jid: { type: "string", description: "Related chat, if any" },
        },
        required: ["direction", "counterparty", "description"],
      },
    },
    {
      name: "resolve_commitment",
      description: "Mark a commitment done or dismiss it (extracted in error / no longer relevant).",
      input_schema: {
        type: "object",
        properties: {
          id: { type: "integer" },
          status: { type: "string", enum: ["done", "dismissed"] },
        },
        required: ["id", "status"],
      },
    },
    {
      name: "set_away_mode",
      description:
        "Turn away-mode auto-replies on or off. While on, the assistant answers incoming direct messages on the user's behalf, in their tone, clearly marked as an auto-reply.",
      input_schema: {
        type: "object",
        properties: {
          enabled: { type: "boolean" },
          note: { type: "string", description: "Optional context to include, e.g. 'in meetings until 3pm'" },
        },
        required: ["enabled"],
      },
    },
  ];

  if (calendarEnabled) {
    tools.push(
      {
        name: "get_calendar_events",
        description: "List Google Calendar events in a time range.",
        input_schema: {
          type: "object",
          properties: {
            time_min: { type: "string", description: "ISO 8601 with timezone offset" },
            time_max: { type: "string", description: "ISO 8601 with timezone offset" },
          },
          required: ["time_min", "time_max"],
        },
      },
      {
        name: "create_calendar_event",
        description:
          "Create a Google Calendar event. Confirm details with the user before creating events with attendees (invites are outward-facing).",
        input_schema: {
          type: "object",
          properties: {
            summary: { type: "string" },
            start: { type: "string", description: "ISO 8601 with timezone offset" },
            end: { type: "string", description: "ISO 8601 with timezone offset" },
            description: { type: "string" },
            attendees: { type: "array", items: { type: "string" }, description: "Attendee emails" },
          },
          required: ["summary", "start", "end"],
        },
      }
    );
  }

  return tools;
}

export async function executeTool(
  ctx: ToolContext,
  name: string,
  input: Record<string, unknown>
): Promise<string> {
  const { store, wa, calendar } = ctx;
  logger.info({ tool: name }, "executing tool");

  switch (name) {
    case "list_chats": {
      const query = (input.query as string | undefined)?.trim();
      const chats = query ? store.searchChats(query) : store.recentChats();
      if (chats.length === 0) return "No chats found.";
      return chats
        .map(
          (c) =>
            `${c.name || "(unnamed)"} | jid: ${c.jid} | ${c.is_group ? "group" : "direct"} | last active: ${fmtTs(c.last_message_at)}`
        )
        .join("\n");
    }

    case "get_chat_history": {
      const chatJid = String(input.chat_jid);
      const limit = Math.min(Number(input.limit ?? 100), 400);
      const hours = input.hours !== undefined ? Number(input.hours) : undefined;
      const sinceTs = hours !== undefined ? Math.floor(Date.now() / 1000) - hours * 3600 : undefined;
      const msgs = store.chatHistory(chatJid, limit, sinceTs);
      if (msgs.length === 0) return "No messages stored for this chat in that window.";
      return msgs
        .map((m) => `[${fmtTs(m.timestamp)}] ${m.from_me ? "me" : m.sender_name || m.sender_jid}: ${m.text}`)
        .join("\n");
    }

    case "send_message": {
      await wa.sendText(String(input.chat_jid), String(input.text));
      return "Message sent.";
    }

    case "schedule_message": {
      const id = store.addScheduledMessage(
        String(input.chat_jid),
        String(input.text),
        parseISO(String(input.send_at))
      );
      return `Scheduled (id ${id}) for ${input.send_at}.`;
    }

    case "list_scheduled_messages": {
      const pending = store.pendingScheduledMessages();
      if (pending.length === 0) return "No pending scheduled messages.";
      return pending
        .map((s) => {
          const chat = store.getChat(s.chat_jid);
          return `#${s.id} → ${chat?.name || s.chat_jid} at ${fmtTs(s.send_at)}: "${s.text}"`;
        })
        .join("\n");
    }

    case "cancel_scheduled_message":
      return store.cancelScheduledMessage(Number(input.id))
        ? "Cancelled."
        : "No pending scheduled message with that id.";

    case "create_reminder": {
      const id = store.addReminder(String(input.text), parseISO(String(input.due_at)));
      return `Reminder #${id} set for ${input.due_at}.`;
    }

    case "list_reminders": {
      const reminders = store.openReminders();
      if (reminders.length === 0) return "No open reminders.";
      return reminders.map((r) => `#${r.id} [${fmtTs(r.due_at)}] ${r.text}`).join("\n");
    }

    case "complete_reminder":
      return store.completeReminder(Number(input.id))
        ? "Done."
        : "No open reminder with that id.";

    case "list_commitments": {
      const commitments = store.openCommitments();
      if (commitments.length === 0) return "No open commitments.";
      return commitments
        .map(
          (c) =>
            `#${c.id} [${c.direction === "owed_by_me" ? "I owe" : "Owed to me"}] ${c.counterparty}: ${c.description}${c.due_at ? ` (due ${fmtTs(c.due_at)})` : ""}`
        )
        .join("\n");
    }

    case "add_commitment": {
      const id = store.addCommitment({
        chat_jid: String(input.chat_jid ?? ""),
        direction: input.direction as "owed_by_me" | "owed_to_me",
        counterparty: String(input.counterparty),
        description: String(input.description),
        due_at: input.due_at ? parseISO(String(input.due_at)) : null,
        source_excerpt: "added manually",
      });
      return `Commitment #${id} recorded.`;
    }

    case "resolve_commitment":
      return store.setCommitmentStatus(Number(input.id), input.status as "done" | "dismissed")
        ? "Updated."
        : "No commitment with that id.";

    case "set_away_mode": {
      const enabled = Boolean(input.enabled);
      store.setSetting("away_mode", enabled ? "1" : "0");
      store.setSetting("away_note", String(input.note ?? ""));
      return enabled
        ? `Away mode ON${input.note ? ` (note: ${input.note})` : ""}. I'll answer incoming direct messages, clearly marked as auto-replies.`
        : "Away mode OFF.";
    }

    case "get_calendar_events": {
      if (!calendar) return "Calendar is not configured.";
      const events = await calendar.listEvents(String(input.time_min), String(input.time_max));
      if (events.length === 0) return "No events in that range.";
      return events
        .map(
          (e) =>
            `${e.start} → ${e.end}: ${e.summary}${e.location ? ` @ ${e.location}` : ""}${e.attendees?.length ? ` (with ${e.attendees.join(", ")})` : ""}`
        )
        .join("\n");
    }

    case "create_calendar_event": {
      if (!calendar) return "Calendar is not configured.";
      const event = await calendar.createEvent(
        String(input.summary),
        String(input.start),
        String(input.end),
        input.description ? String(input.description) : undefined,
        input.attendees as string[] | undefined
      );
      return `Event created: ${event.summary} (${event.start} → ${event.end}).`;
    }

    default:
      throw new Error(`Unknown tool: ${name}`);
  }
}
