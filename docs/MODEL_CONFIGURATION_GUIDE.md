# RAGFlow 模型配置技术指南

## 目录

1. [概述](#概述)
2. [架构设计](#架构设计)
3. [模型类型](#模型类型)
4. [API 接口详解](#api-接口详解)
5. [配置方式](#配置方式)
6. [数据库模型](#数据库模型)
7. [可复现示例](#可复现示例)

---

## 概述

RAGFlow 的模型配置系统支持多种 LLM 供应商（OpenAI、Azure、Google Cloud、Bedrock 等），采用分层架构设计，实现了：

- **多租户隔离**：每个租户独立的模型配置
- **多供应商支持**：30+ LLM 供应商统一接入
- **模型验证**：配置时自动验证 API 可用性
- **使用统计**：Token 使用量跟踪

---

## 架构设计

### 分层架构

```
┌─────────────────────────────────────────────────────────────┐
│                        API 层                                 │
│  api/apps/llm_app.py - 模型配置管理 RESTful API              │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                        服务层                                 │
│  - LLMService: 全局模型元数据管理                             │
│  - TenantLLMService: 租户模型配置与实例化                      │
│  - LLMFactoriesService: 厂商信息管理                          │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      数据模型层                                │
│  - LLMFactories: 厂商信息表                                   │
│  - LLM: 模型元数据表                                          │
│  - TenantLLM: 租户配置表                                      │
│  - Tenant: 租户默认模型表                                     │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      模型抽象层                                │
│  - ChatModel: 对话模型                                        │
│  - EmbeddingModel: 嵌入模型                                   │
│  - RerankModel: 重排模型                                      │
│  - CvModel: 图像理解模型                                      │
│  - Seq2txtModel: 语音转文本                                   │
│  - TTSModel: 文本转语音                                       │
│  - OcrModel: OCR 模型                                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 模型类型

RAGFlow 支持以下模型类型，定义在 `common/constants.py`：

| 类型 | 枚举值 | 用途 |
|------|--------|------|
| 聊天模型 | `chat` | 对话生成、问答 |
| 嵌入模型 | `embedding` | 文本向量化 |
| 语音转文本 | `speech2text` | 语音识别/ASR |
| 图像理解 | `image2text` | 图像描述/视觉理解 |
| 重排序模型 | `rerank` | 检索结果重排 |
| 文本转语音 | `tts` | 语音合成 |
| OCR | `ocr` | 光学字符识别 |

---

## API 接口详解

### 基础路径
所有 API 路径前缀：`/api/v1`（具体根据路由配置）

### 1. 获取支持的厂商列表

**接口**: `GET /llm/factories`

**说明**: 获取系统支持的所有 LLM 厂商信息

**请求示例**:
```bash
curl -X GET "http://localhost:9380/api/v1/llm/factories" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**响应示例**:
```json
{
  "code": 0,
  "data": [
    {
      "name": "OpenAI",
      "logo": "base64_encoded_logo",
      "tags": "LLM,Text Embedding",
      "rank": 1,
      "status": "1",
      "model_types": ["chat", "embedding", "image2text"]
    },
    {
      "name": "Azure-OpenAI",
      "logo": "...",
      "tags": "LLM,Text Embedding",
      "rank": 2,
      "status": "1",
      "model_types": ["chat", "embedding"]
    }
  ]
}
```

**关键字段说明**:
- `name`: 厂商名称（用于后续配置）
- `tags`: 厂商支持的模型类型标签
- `model_types`: 该厂商支持的模型类型列表
- `status`: "1"=有效, "0"=失效

---

### 2. 设置 API Key（批量配置厂商模型）

**接口**: `POST /llm/set_api_key`

**说明**: 为指定厂商设置 API Key，系统会自动配置该厂所有可用模型

**请求参数**:
```json
{
  "llm_factory": "OpenAI",
  "api_key": "sk-xxxxxxxxxxxx",
  "base_url": "https://api.openai.com/v1",
  "model_type": "chat",
  "llm_name": "gpt-4o-mini"
}
```

**验证流程**:
1. 系统自动测试 API Key 有效性
2. 依次测试 Embedding、Chat、Rerank 模型
3. 任一测试通过即保存配置

**响应**:
```json
{
  "code": 0,
  "data": true
}
```

**错误响应示例**:
```json
{
  "code": 1,
  "message": "\nFail to access embedding model(text-embedding-3-small). API key invalid"
}
```

---

### 3. 添加单个 LLM 配置

**接口**: `POST /llm/add_llm`

**说明**: 添加或更新单个模型的配置

**通用请求参数**:
```json
{
  "llm_factory": "OpenAI",
  "llm_name": "gpt-4o-mini",
  "model_type": "chat",
  "api_key": "sk-xxxxx",
  "api_base": "https://api.openai.com/v1",
  "max_tokens": 8192
}
```

**特殊厂商配置示例**:

#### Azure OpenAI
```json
{
  "llm_factory": "Azure-OpenAI",
  "llm_name": "gpt-4o",
  "model_type": "chat",
  "api_key": "YOUR_API_KEY",
  "api_version": "2024-02-01",
  "api_base": "https://your-resource.openai.azure.com"
}
```

#### AWS Bedrock
```json
{
  "llm_factory": "Bedrock",
  "llm_name": "anthropic.claude-3-5-sonnet-20241022-v2:0",
  "model_type": "chat",
  "auth_mode": "api_key",
  "bedrock_ak": "AKIAIOSFODNN7EXAMPLE",
  "bedrock_sk": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
  "bedrock_region": "us-east-1",
  "aws_role_arn": ""
}
```

#### VolcEngine（火山引擎）
```json
{
  "llm_factory": "VolcEngine",
  "llm_name": "doubao-pro-32k",
  "model_type": "chat",
  "ark_api_key": "your_ark_api_key",
  "endpoint_id": "your_endpoint_id"
}
```

#### Google Cloud
```json
{
  "llm_factory": "Google Cloud",
  "llm_name": "gemini-1.5-pro",
  "model_type": "chat",
  "google_project_id": "your-project-id",
  "google_region": "us-central1",
  "google_service_account_key": "base64_encoded_key"
}
```

#### OpenRouter
```json
{
  "llm_factory": "OpenRouter",
  "llm_name": "anthropic/claude-3.5-sonnet",
  "model_type": "chat",
  "api_key": "sk-or-xxxxx",
  "provider_order": "Anthropic|OpenAI|Together"
}
```

**验证流程**:
根据 `model_type` 不同，系统会执行相应验证：
- `embedding`: 调用编码测试
- `chat`: 发送测试对话
- `rerank`: 测试相似度计算
- `image2text`: 测试图像描述
- `tts`: 测试语音合成
- `ocr`: 测试 OCR 可用性

---

### 4. 获取我的模型列表

**接口**: `GET /llm/my_llms?include_details=true`

**说明**: 获取当前租户已配置的所有模型

**请求参数**:
- `include_details` (可选): `true` 返回详细信息

**响应示例**:
```json
{
  "code": 0,
  "data": {
    "OpenAI": {
      "tags": "LLM,Text Embedding,Image2Text",
      "llm": [
        {
          "type": "chat",
          "name": "gpt-4o-mini",
          "used_token": 1234567,
          "api_base": "https://api.openai.com/v1",
          "max_tokens": 16384,
          "status": "1"
        },
        {
          "type": "embedding",
          "name": "text-embedding-3-small",
          "used_token": 523400,
          "api_base": "https://api.openai.com/v1",
          "max_tokens": 8191,
          "status": "1"
        }
      ]
    },
    "Azure-OpenAI": {
      "tags": "LLM,Text Embedding",
      "llm": [
        {
          "type": "chat",
          "name": "gpt-4o",
          "used_token": 0,
          "api_base": "https://your-resource.openai.azure.com",
          "max_tokens": 128000,
          "status": "1"
        }
      ]
    }
  }
}
```

---

### 5. 获取可用模型列表

**接口**: `GET /llm/list?model_type=chat`

**说明**: 获取系统所有可用模型（含可用性状态）

**请求参数**:
- `model_type` (可选): 过滤模型类型

**响应示例**:
```json
{
  "code": 0,
  "data": {
    "OpenAI": [
      {
        "llm_name": "gpt-4o-mini",
        "model_type": "chat",
        "fid": "OpenAI",
        "max_tokens": 16384,
        "available": true,
        "status": "1"
      },
      {
        "llm_name": "gpt-4o",
        "model_type": "chat",
        "fid": "OpenAI",
        "max_tokens": 128000,
        "available": true,
        "status": "1"
      }
    ],
    "Ollama": [
      {
        "llm_name": "llama3.2",
        "model_type": "chat",
        "fid": "Ollama",
        "max_tokens": 128000,
        "available": true,
        "status": "1"
      }
    ]
  }
}
```

**字段说明**:
- `available`: 该模型是否已配置可用
- 自部署厂商（Ollama、Xinference 等）始终显示为可用

---

### 6. 删除模型配置

**接口**: `POST /llm/delete_llm`

**请求参数**:
```json
{
  "llm_factory": "OpenAI",
  "llm_name": "gpt-4o-mini"
}
```

---

### 7. 启用/禁用模型

**接口**: `POST /llm/enable_llm`

**请求参数**:
```json
{
  "llm_factory": "OpenAI",
  "llm_name": "gpt-4o-mini",
  "status": "1"
}
```

**状态值**:
- `"1"`: 启用
- `"0"`: 禁用

---

### 8. 删除整个厂商配置

**接口**: `POST /llm/delete_factory`

**请求参数**:
```json
{
  "llm_factory": "OpenAI"
}
```

---

## 配置方式

### 方式一：通过 API 动态配置

适合运行时动态添加模型配置。

### 方式二：通过配置文件预设

在 `docker/service_conf.yaml.template` 中配置默认模型：

```yaml
user_default_llm:
  factory: 'OpenAI'
  api_key: 'sk-xxxxx'
  base_url: 'https://api.openai.com/v1'
  default_models:
    chat_model: 'gpt-4o-mini'
    embedding_model:
      name: 'text-embedding-3-small'
    rerank_model: 'bge-reranker-v2-m3'
    asr_model: 'whisper-1'
    image2text_model: 'gpt-4o'
```

### 方式三：环境变量配置

在 `docker/.env` 中设置：

```bash
# OpenAI 配置
OPENAI_API_KEY=sk-xxxxx
OPENAI_API_BASE=https://api.openai.com/v1

# 默认模型
CHAT_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small
RERANK_MODEL=bge-reranker-v2-m3
```

---

## 数据库模型

### LLMFactories（厂商信息表）

| 字段 | 类型 | 说明 |
|------|------|------|
| name | varchar(128) | 厂商名称（主键） |
| logo | text | 厂商 Logo（base64） |
| tags | varchar(255) | 支持的模型类型标签 |
| rank | int | 排序权重 |
| status | char(1) | 状态：1=有效，0=失效 |

### LLM（模型元数据表）

| 字段 | 类型 | 说明 |
|------|------|------|
| fid | varchar(128) | 厂商 ID（主键之一） |
| llm_name | varchar(128) | 模型名称（主键之一） |
| model_type | varchar(128) | 模型类型 |
| max_tokens | int | 最大 token 数 |
| tags | varchar(255) | 标签 |
| is_tools | boolean | 是否支持工具调用 |
| status | char(1) | 状态 |

### TenantLLM（租户配置表）

| 字段 | 类型 | 说明 |
|------|------|------|
| tenant_id | varchar(32) | 租户 ID（主键之一） |
| llm_factory | varchar(128) | 厂商名称（主键之一） |
| llm_name | varchar(128) | 模型名称（主键之一） |
| model_type | varchar(128) | 模型类型 |
| api_key | text | API 密钥 |
| api_base | varchar(255) | API 基础 URL |
| max_tokens | int | 最大 token 数 |
| used_tokens | int | 已使用 token 数 |
| status | char(1) | 状态 |

### Tenant（租户默认模型表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | varchar(32) | 租户 ID（主键） |
| llm_id | varchar(128) | 默认聊天模型 |
| embd_id | varchar(128) | 默认嵌入模型 |
| asr_id | varchar(128) | 默认语音识别模型 |
| img2txt_id | varchar(128) | 默认图像理解模型 |
| rerank_id | varchar(128) | 默认重排序模型 |
| tts_id | varchar(256) | 默认 TTS 模型 |

---

## 可复现示例

### 完整配置流程示例

#### 步骤 1：启动 RAGFlow

```bash
cd docker
docker compose -f docker-compose.yml up -d
```

#### 步骤 2：登录获取 Token

```bash
# 首次登录创建用户
curl -X POST "http://localhost:9380/api/v1/user/setup" \
  -H "Content-Type: application/json" \
  -d '{"nickname": "admin", "email": "admin@example.com", "password": "admin123"}'

# 登录获取 token
TOKEN=$(curl -s -X POST "http://localhost:9380/api/v1/user/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "admin123"}' \
  | jq -r '.data.token')
```

#### 步骤 3：查看支持的厂商

```bash
curl -X GET "http://localhost:9380/api/v1/llm/factories" \
  -H "Authorization: Bearer $TOKEN" | jq
```

#### 步骤 4：配置 OpenAI（批量）

```bash
curl -X POST "http://localhost:9380/api/v1/llm/set_api_key" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "llm_factory": "OpenAI",
    "api_key": "sk-your-api-key-here",
    "base_url": "https://api.openai.com/v1"
  }'
```

#### 步骤 5：添加特定模型（单个）

```bash
# 添加 OpenAI 嵌入模型
curl -X POST "http://localhost:9380/api/v1/llm/add_llm" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "llm_factory": "OpenAI",
    "llm_name": "text-embedding-3-large",
    "model_type": "embedding",
    "api_key": "sk-your-api-key-here",
    "api_base": "https://api.openai.com/v1"
  }'
```

#### 步骤 6：查看已配置模型

```bash
curl -X GET "http://localhost:9380/api/v1/llm/my_llms?include_details=true" \
  -H "Authorization: Bearer $TOKEN" | jq
```

#### 步骤 7：查看可用模型列表

```bash
# 查看所有可用模型
curl -X GET "http://localhost:9380/api/v1/llm/list" \
  -H "Authorization: Bearer $TOKEN" | jq

# 只查看聊天模型
curl -X GET "http://localhost:9380/api/v1/llm/list?model_type=chat" \
  -H "Authorization: Bearer $TOKEN" | jq
```

---

### 特殊厂商配置示例

#### Azure OpenAI

```bash
curl -X POST "http://localhost:9380/api/v1/llm/add_llm" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "llm_factory": "Azure-OpenAI",
    "llm_name": "gpt-4o",
    "model_type": "chat",
    "api_key": "your-azure-api-key",
    "api_version": "2024-02-01",
    "api_base": "https://your-resource-name.openai.azure.com"
  }'
```

#### AWS Bedrock

```bash
curl -X POST "http://localhost:9380/api/v1/llm/add_llm" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "llm_factory": "Bedrock",
    "llm_name": "anthropic.claude-3-5-sonnet-20241022-v2:0",
    "model_type": "chat",
    "auth_mode": "api_key",
    "bedrock_ak": "AKIAIOSFODNN7EXAMPLE",
    "bedrock_sk": "your-secret-key",
    "bedrock_region": "us-east-1"
  }'
```

#### Ollama（本地部署）

```bash
# 确保 Ollama 服务可访问
curl -X POST "http://localhost:9380/api/v1/llm/add_llm" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "llm_factory": "Ollama",
    "llm_name": "llama3.2",
    "model_type": "chat",
    "api_key": "any-key",
    "api_base": "http://host.docker.internal:11434"
  }'
```

#### 自部署 OpenAI 兼容 API

```bash
curl -X POST "http://localhost:9380/api/v1/llm/add_llm" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "llm_factory": "OpenAI-API-Compatible",
    "llm_name": "qwen2.5-7b-instruct",
    "model_type": "chat",
    "api_key": "your-api-key",
    "api_base": "http://your-api-server:8000/v1"
  }'
```

---

### 设置默认模型

默认模型设置需要在 Tenant 表中配置。通常在租户创建时自动初始化，也可以通过 API 修改：

```bash
# 设置默认聊天模型
curl -X POST "http://localhost:9380/api/v1/tenant/set_default_model" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "model_type": "chat",
    "model_name": "gpt-4o-mini@OpenAI"
  }'
```

---

### Python 脚本示例

```python
import requests
import json

BASE_URL = "http://localhost:9380/api/v1"

def login(email, password):
    """登录获取 token"""
    resp = requests.post(f"{BASE_URL}/user/login", json={
        "email": email,
        "password": password
    })
    return resp.json()["data"]["token"]

def get_factories(token):
    """获取支持的厂商列表"""
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{BASE_URL}/llm/factories", headers=headers)
    return resp.json()["data"]

def add_llm(token, factory, model_name, model_type, api_key, api_base=None):
    """添加模型配置"""
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "llm_factory": factory,
        "llm_name": model_name,
        "model_type": model_type,
        "api_key": api_key
    }
    if api_base:
        payload["api_base"] = api_base

    resp = requests.post(f"{BASE_URL}/llm/add_llm", headers=headers, json=payload)
    return resp.json()

def get_my_models(token):
    """获取已配置的模型"""
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{BASE_URL}/llm/my_llms?include_details=true", headers=headers)
    return resp.json()["data"]

# 使用示例
if __name__ == "__main__":
    # 登录
    token = login("admin@example.com", "admin123")

    # 查看厂商
    factories = get_factories(token)
    print("支持的厂商:", [f["name"] for f in factories])

    # 添加 OpenAI 聊天模型
    result = add_llm(
        token=token,
        factory="OpenAI",
        model_name="gpt-4o-mini",
        model_type="chat",
        api_key="sk-your-api-key",
        api_base="https://api.openai.com/v1"
    )
    print("添加结果:", result)

    # 查看已配置模型
    my_models = get_my_models(token)
    print("我的模型:", json.dumps(my_models, indent=2, ensure_ascii=False))
```

---

## 支持的厂商列表

以下是 RAGFlow 支持的主要厂商（持续更新）：

| 厂商 | 支持的模型类型 |
|------|----------------|
| OpenAI | chat, embedding, image2text, tts, asr |
| Azure-OpenAI | chat, embedding |
| Google Cloud | chat, embedding |
| AWS Bedrock | chat, embedding |
| Anthropic | chat |
| Cohere | chat, embedding, rerank |
| HuggingFace | chat, embedding |
| Ollama | chat, embedding |
| Xinference | chat, embedding, rerank |
| LocalAI | chat, embedding |
| LM-Studio | chat |
| GPUStack | chat, embedding |
| VolcEngine（火山引擎） | chat |
| Tongyi-Qianwen（通义千问） | chat, embedding |
| Moonshot（月之暗面） | chat |
| 百川智能 | chat |
| 智谱 AI | chat, embedding |
| 01.AI | chat, embedding |
| DeepSeek | chat, embedding |
| Minimax | chat |
| 腾讯混元 | chat |
| 腾讯云 | chat |
| 讯飞星火 | chat, tts |
| 百度文心 | chat, embedding |
| Fish Audio | tts |
| Youdao | embedding |
| BAAI | embedding, rerank |
| OpenRouter | chat |
| MinervaU | ocr |

---

## 故障排查

### 常见错误

#### 1. API Key 验证失败

```
Fail to access model(OpenAI/gpt-4o-mini). Incorrect API key provided
```

**解决方法**：检查 API Key 是否正确，确保账户有可用额度。

#### 2. 网络连接问题

```
Fail to access model(OpenAI/gpt-4o-mini). Connection timeout
```

**解决方法**：检查服务器网络，如使用代理需正确配置 `api_base`。

#### 3. 模型名称错误

```
Fail to access model(OpenAI/invalid-model). Model not found
```

**解决方法**：使用 `/llm/list` 接口查看支持的模型列表。

---

## 相关文件路径

| 文件 | 说明 |
|------|------|
| `api/apps/llm_app.py` | LLM API 路由定义 |
| `api/db/db_models.py` | 数据库模型定义 |
| `api/db/services/llm_service.py` | LLM 服务实现 |
| `api/db/services/tenant_llm_service.py` | 租户 LLM 服务 |
| `rag/llm/__init__.py` | 模型工厂注册 |
| `rag/llm/chat_model.py` | 聊天模型实现 |
| `rag/llm/embedding_model.py` | 嵌入模型实现 |
| `common/constants.py` | 常量定义（LLMType） |
| `common/settings.py` | 全局配置 |
| `docker/service_conf.yaml.template` | 配置文件模板 |
