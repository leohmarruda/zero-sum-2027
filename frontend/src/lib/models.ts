/**
 * Suggested models for the seat model fields. Ids use OpenRouter form; the
 * backend sends OpenAI/Anthropic models straight to the vendor when the user
 * has supplied that vendor's API key (see LlmCallClient._route).
 * The fields stay free text, so any other litellm model id still works.
 */
export interface ModelOption {
  id: string;
  label: string;
}

export const MODEL_OPTIONS: readonly ModelOption[] = [
  { id: "openrouter/openai/gpt-4o-mini", label: "GPT-4o mini" },
  { id: "openrouter/anthropic/claude-haiku-5.5", label: "Claude Haiku 5.5" },
  { id: "openrouter/anthropic/claude-sonnet-5.5", label: "Claude Sonnet 5.5" },
  { id: "openrouter/openai/gpt-6-luna", label: "GPT6 Luna" },
  { id: "openrouter/deepseek/deepseek-v4.1-flash", label: "Deepseek 4.1 Flash" },
];
