import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import clsx from 'clsx';
import {
  HomeIcon,
  DocumentTextIcon,
  UserGroupIcon,
  ChatBubbleLeftRightIcon,
  FolderIcon,
  ChevronRightIcon,
} from '@heroicons/react/24/outline';

interface NavigationItem {
  name: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  current?: boolean;
}

const navigation: NavigationItem[] = [
  { name: '首页', href: '/home', icon: HomeIcon },
  { name: '简历库', href: '/resume-library', icon: DocumentTextIcon },
  { name: '人才信息表', href: '/talent-info', icon: UserGroupIcon },
  { name: 'AI分析对话', href: '/ai-analysis', icon: ChatBubbleLeftRightIcon },
  { name: '文件管理', href: '/file-manager', icon: FolderIcon },
];

interface SidebarProps {
  collapsed?: boolean;
  onToggle?: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ collapsed = false, onToggle }) => {
  const location = useLocation();

  return (
    <nav className={clsx(
      'fixed left-0 top-16 bg-white border-r border-gray-200 h-[calc(100vh-4rem)] transition-all duration-300 ease-in-out flex flex-col shadow-sm z-40',
      collapsed ? 'w-20' : 'w-64'
    )}>
      <div className="flex-1 overflow-y-auto">
        <div className="p-4">
          {!collapsed && (
            <h2 className="px-3 text-xs font-semibold text-gray-500 uppercase tracking-wider mb-4">
              主菜单
            </h2>
          )}
          <ul className="space-y-1">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href;
              return (
                <li key={item.name}>
                  <NavLink
                    to={item.href}
                    className={({ isActive }) =>
                      clsx(
                        'group flex items-center px-3 py-2.5 text-sm font-medium rounded-lg transition-colors',
                        isActive
                          ? 'bg-primary-100 text-primary-700'
                          : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                      )
                    }
                    title={collapsed ? item.name : undefined}
                  >
                    <item.icon
                      className={clsx(
                        'flex-shrink-0',
                        isActive ? 'text-primary-500' : 'text-gray-400 group-hover:text-gray-500',
                        collapsed ? 'h-6 w-6 mx-auto' : 'h-5 w-5 mr-3'
                      )}
                      aria-hidden="true"
                    />
                    {!collapsed && (
                      <>
                        <span className="flex-1">{item.name}</span>
                        {isActive && (
                          <ChevronRightIcon
                            className="h-4 w-4 text-primary-500"
                            aria-hidden="true"
                          />
                        )}
                      </>
                    )}
                  </NavLink>
                </li>
              );
            })}
          </ul>
        </div>
      </div>

      {/* Toggle Button - 固定在底部 */}
      <div className="flex-shrink-0 p-4 border-t border-gray-200 bg-gray-50">
        <button
          onClick={onToggle}
          className={clsx(
            'w-full flex items-center justify-center p-2.5 text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors',
            collapsed && 'px-2'
          )}
          title={collapsed ? '展开侧边栏' : '收起侧边栏'}
        >
          <svg
            className={clsx(
              'h-5 w-5 transition-transform duration-300',
              collapsed ? 'rotate-180' : ''
            )}
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth="2"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M15 19l-7-7 7-7"
            />
          </svg>
          {!collapsed && <span className="ml-2">收起</span>}
        </button>
      </div>
    </nav>
  );
};

export default Sidebar;