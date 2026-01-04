import React from 'react';

interface TalentDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  talent: {
    name: string;
    position: string;
    phone: string;
    email: string;
    experience?: string;
    education?: string;
    skills?: string[];
    status?: 'active' | 'inactive' | 'pending';
    location?: string;
    age?: number;
    salary?: string;
    expectedSalary?: string;
    workHistory?: Array<{
      company: string;
      position: string;
      duration: string;
      description?: string;
    }>;
    projects?: Array<{
      name: string;
      role: string;
      duration: string;
      description: string;
      technologies: string[];
    }>;
    certificates?: string[];
    languages?: Array<{
      language: string;
      level: string;
    }>;
  } | null;
}

const TalentDetailModal: React.FC<TalentDetailModalProps> = ({ isOpen, onClose, talent }) => {
  if (!isOpen || !talent) return null;

  const statusColors = {
    active: 'bg-green-100 text-green-800',
    inactive: 'bg-gray-100 text-gray-800',
    pending: 'bg-yellow-100 text-yellow-800'
  };

  const statusText = {
    active: '在职',
    inactive: '离职',
    pending: '待定'
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* 弹窗头部 */}
        <div className="sticky top-0 bg-white border-b p-6 z-10">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              {/* 头像 */}
              <div className="w-20 h-20 bg-blue-500 rounded-full flex items-center justify-center text-white font-bold text-2xl">
                {talent.name.charAt(0)}
              </div>

              <div>
                <h2 className="text-2xl font-bold text-gray-900">{talent.name}</h2>
                <p className="text-lg text-gray-600">{talent.position}</p>
                <div className="flex items-center gap-3 mt-2">
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${statusColors[talent.status || 'active']}`}>
                    {statusText[talent.status || 'active']}
                  </span>
                  {talent.location && (
                    <span className="text-sm text-gray-500 flex items-center">
                      <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                      </svg>
                      {talent.location}
                    </span>
                  )}
                  {talent.age && (
                    <span className="text-sm text-gray-500">{talent.age}岁</span>
                  )}
                </div>
              </div>
            </div>

            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        {/* 弹窗内容 */}
        <div className="p-6 space-y-6">
          {/* 基本信息 */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                <svg className="w-5 h-5 mr-2 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
                基本信息
              </h3>

              <div className="space-y-3">
                <div className="flex items-center">
                  <span className="text-gray-500 w-20">电话：</span>
                  <span className="text-gray-900">{talent.phone}</span>
                </div>
                <div className="flex items-center">
                  <span className="text-gray-500 w-20">邮箱：</span>
                  <span className="text-gray-900">{talent.email}</span>
                </div>
                {talent.expectedSalary && (
                  <div className="flex items-center">
                    <span className="text-gray-500 w-20">期望薪资：</span>
                    <span className="text-gray-900 font-medium">{talent.expectedSalary}</span>
                  </div>
                )}
              </div>
            </div>

            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                <svg className="w-5 h-5 mr-2 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
                教育背景
              </h3>

              <div className="text-gray-900">
                {talent.education || '暂无信息'}
              </div>
            </div>
          </div>

          {/* 工作经验 */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <svg className="w-5 h-5 mr-2 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
              工作经验
            </h3>

            <div className="text-gray-900">
              {talent.experience || '暂无经验信息'}
            </div>

            {/* 模拟工作历史 */}
            <div className="mt-4 space-y-4">
              <div className="border-l-4 border-blue-500 pl-4">
                <div className="flex items-center justify-between mb-1">
                  <h4 className="font-medium">高级前端工程师</h4>
                  <span className="text-sm text-gray-500">2021.03 - 至今</span>
                </div>
                <p className="text-gray-600 mb-1">阿里巴巴集团</p>
                <p className="text-sm text-gray-500">负责核心业务系统前端开发，带领团队完成多个重点项目</p>
              </div>

              <div className="border-l-4 border-gray-300 pl-4">
                <div className="flex items-center justify-between mb-1">
                  <h4 className="font-medium">前端工程师</h4>
                  <span className="text-sm text-gray-500">2019.07 - 2021.02</span>
                </div>
                <p className="text-gray-600 mb-1">腾讯科技有限公司</p>
                <p className="text-sm text-gray-500">参与微信小程序生态建设，负责开发者工具相关功能开发</p>
              </div>
            </div>
          </div>

          {/* 项目经历 */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <svg className="w-5 h-5 mr-2 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              项目经历
            </h3>

            <div className="space-y-4">
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium text-gray-900">企业级管理平台重构</h4>
                  <span className="text-sm text-gray-500">2022.01 - 2022.06</span>
                </div>
                <p className="text-gray-600 mb-2">担任技术负责人，负责整体架构设计和技术选型</p>
                <div className="flex flex-wrap gap-2">
                  {['React', 'TypeScript', 'Ant Design', 'Redux'].map((tech, index) => (
                    <span key={index} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                      {tech}
                    </span>
                  ))}
                </div>
              </div>

              <div className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium text-gray-900">移动端商城应用</h4>
                  <span className="text-sm text-gray-500">2021.08 - 2021.12</span>
                </div>
                <p className="text-gray-600 mb-2">负责移动端页面开发和性能优化</p>
                <div className="flex flex-wrap gap-2">
                  {['Vue.js', 'Vant', 'Webpack', 'Sass'].map((tech, index) => (
                    <span key={index} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                      {tech}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* 专业技能 */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <svg className="w-5 h-5 mr-2 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
              专业技能
            </h3>

            <div className="flex flex-wrap gap-2">
              {talent.skills?.map((skill, index) => (
                <span
                  key={index}
                  className="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full"
                >
                  {skill}
                </span>
              ))}
            </div>
          </div>

          {/* 证书和语言 */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <svg className="w-5 h-5 mr-2 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
                </svg>
                证书资质
              </h3>

              <div className="space-y-2">
                <div className="flex items-center text-gray-700">
                  <svg className="w-4 h-4 mr-2 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  PMP项目管理认证
                </div>
                <div className="flex items-center text-gray-700">
                  <svg className="w-4 h-4 mr-2 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  AWS云计算认证
                </div>
              </div>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <svg className="w-5 h-5 mr-2 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129" />
                </svg>
                语言能力
              </h3>

              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-gray-700">中文</span>
                  <span className="text-sm text-gray-500">母语</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-700">英语</span>
                  <span className="text-sm text-gray-500">熟练 (CET-6)</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* 弹窗底部 */}
        <div className="sticky bottom-0 bg-white border-t p-6 flex justify-end gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            关闭
          </button>
          <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
            下载简历
          </button>
        </div>
      </div>
    </div>
  );
};

export default TalentDetailModal;