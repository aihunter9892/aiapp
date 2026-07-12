import type {
  ChatMessage,
  ChatRequest,
  ChatResponse,
  ContentBlock,
  LlmClient,
  ToolResultBlock,
  ToolUseBlock,
} from "./types.js";
import { logger } from "../logger.js";

interface OpenAIMessage {
  role: "system" | "user" | "assistant" | "tool";
  content: string | null;
  tool_call_id?: string;
  tool_calls?: Array<{
    id: string;
    type: "function";
    function: { name: string; arguments: string };
  }>;
}

/**
 * Client for any OpenAI-compatible chat-completions endpoint — OpenAI itself,
 * Groq, Ollama, OpenRouter, Together, DeepSeek, Gemini's compatibility
 * endpoint, LM Studio, vLLM, and most other providers. Uses plain fetch:
 * point LLM_BASE_URL at the provider and pick any LLM_MODEL it serves.
 */
export class OpenAICompatibleClient implements LlmClient {
  readonly provider = "openai-compatible";

  constructor(
    private apiKey: string,
    readonly model: string,
    private baseUrl = "https://api.openai.com/v1"
  ) {
    this.baseUrl = this.baseUrl.replace(/\/+$/, "");
  }

  async chat(req: ChatRequest): Promise<ChatResponse> {
    const messages: OpenAIMessage[] = [{ role: "system", content: req.system }];
    for (const m of req.messages) {
      messages.push(...convertMessage(m));
    }

    const body: Record<string, unknown> = {
      model: this.model,
      max_tokens: req.maxTokens,
      messages,
    };
    if (req.tools?.length) {
      body.tools = req.tools.map((t) => ({
        type: "function",
        function: {
          name: t.name,
          description: t.description,
          parameters: t.input_schema,
        },
      }));
    }
    if (req.jsonSchema) {
      body.response_format = {
        type: "json_schema",
        json_schema: { name: "result", schema: req.jsonSchema },
      };
    }

    const res = await fetch(`${this.baseUrl}/chat/completions`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${this.apiKey}`,
      },
      body: JSON.stringify(body),
    });
    if (!res.ok) {
      const errText = await res.text();
      throw new Error(`LLM request failed (${res.status}): ${errText.slice(0, 500)}`);
    }

    const data = (await res.json()) as {
      choices?: Array<{
        message?: {
          content?: string | null;
          tool_calls?: Array<{
            id?: string;
            function?: { name?: string; arguments?: string };
          }>;
        };
        finish_reason?: string;
      }>;
    };
    const choice = data.choices?.[0];
    if (!choice?.message) {
      throw new Error("LLM returned no choices");
    }

    const content: ContentBlock[] = [];
    if (choice.message.content) {
      content.push({ type: "text", text: choice.message.content });
    }
    for (const tc of choice.message.tool_calls ?? []) {
      let input: Record<string, unknown> = {};
      try {
        input = tc.function?.arguments ? JSON.parse(tc.function.arguments) : {};
      } catch (err) {
        logger.warn({ err, args: tc.function?.arguments }, "unparseable tool arguments");
      }
      content.push({
        type: "tool_use",
        id: tc.id ?? `call_${Math.random().toString(36).slice(2)}`,
        name: tc.function?.name ?? "",
        input,
      });
    }

    let stopReason: ChatResponse["stopReason"];
    switch (choice.finish_reason) {
      case "stop":
        stopReason = "end_turn";
        break;
      case "tool_calls":
      case "function_call":
        stopReason = "tool_use";
        break;
      case "length":
        stopReason = "max_tokens";
        break;
      case "content_filter":
        stopReason = "refusal";
        break;
      default:
        stopReason = content.some((b) => b.type === "tool_use") ? "tool_use" : "end_turn";
    }

    return { content, stopReason };
  }
}

function convertMessage(m: ChatMessage): OpenAIMessage[] {
  if (typeof m.content === "string") {
    return [{ role: m.role, content: m.content }];
  }

  if (m.role === "assistant") {
    const texts = m.content
      .filter((b): b is ContentBlock & { type: "text" } => b.type === "text")
      .map((b) => b.text)
      .join("\n");
    const toolUses = m.content.filter((b): b is ToolUseBlock => b.type === "tool_use");
    const out: OpenAIMessage = { role: "assistant", content: texts || null };
    if (toolUses.length) {
      out.tool_calls = toolUses.map((tu) => ({
        id: tu.id,
        type: "function" as const,
        function: { name: tu.name, arguments: JSON.stringify(tu.input) },
      }));
    }
    return [out];
  }

  // user message: may be plain blocks or tool results
  const results = m.content.filter((b): b is ToolResultBlock => b.type === "tool_result");
  if (results.length) {
    return results.map((r) => ({
      role: "tool" as const,
      tool_call_id: r.tool_use_id,
      content: r.is_error ? `ERROR: ${r.content}` : r.content,
    }));
  }
  const text = m.content
    .filter((b): b is ContentBlock & { type: "text" } => b.type === "text")
    .map((b) => b.text)
    .join("\n");
  return [{ role: "user", content: text }];
}
