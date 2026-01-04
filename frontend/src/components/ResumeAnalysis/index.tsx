import React from 'react';
import { FileText } from 'lucide-react';

interface ResumeAnalysisProps {
  resumeData?: {
    name: string;
    position: string;
    experience: string;
    education: string;
    skills: string[];
    score: number;
  };
}

const ResumeAnalysis: React.FC<ResumeAnalysisProps> = ({ resumeData }) => {
  // 如果没有传入简历数据，显示空状态
  if (!resumeData) {
    return (
      <div className="h-full flex flex-col items-center justify-center p-6 text-center">
        <FileText className="w-16 h-16 text-gray-300 mb-4" />
        <h3 className="text-lg font-semibold text-gray-900 mb-2">暂无简历数据</h3>
        <p className="text-sm text-gray-500">
          请先从简历库选择一份简历进行分析
        </p>
      </div>
    );
  }

  const data = resumeData;

  return (
    <div className="h-full flex flex-col bg-white">
      {/* 头部 */}
      <div className="p-6 border-b border-gray-200">
        <h2 className="text-xl font-semibold text-gray-900 mb-2">简历分析</h2>
        <p className="text-sm text-gray-600">当前分析：{data.name} - {data.position}</p>
      </div>

      {/* 内容区域 */}
      <div className="flex-1 overflow-y-auto p-6">
        {/* 总体评分 */}
        {data.score > 0 && (
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6 mb-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">综合评分</h3>
                <p className="text-sm text-gray-600 mt-1">基于技能、经验、教育等综合评估</p>
              </div>
              <div className="text-3xl font-bold text-blue-600">
                {data.score}
                <span className="text-lg text-gray-500">/100</span>
              </div>
            </div>

            {/* 评分进度条 */}
            <div className="mt-4">
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all duration-500"
                  style={{ width: `${data.score}%` }}
                ></div>
              </div>
            </div>
          </div>
        )}

        {/* 基本信息 */}
        <div className="bg-gray-50 rounded-lg p-4 mb-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">基本信息</h3>
          <div className="grid grid-cols-1 gap-3">
            <div className="flex justify-between">
              <span className="text-gray-600">工作经验：</span>
              <span className="font-medium text-gray-900">{data.experience}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">教育背景：</span>
              <span className="font-medium text-gray-900">{data.education}</span>
            </div>
          </div>
        </div>

        {/* 技能标签 */}
        {data.skills && data.skills.length > 0 && (
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">专业技能</h3>
            <div className="flex flex-wrap gap-2">
              {data.skills.map((skill, index) => (
                <span
                  key={index}
                  className="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full"
                >
                  {skill}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* 提示信息 */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-sm text-blue-800">
            💡 提示：请通过左侧对话框与AI助手交流，获取详细的简历分析结果和专业建议。
          </p>
        </div>
      </div>
    </div>
  );
};

export default ResumeAnalysis;