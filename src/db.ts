import Database from "better-sqlite3";
import fs from "node:fs";
import path from "node:path";

export interface StoredMessage {
  id: string;
  chat_jid: string;
  sender_jid: string;
  sender_name: string;
  from_me: number;
  text: string;
  timestamp: number; // unix seconds
}

export interface Chat {
  jid: string;
  name: string;
  is_group: number;
  last_message_at: number;
}

export interface Reminder {
  id: number;
  text: string;
  due_at: number; // unix seconds
  created_at: number;
  done: number;
}

export interface ScheduledMessage {
  id: number;
  chat_jid: string;
  text: string;
  send_at: number; // unix seconds
  sent: number;
  created_at: number;
}

export interface Commitment {
  id: number;
  chat_jid: string;
  direction: "owed_by_me" | "owed_to_me";
  counterparty: string;
  description: string;
  due_at: number | null;
  status: "open" | "done" | "dismissed";
  source_excerpt: string;
  created_at: number;
}

export class Store {
  private db: Database.Database;

  constructor(dataDir: string) {
    fs.mkdirSync(dataDir, { recursive: true });
    this.db = new Database(path.join(dataDir, "talon.db"));
    this.db.pragma("journal_mode = WAL");
    this.migrate();
  }

  private migrate() {
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS messages (
        id TEXT PRIMARY KEY,
        chat_jid TEXT NOT NULL,
        sender_jid TEXT NOT NULL,
        sender_name TEXT NOT NULL DEFAULT '',
        from_me INTEGER NOT NULL DEFAULT 0,
        text TEXT NOT NULL,
        timestamp INTEGER NOT NULL
      );
      CREATE INDEX IF NOT EXISTS idx_messages_chat_ts ON messages(chat_jid, timestamp);
      CREATE INDEX IF NOT EXISTS idx_messages_ts ON messages(timestamp);

      CREATE TABLE IF NOT EXISTS chats (
        jid TEXT PRIMARY KEY,
        name TEXT NOT NULL DEFAULT '',
        is_group INTEGER NOT NULL DEFAULT 0,
        last_message_at INTEGER NOT NULL DEFAULT 0
      );

      CREATE TABLE IF NOT EXISTS reminders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text TEXT NOT NULL,
        due_at INTEGER NOT NULL,
        created_at INTEGER NOT NULL,
        done INTEGER NOT NULL DEFAULT 0
      );

      CREATE TABLE IF NOT EXISTS scheduled_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_jid TEXT NOT NULL,
        text TEXT NOT NULL,
        send_at INTEGER NOT NULL,
        sent INTEGER NOT NULL DEFAULT 0,
        created_at INTEGER NOT NULL
      );

      CREATE TABLE IF NOT EXISTS commitments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_jid TEXT NOT NULL,
        direction TEXT NOT NULL,
        counterparty TEXT NOT NULL,
        description TEXT NOT NULL,
        due_at INTEGER,
        status TEXT NOT NULL DEFAULT 'open',
        source_excerpt TEXT NOT NULL DEFAULT '',
        created_at INTEGER NOT NULL
      );

      CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
      );
    `);
  }

  // ---- settings ----
  getSetting(key: string): string | undefined {
    const row = this.db.prepare("SELECT value FROM settings WHERE key = ?").get(key) as
      | { value: string }
      | undefined;
    return row?.value;
  }

  setSetting(key: string, value: string) {
    this.db
      .prepare(
        "INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value"
      )
      .run(key, value);
  }

  // ---- messages / chats ----
  saveMessage(m: StoredMessage) {
    this.db
      .prepare(
        `INSERT OR IGNORE INTO messages (id, chat_jid, sender_jid, sender_name, from_me, text, timestamp)
         VALUES (@id, @chat_jid, @sender_jid, @sender_name, @from_me, @text, @timestamp)`
      )
      .run(m);
  }

  upsertChat(jid: string, name: string, isGroup: boolean, lastMessageAt: number) {
    this.db
      .prepare(
        `INSERT INTO chats (jid, name, is_group, last_message_at) VALUES (?, ?, ?, ?)
         ON CONFLICT(jid) DO UPDATE SET
           name = CASE WHEN excluded.name != '' THEN excluded.name ELSE chats.name END,
           last_message_at = MAX(chats.last_message_at, excluded.last_message_at)`
      )
      .run(jid, name, isGroup ? 1 : 0, lastMessageAt);
  }

  searchChats(query: string, limit = 10): Chat[] {
    return this.db
      .prepare(
        `SELECT * FROM chats WHERE name LIKE ? OR jid LIKE ? ORDER BY last_message_at DESC LIMIT ?`
      )
      .all(`%${query}%`, `%${query}%`, limit) as Chat[];
  }

  recentChats(limit = 20): Chat[] {
    return this.db
      .prepare(`SELECT * FROM chats ORDER BY last_message_at DESC LIMIT ?`)
      .all(limit) as Chat[];
  }

  getChat(jid: string): Chat | undefined {
    return this.db.prepare(`SELECT * FROM chats WHERE jid = ?`).get(jid) as Chat | undefined;
  }

  chatHistory(chatJid: string, limit = 100, sinceTs?: number): StoredMessage[] {
    if (sinceTs !== undefined) {
      return (
        this.db
          .prepare(
            `SELECT * FROM messages WHERE chat_jid = ? AND timestamp >= ? ORDER BY timestamp DESC LIMIT ?`
          )
          .all(chatJid, sinceTs, limit) as StoredMessage[]
      ).reverse();
    }
    return (
      this.db
        .prepare(`SELECT * FROM messages WHERE chat_jid = ? ORDER BY timestamp DESC LIMIT ?`)
        .all(chatJid, limit) as StoredMessage[]
    ).reverse();
  }

  messagesSince(sinceTs: number, excludeChat?: string, limit = 500): StoredMessage[] {
    if (excludeChat) {
      return this.db
        .prepare(
          `SELECT * FROM messages WHERE timestamp >= ? AND chat_jid != ? ORDER BY timestamp ASC LIMIT ?`
        )
        .all(sinceTs, excludeChat, limit) as StoredMessage[];
    }
    return this.db
      .prepare(`SELECT * FROM messages WHERE timestamp >= ? ORDER BY timestamp ASC LIMIT ?`)
      .all(sinceTs, limit) as StoredMessage[];
  }

  // ---- reminders ----
  addReminder(text: string, dueAt: number): number {
    const res = this.db
      .prepare(`INSERT INTO reminders (text, due_at, created_at) VALUES (?, ?, unixepoch())`)
      .run(text, dueAt);
    return Number(res.lastInsertRowid);
  }

  dueReminders(now: number): Reminder[] {
    return this.db
      .prepare(`SELECT * FROM reminders WHERE done = 0 AND due_at <= ? ORDER BY due_at ASC`)
      .all(now) as Reminder[];
  }

  openReminders(): Reminder[] {
    return this.db
      .prepare(`SELECT * FROM reminders WHERE done = 0 ORDER BY due_at ASC`)
      .all() as Reminder[];
  }

  completeReminder(id: number): boolean {
    return this.db.prepare(`UPDATE reminders SET done = 1 WHERE id = ?`).run(id).changes > 0;
  }

  // ---- scheduled messages ----
  addScheduledMessage(chatJid: string, text: string, sendAt: number): number {
    const res = this.db
      .prepare(
        `INSERT INTO scheduled_messages (chat_jid, text, send_at, created_at) VALUES (?, ?, ?, unixepoch())`
      )
      .run(chatJid, text, sendAt);
    return Number(res.lastInsertRowid);
  }

  dueScheduledMessages(now: number): ScheduledMessage[] {
    return this.db
      .prepare(`SELECT * FROM scheduled_messages WHERE sent = 0 AND send_at <= ? ORDER BY send_at ASC`)
      .all(now) as ScheduledMessage[];
  }

  pendingScheduledMessages(): ScheduledMessage[] {
    return this.db
      .prepare(`SELECT * FROM scheduled_messages WHERE sent = 0 ORDER BY send_at ASC`)
      .all() as ScheduledMessage[];
  }

  markScheduledSent(id: number) {
    this.db.prepare(`UPDATE scheduled_messages SET sent = 1 WHERE id = ?`).run(id);
  }

  cancelScheduledMessage(id: number): boolean {
    return (
      this.db.prepare(`DELETE FROM scheduled_messages WHERE id = ? AND sent = 0`).run(id).changes > 0
    );
  }

  // ---- commitments ----
  addCommitment(c: Omit<Commitment, "id" | "created_at" | "status">): number {
    const res = this.db
      .prepare(
        `INSERT INTO commitments (chat_jid, direction, counterparty, description, due_at, source_excerpt, created_at)
         VALUES (@chat_jid, @direction, @counterparty, @description, @due_at, @source_excerpt, unixepoch())`
      )
      .run(c);
    return Number(res.lastInsertRowid);
  }

  openCommitments(): Commitment[] {
    return this.db
      .prepare(
        `SELECT * FROM commitments WHERE status = 'open' ORDER BY due_at IS NULL, due_at ASC, created_at ASC`
      )
      .all() as Commitment[];
  }

  setCommitmentStatus(id: number, status: "done" | "dismissed"): boolean {
    return (
      this.db.prepare(`UPDATE commitments SET status = ? WHERE id = ?`).run(status, id).changes > 0
    );
  }

  /** naive duplicate check so the background scanner doesn't re-add the same commitment */
  hasSimilarCommitment(chatJid: string, description: string): boolean {
    const row = this.db
      .prepare(
        `SELECT id FROM commitments WHERE chat_jid = ? AND status = 'open' AND description = ?`
      )
      .get(chatJid, description);
    return row !== undefined;
  }

  close() {
    this.db.close();
  }
}
