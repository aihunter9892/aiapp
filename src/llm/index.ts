import type { Config } from "../config.js";
import type { LlmClient } from "./types.js";
import { AnthropicClient } from "./anthropic.js";
import { OpenAICompatibleClient } from "./openai.js";
import { logger } from "../logger.js";

export * from "./types.js";

export function createLlm(cfg: Config): LlmClient {
  const { provider, apiKey, model, baseUrl } = cfg.llm;
  logger.info({ provider, model, baseUrl: baseUrl ?? "(default)" }, "LLM configured");

  switch (provider) {
    case "anthropic":
      return new AnthropicClient(apiKey, model, baseUrl);
    case "openai":
    case "openai-compatible":
      return new OpenAICompatibleClient(apiKey, model, baseUrl);
    default:
      throw new Error(
        `Unknown LLM_PROVIDER "${provider}". Use "anthropic" or "openai" (any OpenAI-compatible endpoint).`
      );
  }
}
