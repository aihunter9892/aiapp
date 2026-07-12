import "dotenv/config";
import path from "node:path";

export interface Config {
  anthropicApiKey: string;
  model: string;
  dataDir: string;
  timezone: string;
  /** "HH:MM" 24h local time for the morning digest */
  digestTime: string;
  /** minutes between background commitment-extraction scans */
  commitmentScanIntervalMin: number;
  assistantName: string;
  google?: {
    clientId: string;
    clientSecret: string;
    refreshToken: string;
    calendarId: string;
  };
}

function env(name: string, fallback?: string): string {
  const v = process.env[name] ?? fallback;
  if (v === undefined) {
    throw new Error(`Missing required environment variable: ${name}`);
  }
  return v;
}

export function loadConfig(): Config {
  const googleConfigured =
    process.env.GOOGLE_CLIENT_ID &&
    process.env.GOOGLE_CLIENT_SECRET &&
    process.env.GOOGLE_REFRESH_TOKEN;

  return {
    anthropicApiKey: env("ANTHROPIC_API_KEY"),
    model: env("TALON_MODEL", "claude-opus-4-8"),
    dataDir: path.resolve(env("TALON_DATA_DIR", "./data")),
    timezone: env("TALON_TIMEZONE", Intl.DateTimeFormat().resolvedOptions().timeZone),
    digestTime: env("TALON_DIGEST_TIME", "07:30"),
    commitmentScanIntervalMin: Number(env("TALON_COMMITMENT_SCAN_MIN", "15")),
    assistantName: env("TALON_NAME", "Talon"),
    google: googleConfigured
      ? {
          clientId: process.env.GOOGLE_CLIENT_ID!,
          clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
          refreshToken: process.env.GOOGLE_REFRESH_TOKEN!,
          calendarId: process.env.GOOGLE_CALENDAR_ID ?? "primary",
        }
      : undefined,
  };
}
