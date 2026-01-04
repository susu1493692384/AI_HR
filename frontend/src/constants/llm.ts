/**
 * LLM Provider Factory Constants
 * Based on RAGFlow LLM configuration
 */

export enum LLMFactory {
  // OpenAI Family
  OpenAI = 'OpenAI',
  AzureOpenAI = 'Azure-OpenAI',
  OpenAiAPICompatible = 'OpenAI-API-Compatible',

  // Chinese Providers
  TongYiQianWen = 'Tongyi-Qianwen',
  ZhipuAI = 'ZHIPU-AI',
  WenXinYiYan = '文心一言',
  DeepSeek = 'DeepSeek',
  Moonshot = 'Moonshot',
  BaiChuan = 'BaiChuan',
  MiniMax = 'MiniMax',
  StepFun = 'StepFun',
  TencentHunYuan = 'Tencent Hunyuan',
  TencentCloud = 'Tencent Cloud',
  XunFeiSpark = 'XunFei Spark',
  BaiduYiYan = 'BaiduYiyan',

  // International Providers
  Anthropic = 'Anthropic',
  Cohere = 'Cohere',
  Mistral = 'Mistral',
  Groq = 'Groq',
  Perplexity = 'Perplexity',
  TogetherAI = 'TogetherAI',
  LeptonAI = 'LeptonAI',
  NovitaAI = 'NovitaAI',
  Upstage = 'Upstage',

  // Cloud Platforms
  GoogleCloud = 'Google Cloud',
  Gemini = 'Gemini',
  Bedrock = 'Bedrock',
  VolcEngine = 'VolcEngine',
  NVIDIA = 'NVIDIA',

  // Open Source / Local
  Ollama = 'Ollama',
  Xinference = 'Xinference',
  LocalAI = 'LocalAI',
  LMStudio = 'LM-Studio',
  ModelScope = 'ModelScope',
  HuggingFace = 'HuggingFace',
  GPUStack = 'GPUStack',
  VLLM = 'VLLM',

  // Routing / Aggregation
  OpenRouter = 'OpenRouter',
  Replicate = 'Replicate',
  PPIO = 'PPIO',
  SILICONFLOW = 'SILICONFLOW',
  PerfXCloud = 'PerfXCloud',

  // Specialized
  FishAudio = 'Fish Audio',
  Jina = 'Jina',
  VoyageAI = 'Voyage AI',
  BAAI = 'BAAI',
  NomicAI = 'nomic-ai',
  SentenceTransformers = 'sentence-transformers',

  // Other
  GiteeAI = 'GiteeAI',
  Ai302 = '302.AI',
  DeepInfra = 'DeepInfra',
  Grok = 'Grok',
  XAI = 'xAI',
  TokenPony = 'TokenPony',
  Meituan = 'Meituan',
  Longcat = 'LongCat',
  CometAPI = 'CometAPI',
  DeerAPI = 'DeerAPI',
  JiekouAI = 'Jiekou.AI',
  Builtin = 'Builtin',
  MinerU = 'MinerU',
  YouDao = 'Youdao',
}

// Icon name mapping for each LLM provider
export const IconMap: Record<LLMFactory, string> = {
  [LLMFactory.TongYiQianWen]: 'tongyi-qianwen',
  [LLMFactory.Moonshot]: 'moonshot',
  [LLMFactory.OpenAI]: 'openai',
  [LLMFactory.ZhipuAI]: 'zhipu',
  [LLMFactory.WenXinYiYan]: 'wenxin',
  [LLMFactory.Ollama]: 'ollama',
  [LLMFactory.Xinference]: 'xinference',
  [LLMFactory.ModelScope]: 'modelscope',
  [LLMFactory.DeepSeek]: 'deepseek',
  [LLMFactory.VolcEngine]: 'volcengine',
  [LLMFactory.BaiChuan]: 'baichuan',
  [LLMFactory.Jina]: 'jina',
  [LLMFactory.MiniMax]: 'MiniMax',
  [LLMFactory.Mistral]: 'mistral',
  [LLMFactory.AzureOpenAI]: 'azure',
  [LLMFactory.Bedrock]: 'bedrock',
  [LLMFactory.Gemini]: 'gemini',
  [LLMFactory.Groq]: 'groq',
  [LLMFactory.OpenRouter]: 'open-router',
  [LLMFactory.LocalAI]: 'local-ai',
  [LLMFactory.StepFun]: 'stepfun',
  [LLMFactory.NVIDIA]: 'nvidia',
  [LLMFactory.LMStudio]: 'lm-studio',
  [LLMFactory.OpenAiAPICompatible]: 'openai-api',
  [LLMFactory.Cohere]: 'cohere',
  [LLMFactory.LeptonAI]: 'lepton',
  [LLMFactory.TogetherAI]: 'together',
  [LLMFactory.PerfXCloud]: 'perfx-cloud',
  [LLMFactory.Upstage]: 'upstage',
  [LLMFactory.NovitaAI]: 'novita-ai',
  [LLMFactory.SILICONFLOW]: 'siliconflow',
  [LLMFactory.PPIO]: 'ppio',
  [LLMFactory.Replicate]: 'replicate',
  [LLMFactory.TencentHunYuan]: 'hunyuan',
  [LLMFactory.XunFeiSpark]: 'spark',
  [LLMFactory.BaiduYiYan]: 'wenxinyiyan',
  [LLMFactory.FishAudio]: 'fish-audio',
  [LLMFactory.TencentCloud]: 'tencent-cloud',
  [LLMFactory.Anthropic]: 'anthropic',
  [LLMFactory.VoyageAI]: 'voyage',
  [LLMFactory.GoogleCloud]: 'google-cloud',
  [LLMFactory.HuggingFace]: 'huggingface',
  [LLMFactory.YouDao]: 'youdao',
  [LLMFactory.BAAI]: 'baai',
  [LLMFactory.NomicAI]: 'nomic-ai',
  [LLMFactory.JinaAI]: 'jina',
  [LLMFactory.SentenceTransformers]: 'sentence-transformers',
  [LLMFactory.GPUStack]: 'gpustack',
  [LLMFactory.VLLM]: 'vllm',
  [LLMFactory.GiteeAI]: 'gitee-ai',
  [LLMFactory.Ai302]: 'ai302',
  [LLMFactory.DeepInfra]: 'deepinfra',
  [LLMFactory.Grok]: 'grok',
  [LLMFactory.XAI]: 'xai',
  [LLMFactory.TokenPony]: 'tokenpony',
  [LLMFactory.Meituan]: 'longcat',
  [LLMFactory.Longcat]: 'longcat',
  [LLMFactory.CometAPI]: 'cometapi',
  [LLMFactory.DeerAPI]: 'deerapi',
  [LLMFactory.JiekouAI]: 'jiekouai',
  [LLMFactory.Builtin]: 'builtin',
  [LLMFactory.MinerU]: 'mineru',
  [LLMFactory.Perplexity]: 'perplexity',
  [LLMFactory.Gemini]: 'gemini',
};

// API Key URL mapping for each provider
export const APIMapUrl: Partial<Record<LLMFactory, string>> = {
  [LLMFactory.OpenAI]: 'https://platform.openai.com/api-keys',
  [LLMFactory.Anthropic]: 'https://console.anthropic.com/settings/keys',
  [LLMFactory.Gemini]: 'https://aistudio.google.com/app/apikey',
  [LLMFactory.DeepSeek]: 'https://platform.deepseek.com/api_keys',
  [LLMFactory.Moonshot]: 'https://platform.moonshot.cn/console/api-keys',
  [LLMFactory.TongYiQianWen]: 'https://dashscope.console.aliyun.com/apiKey',
  [LLMFactory.ZhipuAI]: 'https://open.bigmodel.cn/usercenter/apikeys',
  [LLMFactory.XAI]: 'https://x.ai/api/',
  [LLMFactory.HuggingFace]: 'https://huggingface.co/settings/tokens',
  [LLMFactory.Mistral]: 'https://console.mistral.ai/api-keys/',
  [LLMFactory.Cohere]: 'https://dashboard.cohere.com/api-keys',
  [LLMFactory.BaiduYiYan]: 'https://wenxin.baidu.com/user/key',
  [LLMFactory.Bedrock]: 'https://us-east-1.console.aws.amazon.com/iam/home?region=us-east-2#/users',
  [LLMFactory.AzureOpenAI]: 'https://portal.azure.com/#create/Microsoft.CognitiveServicesOpenAI',
  [LLMFactory.OpenRouter]: 'https://openrouter.ai/keys',
  [LLMFactory.XunFeiSpark]: 'https://console.xfyun.cn/services/cbm',
  [LLMFactory.MiniMax]: 'https://platform.minimaxi.com/user-center/basic-information',
  [LLMFactory.Groq]: 'https://console.groq.com/keys',
  [LLMFactory.NVIDIA]: 'https://build.nvidia.com/settings/api-keys',
  [LLMFactory.SILICONFLOW]: 'https://cloud.siliconflow.cn/account/ak',
  [LLMFactory.Replicate]: 'https://replicate.com/account/api-tokens',
  [LLMFactory.VolcEngine]: 'https://console.volcengine.com/ark',
  [LLMFactory.TencentHunYuan]: 'https://console.cloud.tencent.com/hunyuan/api-key',
  [LLMFactory.TencentCloud]: 'https://console.cloud.tencent.com/cam/capi',
  [LLMFactory.ModelScope]: 'https://modelscope.cn/my/myaccesstoken',
  [LLMFactory.GoogleCloud]: 'https://console.cloud.google.com/apis/credentials',
  [LLMFactory.FishAudio]: 'https://fish.audio/app/api-keys/',
  [LLMFactory.GiteeAI]: 'https://ai.gitee.com/hhxzgrjn/dashboard/settings/tokens',
  [LLMFactory.StepFun]: 'https://platform.stepfun.com/interface-key',
  [LLMFactory.BaiChuan]: 'https://platform.baichuan-ai.com/console/apikey',
  [LLMFactory.PPIO]: 'https://ppio.com/settings/key-management',
  [LLMFactory.VoyageAI]: 'https://dash.voyageai.com/api-keys',
  [LLMFactory.TogetherAI]: 'https://api.together.xyz/settings/api-keys',
  [LLMFactory.NovitaAI]: 'https://novita.ai/dashboard/key',
  [LLMFactory.Upstage]: 'https://console.upstage.ai/api-keys',
  [LLMFactory.CometAPI]: 'https://api.cometapi.com/console/token',
  [LLMFactory.Ai302]: 'https://302.ai/apis/list',
  [LLMFactory.DeerAPI]: 'https://api.deerapi.com/token',
  [LLMFactory.TokenPony]: 'https://www.tokenpony.cn/#/user/keys',
  [LLMFactory.DeepInfra]: 'https://deepinfra.com/dash/api_keys',
};

// Providers that support custom base URL
export const ModelsWithBaseUrl = [
  LLMFactory.OpenAI,
  LLMFactory.AzureOpenAI,
  LLMFactory.TongYiQianWen,
  LLMFactory.MiniMax,
];

// Providers with special modal implementations
export const SpecialModalProviders = [
  LLMFactory.Bedrock,
  LLMFactory.VolcEngine,
  LLMFactory.TencentHunYuan,
  LLMFactory.XunFeiSpark,
  LLMFactory.BaiduYiYan,
  LLMFactory.FishAudio,
  LLMFactory.TencentCloud,
  LLMFactory.GoogleCloud,
  LLMFactory.AzureOpenAI,
  LLMFactory.MinerU,
];

// Local LLM providers
export const LocalLlmProviders = [
  LLMFactory.Ollama,
  LLMFactory.Xinference,
  LLMFactory.LocalAI,
  LLMFactory.LMStudio,
  LLMFactory.ModelScope,
  LLMFactory.HuggingFace,
  LLMFactory.GPUStack,
  LLMFactory.VLLM,
  LLMFactory.OpenAiAPICompatible,
  LLMFactory.OpenRouter,
  LLMFactory.TogetherAI,
  LLMFactory.Replicate,
  LLMFactory.PPIO,
  LLMFactory.SILICONFLOW,
  LLMFactory.PerfXCloud,
  LLMFactory.NovitaAI,
  LLMFactory.Upstage,
  LLMFactory.LeptonAI,
  LLMFactory.DeepInfra,
  LLMFactory.Ai302,
  LLMFactory.GiteeAI,
  LLMFactory.TokenPony,
  LLMFactory.CometAPI,
  LLMFactory.DeerAPI,
  LLMFactory.JiekouAI,
  LLMFactory.Builtin,
];

export const isLocalLlmFactory = (factory: string): boolean => {
  return LocalLlmProviders.includes(factory as LLMFactory);
};

// Model type constants
export enum LlmModelType {
  Chat = 'chat',
  Embedding = 'embedding',
  Image2text = 'image2text',
  Speech2text = 'speech2text',
  Rerank = 'rerank',
  TTS = 'tts',
  Ocr = 'ocr',
}

// Model type display names
export const ModelTypeLabels: Record<LlmModelType, string> = {
  [LlmModelType.Chat]: 'LLM',
  [LlmModelType.Embedding]: 'TEXT EMBEDDING',
  [LlmModelType.Image2text]: 'IMAGE2TEXT',
  [LlmModelType.Speech2text]: 'SPEECH2TEXT',
  [LlmModelType.Rerank]: 'TEXT RE-RANK',
  [LlmModelType.TTS]: 'TTS',
  [LlmModelType.Ocr]: 'OCR',
};

// Model type order for sorting
export const ModelTypeOrder: Record<string, number> = {
  'LLM': 1,
  'TEXT EMBEDDING': 2,
  'TEXT RE-RANK': 3,
  'TTS': 4,
  'SPEECH2TEXT': 5,
  'IMAGE2TEXT': 6,
  'OCR': 7,
  'MODERATION': 8,
};

// Sort tags based on predefined order
export const sortTags = (tags: string): string[] => {
  return tags
    .split(',')
    .map((tag) => tag.trim())
    .sort((a, b) => (ModelTypeOrder[a] || 999) - (ModelTypeOrder[b] || 999));
};
