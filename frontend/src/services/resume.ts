/**
 * 简历 API 服务
 */

import { api } from './api';

export interface Resume {
  id: string;
  filename: string;
  file_type: string;
  file_size: number;
  upload_time: string;
  status: string;
  candidate_name?: string;
  candidate_email?: string;
  candidate_phone?: string;
  candidate_location?: string;
  extracted_text?: string;
  parsed_content?: any;
}

export interface ResumeUploadResponse {
  code: number;
  data: {
    id: string;
    filename: string;
    status: string;
    candidate_name?: string;
  };
  message: string;
}

export interface ResumeListResponse {
  code: number;
  data: Resume[];
  total: number;
}

/**
 * 上传简历
 */
export const uploadResume = async (file: File): Promise<ResumeUploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post<ResumeUploadResponse>('/resumes/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

/**
 * 解析简历
 */
export const parseResume = async (id: string): Promise<{ code: number; data: Resume; message: string }> => {
  const response = await api.post<{ code: number; data: Resume; message: string }>(`/resumes/${id}/parse`);
  return response.data;
};

/**
 * 获取简历列表
 */
export const getResumeList = async (params?: {
  skip?: number;
  limit?: number;
  keyword?: string;
  status?: string;
}): Promise<ResumeListResponse> => {
  const response = await api.get<ResumeListResponse>('/resumes/', { params });
  return response.data;
};

/**
 * 获取简历详情
 */
export const getResumeDetail = async (id: string): Promise<{ code: number; data: Resume }> => {
  const response = await api.get<{ code: number; data: Resume }>(`/resumes/${id}`);
  return response.data;
};

/**
 * 语义搜索简历
 */
export const searchResumes = async (query: string, topK: number = 10, threshold: number = 0.5) => {
  const formData = new FormData();
  formData.append('query', query);
  formData.append('top_k', topK.toString());
  formData.append('threshold', threshold.toString());

  const response = await api.post('/resumes/search', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

/**
 * 删除简历
 */
export const deleteResume = async (id: string): Promise<{ code: number; message: string }> => {
  const response = await api.delete<{ code: number; message: string }>(`/resumes/${id}`);
  return response.data;
};
