import React, { useState, useEffect } from 'react';
import { Outlet } from 'react-router-dom';
import Header from './Header';
import Sidebar from './Sidebar';

const Layout: React.FC = () => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(() => {
    // 从localStorage读取侧边栏状态
    const saved = localStorage.getItem('sidebarCollapsed');
    return saved ? JSON.parse(saved) : false;
  });

  useEffect(() => {
    // 保存侧边栏状态到localStorage
    localStorage.setItem('sidebarCollapsed', JSON.stringify(sidebarCollapsed));
  }, [sidebarCollapsed]);

  const handleSidebarToggle = () => {
    setSidebarCollapsed(!sidebarCollapsed);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <div className="pt-16">
        <Sidebar collapsed={sidebarCollapsed} onToggle={handleSidebarToggle} />
        <main
          className={`
            transition-all duration-300
            ${sidebarCollapsed ? 'ml-20' : 'ml-64'}
          `}
        >
          <div className="main-content p-6">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
};

export default Layout;