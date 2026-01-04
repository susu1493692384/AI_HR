import { api } from './api';

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface UserInfo {
  id: string;
  username: string;
  email: string;
  role: string;
  is_active: boolean;
}

// 登录
export const login = async (data: LoginRequest): Promise<LoginResponse> => {
  const response = await api.post('/auth/login-json', data);
  return response.data;
};

// 获取当前用户信息
export const getCurrentUser = async (): Promise<UserInfo> => {
  const response = await api.get('/auth/me');
  return response.data;
};

// 登出
export const logout = async (): Promise<void> => {
  await api.post('/auth/logout');
};

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
}

export interface RegisterResponse {
  id: string;
  username: string;
  email: string;
  role: string;
  is_active: boolean;
  created_at: string;
}

// 注册
export const register = async (data: RegisterRequest): Promise<RegisterResponse> => {
  const response = await api.post('/auth/register', data);
  return response.data;
};