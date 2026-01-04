# API 文档

## 目录

- [认证](#认证)
- [简历管理](#简历管理)
- [AI 分析](#ai-分析)
- [LLM 配置](#llm-配置)
- [LLM 初始化](#llm-初始化)
- [对话管理](#对话管理)
- [RAGFlow 集成](#ragflow-集成)
- [统计数据](#统计数据)

---

## 基本信息

**Base URL**: `http://localhost:8000`

**API 版本**: `v1`

**所有接口路径前缀**: `/api/v1`

### 认证方式

API 使用 Bearer Token 认证：

```http
Authorization: Bearer <your-token>
```

### 统一响应格式

成功响应：
```json
{
  "code": 0,
  "data": {},
  "message": "success"
}
```

错误响应：
```json
{
  "detail": "错误描述信息"
}
```

---

## 认证

### 用户注册

```http
POST /api/v1/auth/register
```

**请求体**:
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "role": "user"
}
```

**响应**:
```json
{
  "id": "uuid",
  "username": "string",
  "email": "string",
  "role": "user",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "last_login": null
}
```

### 用户登录 (OAuth2)

```http
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded
```

**请求体** (form-data):
```
username=admin&password=admin123456
```

**响应**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 43200
}
```

### 用户登录 (JSON)

```http
POST /api/v1/auth/login-json
Content-Type: application/json
```

**请求体**:
```json
{
  "username": "admin",
  "password": "admin123456"
}
```

**响应**: 同 OAuth2 登录

### 获取当前用户信息

```http
GET /api/v1/auth/me
Authorization: Bearer <token>
```

**响应**:
```json
{
  "id": "uuid",
  "username": "admin",
  "email": "admin@example.com",
  "role": "admin",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "last_login": "2024-01-01T00:00:00Z"
}
```

### 用户登出

```http
POST /api/v1/auth/logout
Authorization: Bearer <token>
```

**响应**:
```json
{
  "message": "登出成功"
}
```

### 修改密码

```http
POST /api/v1/auth/change-password
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "current_password": "old_password",
  "new_password": "new_password"
}
```

**响应**:
```json
{
  "message": "密码修改成功"
}
```

---

## 简历管理

### 获取简历列表

```http
GET /api/v1/resumes?skip=0&limit=20&keyword=前端&status=completed
Authorization: Bearer <token>
```

**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| skip | integer | 否 | 跳过数量，默认 0 |
| limit | integer | 否 | 限制数量，默认 20 |
| keyword | string | 否 | 搜索关键词 |
| status | string | 否 | 状态筛选 (uploaded/parsing/completed/failed) |

**响应**:
```json
{
  "code": 0,
  "data": [
    {
      "id": "uuid",
      "filename": "张三_前端工程师_简历.pdf",
      "file_type": "resume",
      "file_size": 524288,
      "status": "completed",
      "candidate_name": "张三",
      "candidate_email": "zhangsan@example.com",
      "candidate_phone": "13800138000",
      "target_position": "前端工程师",
      "upload_time": "2024-01-01T12:00:00Z",
      "parsed_content": {},
      "extracted_text": "简历文本内容..."
    }
  ],
  "total": 100
}
```

### 上传简历

```http
POST /api/v1/resumes/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**请求体** (form-data):
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file | File | 是 | 简历文件 (PDF/DOC/DOCX/HTML, 最大 10MB) |
| file_type | string | 否 | 文件类型 (resume/attachment/report)，默认 resume |

**响应**:
```json
{
  "id": "uuid",
  "filename": "resume.pdf",
  "status": "uploaded",
  "file_size": 524288,
  "upload_time": "2024-01-01T12:00:00Z"
}
```

### 获取简历详情

```http
GET /api/v1/resumes/{resume_id}
Authorization: Bearer <token>
```

**响应**:
```json
{
  "id": "uuid",
  "filename": "张三_前端工程师_简历.pdf",
  "file_type": "resume",
  "file_size": 524288,
  "file_path": "/uploads/resumes/uuid.pdf",
  "status": "completed",
  "candidate_name": "张三",
  "candidate_email": "zhangsan@example.com",
  "candidate_phone": "13800138000",
  "target_position": "前端工程师",
  "total_experience": "5年",
  "upload_time": "2024-01-01T12:00:00Z",
  "parsed_content": {
    "basic_info": {},
    "work_experience": [],
    "education": [],
    "skills": [],
    "projects": []
  },
  "extracted_text": "完整简历文本..."
}
```

### 下载简历文件

```http
GET /api/v1/resumes/{resume_id}/download
Authorization: Bearer <token>
```

**响应**: 文件流

### 解析简历

```http
POST /api/v1/resumes/{resume_id}/parse
Authorization: Bearer <token>
```

**响应**:
```json
{
  "code": 0,
  "message": "简历解析任务已提交",
  "data": {
    "resume_id": "uuid",
    "status": "parsing"
  }
}
```

### 语义搜索简历

```http
POST /api/v1/resumes/search
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "query": "5年前端开发经验，熟悉React",
  "top_k": 10,
  "filters": {
    "target_position": "前端工程师",
    "min_experience": "3年"
  }
}
```

**响应**:
```json
{
  "code": 0,
  "data": [
    {
      "resume_id": "uuid",
      "filename": "张三_前端工程师_简历.pdf",
      "score": 0.95,
      "highlights": ["5年前端开发经验", "熟练使用React"]
    }
  ]
}
```

### 删除简历

```http
DELETE /api/v1/resumes/{resume_id}
Authorization: Bearer <token>
```

**响应**:
```json
{
  "code": 0,
  "message": "删除成功"
}
```

---

## AI 分析

### 分析简历

```http
POST /api/v1/agent-analysis/analyze/resume
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "resume_id": "uuid",
  "job_description": "资深前端工程师，要求5年以上经验，熟悉React、TypeScript",
  "position": "前端工程师",
  "dimensions": [
    "skills",
    "experience",
    "education",
    "soft_skills"
  ]
}
```

**响应**:
```json
{
  "analysis": {
    "overall_score": 85,
    "recommendation": "建议面试",
    "dimensions": {
      "skills": {
        "score": 90,
        "score_reason": "技术栈匹配度高，掌握React、TypeScript等核心技术",
        "credible_statements": ["5年React开发经验"],
        "needs_verification": ["精通性能优化"],
        "interview_questions": [
          "请介绍一个你优化过的性能案例",
          "如何处理大型前端项目的状态管理"
        ]
      },
      "experience": {
        "score": 85,
        "score_reason": "工作经历相关，有多个完整项目经验",
        "credible_statements": ["参与电商平台开发"],
        "needs_verification": ["负责团队管理"],
        "interview_questions": [
          "描述一下你在电商平台中的职责",
          "如何与其他团队协作"
        ]
      },
      "education": {
        "score": 80,
        "score_reason": "本科学历，计算机相关专业",
        "credible_statements": ["计算机科学学士学位"],
        "needs_verification": [],
        "interview_questions": []
      },
      "soft_skills": {
        "score": 82,
        "score_reason": "软技能表现良好，具备团队协作能力",
        "credible_statements": ["具备团队协作经验"],
        "needs_verification": ["良好的沟通能力"],
        "interview_questions": [
          "举例说明如何处理团队冲突"
        ]
      },
      "stability": {
        "score": 75,
        "score_reason": "职业发展较为稳定，换工作频率适中"
      },
      "development_potential": {
        "score": 88,
        "score_reason": "学习能力强，有持续学习技术的能力"
      },
      "work_attitude": {
        "score": 85,
        "score_reason": "工作态度积极，责任心强"
      }
    },
    "suggestions": [
      "重点考察React实际项目经验",
      "验证性能优化的具体成果"
    ],
    "overall_assessment": "候选人在技术能力方面表现优秀..."
  }
}
```

### 获取分析结果

```http
GET /api/v1/agent-analysis/analyze/{resume_id}
Authorization: Bearer <token>
```

**响应**: 同分析简历接口

---

## LLM 配置

### 获取支持的 LLM 厂商列表

```http
GET /api/v1/llm/factories
Authorization: Bearer <token>
```

**响应**:
```json
{
  "code": 0,
  "data": [
    {
      "name": "OpenAI",
      "logo": "https://...",
      "tags": ["chat", "embedding"],
      "rank": 100,
      "status": "1",
      "model_types": ["chat", "embedding", "image2text"]
    },
    {
      "name": "ZHIPU-AI",
      "logo": "https://...",
      "tags": ["chat"],
      "rank": 90,
      "status": "1",
      "model_types": ["chat"]
    }
  ]
}
```

### 设置 API Key（批量配置）

```http
POST /api/v1/llm/set_api_key
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "llm_factory": "OpenAI",
  "api_key": "sk-...",
  "base_url": "https://api.openai.com/v1",
  "model_type": "chat",
  "llm_name": "gpt-4"
}
```

**响应**:
```json
{
  "code": 0,
  "data": true
}
```

### 添加单个 LLM 配置

```http
POST /api/v1/llm/add_llm
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "llm_factory": "OpenAI",
  "api_key": "sk-...",
  "api_base": "https://api.openai.com/v1",
  "llm_name": "gpt-4",
  "model_type": "chat",
  "max_tokens": 8192
}
```

**响应**:
```json
{
  "code": 0,
  "data": true
}
```

### 删除模型配置

```http
POST /api/v1/llm/delete_llm
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "llm_factory": "OpenAI",
  "llm_name": "gpt-4"
}
```

**响应**:
```json
{
  "code": 0,
  "data": true
}
```

### 启用/禁用模型

```http
POST /api/v1/llm/enable_llm
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "llm_factory": "OpenAI",
  "llm_name": "gpt-4",
  "status": "1"
}
```

**响应**:
```json
{
  "code": 0,
  "data": true
}
```

### 删除整个厂商配置

```http
POST /api/v1/llm/delete_factory
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "llm_factory": "OpenAI"
}
```

**响应**:
```json
{
  "code": 0,
  "data": true
}
```

### 获取我的模型列表

```http
GET /api/v1/llm/my_llms?include_details=true
Authorization: Bearer <token>
```

**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| include_details | boolean | 否 | 是否返回详细信息，默认 false |

**响应**:
```json
{
  "code": 0,
  "data": {
    "OpenAI": {
      "tags": ["chat", "embedding"],
      "llm": [
        {
          "type": "chat",
          "name": "gpt-4",
          "used_token": 15234,
          "status": "1"
        }
      ]
    }
  }
}
```

### 获取可用模型列表

```http
GET /api/v1/llm/list?model_type=chat
Authorization: Bearer <token>
```

**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| model_type | string | 否 | 过滤模型类型 (chat/embedding/rerank等) |

**响应**:
```json
{
  "code": 0,
  "data": {
    "OpenAI": [
      {
        "llm_name": "gpt-4",
        "model_type": "chat",
        "fid": "OpenAI",
        "max_tokens": 8192,
        "available": true,
        "status": "1",
        "tags": ["chat"],
        "is_tools": true
      }
    ]
  }
}
```

### 获取租户信息

```http
GET /api/v1/llm/tenant_info
Authorization: Bearer <token>
```

**响应**:
```json
{
  "code": 0,
  "data": {
    "tenant_id": "uuid",
    "name": "租户",
    "llm_id": "gpt-4@OpenAI",
    "embd_id": "text-embedding-3-small@OpenAI",
    "asr_id": "whisper-1@OpenAI",
    "img2txt_id": "gpt-4o@OpenAI",
    "rerank_id": "bge-reranker-v2-m3@BAAI",
    "tts_id": "tts-1@OpenAI"
  }
}
```

### 设置租户信息

```http
POST /api/v1/llm/set_tenant_info
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "tenant_id": "uuid",
  "llm_id": "gpt-4@OpenAI",
  "embd_id": "text-embedding-3-small@OpenAI",
  "asr_id": "whisper-1@OpenAI",
  "img2txt_id": "gpt-4o@OpenAI",
  "rerank_id": "bge-reranker-v2-m3@BAAI",
  "tts_id": "tts-1@OpenAI"
}
```

**响应**:
```json
{
  "code": 0,
  "data": true
}
```

---

## LLM 初始化

### 初始化 LLM 数据

```http
POST /api/v1/llm-init/init-llm-data?tenant_id=default-tenant
```

**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| tenant_id | string | 否 | 租户ID |

**响应**:
```json
{
  "code": 0,
  "message": "LLM data initialized successfully",
  "data": {
    "tenant_id": "default-tenant",
    "factories_initialized": 25,
    "models_initialized": "hundreds"
  }
}
```

### 重置并重新初始化

```http
POST /api/v1/llm-init/reset-and-init?tenant_id=default-tenant
```

**响应**:
```json
{
  "code": 0,
  "message": "LLM data reset and initialized successfully",
  "data": {
    "tenant_id": "default-tenant",
    "factories_initialized": 25,
    "models_initialized": "hundreds"
  }
}
```

### 检查初始化状态

```http
GET /api/v1/llm-init/check-init-status
```

**响应**:
```json
{
  "code": 0,
  "data": {
    "initialized": true,
    "factory_count": 25
  }
}
```

---

## 对话管理

### 创建对话

```http
POST /api/v1/agent-analysis/conversations
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "title": "简历分析对话",
  "resume_id": "uuid"
}
```

**响应**:
```json
{
  "id": "uuid",
  "title": "简历分析对话",
  "resume_id": "uuid",
  "created_at": "2024-01-01T12:00:00Z",
  "status": "active"
}
```

### 获取对话列表

```http
GET /api/v1/agent-analysis/conversations?limit=50&offset=0
Authorization: Bearer <token>
```

**响应**:
```json
{
  "items": [
    {
      "id": "uuid",
      "title": "简历分析对话",
      "last_message": "最后一条消息...",
      "timestamp": "2024-01-01T12:00:00Z",
      "is_starred": false,
      "message_count": 10,
      "resume_id": "uuid"
    }
  ],
  "total": 50
}
```

### 获取对话详情

```http
GET /api/v1/agent-analysis/conversations/{conversation_id}
Authorization: Bearer <token>
```

**响应**:
```json
{
  "conversation": {
    "id": "uuid",
    "title": "简历分析对话",
    "last_message": "最后一条消息...",
    "timestamp": "2024-01-01T12:00:00Z",
    "is_starred": false,
    "message_count": 10
  },
  "messages": [
    {
      "id": "uuid",
      "conversation_id": "uuid",
      "role": "user",
      "content": "用户消息",
      "created_at": "2024-01-01T12:00:00Z"
    },
    {
      "id": "uuid",
      "conversation_id": "uuid",
      "role": "assistant",
      "content": "AI回复",
      "created_at": "2024-01-01T12:00:00Z"
    }
  ]
}
```

### 删除对话

```http
DELETE /api/v1/agent-analysis/conversations/{conversation_id}
Authorization: Bearer <token>
```

**响应**:
```json
{
  "success": true,
  "message": "删除成功"
}
```

### 发送消息（非流式）

```http
POST /api/v1/agent-analysis/conversations/{conversation_id}/messages
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "content": "请分析这个候选人的技能",
  "resume_id": "uuid",
  "use_agent": true
}
```

**响应**:
```json
{
  "message": {
    "id": "uuid",
    "conversation_id": "uuid",
    "role": "assistant",
    "content": "AI回复内容...",
    "created_at": "2024-01-01T12:00:00Z"
  },
  "conversation_id": "uuid"
}
```

### 发送消息（流式）

```http
POST /api/v1/agent-analysis/conversations/{conversation_id}/stream
Authorization: Bearer <token>
```

**请求体**: 同非流式接口

**响应**: Server-Sent Events 流式响应

```
data: {"type":"user_message","message":{"id":"uuid","role":"user","content":"用户消息"}}

data: {"type":"token","token":"AI","accumulated":"AI"}

data: {"type":"token","token":"回复","accumulated":"AI 回复"}

data: {"type":"done","message":{"role":"assistant","content":"AI回复内容"}}
```

**事件类型**:
| 类型 | 说明 |
|------|------|
| user_message | 用户消息已保存 |
| token | AI回复的token |
| json_data | 隐藏的JSON数据（报告数据） |
| done | 回复完成 |
| error | 错误信息 |

### 获取消息历史

```http
GET /api/v1/agent-analysis/conversations/{conversation_id}/messages?limit=100&offset=0
Authorization: Bearer <token>
```

**响应**:
```json
{
  "items": [
    {
      "id": "uuid",
      "conversation_id": "uuid",
      "role": "user",
      "content": "用户消息",
      "created_at": "2024-01-01T12:00:00Z"
    }
  ],
  "total": 100
}
```

---

## RAGFlow 集成

### 创建知识库

```http
POST /api/v1/ragflow/knowledge-bases
Authorization: Bearer <token>
```

**请求体** (form-data):
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | 知识库名称 |
| description | string | 否 | 知识库描述 |

**响应**:
```json
{
  "success": true,
  "data": {
    "kb_id": "uuid",
    "name": "人才知识库"
  },
  "message": "知识库创建成功"
}
```

### 获取知识库列表

```http
GET /api/v1/ragflow/knowledge-bases
Authorization: Bearer <token>
```

**响应**:
```json
{
  "success": true,
  "data": [],
  "message": "获取知识库列表成功"
}
```

### 上传文档到知识库

```http
POST /api/v1/ragflow/knowledge-bases/{kb_id}/documents
Authorization: Bearer <token>
```

**请求体** (form-data):
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file | File | 是 | 文档文件 |

**响应**:
```json
{
  "success": true,
  "data": {
    "doc_id": "uuid",
    "filename": "resume.pdf"
  },
  "message": "文档上传成功"
}
```

### 获取文档处理状态

```http
GET /api/v1/ragflow/knowledge-bases/{kb_id}/documents/{doc_id}/status
Authorization: Bearer <token>
```

**响应**:
```json
{
  "success": true,
  "data": {
    "status": "completed",
    "progress": 100
  },
  "message": "获取文档状态成功"
}
```

### 搜索知识库

```http
GET /api/v1/ragflow/knowledge-bases/{kb_id}/search?query=前端工程师&top_k=5
Authorization: Bearer <token>
```

**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| query | string | 是 | 搜索关键词 |
| top_k | integer | 否 | 返回结果数，默认 5 |

**响应**:
```json
{
  "success": true,
  "data": [
    {
      "doc_id": "uuid",
      "filename": "张三_简历.pdf",
      "score": 0.95,
      "chunk": "相关内容片段..."
    }
  ],
  "message": "搜索成功"
}
```

### 删除文档

```http
DELETE /api/v1/ragflow/knowledge-bases/{kb_id}/documents/{doc_id}
Authorization: Bearer <token>
```

**响应**:
```json
{
  "success": true,
  "message": "文档删除成功"
}
```

---

## 统计数据

### 获取仪表板统计

```http
GET /api/v1/stats/dashboard
Authorization: Bearer <token>
```

**响应**:
```json
{
  "code": 0,
  "data": {
    "total_resumes": 150,
    "talent_pool": 120,
    "pending": 15,
    "ai_analyzed": 85
  }
}
```

**统计指标说明**:
| 指标 | 说明 |
|------|------|
| total_resumes | 当前用户上传的总简历数 |
| talent_pool | 已解析完成的简历数（status = completed） |
| pending | 待解析的简历数（status = uploaded） |
| ai_analyzed | 已进行AI分析的简历数 |

---

## 错误码说明

### HTTP 状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 401 | 未认证 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

### 业务错误码

| 错误码 | 说明 |
|--------|------|
| 0 | 成功 |
| -1 | 通用错误 |
| 1001 | 用户名或密码错误 |
| 1002 | 用户名或邮箱已存在 |
| 1003 | 用户已被禁用 |
| 2001 | 简历不存在 |
| 2002 | 文件格式不支持 |
| 2003 | 文件大小超限 |
| 2004 | 简历解析失败 |
| 3001 | AI模型未配置 |
| 3002 | AI模型调用失败 |
| 3003 | API Key无效 |
| 4001 | 对话不存在 |
| 4002 | 消息发送失败 |

---

## 附录

### 支持的文件格式

| 类型 | 格式 | MIME 类型 |
|------|------|-----------|
| 简历 | PDF, DOC, DOCX, HTML | application/pdf, application/msword, application/vnd.openxmlformats-officedocument.wordprocessingml.document, text/html |
| 附件 | PDF, DOC, DOCX, ZIP, JPG, PNG | 同上 + application/zip, image/jpeg, image/png |
| 报告 | PDF, HTML | application/pdf, text/html |

### 简历状态说明

| 状态 | 说明 |
|------|------|
| uploaded | 已上传，待解析 |
| parsing | 正在解析 |
| completed | 解析完成 |
| failed | 解析失败 |

### 支持的 AI 模型厂商

| 厂商 | 模型示例 |
|------|----------|
| OpenAI | GPT-4, GPT-3.5-turbo |
| Anthropic | Claude 3.5 Sonnet |
| ZHIPU-AI | GLM-4 |
| Baichuan | Baichuan-53B |
| Qwen | Qwen-Max |
| Ollama | 本地开源模型 |
| Xinference | 本地部署模型 |

---

## 在线文档

启动后端服务后，访问以下地址查看交互式 API 文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 更新日志

### v1.0.0 (2024-01-01)
- 初始版本发布
- 支持简历上传、解析、分析
- 支持多 AI 模型配置
- 支持对话管理
- 支持 RAGFlow 集成
