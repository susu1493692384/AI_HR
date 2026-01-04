# 模型配置页面前端实现文档

## 项目概述

本文档描述了参考 RAGFlow 前端设计实现的模型配置页面功能。该页面用于管理和配置各种 LLM（大语言模型）提供商，支持 60+ 个国内外主流 AI 模型服务。

## 功能特性

### 1. 系统模型设置
- 配置不同场景下的默认模型
- 支持的模型类型：
  - 聊天模型（LLM）
  - 嵌入模型（Embedding）
  - 图像理解模型（Image2Text）
  - 语音转文本模型（Speech2Text）
  - 重排序模型（Rerank）
  - 文本转语音模型（TTS）

### 2. 已添加模型管理
- 展示已配置的模型提供商
- 支持展开/收起查看具体模型列表
- 模型启用/禁用切换
- 模型配置编辑
- 提供商删除功能

### 3. 可添加模型列表
- 展示所有可用的模型提供商
- 搜索功能：按提供商名称搜索
- 标签筛选：按模型类型筛选
- 快速跳转到 API Key 获取页面

### 4. 模型配置弹窗
- **通用 API Key 弹窗**：适用于大多数云服务提供商
- **本地 LLM 弹窗**：适用于 Ollama、Xinference 等本地部署的模型

## 目录结构

```
frontend/src/
├── constants/
│   └── llm.ts                          # LLM 常量定义
├── interfaces/
│   ├── database/
│   │   └── llm.ts                      # 数据库类型定义
│   └── request/
│       └── llm.ts                      # API 请求类型定义
├── services/
│   └── llm/
│       └── index.ts                    # LLM API 服务层
├── hooks/
│   └── llm/
│       └── use-llm-request.tsx         # React Query Hooks
├── utils/
│   └── llm-util.ts                     # LLM 工具函数
├── components/
│   └── llm/
│       ├── LlmIcon.tsx                 # 厂商标识组件
│       └── index.ts
├── lib/
│   └── utils.ts                        # 通用工具函数
└── pages/
    └── UserSettings/
        ├── index.tsx                   # 用户设置主页面
        └── ModelSettings/              # 模型配置模块
            ├── index.tsx               # 主入口组件
            ├── hooks.tsx               # 页面级 Hooks
            ├── components/             # 子组件
            │   ├── SystemSetting.tsx   # 系统模型设置
            │   ├── UsedModel.tsx       # 已添加模型列表
            │   └── AvailableModels.tsx # 可添加模型列表
            └── modal/                  # 配置弹窗组件
                ├── ApiKeyModal.tsx     # API Key 配置弹窗
                └── OllamaModal.tsx     # 本地 LLM 配置弹窗
```

## 文件说明

### 1. 常量定义 (`constants/llm.ts`)

定义了所有支持的 LLM 提供商枚举和相关配置：

```typescript
// LLM 提供商枚举
export enum LLMFactory {
  OpenAI = 'OpenAI',
  Anthropic = 'Anthropic',
  DeepSeek = 'DeepSeek',
  // ... 60+ 个提供商
}

// 图标名称映射
export const IconMap: Record<LLMFactory, string> = {...}

// API Key 获取页面映射
export const APIMapUrl: Partial<Record<LLMFactory, string>> = {...}
```

### 2. 类型定义 (`interfaces/`)

**数据库类型** (`interfaces/database/llm.ts`):
```typescript
export interface IThirdOAIModel {
  available: boolean;
  fid: string;
  llm_name: string;
  model_type: string;
  // ...
}

export interface IFactory {
  name: string;
  logo: string;
  tags: string;
  // ...
}
```

**请求类型** (`interfaces/request/llm.ts`):
```typescript
export interface IAddLlmRequestBody {
  llm_factory: string;
  llm_name: string;
  model_type: string;
  api_base?: string;
  api_key: string | Record<string, any>;
  max_tokens: number;
}
```

### 3. API 服务层 (`services/llm/index.ts`)

封装了所有 LLM 相关的 API 调用：

```typescript
// 获取所有可用模型
export const fetchLlmList = async (params?: ILlmListParams)

// 获取已配置的模型
export const fetchMyLlm = async (params?: { include_details?: boolean })

// 设置 API Key
export const setApiKey = async (params: IApiKeySavingParams)

// 添加新模型
export const addLlm = async (params: IAddLlmRequestBody)

// 删除模型
export const deleteLlm = async (params: IDeleteLlmRequestBody)

// 启用/禁用模型
export const enableLlm = async (params: IDeleteLlmRequestBody & { status?: 0 | 1 })
```

### 4. React Query Hooks (`hooks/llm/use-llm-request.tsx`)

提供数据获取和状态管理的 Hooks：

```typescript
// 获取可用模型列表
export const useFetchLlmList = (modelType?: string)

// 获取已配置模型
export const useFetchMyLlmList = ()

// 获取工厂列表
export const useFetchLlmFactoryList = ()

// 保存 API Key
export const useSaveApiKey = ()

// 添加模型
export const useAddLlm = ()

// 删除模型
export const useDeleteLlm = ()

// 启用/禁用模型
export const useEnableLlm = ()
```

### 5. 页面组件

#### 主入口组件 (`ModelSettings/index.tsx`)

```typescript
const ModelSettings: React.FC = () => {
  // 系统设置
  const { saveSystemModelSettingLoading, onSystemSettingSavingOk } = useSubmitSystemModelSetting();

  // API Key 弹窗
  const { apiKeyVisible, hideApiKeyModal, showApiKeyModal, ... } = useSubmitApiKey();

  // 本地 LLM 弹窗
  const { llmAddingVisible, hideLlmAddingModal, showLlmAddingModal, ... } = useSubmitOllama();

  // 处理添加模型
  const handleAddModel = (llmFactory: string) => {
    if (isLocalLlmFactory(llmFactory)) {
      showLlmAddingModal(llmFactory);
    } else {
      showApiKeyModal({ llm_factory: llmFactory });
    }
  };

  return (
    <div>
      <SystemSetting />
      <UsedModel handleAddModel={handleAddModel} />
      <AvailableModels handleAddModel={handleAddModel} />
      <ApiKeyModal />
      <OllamaModal />
    </div>
  );
};
```

#### 系统设置组件 (`components/SystemSetting.tsx`)

配置系统默认使用的模型：

```typescript
const SystemSetting: React.FC<ISystemSettingProps> = ({ onOk, loading }) => {
  const modelTypes = [
    { id: 'llm_id', label: '聊天模型', required: true },
    { id: 'embd_id', label: '嵌入模型' },
    { id: 'img2txt_id', label: '图像理解模型' },
    { id: 'asr_id', label: '语音转文本模型' },
    { id: 'rerank_id', label: '重排序模型' },
    { id: 'tts_id', label: '文本转语音模型' },
  ];

  return (
    <div>
      {modelTypes.map(item => (
        <SettingItem key={item.id} {...item} />
      ))}
    </div>
  );
};
```

#### 已添加模型组件 (`components/UsedModel.tsx`)

展示和管理已配置的模型：

```typescript
const UsedModel: React.FC<IUsedModelProps> = ({ myLlmList, handleAddModel }) => {
  return (
    <div>
      <div>已添加的模型</div>
      {myLlmList.map(llm => (
        <ModelProviderCard
          key={llm.name}
          item={llm}
          clickApiKey={handleAddModel}
        />
      ))}
    </div>
  );
};
```

#### 可添加模型组件 (`components/AvailableModels.tsx`)

展示可用的模型提供商：

```typescript
const AvailableModels: React.FC<IAvailableModelsProps> = ({ factoryList, handleAddModel }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTag, setSelectedTag] = useState<string | null>(null);

  const filteredModels = useMemo(() => {
    return factoryList.filter(model => {
      const matchesSearch = model.name.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesTag = selectedTag === null || model.tags.includes(selectedTag);
      return matchesSearch && matchesTag;
    });
  }, [factoryList, searchTerm, selectedTag]);

  return (
    <div>
      <SearchInput value={searchTerm} onChange={setSearchTerm} />
      <TagFilter tags={allTags} selected={selectedTag} onSelect={setSelectedTag} />
      <ModelList models={filteredModels} onAdd={handleAddModel} />
    </div>
  );
};
```

### 6. 配置弹窗组件

#### API Key 弹窗 (`modal/ApiKeyModal.tsx`)

适用于大多数云服务提供商：

```typescript
const ApiKeyModal: React.FC<IApiKeyModalProps> = ({
  visible, hideModal, llmFactory, loading, onOk
}) => {
  return (
    <Modal isOpen={visible} onClose={hideModal} title={llmFactory}>
      <input name="api_key" placeholder="请输入 API Key" required />

      {/* 支持自定义 Base URL 的提供商 */}
      {(showBaseUrl) && (
        <input name="base_url" placeholder="https://api.openai.com/v1" />
      )}

      {/* MiniMax 特有的 Group ID */}
      {showGroupId && (
        <input name="group_id" placeholder="请输入 Group ID" />
      )}
    </Modal>
  );
};
```

#### 本地 LLM 弹窗 (`modal/OllamaModal.tsx`)

适用于 Ollama、Xinference 等本地部署的模型：

```typescript
const OllamaModal: React.FC<IOllamaModalProps> = ({
  visible, hideModal, llmFactory, onOk
}) => {
  return (
    <Modal isOpen={visible} onClose={hideModal} title={llmFactory}>
      <select name="model_type">
        <option value="chat">Chat</option>
        <option value="embedding">Embedding</option>
        <option value="image2text">Image2Text</option>
      </select>

      <input name="llm_name" placeholder="例如: llama2, qwen, mistral" />
      <input name="api_base" placeholder="http://localhost:11434" />
      <input name="api_key" placeholder="如果需要认证请填写（可选）" />
      <input type="number" name="max_tokens" defaultValue={8192} />

      {model_type === 'chat' && (
        <input type="checkbox" name="vision" />
      )}
    </Modal>
  );
};
```

### 7. 厂商图标组件 (`components/llm/LlmIcon.tsx`)

```typescript
const LlmIcon: React.FC<ILlmIconProps> = ({ name, size = 'medium' }) => {
  const iconName = IconMap[name as LLMFactory] || name.toLowerCase();
  const IconComponent = ProviderIcons[iconName];

  if (IconComponent) {
    return <IconComponent width={computedSize} height={computedSize} />;
  }

  // 默认回退图标
  return <DefaultIcon name={name} size={computedSize} />;
};
```

## 支持的模型提供商

### 国际厂商
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude 系列)
- Google (Gemini)
- Azure OpenAI
- AWS Bedrock
- Cohere
- Mistral AI
- Groq
- Together AI
- Replicate
- Perplexity
- Lepton AI
- Novita AI
- Upstage
- Voyage AI
- Jina
- NVIDIA
- xAI (Grok)

### 中国厂商
- 阿里巴巴 (通义千问)
- 百度 (文心一言)
- DeepSeek
- 智谱 AI (ChatGLM)
- Moonshot (月之暗面)
- 百川智能
- MiniMax
- 腾讯 (混元、云)
- 讯飞 (星火)
- 360
- 零一万物

### 本地/开源
- Ollama
- Xinference
- LocalAI
- LM Studio
- ModelScope (魔搭)
- Hugging Face
- GPUStack
- VLLM
- OpenAI API Compatible
- OpenRouter
- PPIO
- SILICONFLOW
- Gitee AI
- TokenPony

### 专用模型
- Fish Audio (语音)
- MinerU (OCR)
- BAAI (智源)
- YouDao (有道)

## API 接口说明

### 后端需要实现的接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/llm_list` | 获取所有可用模型列表 |
| GET | `/my_llm` | 获取已配置的模型 |
| GET | `/factories_list` | 获取所有提供商信息 |
| POST | `/set_api_key` | 设置提供商 API Key |
| POST | `/add_llm` | 添加新模型 |
| POST | `/delete_llm` | 删除模型 |
| POST | `/enable_llm` | 启用/禁用模型 |
| POST | `/delete_factory` | 删除提供商 |
| GET | `/tenant_info` | 获取系统设置 |
| POST | `/set_tenant_info` | 保存系统设置 |

### 接口响应格式

```typescript
// 成功响应
{
  "code": 0,
  "data": {...},
  "message": "success"
}

// 错误响应
{
  "code": 1,
  "data": null,
  "message": "error message"
}
```

## 依赖项

确保 `package.json` 包含以下依赖：

```json
{
  "dependencies": {
    "@headlessui/react": "^2.2.9",
    "@tanstack/react-query": "^5.90.12",
    "axios": "^1.13.2",
    "clsx": "^2.1.1",
    "lucide-react": "^0.562.0",
    "react": "^19.2.3",
    "react-dom": "^19.2.3",
    "react-router-dom": "^7.11.0",
    "tailwind-merge": "^3.4.0",
    "tailwindcss": "^4.1.18"
  }
}
```

## 使用说明

### 1. 访问模型配置页面

1. 登录系统
2. 进入"个人设置"
3. 点击"模型配置"标签页

### 2. 添加新模型提供商

**方法一：云服务提供商**
1. 在右侧"可添加的模型"列表中找到提供商
2. 点击提供商卡片上的"添加"按钮
3. 在弹出的对话框中输入 API Key
4. （可选）填写自定义 Base URL
5. 点击"保存"

**方法二：本地模型**
1. 在右侧列表中找到本地模型提供商（如 Ollama）
2. 点击"添加"按钮
3. 填写模型配置：
   - 选择模型类型
   - 输入模型名称
   - 输入 API 地址
   - （可选）输入 API Key
   - 设置最大 Tokens
4. 点击"保存"

### 3. 管理已添加的模型

- **展开/收起模型列表**：点击提供商卡片上的"展开模型"/"收起模型"按钮
- **启用/禁用模型**：点击模型右侧的开关
- **编辑模型配置**：点击模型右侧的编辑图标（仅本地模型）
- **删除提供商**：点击提供商卡片右上角的删除图标

### 4. 配置系统默认模型

在页面左侧"系统模型设置"区域：
1. 选择聊天模型
2. 选择嵌入模型
3. 选择图像理解模型
4. 选择语音转文本模型
5. 选择重排序模型
6. 选择文本转语音模型

配置会自动保存。

## 样式说明

页面使用 Tailwind CSS 进行样式设计，主要设计特点：

- **响应式布局**：支持桌面端和移动端
- **卡片式设计**：每个模块使用卡片容器
- **悬停效果**：鼠标悬停时显示交互反馈
- **颜色系统**：
  - 主色：蓝色 (bg-blue-500)
  - 成功：绿色 (bg-green-500)
  - 警告：橙色 (bg-orange-500)
  - 错误：红色 (bg-red-500)

## 注意事项

1. **后端集成**：当前实现为纯前端，需要与后端 API 对接
2. **类型安全**：所有接口都有 TypeScript 类型定义
3. **状态管理**：使用 React Query 进行数据缓存和状态管理
4. **错误处理**：需要添加全局错误处理和用户提示
5. **国际化**：当前使用中文文本，可扩展支持多语言

## 未来扩展

1. 添加更多专用配置弹窗（Bedrock、Azure 等）
2. 支持模型参数微调（temperature、top_p 等）
3. 添加模型使用统计和费用预估
4. 支持模型测试对话功能
5. 添加模型健康检查
6. 支持批量导入/导出配置

## 参考文档

- [RAGFlow GitHub](https://github.com/infiniflow/ragflow)
- [React Query 文档](https://tanstack.com/query/latest)
- [Tailwind CSS 文档](https://tailwindcss.com/docs)
