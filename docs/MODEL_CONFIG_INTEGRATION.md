# 模型配置功能对接文档

## 功能概述

模型配置模块提供AI模型的管理，包括：
- AI模型列表展示
- 添加/编辑模型配置
- 测试模型连接
- 启用/禁用模型
- API密钥加密存储

## 后端接口（已实现）

后端已实现完整的AI模型管理接口：

| 方法 | 路径 | 描述 | 认证 |
|------|------|------|------|
| GET | `/ai-models/` | 获取模型列表 | 是 |
| POST | `/ai-models/` | 创建模型 | 是 |
| GET | `/ai-models/{id}` | 获取模型详情 | 是 |
| PUT | `/ai-models/{id}` | 更新模型 | 是 |
| DELETE | `/ai-models/{id}` | 删除模型 | 是 |
| POST | `/ai-models/{id}/test` | 测试模型 | 是 |
| PATCH | `/ai-models/{id}/toggle` | 切换激活状态 | 是 |
| GET | `/ai-models/providers` | 获取提供商列表 | 是 |

**后端文件：** `backend/app/api/v1/endpoints/ai_models.py`

## 数据模型

### AIModel

```typescript
interface AIModel {
  id: string;
  name: string;                    // 配置名称
  provider: string;                // 提供商 (openai/baidu/alibaba/google/anthropic)
  model_name: string;              // 模型名称
  api_key_encrypted: string;       // 加密的API密钥 (前端显示为***)
  base_url?: string;               // 自定义API地址
  model_type: string;              // 模型类型 (chat/embedding)
  is_active: boolean;              // 是否激活
  test_results?: TestResult[];     // 测试结果历史
  created_at: string;
  updated_at: string;
}

interface TestResult {
  success: boolean;
  response_time: number;           // 响应时间(ms)
  error_message?: string;
  test_response?: string;
  tested_at: string;
}
```

### 创建/更新模型

```typescript
interface AIModelCreate {
  name: string;
  provider: string;
  model_name: string;
  api_key: string;                  // 明文，后端加密存储
  base_url?: string;
  model_type: string;
  is_active?: boolean;
}

interface AIModelUpdate {
  name?: string;
  model_name?: string;
  api_key?: string;
  base_url?: string;
  is_active?: boolean;
}
```

### 测试模型

```typescript
interface ModelTestRequest {
  test_prompt?: string;             // 测试提示词，默认为"你好"
}

interface ModelTestResponse {
  success: boolean;
  response_time: number;            // 响应时间(ms)
  error_message?: string;
  test_prompt: string;
  test_response?: string;
  tested_at: string;
}
```

### 提供商列表

```typescript
interface ModelProvider {
  value: string;                   // 提供商代码
  label: string;                   // 显示名称
  models: string[];                // 支持的模型列表
}

// 返回的提供商列表
const providers: ModelProvider[] = [
  {
    value: "openai",
    label: "OpenAI",
    models: ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]
  },
  {
    value: "baidu",
    label: "百度文心一言",
    models: ["ernie-bot", "ernie-bot-turbo"]
  },
  {
    value: "alibaba",
    label: "阿里通义千问",
    models: ["qwen-turbo", "qwen-plus", "qwen-max"]
  },
  {
    value: "google",
    label: "Google Gemini",
    models: ["gemini-pro", "gemini-pro-vision"]
  },
  {
    value: "anthropic",
    label: "Anthropic Claude",
    models: ["claude-3-sonnet", "claude-3-opus"]
  }
];
```

## 前端服务层

### 创建AI模型服务

创建 `frontend/src/services/aiModels.ts`：

```typescript
import { api } from './api';

export type Provider =
  | 'openai'
  | 'baidu'
  | 'alibaba'
  | 'google'
  | 'anthropic';

export type ModelType = 'chat' | 'embedding';

export interface AIModel {
  id: string;
  name: string;
  provider: Provider;
  model_name: string;
  api_key_encrypted: string;
  base_url?: string;
  model_type: ModelType;
  is_active: boolean;
  test_results?: TestResult[];
  created_at: string;
  updated_at: string;
}

export interface TestResult {
  success: boolean;
  response_time: number;
  error_message?: string;
  test_response?: string;
  tested_at: string;
}

export interface AIModelCreate {
  name: string;
  provider: Provider;
  model_name: string;
  api_key: string;
  base_url?: string;
  model_type: ModelType;
  is_active?: boolean;
}

export interface AIModelUpdate {
  name?: string;
  model_name?: string;
  api_key?: string;
  base_url?: string;
  is_active?: boolean;
}

export interface ModelTestRequest {
  test_prompt?: string;
}

export interface ModelTestResponse {
  success: boolean;
  response_time: number;
  error_message?: string;
  test_prompt: string;
  test_response?: string;
  tested_at: string;
}

export interface ModelProvider {
  value: Provider;
  label: string;
  models: string[];
}

// 获取模型列表
export const getAIModels = async (): Promise<AIModel[]> => {
  const response = await api.get('/ai-models/');
  return response.data;
};

// 获取模型详情
export const getAIModel = async (id: string): Promise<AIModel> => {
  const response = await api.get(`/ai-models/${id}`);
  return response.data;
};

// 创建模型
export const createAIModel = async (data: AIModelCreate): Promise<AIModel> => {
  const response = await api.post('/ai-models/', data);
  return response.data;
};

// 更新模型
export const updateAIModel = async (
  id: string,
  data: AIModelUpdate
): Promise<AIModel> => {
  const response = await api.put(`/ai-models/${id}`, data);
  return response.data;
};

// 删除模型
export const deleteAIModel = async (id: string) => {
  await api.delete(`/ai-models/${id}`);
};

// 测试模型
export const testAIModel = async (
  id: string,
  testPrompt?: string
): Promise<ModelTestResponse> => {
  const response = await api.post(`/ai-models/${id}/test`, {
    test_prompt: testPrompt || '你好，请介绍一下你自己'
  });
  return response.data;
};

// 切换激活状态
export const toggleAIModel = async (
  id: string,
  isActive: boolean
): Promise<AIModel> => {
  const response = await api.patch(`/ai-models/${id}/toggle`, null, {
    params: { is_active: isActive }
  });
  return response.data;
};

// 获取提供商列表
export const getProviders = async (): Promise<ModelProvider[]> => {
  const response = await api.get('/ai-models/providers');
  return response.data;
};
```

## 前端页面对接

### 模型配置页面

假设有一个模型配置管理页面，可以这样对接：

```typescript
import { useState, useEffect } from 'react';
import {
  getAIModels,
  createAIModel,
  updateAIModel,
  deleteAIModel,
  testAIModel,
  toggleAIModel,
  getProviders
} from '@/services/aiModels';

const ModelSettings = () => {
  const [models, setModels] = useState<AIModel[]>([]);
  const [providers, setProviders] = useState<ModelProvider[]>([]);
  const [loading, setLoading] = useState(false);
  const [testing, setTesting] = useState<string | null>(null);

  // 获取模型列表
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const [modelsData, providersData] = await Promise.all([
          getAIModels(),
          getProviders()
        ]);
        setModels(modelsData);
        setProviders(providersData);
      } catch (error) {
        console.error('获取数据失败:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  // 创建模型
  const handleCreate = async (data: AIModelCreate) => {
    try {
      const newModel = await createAIModel(data);
      setModels(prev => [...prev, newModel]);
      return newModel;
    } catch (error) {
      console.error('创建失败:', error);
      throw error;
    }
  };

  // 更新模型
  const handleUpdate = async (id: string, data: AIModelUpdate) => {
    try {
      const updatedModel = await updateAIModel(id, data);
      setModels(prev => prev.map(m => m.id === id ? updatedModel : m));
      return updatedModel;
    } catch (error) {
      console.error('更新失败:', error);
      throw error;
    }
  };

  // 删除模型
  const handleDelete = async (id: string) => {
    if (confirm('确定要删除这个模型配置吗？')) {
      try {
        await deleteAIModel(id);
        setModels(prev => prev.filter(m => m.id !== id));
      } catch (error) {
        console.error('删除失败:', error);
      }
    }
  };

  // 测试模型
  const handleTest = async (id: string) => {
    setTesting(id);
    try {
      const result = await testAIModel(id, '你好，请介绍一下你自己');
      setModels(prev => prev.map(m => {
        if (m.id === id) {
          return {
            ...m,
            test_results: [
              ...(m.test_results || []),
              {
                success: result.success,
                response_time: result.response_time,
                error_message: result.error_message,
                test_response: result.test_response,
                tested_at: result.tested_at
              }
            ]
          };
        }
        return m;
      }));
      return result;
    } catch (error) {
      console.error('测试失败:', error);
      throw error;
    } finally {
      setTesting(null);
    }
  };

  // 切换激活状态
  const handleToggle = async (id: string, isActive: boolean) => {
    try {
      const updatedModel = await toggleAIModel(id, isActive);
      setModels(prev => prev.map(m => m.id === id ? updatedModel : m));
    } catch (error) {
      console.error('切换状态失败:', error);
    }
  };

  // 获取指定提供商的模型列表
  const getModelsByProvider = (provider: Provider): string[] => {
    return providers.find(p => p.value === provider)?.models || [];
  };

  return (
    // JSX渲染
    <div>
      {/* 模型列表 */}
      {models.map(model => (
        <div key={model.id}>
          <h3>{model.name}</h3>
          <p>提供商: {model.provider}</p>
          <p>模型: {model.model_name}</p>
          <p>状态: {model.is_active ? '激活' : '禁用'}</p>
          <button onClick={() => handleToggle(model.id, !model.is_active)}>
            {model.is_active ? '禁用' : '激活'}
          </button>
          <button
            onClick={() => handleTest(model.id)}
            disabled={testing === model.id}
          >
            {testing === model.id ? '测试中...' : '测试连接'}
          </button>
          <button onClick={() => handleDelete(model.id)}>删除</button>
        </div>
      ))}
    </div>
  );
};
```

## 数据流图

```
┌─────────────────┐
│  ModelSettings  │
│    Component    │
└────────┬────────┘
         │
         ├─ getAIModels() ────────────► GET /ai-models/
         │                                │
         │                                ◄── AIModel[]
         │
         ├─ getProviders() ────────────► GET /ai-models/providers
         │                                │
         │                                ◄── Provider[]
         │
         ├─ createAIModel() ────────────► POST /ai-models/
         │                                │
         │                                ◄── AIModel
         │
         ├─ updateAIModel() ────────────► PUT /ai-models/{id}
         │                                │
         │                                ◄── AIModel
         │
         ├─ deleteAIModel() ────────────► DELETE /ai-models/{id}
         │                                │
         │                                ◄── Success
         │
         ├─ testAIModel() ──────────────► POST /ai-models/{id}/test
         │                                │
         │                                ◄── ModelTestResponse
         │
         └─ toggleAIModel() ────────────► PATCH /ai-models/{id}/toggle
                                          │
                                          ◄── AIModel
```

## 表单验证

### 创建/编辑表单

```typescript
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

// 表单验证规则
const modelSchema = z.object({
  name: z.string().min(1, '请输入配置名称').max(50, '配置名称不能超过50字符'),
  provider: z.enum(['openai', 'baidu', 'alibaba', 'google', 'anthropic'], {
    required_error: '请选择提供商'
  }),
  model_name: z.string().min(1, '请输入模型名称'),
  api_key: z.string().min(1, '请输入API密钥'),
  base_url: z.string().url('请输入有效的URL').optional().or(z.literal('')),
  model_type: z.enum(['chat', 'embedding'], {
    required_error: '请选择模型类型'
  }),
  is_active: z.boolean().default(false)
});

type ModelFormData = z.infer<typeof modelSchema>;

const ModelForm = () => {
  const {
    register,
    handleSubmit,
    formState: { errors },
    watch
  } = useForm<ModelFormData>({
    resolver: zodResolver(modelSchema)
  });

  const selectedProvider = watch('provider');
  const availableModels = getModelsByProvider(selectedProvider);

  const onSubmit = async (data: ModelFormData) => {
    try {
      await createAIModel(data);
      // 成功后处理
    } catch (error) {
      // 错误处理
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      {/* 配置名称 */}
      <input {...register('name')} placeholder="配置名称" />
      {errors.name && <span>{errors.name.message}</span>}

      {/* 提供商选择 */}
      <select {...register('provider')}>
        <option value="">选择提供商</option>
        <option value="openai">OpenAI</option>
        <option value="baidu">百度文心一言</option>
        <option value="alibaba">阿里通义千问</option>
        <option value="google">Google Gemini</option>
        <option value="anthropic">Anthropic Claude</option>
      </select>

      {/* 模型名称（根据提供商动态更新） */}
      <select {...register('model_name')}>
        <option value="">选择模型</option>
        {availableModels.map(model => (
          <option key={model} value={model}>{model}</option>
        ))}
      </select>

      {/* API密钥 */}
      <input
        type="password"
        {...register('api_key')}
        placeholder="API密钥"
      />

      {/* 自定义API地址（可选） */}
      <input {...register('base_url')} placeholder="自定义API地址（可选）" />

      {/* 模型类型 */}
      <select {...register('model_type')}>
        <option value="chat">对话模型</option>
        <option value="embedding">嵌入模型</option>
      </select>

      {/* 激活状态 */}
      <label>
        <input type="checkbox" {...register('is_active')} />
        立即激活
      </label>

      <button type="submit">保存</button>
    </form>
  );
};
```

## 待办事项

- [ ] 创建 `frontend/src/services/aiModels.ts`
- [ ] 创建模型配置管理页面
- [ ] 添加表单验证
- [ ] 添加测试结果显示
- [ ] 添加测试历史记录展示
- [ ] 添加模型使用统计
- [ ] 添加API密钥掩码显示
- [ ] 添加删除确认对话框
