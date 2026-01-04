/**
 * LLM Request Types
 * Based on RAGFlow LLM API request structures
 */

// Add LLM request body
export interface IAddLlmRequestBody {
  llm_factory: string; // e.g., 'Ollama', 'OpenAI'
  llm_name: string; // Model name
  model_type: string; // chat|embedding|speech2text|image2text|rerank|tts
  api_base?: string; // API base URL
  api_key: string | Record<string, any>; // API key or config object
  max_tokens: number; // Maximum tokens
}

// Delete LLM request body
export interface IDeleteLlmRequestBody {
  llm_factory: string;
  llm_name?: string;
}

// API Key saving params
export interface IApiKeySavingParams {
  llm_factory: string;
  api_key: string;
  llm_name?: string;
  model_type?: string;
  base_url?: string;
  group_id?: string; // For MiniMax
}

// System model setting saving params
export interface ISystemModelSettingSavingParams {
  tenant_id: string;
  name?: string;
  llm_id?: string;
  embd_id?: string;
  img2txt_id?: string;
  asr_id?: string;
  rerank_id?: string;
  tts_id?: string;
}

// API Key post body for modal
export interface ApiKeyPostBody {
  api_key: string;
  base_url: string;
  group_id?: string;
}

// LLM list query params
export interface ILlmListParams {
  model_type?: string;
}
