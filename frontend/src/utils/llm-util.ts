/**
 * LLM Utility Functions
 * Based on RAGFlow LLM utilities
 */

import { IThirdOAIModel } from '@/interfaces/database/llm';

/**
 * Get LLM icon name from factory ID and model name
 */
export const getLLMIconName = (fid: string, llm_name: string): string => {
  if (fid === 'FastEmbed') {
    return llm_name.split('/').at(0) ?? '';
  }
  return fid;
};

/**
 * Parse LLM ID to get model name and factory ID
 * Format: llmName@factoryId
 */
export const getLlmNameAndFIdByLlmId = (llmId?: string): {
  fId: string | undefined;
  llmName: string | undefined;
} => {
  const [llmName, fId] = llmId?.split('@') || [];
  return { fId, llmName };
};

/**
 * Get real model name from full model name
 * The names returned by the interface are similar to "deepseek-r1___OpenAI-API"
 */
export function getRealModelName(llmName: string): string {
  return llmName.split('__').at(0) ?? '';
}

/**
 * Build LLM UUID from model data
 * Format: llmName@factoryId
 */
export function buildLlmUuid(llm: IThirdOAIModel): string {
  return `${llm.llm_name}@${llm.fid}`;
}

/**
 * Sort tags based on predefined order
 */
export const sortTags = (tags: string): string[] => {
  const orderMap: Record<string, number> = {
    'LLM': 1,
    'TEXT EMBEDDING': 2,
    'TEXT RE-RANK': 3,
    'TTS': 4,
    'SPEECH2TEXT': 5,
    'IMAGE2TEXT': 6,
    'OCR': 7,
    'MODERATION': 8,
  };

  return tags
    .split(',')
    .map((tag) => tag.trim())
    .sort((a, b) => (orderMap[a] || 999) - (orderMap[b] || 999));
};

/**
 * Check if a factory is a local LLM provider
 */
export const isLocalLlmFactory = (factory: string): boolean => {
  const localProviders = [
    'Ollama',
    'Xinference',
    'LocalAI',
    'LM-Studio',
    'ModelScope',
    'HuggingFace',
    'GPUStack',
    'VLLM',
    'OpenAI-API-Compatible',
    'OpenRouter',
    'TogetherAI',
    'Replicate',
    'PPIO',
    'SILICONFLOW',
    'PerfXCloud',
    'NovitaAI',
    'Upstage',
    'LeptonAI',
    'DeepInfra',
    '302.AI',
    'GiteeAI',
    'TokenPony',
    'CometAPI',
    'DeerAPI',
    'Jiekou.AI',
    'Builtin',
  ];
  return localProviders.includes(factory);
};
