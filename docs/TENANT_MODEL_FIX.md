# 问题解决方案：租户模型配置不一致

## 问题描述

**症状：** 在系统模型配置中添加了智谱AI GLM-4模型，但在AI分析助手中对话时仍然显示"AI 服务暂时不可用"。

**根本原因：**

系统的租户ID机制导致配置不一致：
1. **未登录状态**（API测试时）：使用默认租户ID `00000000-0000-0000-0000-000000000001`
2. **登录用户**：使用用户ID作为租户ID `25a4d1bb-9e85-4040-9943-bf91cb21f4b9`

当您在前端模型配置页面添加模型时，模型被保存到**登录用户的租户ID**下。
但AI分析助手对话时使用的也是**用户的租户ID**，所以应该能正常工作。

## 解决方案

### 方案 1：通过前端重新配置（推荐）

1. **访问模型配置页面**
   ```
   http://localhost:3000/settings
   ```

2. **点击"模型配置"标签**

3. **添加智谱AI模型**
   - 在右侧"可用模型"中找到 "ZHIPU-AI"
   - 点击"添加模型"按钮
   - 填写信息：
     - 模型名称：`glm-4`
     - 模型类型：`chat`
     - API Base：`https://open.bigmodel.cn/api/paas/v4`
     - API Key：您的智谱API密钥
   - 点击"保存"

4. **设置默认模型**
   - 在左侧"系统设置"区域
   - 找到"对话模型"下拉框
   - 选择 `glm-4@ZHIPU-AI`
   - 点击"保存设置"

5. **测试对话**
   - 访问 `http://localhost:3000/ai-analysis`
   - 发送测试消息

### 方案 2：通过API直接配置

如果前端页面有问题，可以使用API直接配置：

```bash
# 1. 添加模型配置
curl -X POST "http://localhost:8000/api/v1/llm/set_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "llm_factory": "ZHIPU-AI",
    "api_key": "您的智谱API密钥",
    "base_url": "https://open.bigmodel.cn/api/paas/v4",
    "model_type": "chat",
    "llm_name": "glm-4"
  }'

# 2. 设置默认模型
curl -X POST "http://localhost:8000/api/v1/llm/set_tenant_info" \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "25a4d1bb-9e85-4040-9943-bf91cb21f4b9",
    "llm_id": "glm-4@ZHIPU-AI"
  }'
```

**注意：** 请将 `您的智谱API密钥` 替换为实际的密钥。

## 验证配置

### 1. 检查模型列表

```bash
curl -s "http://localhost:8000/api/v1/llm/my_llms?include_details=true"
```

**预期响应：**
```json
{
  "code": 0,
  "data": {
    "ZHIPU-AI": {
      "tags": "LLM,Text Embedding",
      "llm": [
        {
          "type": "chat",
          "name": "glm-4",
          "used_token": 0,
          "api_base": "https://open.bigmodel.cn/api/paas/v4",
          "max_tokens": 128000,
          "status": "1"
        }
      ]
    }
  }
}
```

### 2. 检查默认模型设置

```bash
curl -s "http://localhost:8000/api/v1/llm/tenant_info"
```

**预期响应中的 `llm_id` 字段应该是：**
```json
"llm_id": "glm-4@ZHIPU-AI"
```

### 3. 测试对话

访问 AI 分析助手页面，发送消息测试。

如果仍然显示错误，请检查：

1. **浏览器控制台**（F12）是否有错误信息
2. **后端日志**是否有异常
   ```bash
   tail -f backend/logs/app.log
   ```

3. **API密钥是否正确**：
   - 智谱AI密钥格式：`xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.xx.xxxxxxxxxxxxx`
   - 可以在 https://open.bigmodel.cn/ 用户中心获取

## 常见问题

### Q1: 配置保存成功，但对话仍然报错？

**A:** 可能的原因：
1. API密钥无效或余额不足
2. api_base 配置错误
3. 前端缓存问题

**解决方法：**
1. 刷新浏览器页面（Ctrl + Shift + R）
2. 检查后端日志确认具体错误
3. 验证API密钥有效性

### Q2: 如何使用其他模型（如 DeepSeek、通义千问）？

**A:** 参考以下配置：

**DeepSeek:**
```bash
curl -X POST "http://localhost:8000/api/v1/llm/set_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "llm_factory": "DeepSeek",
    "api_key": "您的DeepSeek密钥",
    "base_url": "https://api.deepseek.com/v1",
    "model_type": "chat",
    "llm_name": "deepseek-chat"
  }'
```

**通义千问:**
```bash
curl -X POST "http://localhost:8000/api/v1/llm/set_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "llm_factory": "Tongyi-Qianwen",
    "api_key": "您的通义千问密钥",
    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "model_type": "chat",
    "llm_name": "qwen-turbo"
  }'
```

### Q3: 租户ID是什么？

**A:** 在这个系统中：
- **未登录状态**：使用默认租户ID (`00000000-0000-0000-0000-000000000001`)
- **登录用户**：使用用户ID作为租户ID

每个租户有独立的模型配置和默认模型设置。

## 技术细节

### 后端API端点

1. **`POST /api/v1/llm/set_api_key`**
   - 设置厂商的API密钥
   - 可以批量配置该厂商的多个模型
   - 需要：`llm_factory`, `api_key`
   - 可选：`base_url`, `model_type`, `llm_name`

2. **`POST /api/v1/llm/set_tenant_info`**
   - 设置租户的默认模型
   - 需要：`tenant_id`, `llm_id`
   - `llm_id` 格式：`模型名@厂商名`，例如 `glm-4@ZHIPU-AI`

3. **`GET /api/v1/llm/my_llms`**
   - 获取当前租户已配置的模型列表
   - 参数：`include_details=true` 返回详细信息

4. **`GET /api/v1/llm/tenant_info`**
   - 获取当前租户的默认模型设置
   - 返回 `llm_id`, `embd_id`, `asr_id` 等配置

### 流式对话端点

`POST /api/v1/agent-analysis/conversations/{conversation_id}/stream`

使用当前登录用户的租户ID来：
1. 查询租户的默认模型设置（`tenant.llm_id`）
2. 从 `tenant_llm` 表获取模型的API配置
3. 调用LLM生成流式响应

## 相关文件

- **后端API**: `backend/app/api/v1/endpoints/llm_config.py`
- **LLM服务**: `backend/app/application/services/llm_service.py`
- **对话端点**: `backend/app/api/v1/endpoints/agent_analysis.py`
- **前端配置**: `frontend/src/pages/UserSettings/ModelSettings/`
- **前端Hook**: `frontend/src/hooks/llm/use-llm-request.tsx`

## 后续优化建议

1. **统一租户管理**
   - 考虑为系统添加专门的租户管理功能
   - 允许管理员在多个租户间共享模型配置

2. **配置验证**
   - 添加API密钥有效性验证
   - 在配置时测试模型连接

3. **错误提示优化**
   - 提供更详细的错误信息
   - 引导用户完成配置

4. **前端体验改进**
   - 添加配置向导
   - 显示模型使用统计
   - 提供配置导入/导出功能
