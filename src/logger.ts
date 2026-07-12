import pino from "pino";

export const logger = pino({
  level: process.env.TALON_LOG_LEVEL ?? "info",
  transport: process.stdout.isTTY
    ? { target: "pino/file", options: { destination: 1 } }
    : undefined,
});
