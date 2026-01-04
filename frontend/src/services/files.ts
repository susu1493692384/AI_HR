import { api } from './api';

export interface FileItem {
  id: string;
  name: string;
  type: 'resume' | 'attachment' | 'report';
  format: string;
  size: number;
  uploadDate: string;
  lastModified: string;
  status: 'processing' | 'completed' | 'failed';
}

export interface UploadResponse {
  id: string;
  filename: string;
  status: string;
  file_size: number;
}

export interface FileListResponse {
  code: number;
  data: FileItem[];
  total: number;
}

/**
 * 文件管理服务
 */
export const fileService = {
  /**
   * 上传文件
   */
  async uploadFile(
    file: File,
    type: 'resume' | 'attachment' | 'report'
  ): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post<UploadResponse>('/resumes/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  },

  /**
   * 获取文件列表
   */
  async getFiles(params?: {
    skip?: number;
    limit?: number;
    keyword?: string;
    status?: string;
  }): Promise<FileListResponse> {
    const response = await api.get<FileListResponse>('/resumes/', {
      params: {
        skip: params?.skip || 0,
        limit: params?.limit || 100,
        keyword: params?.keyword,
        status: params?.status,
      },
    });

    // 转换后端数据格式到前端格式
    const data = response.data.data.map((item: any) => ({
      id: item.id,
      name: item.filename,
      type: item.file_type === 'resume' ? 'resume' as const :
            item.file_type === 'attachment' ? 'attachment' as const :
            'report' as const,
      format: item.filename.split('.').pop()?.toUpperCase() || 'UNKNOWN',
      size: item.file_size,
      uploadDate: item.upload_time ? item.upload_time.split('T')[0] : new Date().toISOString().split('T')[0],
      lastModified: item.upload_time ? item.upload_time.split('T')[0] : new Date().toISOString().split('T')[0],
      status: item.status as 'processing' | 'completed' | 'failed',
    }));

    return {
      code: response.data.code,
      data,
      total: response.data.total,
    };
  },

  /**
   * 下载文件
   */
  async downloadFile(fileId: string, filename: string): Promise<void> {
    console.log('开始下载文件:', fileId, filename);
    try {
      const response = await api.get(`/resumes/${fileId}/download`, {
        responseType: 'blob',
      });

      console.log('下载响应:', response);

      // 创建下载链接
      const url = window.URL.createObjectURL(new Blob([response.data], {
        type: response.headers?.['content-type'] || 'application/octet-stream'
      }));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();

      // 清理
      link.remove();
      window.URL.revokeObjectURL(url);
      console.log('文件下载完成:', filename);
    } catch (error) {
      console.error('文件下载失败:', error);
      throw error;
    }
  },

  /**
   * 删除文件
   */
  async deleteFile(fileId: string): Promise<void> {
    await api.delete(`/resumes/${fileId}`);
  },

  /**
   * 获取文件详情
   */
  async getFileDetail(fileId: string): Promise<any> {
    const response = await api.get(`/resumes/${fileId}`);
    return response.data;
  },
};
