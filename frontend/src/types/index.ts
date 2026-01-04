// API相关类型
export interface ApiResponse<T> {
  data: T;
  message: string;
  status: number;
}

// 用户相关类型
export interface User {
  id: string;
  email: string;
  name: string;
  username?: string;
  role?: string;
  avatar?: string;
  createdAt: string;
}

// 简历相关类型
export interface Resume {
  id: string;
  name: string;
  fileUrl: string;
  uploadedAt: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  analysis?: ResumeAnalysis;
  metadata?: {
    fileType: string;
    fileSize: number;
  };
}

export interface ResumeAnalysis {
  id: string;
  resumeId: string;
  score: number;
  skills: string[];
  experience: {
    years: number;
    companies: string[];
  };
  education: {
    degree: string;
    school: string;
  };
  recommendations: string[];
  analyzedAt: string;
}

// AI模型相关类型
export interface AIModel {
  id: string;
  name: string;
  provider: string;
  modelName: string;
  isActive: boolean;
  config: {
    apiKey: string;
    baseUrl?: string;
    temperature?: number;
    maxTokens?: number;
  };
  createdAt: string;
}

// 文件管理相关类型
export interface FileItem {
  id: string;
  name: string;
  type: 'file' | 'folder';
  size?: number;
  url?: string;
  createdAt: string;
  updatedAt: string;
}

// UI相关类型
export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message?: string;
  duration?: number;
}

// 路由相关类型
export interface RouteConfig {
  path: string;
  element: React.ComponentType;
  children?: RouteConfig[];
  meta?: {
    title?: string;
    requiresAuth?: boolean;
  };
}