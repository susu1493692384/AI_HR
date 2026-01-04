# 文件管理功能对接文档

## 功能概述

文件管理模块提供文件的上传、下载、预览、删除等功能，支持：
- 简历文件 (resume)
- 附件材料 (attachment)
- 分析报告 (report)

## 前端实现状态

### 已实现功能

| 功能 | 状态 | 说明 |
|------|------|------|
| 文件列表展示 | ✅ | 网格/列表双视图 |
| 文件搜索 | ✅ | 按文件名搜索 |
| 文件筛选 | ✅ | 类型、格式、日期、状态 |
| 文件预览 | ✅ | 右侧面板预览 |
| 文件上传 | ✅ | 拖拽上传、多文件上传 |
| 单个删除 | ✅ | 带确认对话框 |
| 批量删除 | ✅ | 选中多个文件删除 |
| 点击选中 | ✅ | 单击选中并预览 |
| 多选操作 | ✅ | Ctrl+点击多选 |

### 页面文件

```
frontend/src/pages/FileManager/index.tsx
```

### 组件文件

```
frontend/src/components/
├── FileList/index.tsx           # 文件列表组件
├── FilePreview/index.tsx        # 文件预览组件
└── FileUploadModal/index.tsx    # 上传模态框
```

## 后端接口对接

### 需要的后端接口

建议后端提供以下接口：

| 方法 | 路径 | 描述 | 请求体 |
|------|------|------|--------|
| GET | `/files/` | 获取文件列表 | - |
| POST | `/files/upload` | 上传文件 | FormData |
| GET | `/files/{id}` | 获取文件详情 | - |
| GET | `/files/{id}/download` | 下载文件 | - |
| DELETE | `/files/{id}` | 删除文件 | - |
| DELETE | `/files/batch` | 批量删除 | `{ ids: string[] }` |

### 请求/响应格式

**1. 获取文件列表**

```typescript
// 请求
GET /api/v1/files/?type=resume&format=PDF&status=completed&keyword=xxx

// 响应
interface FileItem {
  id: string;
  name: string;
  type: 'resume' | 'attachment' | 'report';
  format: string;          // PDF, DOCX, ZIP等
  size: number;            // 字节
  upload_date: string;
  last_modified: string;
  status: 'processing' | 'completed' | 'failed';
  file_path: string;
}

interface FileListResponse {
  items: FileItem[];
  total: number;
}
```

**2. 上传文件**

```typescript
// 请求
POST /api/v1/files/upload
Content-Type: multipart/form-data

{
  file: File,
  type: 'resume' | 'attachment' | 'report'
}

// 响应
interface UploadResponse {
  success: boolean;
  file_id: string;
  message: string;
}
```

**3. 删除文件**

```typescript
// 请求
DELETE /api/v1/files/{id}

// 响应
{
  success: true,
  message: "文件删除成功"
}
```

**4. 批量删除**

```typescript
// 请求
DELETE /api/v1/files/batch
{
  ids: ["id1", "id2", "id3"]
}

// 响应
{
  success: true,
  deleted_count: 3,
  message: "成功删除3个文件"
}
```

## 前端服务层对接

### 创建文件服务

创建 `frontend/src/services/files.ts`：

```typescript
import { api } from './api';

export interface FileItem {
  id: string;
  name: string;
  type: 'resume' | 'attachment' | 'report';
  format: string;
  size: number;
  upload_date: string;
  last_modified: string;
  status: 'processing' | 'completed' | 'failed';
  file_path: string;
}

export interface FileListParams {
  skip?: number;
  limit?: number;
  keyword?: string;
  type?: 'all' | 'resume' | 'attachment' | 'report';
  format?: string;
  status?: string;
  date_from?: string;
  date_to?: string;
}

export interface UploadParams {
  file: File;
  type: 'resume' | 'attachment' | 'report';
}

// 获取文件列表
export const getFiles = async (params: FileListParams): Promise<FileItem[]> => {
  const response = await api.get('/files/', { params });
  return response.data;
};

// 上传文件
export const uploadFile = async (data: UploadParams) => {
  const formData = new FormData();
  formData.append('file', data.file);
  formData.append('type', data.type);

  const response = await api.post('/files/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return response.data;
};

// 下载文件
export const downloadFile = async (id: string) => {
  const response = await api.get(`/files/${id}/download`, {
    responseType: 'blob'
  });

  // 创建下载链接
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', `file_${id}`);
  document.body.appendChild(link);
  link.click();
  link.remove();
};

// 删除文件
export const deleteFile = async (id: string) => {
  await api.delete(`/files/${id}`);
};

// 批量删除
export const deleteFilesBatch = async (ids: string[]) => {
  await api.delete('/files/batch', { data: { ids } });
};
```

### 更新FileManager页面

将模拟数据替换为API调用：

```typescript
// frontend/src/pages/FileManager/index.tsx

import { getFiles, uploadFile, deleteFile, deleteFilesBatch } from '@/services/files';

const FileManager: React.FC = () => {
  const [files, setFiles] = useState<FileItem[]>([]);
  const [loading, setLoading] = useState(false);

  // 获取文件列表
  useEffect(() => {
    const fetchFiles = async () => {
      setLoading(true);
      try {
        const data = await getFiles({
          skip: 0,
          limit: 100,
          keyword: searchTerm,
          type: filterType,
          format: filterFormat,
          status: filterStatus
        });
        setFiles(data);
      } catch (error) {
        console.error('获取文件失败:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchFiles();
  }, [searchTerm, filterType, filterFormat, filterStatus]);

  // 上传文件
  const handleUpload = async (uploadedFiles: File[], type: 'resume' | 'attachment' | 'report') => {
    for (const file of uploadedFiles) {
      try {
        const result = await uploadFile({ file, type });
        console.log('上传成功:', result);
        // 刷新文件列表
        // ...
      } catch (error) {
        console.error('上传失败:', error);
      }
    }
  };

  // 删除单个文件
  const handleDeleteFile = async (fileId: string) => {
    if (confirm('确定要删除这个文件吗？')) {
      try {
        await deleteFile(fileId);
        setFiles(prev => prev.filter(f => f.id !== fileId));
      } catch (error) {
        console.error('删除失败:', error);
      }
    }
  };

  // 批量删除
  const handleDeleteSelected = async () => {
    if (selectedFiles.length === 0) return;

    if (confirm(`确定要删除选中的 ${selectedFiles.length} 个文件吗？`)) {
      try {
        await deleteFilesBatch(selectedFiles);
        setFiles(prev => prev.filter(f => !selectedFiles.includes(f.id)));
        setSelectedFiles([]);
      } catch (error) {
        console.error('批量删除失败:', error);
      }
    }
  };

  return (
    // JSX...
  );
};
```

## 数据流图

```
┌─────────────────┐
│   FileManager   │
│    Component    │
└────────┬────────┘
         │
         ├─ getFiles() ────────► GET /files/
         │                        │
         │                        ◄── FileListResponse
         │
         ├─ uploadFile() ───────► POST /files/upload
         │                        │
         │                        ◄── UploadResponse
         │
         ├─ deleteFile() ────────► DELETE /files/{id}
         │                        │
         │                        ◄── SuccessResponse
         │
         └─ deleteFilesBatch() ─► DELETE /files/batch
                                  │
                                  ◄── BatchDeleteResponse
```

## 待办事项

- [ ] 后端实现 `/files/` 接口
- [ ] 后端实现 `/files/upload` 接口
- [ ] 后端实现 `/files/{id}/download` 接口
- [ ] 后端实现 `/files/{id}` 删除接口
- [ ] 后端实现 `/files/batch` 批量删除接口
- [ ] 创建 `frontend/src/services/files.ts`
- [ ] 更新 FileManager 页面对接真实API
- [ ] 添加错误处理和loading状态
- [ ] 添加文件上传进度显示
