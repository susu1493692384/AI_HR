/**
 * LLM Database Types
 * Based on RAGFlow LLM data structures
 */

// Third-party OAI model interface
export interface IThirdOAIModel {
  available: boolean;
  create_date: string;
  create_time: number;
  fid: string; // Factory ID
  id: number;
  llm_name: string;
  max_tokens: number;
  model_type: string;
  status: string; // '0' or '1'
  tags: string;
  update_date: string;
  update_time: number;
  tenant_id?: string;
  tenant_name?: string;
  is_tools: boolean;
}

// Collection of third-party OAI models keyed by factory name
export type IThirdOAIModelCollection = Record<string, IThirdOAIModel[]>;

// Factory interface (LLM provider)
export interface IFactory {
  create_date: string;
  create_time: number;
  logo: string;
  name: string;
  status: string;
  tags: string;
  update_date: string;
  update_time: number;
}

// Individual LLM item
export interface ILlm {
  name: string;
  type: string;
  status: '0' | '1';
  used_token: number;
}

// My LLM value (factory with its models)
export interface IMyLlmValue {
  llm: ILlm[];
  tags: string;
}

// LLM item with factory information
export interface ILlmItem {
  name: string; // Factory name
  logo: string;
  llm: ILlm[];
  tags: string;
}

// System tenant info for model settings
export interface ITenantInfo {
  tenant_id: string;
  name?: string;
  llm_id?: string;
  embd_id?: string;
  img2txt_id?: string;
  asr_id?: string;
  rerank_id?: string;
  tts_id?: string;
}

// API response wrapper
export interface IResponse<T = any> {
  code: number;
  data: T;
  message?: string;
}
