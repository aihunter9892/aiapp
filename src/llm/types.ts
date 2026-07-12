/**
 * Provider-agnostic LLM interface. Talon's brain works against this contract,
 * so any provider (Anthropic, OpenAI, or anything OpenAI-compatible: Groq,
 * Ollama, OpenRouter, Together, DeepSeek, Gemini's compat endpoint, …) can
 * power the assistant. Pick the provider AND the model in .env.
 */

export interface ToolDefinition {
  name: string;
  description: string;
  input_schema: Record<string, unknown>;
}

export interface TextBlock {
  type: "text";
  text: string;
}

export interface ToolUseBlock {
  type: "tool_use";
  id: string;
  name: string;
  input: Record<string, unknown>;
}

export type ContentBlock = TextBlock | ToolUseBlock;

export interface ToolResultBlock {
  type: "tool_result";
  tool_use_id: string;
  content: string;
  is_error?: boolean;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string | Array<ContentBlock | ToolResultBlock>;
}

export interface ChatRequest {
  system: string;
  messages: ChatMessage[];
  tools?: ToolDefinition[];
  maxTokens: number;
  /** When set, the provider is asked to return JSON matching this schema. */
  jsonSchema?: Record<string, unknown>;
}

export interface ChatResponse {
  content: ContentBlock[];
  stopReason: "end_turn" | "tool_use" | "max_tokens" | "refusal" | "other";
}

export interface LlmClient {
  readonly provider: string;
  readonly model: string;
  chat(req: ChatRequest): Promise<ChatResponse>;
}

export function textOf(response: ChatResponse): string {
  return response.content
    .filter((b): b is TextBlock => b.type === "text")
    .map((b) => b.text)
    .join("\n")
    .trim();
}

export function toolUsesOf(response: ChatResponse): ToolUseBlock[] {
  return response.content.filter((b): b is ToolUseBlock => b.type === "tool_use");
}
