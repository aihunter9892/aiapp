import type { Config } from "../config.js";
import {
  textOf,
  toolUsesOf,
  type ChatMessage,
  type LlmClient,
  type ToolDefinition,
  type ToolResultBlock,
} from "../llm/index.js";
import { buildSystemPrompt } from "./prompts.js";
import { buildTools, executeTool, type ToolContext } from "./tools.js";
import { logger } from "../logger.js";

const MAX_TOOL_ITERATIONS = 12;
const MAX_HISTORY_TURNS = 30;

/**
 * The conversational agent behind the self-chat. Maintains a rolling
 * in-memory conversation and runs a provider-agnostic tool-use loop —
 * works with whichever LLM API and model the user configured.
 */
export class Agent {
  private history: ChatMessage[] = [];
  private system: string;
  private tools: ToolDefinition[];
  private busy: Promise<void> = Promise.resolve();

  constructor(
    private cfg: Config,
    private llm: LlmClient,
    private ctx: ToolContext
  ) {
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
      const response = await this.llm.chat({
        system: this.system,
        messages: this.history,
        tools: this.tools,
        maxTokens: 4096,
      });

      this.history.push({ role: "assistant", content: response.content });

      const toolUses = toolUsesOf(response);
      const textBlocks = textOf(response);

      if (response.stopReason === "refusal") {
        finalText = "I can't help with that one.";
        break;
      }

      if (toolUses.length === 0) {
        finalText = textBlocks || "(done)";
        break;
      }

      const results: ToolResultBlock[] = [];
      for (const tu of toolUses) {
        try {
          const output = await executeTool(this.ctx, tu.name, tu.input);
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
