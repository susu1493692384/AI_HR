# 简历库功能对接文档

## 功能概述

简历库模块提供简历的集中管理，包括：
- 简历列表展示（卡片/列表视图）
- 简历搜索和筛选
- 简历上传
- 简历详情查看
- 简历编辑和删除

## 前端实现状态

### 已实现功能

| 功能 | 状态 | 说明 |
|------|------|------|
| 简历列表 | ✅ | 卡片网格布局 |
| 搜索功能 | ✅ | 按姓名、职位搜索 |
| 筛选功能 | ✅ | 部门、职位、工作经验筛选 |
| 状态筛选 | ✅ | 新简历/面试中/已录用/已淘汰 |
| 简历上传 | ✅ | 拖拽上传 |
| 详情查看 | ✅ | 模态框显示 |

### 页面文件

```
frontend/src/pages/ResumeLibrary/index.tsx
```

### 组件文件

```
frontend/src/components/
├── ResumeUpload/index.tsx        # 简历上传组件
├── TalentCard/index.tsx          # 人才卡片组件
└── TalentDetailModal/index.tsx   # 详情模态框
```

## 后端接口对接

### 接口列表

| 方法 | 路径 | 描述 | 认证 |
|------|------|------|------|
| GET | `/resumes/` | 获取简历列表 | 是 |
| POST | `/resumes/upload` | 上传简历 | 是 |
| GET | `/resumes/{id}` | 获取简历详情 | 是 |
| PUT | `/resumes/{id}` | 更新简历信息 | 是 |
| DELETE | `/resumes/{id}` | 删除简历 | 是 |
| GET | `/resumes/stats` | 获取统计数据 | 是 |
| POST | `/resumes/{id}/status` | 更新简历状态 | 是 |

### 请求/响应格式

**1. 获取简历列表**

```typescript
// 请求
GET /api/v1/resumes/?skip=0&limit=20&keyword=张三&department=技术部&position=前端&status=新简历

// 响应
interface Resume {
  id: string;
  name: string;
  gender: 'male' | 'female' | 'other';
  age: number;
  phone: string;
  email: string;
  department?: string;
  position?: string;
  experience: number;  // 年
  education: string;
  skills: string[];
  status: 'new' | 'interviewing' | 'hired' | 'rejected';
  file_path: string;
  file_name: string;
  upload_date: string;
  last_modified: string;
  source?: string;  // 来源：网站/推荐/自荐
  tags?: string[];
  notes?: string;
}

interface ResumeListResponse {
  items: Resume[];
  total: number;
  stats: {
    total: number;
    new: number;
    interviewing: number;
    hired: number;
    rejected: number;
  };
}
```

**2. 上传简历**

```typescript
// 请求
POST /api/v1/resumes/upload
Content-Type: multipart/form-data

{
  file: File,
  parse_info?: boolean  // 是否解析简历信息
}

// 响应
interface UploadResponse {
  success: boolean;
  resume_id: string;
  parsed_info?: {
    name: string;
    phone: string;
    email: string;
    education: string;
    experience: number;
    skills: string[];
  };
  message: string;
}
```

**3. 更新简历状态**

```typescript
// 请求
POST /api/v1/resumes/{id}/status
{
  status: 'interviewing' | 'hired' | 'rejected',
  notes?: string
}

// 响应
{
  success: true,
  message: "状态更新成功"
}
```

**4. 获取统计数据**

```typescript
// 请求
GET /api/v1/resumes/stats

// 响应
interface ResumeStats {
  total: number;
  new: number;
  interviewing: number;
  hired: number;
  rejected: number;
  by_department: {
    [key: string]: number;
  };
  by_position: {
    [key: string]: number;
  };
  recent_uploads: number;  // 近7天上傳数
}
```

## 前端服务层

### 创建简历服务

创建 `frontend/src/services/resumes.ts`：

```typescript
import { api } from './api';

export type Gender = 'male' | 'female' | 'other';
export type ResumeStatus = 'new' | 'interviewing' | 'hired' | 'rejected';

export interface Resume {
  id: string;
  name: string;
  gender: Gender;
  age: number;
  phone: string;
  email: string;
  department?: string;
  position?: string;
  experience: number;
  education: string;
  skills: string[];
  status: ResumeStatus;
  file_path: string;
  file_name: string;
  upload_date: string;
  last_modified: string;
  source?: string;
  tags?: string[];
  notes?: string;
}

export interface ResumeListParams {
  skip?: number;
  limit?: number;
  keyword?: string;
  department?: string;
  position?: string;
  status?: ResumeStatus;
  experience_min?: number;
  experience_max?: number;
  education?: string;
}

export interface ResumeStats {
  total: number;
  new: number;
  interviewing: number;
  hired: number;
  rejected: number;
  by_department: Record<string, number>;
  by_position: Record<string, number>;
  recent_uploads: number;
}

export interface UploadResponse {
  success: boolean;
  resume_id: string;
  parsed_info?: {
    name: string;
    phone: string;
    email: string;
    education: string;
    experience: number;
    skills: string[];
  };
  message: string;
}

// 获取简历列表
export const getResumes = async (params: ResumeListParams = {}): Promise<{
  items: Resume[];
  total: number;
}> => {
  const response = await api.get('/resumes/', { params });
  return response.data;
};

// 获取简历详情
export const getResume = async (id: string): Promise<Resume> => {
  const response = await api.get(`/resumes/${id}`);
  return response.data;
};

// 上传简历
export const uploadResume = async (file: File, options?: {
  parse_info?: boolean;
}): Promise<UploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  if (options?.parse_info !== undefined) {
    formData.append('parse_info', String(options.parse_info));
  }

  const response = await api.post('/resumes/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return response.data;
};

// 更新简历
export const updateResume = async (id: string, data: Partial<Resume>): Promise<Resume> => {
  const response = await api.put(`/resumes/${id}`, data);
  return response.data;
};

// 删除简历
export const deleteResume = async (id: string) => {
  await api.delete(`/resumes/${id}`);
};

// 更新简历状态
export const updateResumeStatus = async (
  id: string,
  status: ResumeStatus,
  notes?: string
) => {
  await api.post(`/resumes/${id}/status`, { status, notes });
};

// 获取统计数据
export const getResumeStats = async (): Promise<ResumeStats> => {
  const response = await api.get('/resumes/stats');
  return response.data;
};

// 批量更新状态
export const batchUpdateStatus = async (
  ids: string[],
  status: ResumeStatus
) => {
  await api.post('/resumes/batch/status', { ids, status });
};
```

### 使用示例

```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  getResumes,
  uploadResume,
  deleteResume,
  updateResumeStatus,
  getResumeStats
} from '@/services/resumes';

const ResumeLibrary = () => {
  const queryClient = useQueryClient();

  // 查询简历列表
  const { data: resumesData, isLoading } = useQuery({
    queryKey: ['resumes', filters],
    queryFn: () => getResumes(filters)
  });

  // 查询统计数据
  const { data: stats } = useQuery({
    queryKey: ['resume-stats'],
    queryFn: getResumeStats
  });

  // 上传简历
  const uploadMutation = useMutation({
    mutationFn: (file: File) => uploadResume(file, { parse_info: true }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['resumes'] });
      queryClient.invalidateQueries({ queryKey: ['resume-stats'] });
    }
  });

  // 更新状态
  const updateStatusMutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: ResumeStatus }) =>
      updateResumeStatus(id, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['resumes'] });
      queryClient.invalidateQueries({ queryKey: ['resume-stats'] });
    }
  });

  // 删除简历
  const deleteMutation = useMutation({
    mutationFn: deleteResume,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['resumes'] });
      queryClient.invalidateQueries({ queryKey: ['resume-stats'] });
    }
  });

  return (
    // JSX...
  );
};
```

## 筛选条件映射

```typescript
// 前端筛选值 → 后端参数映射
const filterMapping = {
  // 状态
  status: {
    'all': undefined,
    'new': 'new',
    'interviewing': 'interviewing',
    'hired': 'hired',
    'rejected': 'rejected'
  },

  // 部门
  department: {
    'all': undefined,
    'tech': '技术部',
    'product': '产品部',
    'design': '设计部',
    'operations': '运营部'
  },

  // 职位
  position: {
    'all': undefined,
    'frontend': '前端工程师',
    'backend': '后端工程师',
    'fullstack': '全栈工程师',
    'product-manager': '产品经理',
    'ui-designer': 'UI设计师'
  },

  // 工作经验（年）
  experience: {
    'all': undefined,
    'intern': [0, 1],
    'junior': [1, 3],
    'mid': [3, 5],
    'senior': [5, 10],
    'expert': [10, null]
  },

  // 学历
  education: {
    'all': undefined,
    'bachelor': '本科',
    'master': '硕士',
    'phd': '博士',
    'other': '其他'
  }
};
```

## 数据流图

```
┌─────────────────┐
│  ResumeLibrary  │
│    Component    │
└────────┬────────┘
         │
         ├─ getResumes() ────────────► GET /resumes/
         │                               │
         │                               ◄── Resume[] + Stats
         │
         ├─ getResume() ──────────────► GET /resumes/{id}
         │                               │
         │                               ◄── Resume
         │
         ├─ uploadResume() ────────────► POST /resumes/upload
         │                               │
         │                               ◄── UploadResponse
         │
         ├─ updateResumeStatus() ──────► POST /resumes/{id}/status
         │                               │
         │                               ◄── Success
         │
         ├─ deleteResume() ────────────► DELETE /resumes/{id}
         │                               │
         │                               ◄── Success
         │
         └─ getResumeStats() ──────────► GET /resumes/stats
                                         │
                                         ◄── ResumeStats
```

## 待办事项

- [ ] 后端实现简历列表接口（支持多条件筛选）
- [ ] 后端实现简历上传和解析功能
- [ ] 后端实现简历CRUD接口
- [ ] 后端实现状态更新接口
- [ ] 后端实现统计数据接口
- [ ] 创建 `frontend/src/services/resumes.ts`
- [ ] 更新 ResumeLibrary 页面对接真实API
- [ ] 添加简历导出功能
- [ ] 添加简历去重功能
- [ ] 添加简历评论/备注功能
