import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/common';
import Button from '@/components/common/Button';
import { useAuthStore } from '@/stores/authStore';
import ModelSettings from './ModelSettings';

const UserSettings: React.FC = () => {
  const { user } = useAuthStore();
  const location = useLocation();
  const [activeTab, setActiveTab] = useState('profile');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  // 检查URL参数或state，决定默认打开哪个标签页
  useEffect(() => {
    if (location.state?.tab) {
      setActiveTab(location.state.tab);
    }
  }, [location]);
  const [formData, setFormData] = useState({
    name: user?.name || '',
    email: user?.email || '',
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
    notifications: {
      email: true,
      browser: true,
      resumeAnalysis: true,
      systemUpdates: false,
    },
    theme: 'light',
    language: 'zh-CN',
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const target = e.target as HTMLInputElement;
    const { name, value, type, checked } = target;

    if (name.includes('.')) {
      const [parent, child] = name.split('.');
      setFormData(prev => ({
        ...prev,
        [parent]: {
          ...prev[parent as keyof typeof prev] as any,
          [child]: type === 'checkbox' ? checked : value,
        },
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: type === 'checkbox' ? checked : value,
      }));
    }
  };

  const handleSaveProfile = (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: 实现保存个人信息的逻辑
    console.log('保存个人信息:', formData);
  };

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setMessage('');

    // 验证密码
    if (formData.newPassword !== formData.confirmPassword) {
      setError('两次输入的密码不一致');
      setLoading(false);
      return;
    }

    if (formData.newPassword.length < 6) {
      setError('新密码长度至少为6位');
      setLoading(false);
      return;
    }

    try {
      const token = localStorage.getItem('token');

      const response = await fetch('/api/v1/auth/change-password', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          current_password: formData.currentPassword,
          new_password: formData.newPassword,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || '修改密码失败');
      }

      setMessage('密码修改成功！请使用新密码重新登录。');

      // 清空表单
      setFormData(prev => ({
        ...prev,
        currentPassword: '',
        newPassword: '',
        confirmPassword: '',
      }));

      // 3秒后自动登出，让用户用新密码重新登录
      setTimeout(() => {
        localStorage.clear();
        window.location.href = '/login';
      }, 3000);

    } catch (err: any) {
      setError(err.message || '修改密码失败，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  const handleSavePreferences = (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: 实现保存偏好的逻辑
    console.log('保存偏好设置:', formData);
  };

  const tabs = [
    { id: 'profile', name: '个人信息', icon: '👤' },
    { id: 'security', name: '安全设置', icon: '🔒' },
    { id: 'notifications', name: '通知设置', icon: '🔔' },
    { id: 'preferences', name: '偏好设置', icon: '⚙️' },
    { id: 'models', name: '模型配置', icon: '🤖' },
  ];

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">个人设置</h1>
        <p className="mt-1 text-sm text-gray-600">管理您的个人信息和系统偏好</p>
      </div>

      <div className="flex flex-col lg:flex-row gap-6">
        {/* 侧边栏 */}
        <div className="lg:w-64">
          <Card>
            <CardContent className="p-4">
              <nav className="space-y-1">
                {tabs.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`w-full flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors ${
                      activeTab === tab.id
                        ? 'bg-primary-100 text-primary-700'
                        : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                    }`}
                  >
                    <span className="mr-3 text-lg">{tab.icon}</span>
                    {tab.name}
                  </button>
                ))}
              </nav>
            </CardContent>
          </Card>
        </div>

        {/* 主要内容 */}
        <div className="flex-1">
          {/* 个人信息 */}
          {activeTab === 'profile' && (
            <Card>
              <CardHeader>
                <CardTitle>个人信息</CardTitle>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSaveProfile} className="space-y-6">
                  {/* 头像上传 */}
                  <div className="flex items-center space-x-6">
                    <div className="shrink-0">
                      <img
                        className="h-24 w-24 object-cover rounded-full"
                        src={`https://ui-avatars.com/api/?name=${encodeURIComponent(formData.name)}&background=6366f1&color=fff&size=128`}
                        alt="头像"
                      />
                    </div>
                    <div>
                      <Button type="button" variant="outline">
                        更换头像
                      </Button>
                      <p className="mt-1 text-sm text-gray-500">
                        支持 JPG、PNG 格式，最大 2MB
                      </p>
                    </div>
                  </div>

                  {/* 基本信息 */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        姓名
                      </label>
                      <input
                        type="text"
                        name="name"
                        value={formData.name}
                        onChange={handleInputChange}
                        className="input"
                        placeholder="请输入姓名"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        邮箱地址
                      </label>
                      <input
                        type="email"
                        name="email"
                        value={formData.email}
                        onChange={handleInputChange}
                        className="input"
                        placeholder="请输入邮箱"
                        disabled
                      />
                      <p className="mt-1 text-xs text-gray-500">
                        邮箱地址不可修改，如需更改请联系系统管理员
                      </p>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        部门
                      </label>
                      <input
                        type="text"
                        defaultValue="技术部"
                        className="input"
                        disabled
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        职位
                      </label>
                      <input
                        type="text"
                        defaultValue="系统管理员"
                        className="input"
                        disabled
                      />
                    </div>
                  </div>

                  <div className="flex justify-end">
                    <Button type="submit">保存更改</Button>
                  </div>
                </form>
              </CardContent>
            </Card>
          )}

          {/* 安全设置 */}
          {activeTab === 'security' && (
            <Card>
              <CardHeader>
                <CardTitle>修改密码</CardTitle>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleChangePassword} className="space-y-6">
                  {error && (
                    <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-md text-sm">
                      {error}
                    </div>
                  )}

                  {message && (
                    <div className="bg-green-50 border border-green-200 text-green-600 px-4 py-3 rounded-md text-sm">
                      {message}
                    </div>
                  )}

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      当前密码
                    </label>
                    <input
                      type="password"
                      name="currentPassword"
                      value={formData.currentPassword}
                      onChange={handleInputChange}
                      className="input"
                      placeholder="请输入当前密码"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      新密码
                    </label>
                    <input
                      type="password"
                      name="newPassword"
                      value={formData.newPassword}
                      onChange={handleInputChange}
                      className="input"
                      placeholder="请输入新密码（至少8位）"
                      minLength={8}
                      required
                    />
                    <p className="mt-1 text-xs text-gray-500">
                      密码必须包含大小写字母、数字和特殊字符
                    </p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      确认新密码
                    </label>
                    <input
                      type="password"
                      name="confirmPassword"
                      value={formData.confirmPassword}
                      onChange={handleInputChange}
                      className="input"
                      placeholder="请再次输入新密码"
                      required
                    />
                    {formData.confirmPassword && formData.newPassword !== formData.confirmPassword && (
                      <p className="mt-1 text-xs text-red-500">
                        两次输入的密码不一致
                      </p>
                    )}
                  </div>

                  <div className="flex justify-end space-x-3">
                    <Button type="button" variant="outline" disabled={loading}>
                      取消
                    </Button>
                    <Button type="submit" disabled={loading}>
                      {loading ? '修改中...' : '修改密码'}
                    </Button>
                  </div>
                </form>
              </CardContent>
            </Card>
          )}

          {/* 通知设置 */}
          {activeTab === 'notifications' && (
            <Card>
              <CardHeader>
                <CardTitle>通知设置</CardTitle>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSavePreferences} className="space-y-6">
                  <div className="space-y-4">
                    <h3 className="text-lg font-medium text-gray-900">通知方式</h3>

                    <div className="space-y-3">
                      <label className="flex items-center">
                        <input
                          type="checkbox"
                          name="notifications.email"
                          checked={formData.notifications.email}
                          onChange={handleInputChange}
                          className="h-4 w-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                        />
                        <span className="ml-2 text-sm text-gray-700">
                          邮件通知
                        </span>
                      </label>

                      <label className="flex items-center">
                        <input
                          type="checkbox"
                          name="notifications.browser"
                          checked={formData.notifications.browser}
                          onChange={handleInputChange}
                          className="h-4 w-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                        />
                        <span className="ml-2 text-sm text-gray-700">
                          浏览器通知
                        </span>
                      </label>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <h3 className="text-lg font-medium text-gray-900">通知类型</h3>

                    <div className="space-y-3">
                      <label className="flex items-center justify-between">
                        <div className="flex items-center">
                          <input
                            type="checkbox"
                            name="notifications.resumeAnalysis"
                            checked={formData.notifications.resumeAnalysis}
                            onChange={handleInputChange}
                            className="h-4 w-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                          />
                          <span className="ml-2 text-sm text-gray-700">
                            简历分析完成通知
                          </span>
                        </div>
                        <span className="text-xs text-gray-500">
                          当简历分析完成后通知
                        </span>
                      </label>

                      <label className="flex items-center justify-between">
                        <div className="flex items-center">
                          <input
                            type="checkbox"
                            name="notifications.systemUpdates"
                            checked={formData.notifications.systemUpdates}
                            onChange={handleInputChange}
                            className="h-4 w-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                          />
                          <span className="ml-2 text-sm text-gray-700">
                            系统更新通知
                          </span>
                        </div>
                        <span className="text-xs text-gray-500">
                          系统功能更新时通知
                        </span>
                      </label>
                    </div>
                  </div>

                  <div className="flex justify-end">
                    <Button type="submit">保存设置</Button>
                  </div>
                </form>
              </CardContent>
            </Card>
          )}

          {/* 偏好设置 */}
          {activeTab === 'preferences' && (
            <Card>
              <CardHeader>
                <CardTitle>偏好设置</CardTitle>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSavePreferences} className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        主题模式
                      </label>
                      <select
                        name="theme"
                        value={formData.theme}
                        onChange={handleInputChange}
                        className="input"
                      >
                        <option value="light">浅色模式</option>
                        <option value="dark">深色模式</option>
                        <option value="auto">跟随系统</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        语言设置
                      </label>
                      <select
                        name="language"
                        value={formData.language}
                        onChange={handleInputChange}
                        className="input"
                      >
                        <option value="zh-CN">简体中文</option>
                        <option value="zh-TW">繁体中文</option>
                        <option value="en-US">English</option>
                      </select>
                    </div>
                  </div>

                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h4 className="text-sm font-medium text-gray-900 mb-2">存储空间使用情况</h4>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">已使用</span>
                        <span className="font-medium">256 MB / 10 GB</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div className="bg-primary-600 h-2 rounded-full" style={{ width: '2.56%' }}></div>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <h3 className="text-lg font-medium text-gray-900">数据管理</h3>
                    <div className="flex flex-col sm:flex-row gap-3">
                      <Button type="button" variant="outline">
                        导出个人数据
                      </Button>
                      <Button type="button" variant="outline" className="text-red-600 border-red-300 hover:bg-red-50">
                        删除账户
                      </Button>
                    </div>
                  </div>

                  <div className="flex justify-end">
                    <Button type="submit">保存偏好</Button>
                  </div>
                </form>
              </CardContent>
            </Card>
          )}

          {/* 模型配置 */}
          {activeTab === 'models' && (
            <ModelSettings />
          )}
        </div>
      </div>
    </div>
  );
};

export default UserSettings;