import makeWASocket, {
  useMultiFileAuthState,
  DisconnectReason,
  jidNormalizedUser,
  type WAMessage,
  type WASocket,
} from "baileys";
import qrcode from "qrcode-terminal";
import path from "node:path";
import { logger } from "./logger.js";
import type { Store } from "./db.js";

export interface IncomingMessage {
  id: string;
  chatJid: string;
  senderJid: string;
  senderName: string;
  fromMe: boolean;
  isGroup: boolean;
  isSelfChat: boolean;
  text: string;
  timestamp: number;
}

type MessageHandler = (msg: IncomingMessage) => void | Promise<void>;

/** Extract the human-readable text from a Baileys message, if any. */
export function extractText(msg: WAMessage): string {
  let m = msg.message;
  if (!m) return "";
  if (m.ephemeralMessage?.message) m = m.ephemeralMessage.message;
  if (m.viewOnceMessage?.message) m = m.viewOnceMessage.message;
  return (
    m.conversation ??
    m.extendedTextMessage?.text ??
    m.imageMessage?.caption ??
    m.videoMessage?.caption ??
    m.documentMessage?.caption ??
    ""
  );
}

export class WhatsAppClient {
  private sock: WASocket | null = null;
  private handlers: MessageHandler[] = [];
  /** ids of messages this process sent, so we never react to our own output */
  private sentByUs = new Set<string>();
  private groupNameCache = new Map<string, string>();
  ownJid = "";

  constructor(
    private store: Store,
    private dataDir: string
  ) {}

  onMessage(handler: MessageHandler) {
    this.handlers.push(handler);
  }

  async connect(): Promise<void> {
    const { state, saveCreds } = await useMultiFileAuthState(
      path.join(this.dataDir, "auth")
    );

    const sock = makeWASocket({
      auth: state,
      syncFullHistory: false,
      markOnlineOnConnect: false,
    });
    this.sock = sock;

    sock.ev.on("creds.update", saveCreds);

    sock.ev.on("connection.update", (update) => {
      const { connection, lastDisconnect, qr } = update;
      if (qr) {
        console.log("\nScan this QR code with WhatsApp (Settings → Linked Devices → Link a Device):\n");
        qrcode.generate(qr, { small: true });
      }
      if (connection === "open") {
        this.ownJid = jidNormalizedUser(sock.user?.id ?? "");
        logger.info({ jid: this.ownJid }, "WhatsApp connected");
        console.log(`\n✅ Connected as ${this.ownJid}. Message yourself on WhatsApp to talk to your assistant.\n`);
      }
      if (connection === "close") {
        const statusCode = (lastDisconnect?.error as { output?: { statusCode?: number } } | undefined)
          ?.output?.statusCode;
        if (statusCode === DisconnectReason.loggedOut) {
          console.error("Logged out of WhatsApp. Delete the auth folder and re-pair.");
          process.exit(1);
        }
        logger.warn({ statusCode }, "connection closed, reconnecting…");
        setTimeout(() => void this.connect(), 2000);
      }
    });

    sock.ev.on("messages.upsert", async ({ messages, type }) => {
      if (type !== "notify" && type !== "append") return;
      for (const raw of messages) {
        try {
          await this.handleRawMessage(raw);
        } catch (err) {
          logger.error({ err }, "failed to handle message");
        }
      }
    });
  }

  private async handleRawMessage(raw: WAMessage) {
    const chatJid = raw.key.remoteJid;
    if (!chatJid || chatJid === "status@broadcast") return;
    const id = raw.key.id ?? "";
    if (!id || this.sentByUs.has(id)) return;

    const text = extractText(raw);
    if (!text) return;

    const fromMe = raw.key.fromMe === true;
    const isGroup = chatJid.endsWith("@g.us");
    const senderJid = fromMe
      ? this.ownJid
      : jidNormalizedUser(raw.key.participant ?? chatJid);
    const timestamp = Number(raw.messageTimestamp ?? Math.floor(Date.now() / 1000));
    const senderName = fromMe ? "me" : (raw.pushName ?? "");
    const chatName = isGroup
      ? await this.groupName(chatJid)
      : fromMe
        ? ""
        : (raw.pushName ?? "");

    this.store.saveMessage({
      id,
      chat_jid: chatJid,
      sender_jid: senderJid,
      sender_name: senderName,
      from_me: fromMe ? 1 : 0,
      text,
      timestamp,
    });
    this.store.upsertChat(chatJid, chatName, isGroup, timestamp);

    const msg: IncomingMessage = {
      id,
      chatJid,
      senderJid,
      senderName,
      fromMe,
      isGroup,
      isSelfChat: chatJid === this.ownJid,
      text,
      timestamp,
    };
    for (const handler of this.handlers) {
      await handler(msg);
    }
  }

  private async groupName(jid: string): Promise<string> {
    const cached = this.groupNameCache.get(jid);
    if (cached) return cached;
    try {
      const meta = await this.sock!.groupMetadata(jid);
      this.groupNameCache.set(jid, meta.subject);
      return meta.subject;
    } catch {
      return "";
    }
  }

  async sendText(chatJid: string, text: string): Promise<void> {
    if (!this.sock) throw new Error("WhatsApp not connected");
    const sent = await this.sock.sendMessage(chatJid, { text });
    const id = sent?.key?.id;
    if (id) {
      this.sentByUs.add(id);
      // keep the dedupe set bounded
      if (this.sentByUs.size > 2000) {
        const first = this.sentByUs.values().next().value;
        if (first) this.sentByUs.delete(first);
      }
      // record our own outbound message so history stays complete
      this.store.saveMessage({
        id,
        chat_jid: chatJid,
        sender_jid: this.ownJid,
        sender_name: "assistant",
        from_me: 1,
        text,
        timestamp: Math.floor(Date.now() / 1000),
      });
    }
  }

  async sendToSelf(text: string): Promise<void> {
    if (!this.ownJid) throw new Error("Not connected yet");
    await this.sendText(this.ownJid, text);
  }
}
