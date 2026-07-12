import Anthropic from "@anthropic-ai/sdk";
import type { Config } from "../config.js";
import { buildSystemPrompt } from "./prompts.js";
import { buildTools, executeTool, type ToolContext } from "./tools.js";
import { logger } from "../logger.js";

const MAX_TOOL_ITERATIONS = 12;
const MAX_HISTORY_TURNS = 30;

/**
 * The conversational agent behind the self-chat. Maintains a rolling
 * in-memory conversation and runs a manual tool-use loop against Claude.
 */
export class Agent {
  private client: Anthropic;
  private history: Anthropic.MessageParam[] = [];
  private system: string;
  private tools: Anthropic.Tool[];
  private busy: Promise<void> = Promise.resolve();

  constructor(
    private cfg: Config,
    private ctx: ToolContext
  ) {
    this.client = new Anthropic({ apiKey: cfg.anthropicApiKey });
    const calendarEnabled = Boolean(ctx.calendar);
    this.system = buildSystemPrompt(cfg, calendarEnabled);
    this.tools = buildTools(calendarEnabled);
  }

  /** Serialize handling so rapid-fire messages don't interleave tool loops. */
  handle(userText: string): Promise<string> {
    const run = this.busy.then(() => this.runTurn(userText));
    this.busy = run.then(
      () => undefined,
      () => undefined
    );
    return run;
  }

  private async runTurn(userText: string): Promise<string> {
    const now = new Date();
    const stamped = `[current time: ${now.toISOString()} | ${now.toLocaleString("en-GB", { timeZone: this.cfg.timezone })} ${this.cfg.timezone}]\n${userText}`;

    this.history.push({ role: "user", content: stamped });
    this.trimHistory();

    let finalText = "";

    for (let i = 0; i < MAX_TOOL_ITERATIONS; i++) {
      const response = await this.client.messages.create({
        model: this.cfg.model,
        max_tokens: 4096,
        thinking: { type: "adaptive" },
        system: [{ type: "text", text: this.system, cache_control: { type: "ephemeral" } }],
        tools: this.tools,
        messages: this.history,
      });

      this.history.push({ role: "assistant", content: response.content });

      const toolUses = response.content.filter(
        (b): b is Anthropic.ToolUseBlock => b.type === "tool_use"
      );
      const textBlocks = response.content
        .filter((b): b is Anthropic.TextBlock => b.type === "text")
        .map((b) => b.text)
        .join("\n")
        .trim();

      if (response.stop_reason === "refusal") {
        finalText = "I can't help with that one.";
        break;
      }

      if (toolUses.length === 0) {
        finalText = textBlocks || "(done)";
        break;
      }

      const results: Anthropic.ToolResultBlockParam[] = [];
      for (const tu of toolUses) {
        try {
          const output = await executeTool(this.ctx, tu.name, tu.input as Record<string, unknown>);
          results.push({ type: "tool_result", tool_use_id: tu.id, content: output });
        } catch (err) {
          const message = err instanceof Error ? err.message : String(err);
          logger.error({ tool: tu.name, err: message }, "tool failed");
          results.push({
            type: "tool_result",
            tool_use_id: tu.id,
            content: `Error: ${message}`,
            is_error: true,
          });
        }
      }
      this.history.push({ role: "user", content: results });

      if (i === MAX_TOOL_ITERATIONS - 1) {
        finalText = textBlocks || "I hit my step limit on that one — ask me to continue if needed.";
      }
    }

    return finalText;
  }

  /**
   * Keep the rolling window bounded. Trimming must never strand a tool_use
   * without its tool_result, so we only cut at user-text boundaries.
   */
  private trimHistory() {
    if (this.history.length <= MAX_HISTORY_TURNS * 2) return;
    // find the first plain-text user message after the overflow point
    let cut = this.history.length - MAX_HISTORY_TURNS * 2;
    while (cut < this.history.length) {
      const m = this.history[cut];
      if (m.role === "user" && typeof m.content === "string") break;
      cut++;
    }
    if (cut > 0 && cut < this.history.length) {
      this.history = this.history.slice(cut);
    }
  }
}
