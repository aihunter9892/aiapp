import "dotenv/config";
import path from "node:path";

export interface LlmConfig {
  /** "anthropic" (default) or "openai" — the latter works with any OpenAI-compatible endpoint */
  provider: string;
  apiKey: string;
  /** The model to use — any model your chosen provider serves */
  model: string;
  /** Override the API base URL (e.g. Groq, Ollama, OpenRouter, a proxy) */
  baseUrl?: string;
}

export interface Config {
  llm: LlmConfig;
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

const DEFAULT_MODELS: Record<string, string> = {
  anthropic: "claude-opus-4-8",
  openai: "gpt-4o",
  "openai-compatible": "gpt-4o",
};

function loadLlmConfig(): LlmConfig {
  const provider = (process.env.LLM_PROVIDER ?? "anthropic").toLowerCase();
  const apiKey =
    process.env.LLM_API_KEY ??
    (provider === "anthropic" ? process.env.ANTHROPIC_API_KEY : undefined) ??
    (provider !== "anthropic" ? process.env.OPENAI_API_KEY : undefined);
  if (!apiKey) {
    throw new Error(
      `No API key configured. Set LLM_API_KEY (or ANTHROPIC_API_KEY / OPENAI_API_KEY matching LLM_PROVIDER=${provider}).`
    );
  }
  const model =
    process.env.LLM_MODEL ??
    process.env.TALON_MODEL ?? // backwards compatible
    DEFAULT_MODELS[provider] ??
    DEFAULT_MODELS.anthropic;

  return {
    provider,
    apiKey,
    model,
    baseUrl: process.env.LLM_BASE_URL || undefined,
  };
}

export function loadConfig(): Config {
  const googleConfigured =
    process.env.GOOGLE_CLIENT_ID &&
    process.env.GOOGLE_CLIENT_SECRET &&
    process.env.GOOGLE_REFRESH_TOKEN;

  return {
    llm: loadLlmConfig(),
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
