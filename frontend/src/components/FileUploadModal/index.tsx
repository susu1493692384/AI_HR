import React, { useState, useRef } from 'react';

interface FileUploadModalProps {
  onClose: () => void;
  onUpload: (files: File[], type: 'resume' | 'attachment' | 'report') => Promise<void>;
}

const FileUploadModal: React.FC<FileUploadModalProps> = ({ onClose, onUpload }) => {
  const [uploadType, setUploadType] = useState<'resume' | 'attachment' | 'report'>('resume');
  const [files, setFiles] = useState<File[]>([]);
  const [isDragOver, setIsDragOver] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);

    const droppedFiles = Array.from(e.dataTransfer.files);
    handleFilesSelect(droppedFiles);
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = e.target.files;
    if (selectedFiles) {
      handleFilesSelect(Array.from(selectedFiles));
    }
  };

  const handleFilesSelect = (selectedFiles: File[]) => {
    // 验证文件类型
    const validTypes = {
      resume: ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
      attachment: ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                   'application/zip', 'application/x-zip-compressed', 'image/jpeg', 'image/png', 'image/jpg'],
      report: ['application/pdf', 'text/html']
    };

    // 验证文件扩展名
    const validExtensions = {
      resume: ['.pdf', '.doc', '.docx'],
      attachment: ['.pdf', '.doc', '.docx', '.zip', '.jpg', '.jpeg', '.png'],
      report: ['.pdf', '.html', '.htm']
    };

    const maxSize = 10 * 1024 * 1024; // 10MB

    const validFiles = selectedFiles.filter(file => {
      const fileNameLower = file.name.toLowerCase();

      // 检查 MIME 类型或文件扩展名
      const isValidType = validTypes[uploadType].includes(file.type) ||
                          validExtensions[uploadType].some(ext => fileNameLower.endsWith(ext));

      if (!isValidType) {
        alert(`不支持的文件类型: ${file.name}`);
        return false;
      }
      if (file.size > maxSize) {
        alert(`文件太大: ${file.name} (最大10MB)`);
        return false;
      }
      return true;
    });

    setFiles(prev => [...prev, ...validFiles]);
  };

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleUpload = async () => {
    if (files.length === 0) return;

    setIsUploading(true);

    try {
      await onUpload(files, uploadType);
      // 上传成功后关闭模态框
      onClose();
    } catch (error) {
      console.error('上传失败:', error);
      setIsUploading(false);
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
    return (bytes / 1024 / 1024).toFixed(2) + ' MB';
  };

  const getUploadTypeInfo = () => {
    switch (uploadType) {
      case 'resume':
        return {
          title: '上传简历',
          description: '支持 PDF、DOC、DOCX 格式，单文件最大 10MB',
          icon: <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        };
      case 'attachment':
        return {
          title: '上传附件',
          description: '支持 PDF、DOC、DOCX、图片、ZIP 等格式，单文件最大 10MB',
          icon: <svg className="w-8 h-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
          </svg>
        };
      case 'report':
        return {
          title: '上传报告',
          description: '支持 PDF、HTML 格式，单文件最大 10MB',
          icon: <svg className="w-8 h-8 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v1a2 2 0 002 2h6a2 2 0 002-2v-1m-6 4h6m-6 4h6m2 5H7a2 2 0 01-2-2V8a2 2 0 012-2h6l4 4v10" />
          </svg>
        };
    }
  };

  const uploadTypeInfo = getUploadTypeInfo();

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-xl max-w-3xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        {/* 头部 */}
        <div className="flex items-center justify-between p-6 border-b">
          <div className="flex items-center space-x-3">
            {uploadTypeInfo.icon}
            <h2 className="text-xl font-semibold text-gray-900">{uploadTypeInfo.title}</h2>
          </div>
          <button
            onClick={onClose}
            disabled={isUploading}
            className="text-gray-400 hover:text-gray-600 disabled:opacity-50 transition-colors"
          >
            <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* 类型选择 */}
        <div className="px-6 py-4 border-b bg-gray-50">
          <div className="flex space-x-4">
            <button
              onClick={() => setUploadType('resume')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                uploadType === 'resume'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-100'
              }`}
            >
              简历文件
            </button>
            <button
              onClick={() => setUploadType('attachment')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                uploadType === 'attachment'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-100'
              }`}
            >
              附件材料
            </button>
            <button
              onClick={() => setUploadType('report')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                uploadType === 'report'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-100'
              }`}
            >
              分析报告
            </button>
          </div>
        </div>

        {/* 上传区域 */}
        <div className="p-6">
          <div className="mb-4">
            <p className="text-sm text-gray-600">{uploadTypeInfo.description}</p>
          </div>

          <div
            className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
              isDragOver
                ? 'border-blue-400 bg-blue-50'
                : 'border-gray-300 hover:border-gray-400'
            }`}
            onDragEnter={handleDragEnter}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <input
              ref={fileInputRef}
              type="file"
              multiple
              accept={uploadType === 'resume' ? '.pdf,.doc,.docx' :
                     uploadType === 'attachment' ? '.pdf,.doc,.docx,.zip,.jpg,.jpeg,.png' : '.pdf,.html'}
              onChange={handleFileSelect}
              className="hidden"
            />
            <svg className="w-16 h-16 mx-auto mb-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
            <p className="text-lg font-medium text-gray-900 mb-2">
              点击或拖拽文件至此区域上传
            </p>
            <button
              onClick={() => fileInputRef.current?.click()}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              选择文件
            </button>
          </div>

          {/* 文件列表 */}
          {files.length > 0 && (
            <div className="mt-6">
              <h3 className="text-sm font-medium text-gray-900 mb-3">待上传文件 ({files.length})</h3>
              <div className="space-y-2">
                {files.map((file, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                  >
                    <div className="flex items-center space-x-3">
                      <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                      <div>
                        <p className="text-sm font-medium text-gray-900">{file.name}</p>
                        <p className="text-xs text-gray-500">{formatFileSize(file.size)}</p>
                      </div>
                    </div>
                    <button
                      onClick={() => removeFile(index)}
                      className="text-gray-400 hover:text-red-500 transition-colors"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* 底部操作 */}
        <div className="px-6 py-4 border-t bg-gray-50 flex justify-between">
          <div className="text-sm text-gray-600">
            {files.length > 0 && (
              <span>共 {files.length} 个文件，总大小 {formatFileSize(files.reduce((sum, f) => sum + f.size, 0))}</span>
            )}
          </div>
          <div className="flex space-x-3">
            <button
              onClick={onClose}
              disabled={isUploading}
              className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 transition-colors"
            >
              取消
            </button>
            <button
              onClick={handleUpload}
              disabled={files.length === 0 || isUploading}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
            >
              {isUploading ? (
                <div className="flex items-center">
                  <svg className="animate-spin h-5 w-5 mr-2" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth={4} fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  上传中...
                </div>
              ) : (
                '开始上传'
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FileUploadModal;