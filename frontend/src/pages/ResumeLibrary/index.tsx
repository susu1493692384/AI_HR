import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Sparkles } from 'lucide-react';
import { getResumeList, uploadResume, deleteResume, searchResumes, parseResume, getResumeDetail, Resume } from '@/services/resume';
import { conversationsService } from '@/services/conversations';
import ResumeCard from '@/components/ResumeCard';
import UploadModal from '@/components/UploadModal';

const ResumeLibrary: React.FC = () => {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [isSemanticSearch, setIsSemanticSearch] = useState(false);
  const [searchResults, setSearchResults] = useState<Resume[]>([]);
  const [selectedResume, setSelectedResume] = useState<Resume | null>(null);
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);
  const [isCreatingConversation, setIsCreatingConversation] = useState(false);

  const queryClient = useQueryClient();

  // 获取简历列表
  const { data: resumesData, isLoading, refetch } = useQuery({
    queryKey: ['resumes'],
    queryFn: () => getResumeList(),
  });

  // 上传简历 mutation
  const uploadMutation = useMutation({
    mutationFn: uploadResume,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['resumes'] });
      setIsUploadModalOpen(false);
    },
  });

  // 删除简历 mutation
  const deleteMutation = useMutation({
    mutationFn: deleteResume,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['resumes'] });
    },
    onError: (error: any) => {
      if (error.response?.status === 404) {
        alert('简历不存在或已被删除');
        queryClient.invalidateQueries({ queryKey: ['resumes'] });
      } else {
        alert('删除失败：' + (error.response?.data?.detail || error.message));
      }
    },
  });

  // 语义搜索 mutation
  const searchMutation = useMutation({
    mutationFn: (query: string) => searchResumes(query, 10, 0.3),
    onSuccess: (data) => {
      setSearchResults(data.data);
    },
  });

  // 解析简历 mutation
  const parseMutation = useMutation({
    mutationFn: parseResume,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['resumes'] });
      setSelectedResume(data.data);
    },
  });

  // 获取简历详情
  const { data: resumeDetail } = useQuery({
    queryKey: ['resume', selectedResume?.id],
    queryFn: () => getResumeDetail(selectedResume!.id),
    enabled: !!selectedResume?.id && isDetailModalOpen,
  });

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) {
      setSearchResults([]);
      return;
    }

    if (isSemanticSearch) {
      searchMutation.mutate(searchQuery);
    } else {
      // 关键词搜索
      refetch();
    }
  };

  const handleAddResume = () => {
    setIsUploadModalOpen(true);
  };

  const handleCloseUploadModal = () => {
    setIsUploadModalOpen(false);
  };

  const handleUpload = async (file: File) => {
    await uploadMutation.mutateAsync(file);
  };

  const handleDelete = async (id: string) => {
    if (window.confirm('确定要删除这份简历吗？')) {
      await deleteMutation.mutateAsync(id);
    }
  };

  const handleCardClick = async (resume: Resume) => {
    setSelectedResume(resume);
    setIsDetailModalOpen(true);
  };

  const handleParse = async () => {
    if (selectedResume) {
      await parseMutation.mutateAsync(selectedResume.id);
    }
  };

  const handleCloseDetailModal = () => {
    setIsDetailModalOpen(false);
    setSelectedResume(null);
  };

  // AI分析对话功能 - 创建新对话并关联简历
  const handleAIChat = async (resume: Resume) => {
    try {
      setIsCreatingConversation(true);

      // 创建新对话并关联简历
      const newConversation = await conversationsService.createConversation({
        title: `${resume.candidate_name || resume.filename} - AI分析`,
        resume_id: resume.id
      });

      // 跳转到AI分析页面
      navigate(`/ai-analysis/${newConversation.id}`, {
        state: {
          resumeId: resume.id,
          resumeName: resume.candidate_name || resume.filename
        }
      });
    } catch (error) {
      console.error('创建对话失败:', error);
      // 即使创建失败，也跳转到AI分析页面（会自动创建新对话）
      navigate('/ai-analysis');
    } finally {
      setIsCreatingConversation(false);
    }
  };

  // 使用详情数据更新selectedResume
  const currentResume = resumeDetail?.data || selectedResume;

  const resumes = resumesData?.data || [];
  const displayResumes = searchResults.length > 0 || isSemanticSearch ? searchResults : resumes;

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 mb-8">简历库</h1>

      {/* 搜索和操作区域 */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="flex flex-col sm:flex-row gap-4">
          {/* 搜索框 */}
          <form onSubmit={handleSearch} className="flex-1 flex gap-2">
            <div className="relative flex-1">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder={isSemanticSearch ? "输入自然语言搜索，如'有Java经验的工程师'..." : "搜索简历（姓名、职位、技能等）..."}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <svg
                className="absolute left-3 top-2.5 h-5 w-5 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                />
              </svg>
            </div>
            <button
              type="button"
              onClick={() => {
                setIsSemanticSearch(!isSemanticSearch);
                setSearchResults([]);
              }}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                isSemanticSearch
                  ? 'bg-purple-100 text-purple-700 border border-purple-300'
                  : 'bg-gray-100 text-gray-700 border border-gray-300'
              }`}
            >
              {isSemanticSearch ? '语义搜索' : '关键词搜索'}
            </button>
            <button
              type="submit"
              disabled={searchMutation.isPending}
              className="px-6 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors duration-200"
            >
              {searchMutation.isPending ? '搜索中...' : '搜索'}
            </button>
          </form>

          {/* 添加简历按钮 */}
          <button
            onClick={handleAddResume}
            className="px-6 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors duration-200 flex items-center gap-2"
          >
            <svg
              className="h-5 w-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 4v16m8-8H4"
              />
            </svg>
            添加简历
          </button>
        </div>

        {/* 搜索结果提示 */}
        {isSemanticSearch && searchResults.length > 0 && (
          <div className="mt-4 p-3 bg-purple-50 border border-purple-200 rounded-lg">
            <p className="text-sm text-purple-800">
              找到 {searchResults.length} 份相关简历（按相似度排序）
            </p>
          </div>
        )}
      </div>

      {/* 简历列表区域 */}
      <div className="bg-white rounded-lg shadow p-6">
        {isLoading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p className="mt-4 text-gray-600">加载中...</p>
          </div>
        ) : displayResumes.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {displayResumes.map((resume) => (
              <div
                key={resume.id}
                onClick={() => handleCardClick(resume)}
                className="cursor-pointer"
              >
                <ResumeCard
                  resume={resume}
                  onDelete={handleDelete}
                  showSimilarity={isSemanticSearch}
                  onAIChat={handleAIChat}
                />
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <svg
              className="mx-auto h-12 w-12 text-gray-400 mb-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
            <p className="text-gray-600 text-lg">
              {searchQuery ? '未找到匹配的简历' : '暂无简历数据'}
            </p>
            <p className="text-gray-400 mt-2">
              {searchQuery ? '尝试其他搜索关键词' : '点击上方"添加简历"按钮开始添加'}
            </p>
          </div>
        )}
      </div>

      {/* 上传弹窗 */}
      <UploadModal
        isOpen={isUploadModalOpen}
        onClose={handleCloseUploadModal}
        onUpload={handleUpload}
        uploading={uploadMutation.isPending}
      />

      {/* 简历详情弹窗 */}
      {isDetailModalOpen && currentResume && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" onClick={handleCloseDetailModal}>
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
            {/* 弹窗头部 */}
            <div className="flex items-center justify-between p-6 border-b sticky top-0 bg-white">
              <div>
                <h2 className="text-2xl font-semibold text-gray-900">{currentResume.filename}</h2>
                <p className="text-sm text-gray-500 mt-1">
                  上传时间: {new Date(currentResume.upload_time).toLocaleString('zh-CN')}
                </p>
              </div>
              <button
                onClick={handleCloseDetailModal}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* 弹窗内容 */}
            <div className="p-6">
              {/* 状态和操作 */}
              <div className="flex items-center justify-between mb-6">
                <div>
                  {currentResume.status === 'uploaded' && (
                    <span className="px-3 py-1 text-sm font-medium bg-gray-100 text-gray-800 rounded-full">已上传</span>
                  )}
                  {currentResume.status === 'parsing' && (
                    <span className="px-3 py-1 text-sm font-medium bg-yellow-100 text-yellow-800 rounded-full">解析中</span>
                  )}
                  {currentResume.status === 'completed' && (
                    <span className="px-3 py-1 text-sm font-medium bg-green-100 text-green-800 rounded-full">已完成</span>
                  )}
                  {currentResume.status === 'failed' && (
                    <span className="px-3 py-1 text-sm font-medium bg-red-100 text-red-800 rounded-full">失败</span>
                  )}
                </div>
                <div className="flex gap-3">
                  {/* AI分析对话按钮 */}
                  <button
                    onClick={() => handleAIChat(currentResume)}
                    disabled={isCreatingConversation}
                    className="px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-all flex items-center shadow-md hover:shadow-lg"
                  >
                    {isCreatingConversation ? (
                      <>
                        <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        创建中...
                      </>
                    ) : (
                      <>
                        <Sparkles className="w-4 h-4 mr-2" />
                        AI分析对话
                      </>
                    )}
                  </button>

                  {currentResume.status === 'uploaded' && (
                    <button
                      onClick={handleParse}
                      disabled={parseMutation.isPending}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center"
                    >
                      {parseMutation.isPending ? (
                        <>
                          <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                          </svg>
                          解析中...
                        </>
                      ) : (
                        <>
                          <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                          </svg>
                          解析简历
                        </>
                      )}
                    </button>
                  )}
                  <button
                    onClick={() => handleDelete(currentResume.id)}
                    className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                  >
                    删除
                  </button>
                </div>
              </div>

              {/* 候选人信息 */}
              {(currentResume.candidate_name || currentResume.candidate_email || currentResume.candidate_phone || currentResume.candidate_location) && (
                <div className="mb-6 p-4 bg-gray-50 rounded-lg">
                  <h3 className="text-lg font-medium text-gray-900 mb-3">候选人信息</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {currentResume.candidate_name && (
                      <div>
                        <span className="text-sm text-gray-500">姓名:</span>
                        <span className="ml-2 text-gray-900">{currentResume.candidate_name}</span>
                      </div>
                    )}
                    {currentResume.candidate_email && (
                      <div>
                        <span className="text-sm text-gray-500">邮箱:</span>
                        <span className="ml-2 text-gray-900">{currentResume.candidate_email}</span>
                      </div>
                    )}
                    {currentResume.candidate_phone && (
                      <div>
                        <span className="text-sm text-gray-500">电话:</span>
                        <span className="ml-2 text-gray-900">{currentResume.candidate_phone}</span>
                      </div>
                    )}
                    {currentResume.candidate_location && (
                      <div>
                        <span className="text-sm text-gray-500">地点:</span>
                        <span className="ml-2 text-gray-900">{currentResume.candidate_location}</span>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* 提取的文本 */}
              {currentResume.extracted_text && (
                <div className="mb-6">
                  <h3 className="text-lg font-medium text-gray-900 mb-3">简历内容</h3>
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <pre className="whitespace-pre-wrap text-sm text-gray-700 font-sans">
                      {currentResume.extracted_text}
                    </pre>
                  </div>
                </div>
              )}

              {/* 文件信息 */}
              <div className="text-sm text-gray-500">
                <p>文件大小: {(currentResume.file_size / 1024).toFixed(1)} KB</p>
                <p>文件类型: {currentResume.file_type}</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ResumeLibrary;
