import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/common';
import Button from '@/components/common/Button';
import { useAuthStore } from '@/stores/authStore';
import { login as loginUser } from '@/services/auth';
import { useNavigate, useLocation, Link } from 'react-router-dom';

const Login: React.FC = () => {
  const [formData, setFormData] = useState({
    username: 'admin',
    password: 'admin123',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { login } = useAuthStore();
  const navigate = useNavigate();
  const location = useLocation();

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await loginUser(formData);
      const { access_token } = response;

      // 存储 token
      localStorage.setItem('token', access_token);

      // 获取用户信息
      const response2 = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/v1/auth/me`, {
        headers: {
          'Authorization': `Bearer ${access_token}`,
          'Content-Type': 'application/json',
        },
      });
      const userData = await response2.json();

      // 调用 store 的 login 方法
      login(access_token, {
        id: userData.id,
        username: userData.username,
        email: userData.email,
        role: userData.role,
        name: userData.username,
        createdAt: new Date().toISOString(),
      });

      // 存储用户信息到 localStorage
      localStorage.setItem('user', JSON.stringify(userData));

      // 跳转到之前访问的页面或首页
      const from = location.state?.from?.pathname || '/home';
      navigate(from, { replace: true });

    } catch (err: any) {
      setError(err.response?.data?.detail || '登录失败，请检查用户名和密码');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            登录到 AI HR System
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            请输入您的账号信息
          </p>
        </div>
        <Card>
          <CardHeader>
            <CardTitle>登录</CardTitle>
          </CardHeader>
          <CardContent>
            <form className="space-y-4" onSubmit={handleLogin}>
              {error && (
                <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-md text-sm">
                  {error}
                </div>
              )}

              <div>
                <label htmlFor="username" className="block text-sm font-medium text-gray-700">
                  用户名或邮箱
                </label>
                <input
                  id="username"
                  name="username"
                  type="text"
                  autoComplete="username"
                  required
                  value={formData.username}
                  onChange={handleInputChange}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                  placeholder="请输入用户名或邮箱"
                />
              </div>

              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                  密码
                </label>
                <input
                  id="password"
                  name="password"
                  type="password"
                  autoComplete="current-password"
                  required
                  value={formData.password}
                  onChange={handleInputChange}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                  placeholder="请输入密码"
                />
              </div>

              <div className="flex items-center justify-between text-sm">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    className="h-4 w-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                    defaultChecked
                  />
                  <span className="ml-2 text-gray-600">记住我</span>
                </label>
                <a href="#" className="text-primary-600 hover:text-primary-500">
                  忘记密码？
                </a>
              </div>

              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? '登录中...' : '登录'}
              </Button>

              <div className="mt-4 text-center">
                <p className="text-sm text-gray-600">
                  还没有账号？
                  <Link to="/register" className="font-medium text-primary-600 hover:text-primary-500 ml-1">
                    立即注册
                  </Link>
                </p>
              </div>
            </form>

            <div className="mt-6">
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-gray-300" />
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-2 bg-white text-gray-500">默认账户</span>
                </div>
              </div>
              <div className="mt-4 text-center text-sm text-gray-600">
                <p>用户名: <span className="font-medium">admin</span></p>
                <p>密码: <span className="font-medium">admin123</span></p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Login;