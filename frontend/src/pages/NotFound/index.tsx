import React from 'react';
import { Link } from 'react-router-dom';
import Button from '@/components/common/Button';

const NotFound: React.FC = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <h1 className="text-9xl font-bold text-primary-600">404</h1>
        <h2 className="mt-4 text-3xl font-bold text-gray-900">页面未找到</h2>
        <p className="mt-2 text-base text-gray-600">抱歉，您访问的页面不存在。</p>
        <div className="mt-6">
          <Link to="/home">
            <Button>返回首页</Button>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default NotFound;