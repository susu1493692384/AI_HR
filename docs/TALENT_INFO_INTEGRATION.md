# 人才信息表功能对接文档

## 功能概述

人才信息表模块提供候选人信息的结构化管理，包括：
- 候选人信息列表（表格视图）
- 信息编辑（单行编辑/弹窗编辑）
- 状态管理
- 数据导入导出
- 高级筛选和排序

## 前端实现状态

### 已实现功能

| 功能 | 状态 | 说明 |
|------|------|------|
| 信息表格 | ✅ | 可编辑单元格 |
| 状态列 | ✅ | 下拉选择状态 |
| 操作列 | ✅ | 编辑/删除按钮 |
| 分页功能 | ✅ | 每页显示数量 |
| 全选功能 | ✅ | 批量操作 |

### 页面文件

```
frontend/src/pages/TalentInfo/index.tsx
```

## 后端接口对接

### 接口列表

| 方法 | 路径 | 描述 | 认证 |
|------|------|------|------|
| GET | `/talents/` | 获取人才列表 | 是 |
| POST | `/talents/` | 创建人才记录 | 是 |
| GET | `/talents/{id}` | 获取人才详情 | 是 |
| PUT | `/talents/{id}` | 更新人才信息 | 是 |
| PATCH | `/talents/{id}` | 部分更新 | 是 |
| DELETE | `/talents/{id}` | 删除人才记录 | 是 |
| POST | `/talents/import` | 批量导入 | 是 |
| GET | `/talents/export` | 导出数据 | 是 |
| POST | `/talents/batch` | 批量更新 | 是 |

### 请求/响应格式

**1. 获取人才列表**

```typescript
// 请求
GET /api/v1/talents/?skip=0&limit=20&keyword=张三&department=技术部&status=面试中&sort_by=created_at&order=desc

// 响应
interface Talent {
  id: string;
  name: string;
  gender: 'male' | 'female' | 'other';
  age: number;
  phone: string;
  email: string;
  department?: string;
  position?: string;
  experience: number;
  education: string;
  salary_expectation?: number;
  current_salary?: number;
  status: 'new' | 'resume_screened' | 'interview_scheduled' |
          'interviewing' | 'technical_interview' | 'hr_interview' |
          'offer_sent' | 'hired' | 'rejected';
  resume_score?: number;
  interview_date?: string;
  interviewer?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
  created_by?: string;
}

interface TalentListResponse {
  items: Talent[];
  total: number;
  summary: {
    total: number;
    by_status: Record<string, number>;
    by_department: Record<string, number>;
  };
}
```

**2. 创建/更新人才**

```typescript
// 请求
POST /api/v1/talents/
PUT /api/v1/talents/{id}

interface TalentCreate {
  name: string;
  gender: 'male' | 'female' | 'other';
  age?: number;
  phone: string;
  email: string;
  department?: string;
  position?: string;
  experience?: number;
  education?: string;
  salary_expectation?: number;
  current_salary?: number;
  status?: string;
  notes?: string;
}

// 响应
{
  id: string;
  ...Talent
}
```

**3. 部分更新（单字段）**

```typescript
// 请求
PATCH /api/v1/talents/{id}
{
  "status": "interviewing",
  "interview_date": "2024-01-20T14:00:00",
  "interviewer": "张经理"
}

// 响应
{
  success: true,
  message: "更新成功"
}
```

**4. 批量导入**

```typescript
// 请求
POST /api/v1/talents/import
Content-Type: multipart/form-data

{
  file: File,  // Excel/CSV
  update_existing?: boolean  // 是否更新已存在的记录
}

// 响应
interface ImportResponse {
  success: boolean;
  total: number;
  created: number;
  updated: number;
  failed: number;
  errors?: Array<{
    row: number;
    reason: string;
  }>;
}
```

**5. 导出数据**

```typescript
// 请求
GET /api/v1/talents/export?format=xlsx&status=interviewing

// 响应
// 返回文件流，前端触发下载
Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
Content-Disposition: attachment; filename="talents_20241223.xlsx"
```

## 前端服务层

### 创建人才服务

创建 `frontend/src/services/talents.ts`：

```typescript
import { api } from './api';

export type Gender = 'male' | 'female' | 'other';
export type TalentStatus =
  | 'new'
  | 'resume_screened'
  | 'interview_scheduled'
  | 'interviewing'
  | 'technical_interview'
  | 'hr_interview'
  | 'offer_sent'
  | 'hired'
  | 'rejected';

export interface Talent {
  id: string;
  name: string;
  gender: Gender;
  age?: number;
  phone: string;
  email: string;
  department?: string;
  position?: string;
  experience?: number;
  education?: string;
  salary_expectation?: number;
  current_salary?: number;
  status: TalentStatus;
  resume_score?: number;
  interview_date?: string;
  interviewer?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
  created_by?: string;
}

export interface TalentListParams {
  skip?: number;
  limit?: number;
  keyword?: string;
  department?: string;
  position?: string;
  status?: TalentStatus;
  education?: string;
  experience_min?: number;
  experience_max?: number;
  salary_min?: number;
  salary_max?: number;
  sort_by?: string;
  order?: 'asc' | 'desc';
}

export interface TalentCreate {
  name: string;
  gender: Gender;
  age?: number;
  phone: string;
  email: string;
  department?: string;
  position?: string;
  experience?: number;
  education?: string;
  salary_expectation?: number;
  current_salary?: number;
  status?: TalentStatus;
  notes?: string;
}

export interface ImportResponse {
  success: boolean;
  total: number;
  created: number;
  updated: number;
  failed: number;
  errors?: Array<{
    row: number;
    reason: string;
  }>;
}

// 获取人才列表
export const getTalents = async (
  params: TalentListParams = {}
): Promise<{ items: Talent[]; total: number; summary: any }> => {
  const response = await api.get('/talents/', { params });
  return response.data;
};

// 获取人才详情
export const getTalent = async (id: string): Promise<Talent> => {
  const response = await api.get(`/talents/${id}`);
  return response.data;
};

// 创建人才
export const createTalent = async (data: TalentCreate): Promise<Talent> => {
  const response = await api.post('/talents/', data);
  return response.data;
};

// 更新人才
export const updateTalent = async (id: string, data: Partial<Talent>): Promise<Talent> => {
  const response = await api.put(`/talents/${id}`, data);
  return response.data;
};

// 部分更新
export const patchTalent = async (
  id: string,
  data: Partial<Talent>
): Promise<{ success: boolean }> => {
  const response = await api.patch(`/talents/${id}`, data);
  return response.data;
};

// 删除人才
export const deleteTalent = async (id: string) => {
  await api.delete(`/talents/${id}`);
};

// 批量删除
export const deleteTalentsBatch = async (ids: string[]) => {
  await api.post('/talents/batch-delete', { ids });
};

// 批量更新
export const updateTalentsBatch = async (data: {
  ids: string[];
  updates: Partial<Talent>;
}) => {
  await api.post('/talents/batch', data);
};

// 导入数据
export const importTalents = async (
  file: File,
  options?: { update_existing?: boolean }
): Promise<ImportResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  if (options?.update_existing !== undefined) {
    formData.append('update_existing', String(options.update_existing));
  }

  const response = await api.post('/talents/import', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return response.data;
};

// 导出数据
export const exportTalents = async (params?: {
  status?: TalentStatus;
  department?: string;
  format?: 'xlsx' | 'csv';
}) => {
  const response = await api.get('/talents/export', {
    params,
    responseType: 'blob'
  });

  // 创建下载链接
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement('a');
  link.href = url;
  const date = new Date().toISOString().split('T')[0];
  link.setAttribute('download', `talents_${date}.xlsx`);
  document.body.appendChild(link);
  link.click();
  link.remove();
};

// 获取筛选选项
export const getTalentFilters = async (): Promise<{
  departments: string[];
  positions: string[];
  educations: string[];
}> => {
  const response = await api.get('/talents/filters');
  return response.data;
};
```

### 使用示例

```typescript
import { useState } from 'react';
import {
  getTalents,
  createTalent,
  updateTalent,
  deleteTalent,
  exportTalents
} from '@/services/talents';

const TalentInfo = () => {
  const [talents, setTalents] = useState<Talent[]>([]);
  const [loading, setLoading] = useState(false);
  const [pagination, setPagination] = useState({ page: 1, pageSize: 20, total: 0 });

  // 获取数据
  const fetchTalents = async () => {
    setLoading(true);
    try {
      const result = await getTalents({
        skip: (pagination.page - 1) * pagination.pageSize,
        limit: pagination.pageSize,
        ...filters
      });
      setTalents(result.items);
      setPagination(prev => ({ ...prev, total: result.total }));
    } catch (error) {
      console.error('获取数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  // 单元格编辑
  const handleCellEdit = async (id: string, field: string, value: any) => {
    try {
      await updateTalent(id, { [field]: value });
      setTalents(prev =>
        prev.map(t => t.id === id ? { ...t, [field]: value } : t)
      );
    } catch (error) {
      console.error('更新失败:', error);
    }
  };

  // 状态更新
  const handleStatusChange = async (id: string, status: TalentStatus) => {
    try {
      await updateTalent(id, { status });
      setTalents(prev =>
        prev.map(t => t.id === id ? { ...t, status } : t)
      );
    } catch (error) {
      console.error('状态更新失败:', error);
    }
  };

  // 导出
  const handleExport = async () => {
    try {
      await exportTalents({
        status: filters.status,
        department: filters.department,
        format: 'xlsx'
      });
    } catch (error) {
      console.error('导出失败:', error);
    }
  };

  return (
    // JSX...
  );
};
```

## 状态流转

```typescript
// 人才状态流转规则
const statusFlow: Record<TalentStatus, TalentStatus[]> = {
  'new': ['resume_screened', 'rejected'],
  'resume_screened': ['interview_scheduled', 'rejected'],
  'interview_scheduled': ['interviewing', 'rejected'],
  'interviewing': ['technical_interview', 'hr_interview', 'rejected'],
  'technical_interview': ['hr_interview', 'rejected'],
  'hr_interview': ['offer_sent', 'rejected'],
  'offer_sent': ['hired', 'rejected'],
  'hired': [],
  'rejected': ['new']  // 可以重新激活
};

// 状态显示文本
const statusLabels: Record<TalentStatus, string> = {
  'new': '新简历',
  'resume_screened': '简历筛选',
  'interview_scheduled': '待面试',
  'interviewing': '面试中',
  'technical_interview': '技术面试',
  'hr_interview': 'HR面试',
  'offer_sent': '已发Offer',
  'hired': '已录用',
  'rejected': '已淘汰'
};

// 状态颜色
const statusColors: Record<TalentStatus, string> = {
  'new': 'blue',
  'resume_screened': 'cyan',
  'interview_scheduled': 'purple',
  'interviewing': 'orange',
  'technical_interview': 'yellow',
  'hr_interview': 'pink',
  'offer_sent': 'indigo',
  'hired': 'green',
  'rejected': 'gray'
};
```

## 数据流图

```
┌─────────────────┐
│   TalentInfo    │
│    Component    │
└────────┬────────┘
         │
         ├─ getTalents() ─────────────► GET /talents/
         │                                │
         │                                ◄── Talent[] + Summary
         │
         ├─ createTalent() ────────────► POST /talents/
         │                                │
         │                                ◄── Talent
         │
         ├─ updateTalent() ────────────► PUT /talents/{id}
         │                                │
         │                                ◄── Talent
         │
         ├─ patchTalent() ─────────────► PATCH /talents/{id}
         │                                │
         │                                ◄── Success
         │
         ├─ deleteTalent() ────────────► DELETE /talents/{id}
         │                                │
         │                                ◄── Success
         │
         ├─ importTalents() ────────────► POST /talents/import
         │                                │
         │                                ◄── ImportResponse
         │
         └─ exportTalents() ────────────► GET /talents/export
                                          │
                                          ◄── File Blob
```

## Excel导入格式

```csv
姓名,性别,年龄,手机,邮箱,部门,职位,工作年限,学历,期望薪资,当前薪资,状态,面试时间,面试官,备注
张三,男,28,13800138000,zhangsan@email.com,技术部,前端工程师,5,本科,20000,18000,面试中,2024-01-20 14:00,李经理,
李四,女,26,13900139000,lisi@email.com,产品部,产品经理,3,硕士,25000,22000,新简历,,,
```

## 待办事项

- [ ] 后端实现人才CRUD接口
- [ ] 后端实现批量导入功能
- [ ] 后端实现数据导出功能
- [ ] 后端实现批量更新接口
- [ ] 创建 `frontend/src/services/talents.ts`
- [ ] 更新 TalentInfo 页面对接真实API
- [ ] 添加单元格编辑验证
- [ ] 添加操作日志记录
- [ ] 添加数据权限控制
