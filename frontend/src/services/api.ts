import axios, { AxiosResponse } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// 开发环境：清除可能存在的旧 token，避免认证问题
if (import.meta.env.DEV) {
  const token = localStorage.getItem('token');
  if (token) {
    // 检查是否是有效的 UUID 格式（简单检查）
    try {
      const parts = token.split('.');
      if (parts.length !== 3) {
        // 不是有效的 JWT 格式，清除
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        console.log('已清除无效的认证信息');
      }
    } catch {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
    }
  }
}

// 创建 axios 实例
export const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器 - 添加认证 token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器 - 处理认证错误
api.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      // Token 过期或无效，清除本地存储并跳转到登录页
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);