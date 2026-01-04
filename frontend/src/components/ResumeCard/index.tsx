import React from 'react';
import { useNavigate } from 'react-router-dom';
import { MessageSquare, Trash2 } from 'lucide-react';
import { Resume } from '@/services/resume';

interface ResumeCardProps {
  resume: Resume;
  onDelete: (id: string) => void;
  showSimilarity?: boolean;
  onAIChat?: (resume: Resume) => void;
}

const ResumeCard: React.FC<ResumeCardProps> = ({ resume, onDelete, showSimilarity = false, onAIChat }) => {
  const navigate = useNavigate();

  const getStatusBadge = () => {
    switch (resume.status) {
      case 'completed':
        return <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-full">已完成</span>;
      case 'parsing':
        return <span className="px-2 py-1 text-xs font-medium bg-yellow-100 text-yellow-800 rounded-full">解析中</span>;
      case 'embedding':
        return <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded-full">向量化中</span>;
      case 'failed':
        return <span className="px-2 py-1 text-xs font-medium bg-red-100 text-red-800 rounded-full">失败</span>;
      default:
        return <span className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-800 rounded-full">{resume.status}</span>;
    }
  };

  const handleAIChat = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (onAIChat) {
      onAIChat(resume);
    }
  };

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-5 hover:shadow-md transition-shadow">
      {/* 头部信息 */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-2">
            <h3 className="text-lg font-semibold text-gray-900 truncate">
              {resume.candidate_name || '未知姓名'}
            </h3>
            {getStatusBadge()}
          </div>
          <p className="text-sm text-gray-600 truncate">{resume.filename}</p>
        </div>

        {/* 操作按钮 */}
        <div className="flex items-center gap-1 ml-2">
          {/* AI分析对话按钮 */}
          <button
            onClick={handleAIChat}
            className="text-blue-500 hover:text-blue-700 hover:bg-blue-50 p-1.5 rounded-lg transition-all"
            title="AI分析对话"
          >
            <MessageSquare className="h-4 w-4" />
          </button>
          {/* 删除按钮 */}
          <button
            onClick={(e) => {
              e.stopPropagation();
              onDelete(resume.id);
            }}
            className="text-gray-400 hover:text-red-600 hover:bg-red-50 p-1.5 rounded-lg transition-all"
            title="删除"
          >
            <Trash2 className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* 候选人信息 */}
      {(resume.candidate_email || resume.candidate_phone || resume.candidate_location) && (
        <div className="space-y-1 mb-3 pb-3 border-b border-gray-100">
          {resume.candidate_email && (
            <div className="flex items-center text-sm text-gray-600">
              <svg className="h-4 w-4 mr-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
              <span className="truncate">{resume.candidate_email}</span>
            </div>
          )}
          {resume.candidate_phone && (
            <div className="flex items-center text-sm text-gray-600">
              <svg className="h-4 w-4 mr-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 8V5z" />
              </svg>
              <span>{resume.candidate_phone}</span>
            </div>
          )}
          {resume.candidate_location && (
            <div className="flex items-center text-sm text-gray-600">
              <svg className="h-4 w-4 mr-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              <span>{resume.candidate_location}</span>
            </div>
          )}
        </div>
      )}

      {/* 相似度评分（语义搜索时显示） */}
      {showSimilarity && (resume as any).similarity && (
        <div className="mb-3 pb-3 border-b border-gray-100">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">匹配度</span>
            <span className="text-sm font-semibold text-purple-600">
              {Math.round((resume as any).similarity * 100)}%
            </span>
          </div>
          <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-purple-600 h-2 rounded-full transition-all"
              style={{ width: `${(resume as any).similarity * 100}%` }}
            />
          </div>
        </div>
      )}

      {/* 文件信息 */}
      <div className="flex items-center justify-between text-xs text-gray-500">
        <div className="flex items-center gap-4">
          <span>{(resume.file_size / 1024).toFixed(1)} KB</span>
          <span>{resume.file_type}</span>
        </div>
        <span>{new Date(resume.upload_time).toLocaleDateString('zh-CN')}</span>
      </div>
    </div>
  );
};

export default ResumeCard;
