# AI 模型配置快速指南

## 📋 目录
1. [通过前端页面配置（推荐）](#通过前端页面配置推荐)
2. [通过 API 直接配置](#通过-api-直接配置)
3. [验证配置](#验证配置)
4. [常见问题](#常见问题)

---

## 🖥️ 通过前端页面配置（推荐）

### 步骤 1：访问模型配置页面

1. 确保前端服务正在运行：
   ```bash
   cd frontend
   npm run dev
   ```

2. 在浏览器中访问：
   ```
   http://localhost:3000/settings
   ```

3. 点击左侧导航栏的 **"模型配置"** 标签（🤖 图标）

### 步骤 2：添加 OpenAI 模型（示例）

#### 2.1 在右侧"可用模型"列表中找到 "OpenAI"
- 点击 OpenAI 卡片上的 **"添加模型"** 按钮

#### 2.2 填写 API 配置信息

在弹出的对话框中填写：

| 字段 | 值 | 说明 |
|------|-----|------|
| **模型名称** | `gpt-4o-mini` 或 `gpt-3.5-turbo` | 选择要使用的模型 |
| **模型类型** | `chat` | 对话模型 |
| **API Base** | `https://api.openai.com/v1` | OpenAI API 地址 |
| **API Key** | `sk-您的密钥` | 您的 OpenAI API 密钥 |

**获取 API Key：**
- 访问 https://platform.openai.com/api-keys
- 登录后点击 "Create new secret key"
- 复制生成的密钥（格式：`sk-...`）

#### 2.3 保存配置
- 点击 **"保存"** 按钮
- 系统会自动验证 API 密钥
- 验证成功后，模型会出现在左侧"我的模型"列表中

### 步骤 3：设置为默认模型

在左侧"系统设置"区域：
1. 找到 **"对话模型"** 下拉框
2. 选择刚添加的模型（例如：`gpt-4o-mini@OpenAI`）
3. 点击 **"保存设置"**

### 步骤 4：测试对话

1. 访问 **"AI 分析助手"** 页面：
   ```
   http://localhost:3000/ai-analysis
   ```

2. 发送测试消息：
   ```
   你好，请介绍一下你自己
   ```

3. 如果看到 AI 正常回复，说明配置成功！✅

---

## 🔧 通过 API 直接配置

如果您希望通过 API 直接配置，可以使用以下方法：

### 方法 1：设置 API Key（批量配置）

```bash
# 1. 登录获取 Token
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "your-password"}' \
  | jq -r '.data.access_token')

# 2. 设置 OpenAI API Key
curl -X POST "http://localhost:8000/api/v1/llm/set_api_key" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "llm_factory": "OpenAI",
    "api_key": "sk-您的API密钥",
    "base_url": "https://api.openai.com/v1",
    "model_type": "chat",
    "llm_name": "gpt-4o-mini"
  }'
```

### 方法 2：添加单个模型

```bash
curl -X POST "http://localhost:8000/api/v1/llm/add_llm" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "llm_factory": "OpenAI",
    "llm_name": "gpt-4o-mini",
    "model_type": "chat",
    "api_key": "sk-您的API密钥",
    "api_base": "https://api.openai.com/v1",
    "max_tokens": 8192
  }'
```

### 方法 3：设置默认模型

```bash
curl -X POST "http://localhost:8000/api/v1/llm/set_tenant_info" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "llm_id": "gpt-4o-mini@OpenAI"
  }'
```

---

## ✅ 验证配置

### 1. 检查已配置的模型

```bash
curl -X GET "http://localhost:8000/api/v1/llm/my_llms?include_details=true" \
  -H "Authorization: Bearer $TOKEN" | jq
```

**预期响应示例：**
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
          "used_token": 0,
          "api_base": "https://api.openai.com/v1",
          "max_tokens": 8192,
          "status": "1"
        }
      ]
    }
  }
}
```

### 2. 检查系统设置

```bash
curl -X GET "http://localhost:8000/api/v1/llm/tenant_info" \
  -H "Authorization: Bearer $TOKEN" | jq
```

### 3. 测试流式对话

```bash
# 创建对话
CONV_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/agent-analysis/conversations" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "测试对话"}')

CONV_ID=$(echo $CONV_RESPONSE | jq -r '.id')

# 发送消息并获取流式响应
curl -X POST "http://localhost:8000/api/v1/agent-analysis/conversations/$CONV_ID/stream" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content": "你好"}'
```

---

## 🌟 其他推荐的模型配置

### 智谱 AI（GLM-4）

适合国内用户，无需翻墙：

```json
{
  "llm_factory": "ZHIPU-AI",
  "llm_name": "glm-4",
  "model_type": "chat",
  "api_key": "您的智谱API密钥",
  "api_base": "https://open.bigmodel.cn/api/paas/v4"
}
```

**获取密钥：** https://open.bigmodel.cn/

### 通义千问（阿里云）

```json
{
  "llm_factory": "Tongyi-Qianwen",
  "llm_name": "qwen-turbo",
  "model_type": "chat",
  "api_key": "您的通义API密钥",
  "api_base": "https://dashscope.aliyuncs.com/compatible-mode/v1"
}
```

**获取密钥：** https://dashscope.aliyuncs.com/

### DeepSeek（性价比高）

```json
{
  "llm_factory": "DeepSeek",
  "llm_name": "deepseek-chat",
  "model_type": "chat",
  "api_key": "您的DeepSeek密钥",
  "api_base": "https://api.deepseek.com/v1"
}
```

**获取密钥：** https://platform.deepseek.com/

### Ollama（本地部署，免费）

如果您本地运行了 Ollama：

```bash
# 1. 启动 Ollama 服务
ollama serve

# 2. 下载模型
ollama pull llama3.2

# 3. 在前端添加 Ollama 配置
# 厂商：Ollama
# 模型名称：llama3.2
# API Base：http://localhost:11434
```

---

## ❓ 常见问题

### 1. API Key 验证失败

**错误提示：**
```
Fail to access model(OpenAI/gpt-4o-mini). Incorrect API key provided
```

**解决方法：**
- 检查 API Key 是否正确（格式应为 `sk-...`）
- 确认 OpenAI 账户有可用额度
- 检查是否复制了完整的密钥（没有多余空格）

### 2. 网络连接超时

**错误提示：**
```
Fail to access model(OpenAI/gpt-4o-mini). Connection timeout
```

**解决方法：**
- 如果在国内，建议使用国内模型（智谱、通义、DeepSeek）
- 或配置代理：
  ```bash
  export https_proxy=http://127.0.0.1:7890
  export http_proxy=http://127.0.0.1:7890
  ```

### 3. 对话不显示消息

**问题：** 配置成功后，对话页面仍然不显示消息

**可能原因：**
1. 浏览器缓存问题
   - 解决：按 `Ctrl + Shift + R` 强制刷新

2. Token 过期
   - 解决：重新登录

3. 前端未重新加载
   - 解决：刷新页面或重启前端服务

### 4. 消息显示"AI 服务暂时不可用"

**检查清单：**
1. 确认模型已添加到"我的模型"
2. 确认已设置为默认模型
3. 检查后端日志：
   ```bash
   cd backend
   tail -f logs/app.log
   ```
4. 验证 API 密钥有效性

---

## 📚 相关文档

- [模型配置技术指南](./MODEL_CONFIGURATION_GUIDE.md) - 完整的架构说明
- [模型设置实现文档](./model-settings-implementation.md) - 前端实现细节

---

## 🎯 下一步

配置成功后，您可以：

1. **测试简历分析功能**
   - 访问"简历库"页面
   - 上传简历并触发分析
   - 系统会使用 4 个专家智能体并行分析

2. **使用 AI 对话助手**
   - 向 AI 提问关于简历的问题
   - 获取招聘建议和意见

3. **监控 Token 使用量**
   - 在"我的模型"中查看消耗的 token 数量
   - 合理控制成本

---

**需要帮助？**
- 检查后端日志：`backend/logs/app.log`
- 检查前端控制台：浏览器开发者工具 Console
- 确保服务状态：
  - 后端：http://localhost:8000/docs（API 文档）
  - 前端：http://localhost:3000
