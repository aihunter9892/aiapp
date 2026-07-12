import Anthropic from "@anthropic-ai/sdk";
import type {
  ChatRequest,
  ChatResponse,
  ContentBlock,
  LlmClient,
} from "./types.js";

/** Models that support adaptive thinking (Claude 4.6+ families). */
function supportsAdaptiveThinking(model: string): boolean {
  return /fable|mythos|opus-4-[678]|sonnet-4-6|sonnet-5/.test(model);
}

export class AnthropicClient implements LlmClient {
  readonly provider = "anthropic";
  private client: Anthropic;

  constructor(
    apiKey: string,
    readonly model: string,
    baseUrl?: string
  ) {
    this.client = new Anthropic({ apiKey, ...(baseUrl ? { baseURL: baseUrl } : {}) });
  }

  async chat(req: ChatRequest): Promise<ChatResponse> {
    const params: Anthropic.MessageCreateParamsNonStreaming = {
      model: this.model,
      max_tokens: req.maxTokens,
      system: [
        { type: "text", text: req.system, cache_control: { type: "ephemeral" } },
      ],
      messages: req.messages as unknown as Anthropic.MessageParam[],
    };

    if (supportsAdaptiveThinking(this.model)) {
      params.thinking = { type: "adaptive" };
    }
    if (req.tools?.length) {
      params.tools = req.tools as unknown as Anthropic.Tool[];
    }
    if (req.jsonSchema) {
      (params as unknown as Record<string, unknown>).output_config = {
        format: { type: "json_schema", schema: req.jsonSchema },
      };
    }

    const response = await this.client.messages.create(params);

    const content: ContentBlock[] = [];
    for (const block of response.content) {
      if (block.type === "text") {
        content.push({ type: "text", text: block.text });
      } else if (block.type === "tool_use") {
        content.push({
          type: "tool_use",
          id: block.id,
          name: block.name,
          input: block.input as Record<string, unknown>,
        });
      }
      // thinking blocks are internal; not surfaced to the app
    }

    let stopReason: ChatResponse["stopReason"];
    switch (response.stop_reason) {
      case "end_turn":
      case "stop_sequence":
        stopReason = "end_turn";
        break;
      case "tool_use":
        stopReason = "tool_use";
        break;
      case "max_tokens":
        stopReason = "max_tokens";
        break;
      case "refusal":
        stopReason = "refusal";
        break;
      default:
        stopReason = "other";
    }

    return { content, stopReason };
  }
}
