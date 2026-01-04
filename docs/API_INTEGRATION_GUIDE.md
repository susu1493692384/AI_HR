# 前后端对接指南

## 目录
- [概述](#概述)
- [API基础配置](#api基础配置)
- [接口文档](#接口文档)
- [前端服务层](#前端服务层)
- [对接流程](#对接流程)
- [常见问题](#常见问题)

## 概述

本项目采用前后端分离架构：
- **后端**: FastAPI + SQLAlchemy + PostgreSQL
- **前端**: React + TypeScript + Vite + TailwindCSS
- **认证**: JWT Bearer Token

## API基础配置

### 后端配置

后端默认运行在 `http://localhost:8000`

```bash
# 启动后端服务
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

### 前端配置

在 `frontend/.env` 中配置API地址：

```env
VITE_API_URL=http://localhost:8000
```

### Axios配置

前端已配置好axios实例 (`frontend/src/services/api.ts`)：

```typescript
export const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});
```

**自动处理：**
- 请求拦截器：自动添加 `Authorization: Bearer {token}`
- 响应拦截器：401自动跳转登录页

## 接口文档

### 认证接口 `/auth`

| 方法 | 路径 | 描述 | 认证 |
|------|------|------|------|
| POST | `/auth/login-json` | 用户登录 | 否 |
| GET | `/auth/me` | 获取当前用户信息 | 是 |
| POST | `/auth/logout` | 用户登出 | 是 |

**登录请求：**
```typescript
interface LoginRequest {
  username: string;
  password: string;
}

interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}
```

### 简历接口 `/resumes`

| 方法 | 路径 | 描述 | 认证 |
|------|------|------|------|
| GET | `/resumes/` | 获取简历列表 | 是 |
| POST | `/resumes/upload` | 上传简历 | 是 |
| GET | `/resumes/{id}` | 获取简历详情 | 是 |
| DELETE | `/resumes/{id}` | 删除简历 | 是 |
| POST | `/resumes/{id}/analyze` | 触发简历分析 | 是 |
| GET | `/resumes/{id}/analysis` | 获取分析结果 | 是 |

**查询参数：**
- `skip`: 跳过条数 (默认0)
- `limit`: 返回条数 (默认100, 最大1000)
- `keyword`: 搜索关键词
- `status`: 状态筛选

**上传简历：**
```typescript
// 使用 FormData
const formData = new FormData();
formData.append('file', fileBlob);
formData.append('job_position_id', positionId);

await api.post('/resumes/upload', formData, {
  headers: { 'Content-Type': 'multipart/form-data' }
});
```

### AI模型接口 `/ai-models`

| 方法 | 路径 | 描述 | 认证 |
|------|------|------|------|
| GET | `/ai-models/` | 获取AI模型列表 | 是 |
| POST | `/ai-models/` | 创建AI模型 | 是 |
| PUT | `/ai-models/{id}` | 更新AI模型 | 是 |
| DELETE | `/ai-models/{id}` | 删除AI模型 | 是 |

### RAG接口 `/ragflow`

| 方法 | 路径 | 描述 | 认证 |
|------|------|------|------|
| POST | `/ragflow/upload` | 上传文档到RAG | 是 |
| GET | `/ragflow/documents` | 获取文档列表 | 是 |
| DELETE | `/ragflow/documents/{id}` | 删除文档 | 是 |

## 前端服务层

### 现有服务

**认证服务** (`frontend/src/services/auth.ts`)：
```typescript
import { login, getCurrentUser, logout } from '@/services/auth';

// 登录
const result = await login({ username, password });

// 获取用户信息
const user = await getCurrentUser();

// 登出
await logout();
```

### 需要创建的服务

建议创建以下服务文件：

```
frontend/src/services/
├── api.ts          # 已存在 - axios配置
├── auth.ts         # 已存在 - 认证服务
├── resumes.ts      # 待创建 - 简历服务
├── files.ts        # 待创建 - 文件服务
├── conversations.ts # 待创建 - 对话服务
└── ai.ts           # 待创建 - AI服务
```

### 简历服务示例

创建 `frontend/src/services/resumes.ts`：

```typescript
import { api } from './api';

export interface Resume {
  id: string;
  name: string;
  file_path: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface ResumeUploadRequest {
  file: File;
  job_position_id: string;
}

export interface AnalysisRequest {
  job_position_id: string;
  ai_model_id: string;
}

// 获取简历列表
export const getResumes = async (params?: {
  skip?: number;
  limit?: number;
  keyword?: string;
  status?: string;
}): Promise<Resume[]> => {
  const response = await api.get('/resumes/', { params });
  return response.data;
};

// 上传简历
export const uploadResume = async (data: ResumeUploadRequest) => {
  const formData = new FormData();
  formData.append('file', data.file);
  formData.append('job_position_id', data.job_position_id);

  const response = await api.post('/resumes/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return response.data;
};

// 获取简历详情
export const getResume = async (id: string): Promise<Resume> => {
  const response = await api.get(`/resumes/${id}`);
  return response.data;
};

// 删除简历
export const deleteResume = async (id: string) => {
  await api.delete(`/resumes/${id}`);
};

// 分析简历
export const analyzeResume = async (id: string, data: AnalysisRequest) => {
  const response = await api.post(`/resumes/${id}/analyze`, data);
  return response.data;
};

// 获取分析结果
export const getAnalysisResult = async (id: string) => {
  const response = await api.get(`/resumes/${id}/analysis`);
  return response.data;
};
```

## 对接流程

### 1. 页面组件对接示例

```typescript
import { getResumes, uploadResume, deleteResume } from '@/services/resumes';
import { useState, useEffect } from 'react';

const ResumeLibrary = () => {
  const [resumes, setResumes] = useState([]);
  const [loading, setLoading] = useState(false);

  // 获取简历列表
  useEffect(() => {
    const fetchResumes = async () => {
      setLoading(true);
      try {
        const data = await getResumes({ limit: 20 });
        setResumes(data);
      } catch (error) {
        console.error('获取简历失败:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchResumes();
  }, []);

  // 上传简历
  const handleUpload = async (file: File) => {
    try {
      const result = await uploadResume({
        file,
        job_position_id: 'position-id'
      });
      console.log('上传成功:', result);
    } catch (error) {
      console.error('上传失败:', error);
    }
  };

  // 删除简历
  const handleDelete = async (id: string) => {
    if (confirm('确定删除这份简历吗？')) {
      try {
        await deleteResume(id);
        setResumes(resumes.filter(r => r.id !== id));
      } catch (error) {
        console.error('删除失败:', error);
      }
    }
  };

  return (
    // JSX渲染
    <div>...</div>
  );
};
```

### 2. 使用React Query管理数据

```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getResumes, uploadResume, deleteResume } from '@/services/resumes';

const ResumeLibrary = () => {
  const queryClient = useQueryClient();

  // 查询简历列表
  const { data: resumes, isLoading } = useQuery({
    queryKey: ['resumes'],
    queryFn: () => getResumes()
  });

  // 上传简历
  const uploadMutation = useMutation({
    mutationFn: uploadResume,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['resumes'] });
    }
  });

  // 删除简历
  const deleteMutation = useMutation({
    mutationFn: deleteResume,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['resumes'] });
    }
  });

  return (
    // JSX渲染
    <div>...</div>
  );
};
```

## 常见问题

### CORS错误

如果遇到CORS错误，检查后端配置：

```python
# backend/app/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # 前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 401认证错误

确保登录后正确保存token：

```typescript
// 登录成功后
const result = await login({ username, password });
localStorage.setItem('token', result.access_token);
```

### 文件上传失败

确保使用正确的Content-Type：

```typescript
const formData = new FormData();
formData.append('file', file);

await api.post('/resumes/upload', formData, {
  headers: {
    'Content-Type': 'multipart/form-data'  // 重要！
  }
});
```

### 环境变量不生效

重启Vite开发服务器：

```bash
cd frontend
# Ctrl+C 停止
npm run dev  # 重新启动
```

## 开发调试

### 查看API请求

1. 浏览器开发者工具 → Network 标签
2. 查看请求URL、Headers、Payload

### 测试API

使用后端自动生成的文档：
```
http://localhost:8000/docs
```

### 查看日志

```bash
# 后端日志会输出到终端
# 前端日志在浏览器控制台
```
