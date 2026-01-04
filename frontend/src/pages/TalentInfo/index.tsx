import React, { useState } from 'react';
import { Search, Filter, Plus, Download } from 'lucide-react';
import TalentCard from '@/components/TalentCard';

const TalentInfo: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterOpen, setFilterOpen] = useState(false);

  // 模拟人才数据
  const mockTalents = [
    {
      name: '张小明',
      position: '前端工程师',
      phone: '138-0000-1234',
      email: 'zhangxm@example.com',
      experience: '5年',
      education: '本科 - 计算机科学与技术',
      skills: ['React', 'Vue', 'TypeScript', 'Node.js', 'Webpack'],
      status: 'active' as const
    },
    {
      name: '李雅静',
      position: 'UI设计师',
      phone: '139-0000-5678',
      email: 'liyj@example.com',
      experience: '3年',
      education: '硕士 - 设计艺术学',
      skills: ['Figma', 'Sketch', 'Photoshop', 'Illustrator', 'After Effects'],
      status: 'active' as const
    },
    {
      name: '王大山',
      position: '产品经理',
      phone: '136-0000-9012',
      email: 'wangds@example.com',
      experience: '7年',
      education: 'MBA - 工商管理',
      skills: ['需求分析', '项目管理', '数据分析', '用户研究', 'Axure'],
      status: 'active' as const
    },
    {
      name: '赵小敏',
      position: '全栈工程师',
      phone: '135-0000-3456',
      email: 'zhaoxm@example.com',
      experience: '6年',
      education: '本科 - 软件工程',
      skills: ['React', 'Node.js', 'Python', 'PostgreSQL', 'Docker'],
      status: 'pending' as const
    }
  ];

  const filteredTalents = mockTalents.filter(talent =>
    talent.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    talent.position.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="p-6">
      {/* 页面头部 */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">人才信息</h1>
            <p className="text-gray-600 mt-1">管理和查看候选人信息</p>
          </div>
          <button className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
            <Plus className="w-4 h-4" />
            <span>添加人才</span>
          </button>
        </div>
      </div>

      {/* 搜索和筛选栏 */}
      <div className="bg-white rounded-lg shadow-sm p-4 mb-6">
        <div className="flex items-center space-x-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="搜索人才姓名或职位..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <button
            onClick={() => setFilterOpen(!filterOpen)}
            className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
              filterOpen ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            <Filter className="w-4 h-4" />
            <span>筛选</span>
          </button>
          <button className="flex items-center space-x-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors">
            <Download className="w-4 h-4" />
            <span>导出</span>
          </button>
        </div>

        {/* 筛选选项 */}
        {filterOpen && (
          <div className="mt-4 pt-4 border-t border-gray-200 grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">职位类型</label>
              <select className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option>全部</option>
                <option>技术类</option>
                <option>设计类</option>
                <option>产品类</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">工作经验</label>
              <select className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option>全部</option>
                <option>1-3年</option>
                <option>3-5年</option>
                <option>5-10年</option>
                <option>10年以上</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">状态</label>
              <select className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option>全部</option>
                <option>在职</option>
                <option>离职</option>
                <option>待定</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">教育程度</label>
              <select className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option>全部</option>
                <option>专科</option>
                <option>本科</option>
                <option>硕士</option>
                <option>博士</option>
              </select>
            </div>
          </div>
        )}
      </div>

      {/* 统计信息 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white rounded-lg shadow-sm p-4">
          <div className="text-sm text-gray-600">总人才数</div>
          <div className="text-2xl font-bold text-gray-900 mt-1">{mockTalents.length}</div>
        </div>
        <div className="bg-white rounded-lg shadow-sm p-4">
          <div className="text-sm text-gray-600">在职</div>
          <div className="text-2xl font-bold text-green-600 mt-1">
            {mockTalents.filter(t => t.status === 'active').length}
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-sm p-4">
          <div className="text-sm text-gray-600">本月新增</div>
          <div className="text-2xl font-bold text-blue-600 mt-1">3</div>
        </div>
        <div className="bg-white rounded-lg shadow-sm p-4">
          <div className="text-sm text-gray-600">待处理</div>
          <div className="text-2xl font-bold text-yellow-600 mt-1">
            {mockTalents.filter(t => t.status === 'pending').length}
          </div>
        </div>
      </div>

      {/* 人才卡片列表 */}
      {filteredTalents.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg shadow-sm">
          <svg className="w-16 h-16 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
          </svg>
          <p className="text-gray-500">未找到匹配的人才信息</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredTalents.map((talent, index) => (
            <TalentCard key={index} {...talent} />
          ))}
        </div>
      )}
    </div>
  );
};

export default TalentInfo;
