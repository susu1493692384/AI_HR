import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  ArrowRightOnRectangleIcon,
  Cog6ToothIcon,
} from '@heroicons/react/24/outline';
import { UserCircleIcon } from '@heroicons/react/24/solid';
import { Menu, MenuButton, MenuItem, MenuItems } from '@headlessui/react';

const Header = () => {
  const navigate = useNavigate();
  const [showLogoutConfirm, setShowLogoutConfirm] = useState(false);

  // ESC 键关闭对话框
  React.useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && showLogoutConfirm) {
        setShowLogoutConfirm(false);
      }
    };

    if (showLogoutConfirm) {
      document.addEventListener('keydown', handleKeyDown);
    }

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [showLogoutConfirm]);

  const handleLogout = () => {
    setShowLogoutConfirm(true);
  };

  const confirmLogout = async () => {
    try {
      // 显示加载状态
      const confirmButton = document.querySelector('[data-confirm-logout]') as HTMLButtonElement;
      if (confirmButton) {
        confirmButton.setAttribute('data-loading', 'true');
        confirmButton.textContent = '退出中...';
        confirmButton.disabled = true;
      }

      // 清除认证信息
      localStorage.removeItem('token');
      localStorage.removeItem('user');

      // 清除可能存在的其他认证相关数据
      localStorage.removeItem('refreshToken');
      localStorage.removeItem('permissions');
      localStorage.removeItem('rememberMe');

      // 调用 store 的 logout 方法
      try {
        const { useAuthStore } = await import('@/stores/authStore');
        const { logout } = useAuthStore.getState();
        logout();
      } catch (error) {
        console.error('Failed to access auth store:', error);
      }

      // 可选：调用后端登出接口（如果有的话）
      // await fetch('/api/auth/logout', { method: 'POST' });

      // 延迟一秒，让用户看到退出效果
      await new Promise(resolve => setTimeout(resolve, 500));

      // 导航到登录页
      navigate('/login', {
        replace: true,
        state: { message: '您已成功退出登录' }
      });

      // 关闭确认对话框
      setShowLogoutConfirm(false);

    } catch (error) {
      console.error('退出登录时发生错误:', error);

      // 恢复按钮状态
      const confirmButton = document.querySelector('[data-confirm-logout]') as HTMLButtonElement;
      if (confirmButton) {
        confirmButton.setAttribute('data-loading', 'false');
        confirmButton.textContent = '确认退出';
        confirmButton.disabled = false;
      }

      // 显示错误提示（可以使用 toast 或其他通知组件）
      alert('退出登录失败，请重试');
    }
  };

  const cancelLogout = () => {
    setShowLogoutConfirm(false);
  };

  return (
    <header className="bg-white border-b border-gray-200 h-16 fixed top-0 left-0 right-0 z-50">
      <div className="h-full px-6 flex items-center justify-between">
        {/* Logo and Brand */}
        <div className="flex items-center space-x-4">
          <Link to="/home" className="flex items-center space-x-3">
            <div className="h-8 w-8 bg-primary-600 rounded-lg flex items-center justify-center">
              <svg
                className="h-5 w-5 text-white"
                fill="none"
                viewBox="0 0 24 24"
                strokeWidth="2"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
                />
              </svg>
            </div>
            <h1 className="text-xl font-bold text-gray-900">AI HR System</h1>
          </Link>
        </div>

        {/* User Menu */}
        <div className="flex items-center space-x-4">
          {/* System Info */}
          <Menu as="div" className="relative">
            <MenuButton className="flex items-center space-x-2 px-3 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors">
              <Cog6ToothIcon className="h-5 w-5" />
              <span>系统信息</span>
            </MenuButton>
            <MenuItems className="dropdown-menu absolute right-0 z-10 mt-2 w-56 origin-top-right rounded-md bg-white shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none">
              <div className="py-1">
                <div className="px-4 py-2 border-b border-gray-100">
                  <p className="text-sm font-medium text-gray-900">系统版本</p>
                  <p className="text-xs text-gray-500">v1.0.0</p>
                </div>
                <MenuItem>
                  <button className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">
                    帮助文档
                  </button>
                </MenuItem>
                <MenuItem>
                  <button className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">
                    关于我们
                  </button>
                </MenuItem>
              </div>
            </MenuItems>
          </Menu>

          {/* User Dropdown */}
          <Menu as="div" className="relative">
            <MenuButton className="flex items-center space-x-2">
              <UserCircleIcon className="h-8 w-8 text-gray-400" />
              <span className="text-sm font-medium text-gray-700">管理员</span>
            </MenuButton>
            <MenuItems className="dropdown-menu absolute right-0 z-10 mt-2 w-56 origin-top-right rounded-md bg-white shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none">
              <div className="py-1">
                <MenuItem>
                  <button
                    onClick={() => navigate('/settings')}
                    className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    个人设置
                  </button>
                </MenuItem>
                <div className="border-t border-gray-100">
                  <MenuItem>
                    <button
                      onClick={handleLogout}
                      className="flex items-center w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                    >
                      <ArrowRightOnRectangleIcon className="mr-2 h-4 w-4" />
                      退出登录
                    </button>
                  </MenuItem>
                </div>
              </div>
            </MenuItems>
          </Menu>
        </div>
      </div>

      {/* 退出登录确认对话框 */}
      {showLogoutConfirm && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
          onClick={(e) => {
            if (e.target === e.currentTarget) {
              cancelLogout();
            }
          }}
        >
          <div className="bg-white rounded-lg p-6 max-w-sm w-full mx-4">
            <div className="flex items-center mb-4">
              <div className="flex-shrink-0 w-12 h-12 rounded-full bg-red-100 flex items-center justify-center">
                <ArrowRightOnRectangleIcon className="h-6 w-6 text-red-600" />
              </div>
              <div className="ml-4">
                <h3 className="text-lg font-medium text-gray-900">确认退出</h3>
                <p className="text-sm text-gray-500 mt-1">
                  您确定要退出登录吗？退出后需要重新登录才能访问系统。
                </p>
              </div>
            </div>
            <div className="flex justify-end space-x-3 mt-6">
              <button
                onClick={cancelLogout}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-colors"
              >
                取消
              </button>
              <button
                onClick={confirmLogout}
                data-confirm-logout
                className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed disabled:bg-gray-400"
              >
                确认退出
              </button>
            </div>
          </div>
        </div>
      )}
    </header>
  );
};

export default Header;