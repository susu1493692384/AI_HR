import React, { useState, useEffect } from 'react';
import { Search, Filter, Grid3x3, List, Upload, FolderOpen, FileText, Image, Archive, X, Trash2, RefreshCw } from 'lucide-react';
import FileList from '@/components/FileList';
import FilePreview from '@/components/FilePreview';
import FileUploadModal from '@/components/FileUploadModal';
import { fileService, FileItem } from '@/services/files';

const FileManager: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [selectedFiles, setSelectedFiles] = useState<string[]>([]);
  const [filterOpen, setFilterOpen] = useState(false);
  const [previewFile, setPreviewFile] = useState<FileItem | null>(null);
  const [showPreview, setShowPreview] = useState(false);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 筛选条件状态
  const [filterType, setFilterType] = useState<'all' | 'resume' | 'attachment' | 'report'>('all');
  const [filterFormat, setFilterFormat] = useState<string>('all');
  const [filterDate, setFilterDate] = useState<string>('all');
  const [filterStatus, setFilterStatus] = useState<string>('all');

  const [files, setFiles] = useState<FileItem[]>([]);

  // 加载文件列表
  const loadFiles = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fileService.getFiles({
        keyword: searchTerm || undefined,
        status: filterStatus !== 'all' ? filterStatus : undefined,
      });
      setFiles(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || '加载文件列表失败');
      console.error('加载文件列表失败:', err);
    } finally {
      setLoading(false);
    }
  };

  // 初始加载和搜索时重新加载
  useEffect(() => {
    loadFiles();
  }, []);

  // 防抖搜索
  useEffect(() => {
    const timer = setTimeout(() => {
      loadFiles();
    }, 500);
    return () => clearTimeout(timer);
  }, [searchTerm]);

  // 获取筛选后的文件列表
  const filteredFiles = files.filter(file => {
    // 搜索关键词筛选
    const matchesSearch = file.name.toLowerCase().includes(searchTerm.toLowerCase());

    // 文件类型筛选
    const matchesType = filterType === 'all' || file.type === filterType;

    // 文件格式筛选
    const matchesFormat = filterFormat === 'all' || file.format === filterFormat;

    // 状态筛选
    const matchesStatus = filterStatus === 'all' || file.status === filterStatus;

    // 日期筛选
    let matchesDate = true;
    if (filterDate !== 'all') {
      const fileDate = new Date(file.uploadDate);
      const today = new Date();
      today.setHours(0, 0, 0, 0);

      if (filterDate === 'today') {
        const todayStr = today.toISOString().split('T')[0];
        matchesDate = file.uploadDate === todayStr;
      } else if (filterDate === 'week') {
        const weekAgo = new Date(today);
        weekAgo.setDate(weekAgo.getDate() - 7);
        matchesDate = fileDate >= weekAgo;
      } else if (filterDate === 'month') {
        const monthAgo = new Date(today);
        monthAgo.setDate(monthAgo.getDate() - 30);
        matchesDate = fileDate >= monthAgo;
      }
    }

    return matchesSearch && matchesType && matchesFormat && matchesStatus && matchesDate;
  });

  // 重置筛选
  const handleResetFilters = () => {
    setFilterType('all');
    setFilterFormat('all');
    setFilterDate('all');
    setFilterStatus('all');
    setSearchTerm('');
  };

  // 检查是否有筛选条件
  const hasActiveFilters = filterType !== 'all' || filterFormat !== 'all' ||
                           filterDate !== 'all' || filterStatus !== 'all' ||
                           searchTerm !== '';

  // 获取可用的文件格式选项（基于当前文件）
  const availableFormats = Array.from(new Set(files.map(f => f.format))).sort();

  const handleUpload = async (uploadedFiles: File[], type: 'resume' | 'attachment' | 'report') => {
    setLoading(true);
    setError(null);

    try {
      // 逐个上传文件
      for (const file of uploadedFiles) {
        await fileService.uploadFile(file, type);
      }

      // 上传完成后重新加载文件列表
      await loadFiles();
    } catch (err: any) {
      setError(err.response?.data?.detail || '文件上传失败');
      console.error('文件上传失败:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectFile = (file: FileItem) => {
    setPreviewFile(file);
    setShowPreview(true);
  };

  const handleClosePreview = () => {
    setShowPreview(false);
  };

  const handleSelectMultiple = (ids: string[]) => {
    setSelectedFiles(ids);
  };

  // 下载文件
  const handleDownloadFile = async (fileId: string, fileName: string) => {
    try {
      await fileService.downloadFile(fileId, fileName);
    } catch (err: any) {
      setError(err.response?.data?.detail || '下载文件失败');
      console.error('下载文件失败:', err);
    }
  };

  // 删除单个文件
  const handleDeleteFile = async (fileId: string) => {
    if (confirm('确定要删除这个文件吗？此操作不可恢复。')) {
      setLoading(true);
      setError(null);
      try {
        await fileService.deleteFile(fileId);
        // 重新加载文件列表
        await loadFiles();

        // 如果删除的是当前预览的文件，关闭预览
        if (previewFile?.id === fileId) {
          setShowPreview(false);
          setPreviewFile(null);
        }

        setSelectedFiles(prev => prev.filter(id => id !== fileId));
      } catch (err: any) {
        setError(err.response?.data?.detail || '删除文件失败');
        console.error('删除文件失败:', err);
      } finally {
        setLoading(false);
      }
    }
  };

  // 批量删除选中的文件
  const handleDeleteSelected = async () => {
    if (selectedFiles.length === 0) return;

    if (confirm(`确定要删除选中的 ${selectedFiles.length} 个文件吗？此操作不可恢复。`)) {
      setLoading(true);
      setError(null);
      try {
        // 逐个删除文件
        for (const fileId of selectedFiles) {
          await fileService.deleteFile(fileId);
        }

        // 重新加载文件列表
        await loadFiles();

        // 如果删除的文件包含当前预览的文件，关闭预览
        if (previewFile && selectedFiles.includes(previewFile.id)) {
          setShowPreview(false);
          setPreviewFile(null);
        }

        setSelectedFiles([]);
      } catch (err: any) {
        setError(err.response?.data?.detail || '批量删除失败');
        console.error('批量删除失败:', err);
      } finally {
        setLoading(false);
      }
    }
  };

  return (
    <div className="flex">
      {/* 主内容区域 */}
      <div className={`flex-1 transition-all duration-300 ${showPreview ? 'pr-96' : ''}`}>
        <div className="p-6">
      {/* 页面头部 */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">文件管理</h1>
            <p className="text-gray-600 mt-1">管理简历、附件和报告文件</p>
          </div>
          <div className="flex items-center space-x-3">
            <button
              onClick={loadFiles}
              disabled={loading}
              className="flex items-center space-x-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors disabled:opacity-50"
              title="刷新"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              <span>刷新</span>
            </button>
            {selectedFiles.length > 0 && (
              <button
                onClick={handleDeleteSelected}
                disabled={loading}
                className="flex items-center space-x-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50"
              >
                <Trash2 className="w-4 h-4" />
                <span>删除选中 ({selectedFiles.length})</span>
              </button>
            )}
            <button
              onClick={() => setShowUploadModal(true)}
              disabled={loading}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
            >
              <Upload className="w-4 h-4" />
              <span>上传文件</span>
            </button>
          </div>
        </div>
        {/* 错误提示 */}
        {error && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-center">
              <svg className="w-5 h-5 text-red-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
              <span className="text-red-700">{error}</span>
              <button
                onClick={() => setError(null)}
                className="ml-auto text-red-600 hover:text-red-700"
              >
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              </button>
            </div>
          </div>
        )}
      </div>

      {/* 搜索和工具栏 */}
      <div className="bg-white rounded-lg shadow-sm p-4 mb-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4 flex-1">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="搜索文件名..."
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
          </div>

          {/* 视图切换 */}
          <div className="flex items-center space-x-2 ml-4">
            <button
              onClick={() => setViewMode('grid')}
              className={`p-2 rounded-lg transition-colors ${
                viewMode === 'grid' ? 'bg-blue-100 text-blue-600' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              <Grid3x3 className="w-4 h-4" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`p-2 rounded-lg transition-colors ${
                viewMode === 'list' ? 'bg-blue-100 text-blue-600' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              <List className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* 筛选选项 */}
        {filterOpen && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">文件类型</label>
                <select
                  value={filterType}
                  onChange={(e) => setFilterType(e.target.value as any)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="all">全部</option>
                  <option value="resume">简历</option>
                  <option value="attachment">附件</option>
                  <option value="report">报告</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">文件格式</label>
                <select
                  value={filterFormat}
                  onChange={(e) => setFilterFormat(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="all">全部</option>
                  {availableFormats.map(format => (
                    <option key={format} value={format}>{format}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">上传日期</label>
                <select
                  value={filterDate}
                  onChange={(e) => setFilterDate(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="all">全部</option>
                  <option value="today">今天</option>
                  <option value="week">最近7天</option>
                  <option value="month">最近30天</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">状态</label>
                <select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="all">全部</option>
                  <option value="completed">已完成</option>
                  <option value="processing">处理中</option>
                  <option value="failed">失败</option>
                </select>
              </div>
            </div>

            {/* 筛选结果和重置按钮 */}
            <div className="flex items-center justify-between mt-4">
              <div className="text-sm text-gray-600">
                {hasActiveFilters ? (
                  <span>找到 <span className="font-semibold text-blue-600">{filteredFiles.length}</span> 个文件</span>
                ) : (
                  <span>共 <span className="font-semibold">{files.length}</span> 个文件</span>
                )}
              </div>
              {hasActiveFilters && (
                <button
                  onClick={handleResetFilters}
                  className="flex items-center space-x-1 text-sm text-blue-600 hover:text-blue-700 transition-colors"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  <span>重置筛选</span>
                </button>
              )}
            </div>

            {/* 活跃筛选标签 */}
            {hasActiveFilters && (
              <div className="flex flex-wrap gap-2 mt-3">
                {filterType !== 'all' && (
                  <span className="inline-flex items-center px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full">
                    类型: {filterType === 'resume' ? '简历' : filterType === 'attachment' ? '附件' : '报告'}
                    <button
                      onClick={() => setFilterType('all')}
                      className="ml-1 hover:text-blue-900"
                    >
                      <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </span>
                )}
                {filterFormat !== 'all' && (
                  <span className="inline-flex items-center px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full">
                    格式: {filterFormat}
                    <button
                      onClick={() => setFilterFormat('all')}
                      className="ml-1 hover:text-blue-900"
                    >
                      <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </span>
                )}
                {filterDate !== 'all' && (
                  <span className="inline-flex items-center px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full">
                    日期: {filterDate === 'today' ? '今天' : filterDate === 'week' ? '最近7天' : '最近30天'}
                    <button
                      onClick={() => setFilterDate('all')}
                      className="ml-1 hover:text-blue-900"
                    >
                      <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </span>
                )}
                {filterStatus !== 'all' && (
                  <span className="inline-flex items-center px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full">
                    状态: {filterStatus === 'completed' ? '已完成' : filterStatus === 'processing' ? '处理中' : '失败'}
                    <button
                      onClick={() => setFilterStatus('all')}
                      className="ml-1 hover:text-blue-900"
                    >
                      <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </span>
                )}
                {searchTerm && (
                  <span className="inline-flex items-center px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full">
                    搜索: "{searchTerm}"
                    <button
                      onClick={() => setSearchTerm('')}
                      className="ml-1 hover:text-blue-900"
                    >
                      <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </span>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      {/* 统计信息 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white rounded-lg shadow-sm p-4">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <FileText className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <div className="text-sm text-gray-600">总文件数</div>
              <div className="text-2xl font-bold text-gray-900 mt-1">{files.length}</div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-sm p-4">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <FileText className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <div className="text-sm text-gray-600">简历文件</div>
              <div className="text-2xl font-bold text-gray-900 mt-1">
                {files.filter(f => f.type === 'resume').length}
              </div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-sm p-4">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center">
              <Archive className="w-5 h-5 text-yellow-600" />
            </div>
            <div>
              <div className="text-sm text-gray-600">附件文件</div>
              <div className="text-2xl font-bold text-gray-900 mt-1">
                {files.filter(f => f.type === 'attachment').length}
              </div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-sm p-4">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
              <Image className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <div className="text-sm text-gray-600">总存储</div>
              <div className="text-2xl font-bold text-gray-900 mt-1">32 MB</div>
            </div>
          </div>
        </div>
      </div>

      {/* 快捷文件夹 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <button className="flex items-center space-x-3 p-4 bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow">
          <FolderOpen className="w-8 h-8 text-blue-500" />
          <div className="text-left">
            <div className="font-medium text-gray-900">全部文件</div>
            <div className="text-sm text-gray-500">{files.length} 个文件</div>
          </div>
        </button>
        <button className="flex items-center space-x-3 p-4 bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow">
          <FileText className="w-8 h-8 text-green-500" />
          <div className="text-left">
            <div className="font-medium text-gray-900">简历库</div>
            <div className="text-sm text-gray-500">{files.filter(f => f.type === 'resume').length} 个文件</div>
          </div>
        </button>
        <button className="flex items-center space-x-3 p-4 bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow">
          <Archive className="w-8 h-8 text-yellow-500" />
          <div className="text-left">
            <div className="font-medium text-gray-900">附件</div>
            <div className="text-sm text-gray-500">{files.filter(f => f.type === 'attachment').length} 个文件</div>
          </div>
        </button>
        <button className="flex items-center space-x-3 p-4 bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow">
          <Image className="w-8 h-8 text-purple-500" />
          <div className="text-left">
            <div className="font-medium text-gray-900">分析报告</div>
            <div className="text-sm text-gray-500">{files.filter(f => f.type === 'report').length} 个文件</div>
          </div>
        </button>
      </div>

      {/* 文件列表 */}
      <div className="bg-white rounded-lg shadow-sm">
        <FileList
          files={filteredFiles}
          viewMode={viewMode}
          selectedFiles={selectedFiles}
          onSelectFile={handleSelectFile}
          onSelectMultiple={handleSelectMultiple}
          onDeleteFile={handleDeleteFile}
          onDownloadFile={handleDownloadFile}
        />
      </div>
        </div>
      </div>

      {/* 文件预览侧边栏 */}
      {showPreview && previewFile && (
        <div className="fixed right-0 top-16 w-96 h-[calc(100vh-4rem)] bg-white border-l border-gray-200 shadow-xl transform transition-transform duration-300 z-40">
          {/* 头部 */}
          <div className="flex items-center justify-between p-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">文件预览</h3>
            <button
              onClick={handleClosePreview}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <X className="w-5 h-5 text-gray-600" />
            </button>
          </div>

          {/* 预览内容 */}
          <FilePreview file={previewFile} onDelete={handleDeleteFile} />
        </div>
      )}

      {/* 上传文件模态框 */}
      {showUploadModal && (
        <FileUploadModal
          onClose={() => setShowUploadModal(false)}
          onUpload={handleUpload}
        />
      )}
    </div>
  );
};

export default FileManager;
