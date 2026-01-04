import React from 'react';

interface FileItem {
  id: string;
  name: string;
  type: 'resume' | 'attachment' | 'report';
  format: string;
  size: number;
  uploadDate: string;
  lastModified: string;
  status: 'processing' | 'completed' | 'failed';
  }

interface FilePreviewProps {
  file: FileItem;
  onDelete?: (fileId: string) => void;
}

const FilePreview: React.FC<FilePreviewProps> = ({ file, onDelete }) => {
  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
    return (bytes / 1024 / 1024).toFixed(2) + ' MB';
  };

  const getFileIcon = (format: string) => {
    if (format === 'PDF') {
      return <svg className="w-16 h-16 text-red-500" fill="currentColor" viewBox="0 0 24 24">
        <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z" />
      </svg>;
    } else if (format === 'DOCX' || format === 'DOC') {
      return <svg className="w-16 h-16 text-blue-500" fill="currentColor" viewBox="0 0 24 24">
        <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20M8,12H16V14H8V12M8,16H13V18H8V16Z" />
      </svg>;
    } else if (format === 'ZIP') {
      return <svg className="w-16 h-16 text-yellow-600" fill="currentColor" viewBox="0 0 24 24">
        <path d="M20.54,5.23L19.15,3.55C18.88,3.21 18.47,3 18,3H6A2,2 0 0,0 4,5V19A2,2 0 0,0 6,21H18A2,2 0 0,0 20,19V9C20,6.24 20.56,5.7 20.54,5.23M13,9V4.5L18.5,9M7,13H17V15H7M7,17H13V19H7V17Z" />
      </svg>;
    } else {
      return <svg className="w-16 h-16 text-gray-500" fill="currentColor" viewBox="0 0 24 24">
        <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z" />
      </svg>;
    }
  };

  return (
    <div className="flex-1 overflow-y-auto p-6">
      {/* 文件图标和名称 */}
      <div className="text-center mb-6">
        {getFileIcon(file.format)}
        <h2 className="mt-3 text-lg font-semibold text-gray-900 truncate">{file.name}</h2>
      </div>

      {/* 文件基本信息 */}
      <div className="bg-gray-50 rounded-lg p-4 mb-6">
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-gray-600">文件类型</span>
            <p className="font-medium text-gray-900 mt-1">{file.format}</p>
          </div>
          <div>
            <span className="text-gray-600">文件大小</span>
            <p className="font-medium text-gray-900 mt-1">{formatFileSize(file.size)}</p>
          </div>
          <div>
            <span className="text-gray-600">上传日期</span>
            <p className="font-medium text-gray-900 mt-1">{file.uploadDate}</p>
          </div>
          <div>
            <span className="text-gray-600">最后修改</span>
            <p className="font-medium text-gray-900 mt-1">{file.lastModified}</p>
          </div>
        </div>
      </div>

      {/* 操作按钮 */}
      <div className="border-t pt-6">
        <div className="flex space-x-3 mb-3">
          <button className="flex-1 px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center">
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            下载
          </button>
          <button className="flex-1 px-4 py-2 bg-gray-100 text-gray-700 text-sm rounded-lg hover:bg-gray-200 transition-colors flex items-center justify-center">
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m9.032 4.026a9.001 9.001 0 01-7.432 0m9.032-4.026A9.001 9.001 0 0112 3c-4.474 0-8.268 2.943-9.543 7a9.97 9.97 0 011.827 3.342M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            分享
          </button>
        </div>
        {onDelete && (
          <button
            onClick={() => onDelete(file.id)}
            className="w-full px-4 py-2 bg-red-50 text-red-600 text-sm rounded-lg hover:bg-red-100 transition-colors flex items-center justify-center"
          >
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
            删除文件
          </button>
        )}
      </div>
    </div>
  );
};

export default FilePreview;