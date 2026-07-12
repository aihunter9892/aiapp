import { loadConfig } from "./config.js";
import { Store } from "./db.js";
import { WhatsAppClient } from "./whatsapp.js";
import { Agent } from "./agent/agent.js";
import { GoogleCalendar } from "./integrations/calendar.js";
import { CommitmentScanner } from "./features/commitments.js";
import { DigestBuilder } from "./features/digest.js";
import { AwayResponder } from "./features/away.js";
import { Scheduler } from "./features/scheduler.js";
import { logger } from "./logger.js";

async function main() {
  const cfg = loadConfig();
  const store = new Store(cfg.dataDir);
  const wa = new WhatsAppClient(store, cfg.dataDir);
  const calendar = cfg.google ? new GoogleCalendar(cfg.google) : undefined;

  const agent = new Agent(cfg, { store, wa, calendar });
  const away = new AwayResponder(cfg, store, wa);
  const commitments = new CommitmentScanner(cfg, store, () => wa.ownJid);
  const digest = new DigestBuilder(cfg, store, () => wa.ownJid, calendar);
  const scheduler = new Scheduler(cfg, store, wa, digest, commitments);

  wa.onMessage(async (msg) => {
    // Self-chat = the command center: talk to the assistant.
    if (msg.isSelfChat && msg.fromMe) {
      try {
        const reply = await agent.handle(msg.text);
        if (reply) await wa.sendToSelf(reply);
      } catch (err) {
        logger.error({ err }, "agent turn failed");
        await wa.sendToSelf("⚠️ Something went wrong handling that — try again.");
      }
      return;
    }
    // Everything else: candidate for away-mode auto-reply.
    await away.maybeReply(msg);
  });

  await wa.connect();
  scheduler.start();

  const shutdown = () => {
    logger.info("shutting down");
    scheduler.stop();
    store.close();
    process.exit(0);
  };
  process.on("SIGINT", shutdown);
  process.on("SIGTERM", shutdown);
}

main().catch((err) => {
  console.error("Fatal:", err);
  process.exit(1);
});
