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

interface FileListProps {
  files: FileItem[];
  viewMode: 'grid' | 'list';
  selectedFiles: string[];
  onSelectFile: (file: FileItem) => void;
  onSelectMultiple: (ids: string[]) => void;
  onDeleteFile?: (fileId: string) => void;
  onDownloadFile?: (fileId: string, fileName: string) => void;
}

const FileList: React.FC<FileListProps> = ({
  files,
  viewMode,
  selectedFiles,
  onSelectFile,
  onSelectMultiple,
  onDeleteFile,
  onDownloadFile
}) => {
  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
    return (bytes / 1024 / 1024).toFixed(2) + ' MB';
  };

  const getFileIcon = (_type: string, format: string) => {
    const iconClass = "w-8 h-8";

    if (format === 'PDF') {
      return <svg className={`${iconClass} text-red-500`} fill="currentColor" viewBox="0 0 24 24">
        <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z" />
      </svg>;
    } else if (format === 'DOCX' || format === 'DOC') {
      return <svg className={`${iconClass} text-blue-500`} fill="currentColor" viewBox="0 0 24 24">
        <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20M8,12H16V14H8V12M8,16H13V18H8V16Z" />
      </svg>;
    } else if (format === 'HTML') {
      return <svg className={`${iconClass} text-orange-500`} fill="currentColor" viewBox="0 0 24 24">
        <path d="M12,17.56L16.07,16.43L16.62,10.33H9.38L9.2,8.3H16.8L17,6.31H7L7.56,12.32H14.45L14.22,14.9L12,15.5L9.78,14.9L9.64,13.24H7.64L7.93,16.43L12,17.56M4.07,3H15.93L18.5,16.91L12,22L5.5,16.91L4.07,3Z" />
      </svg>;
    } else if (format === 'ZIP') {
      return <svg className={`${iconClass} text-yellow-600`} fill="currentColor" viewBox="0 0 24 24">
        <path d="M20.54,5.23L19.15,3.55C18.88,3.21 18.47,3 18,3H6A2,2 0 0,0 4,5V19A2,2 0 0,0 6,21H18A2,2 0 0,0 20,19V9C20,6.24 20.56,5.7 20.54,5.23M13,9V4.5L18.5,9M7,13H17V15H7M7,17H13V19H7V17Z" />
      </svg>;
    } else {
      return <svg className={`${iconClass} text-gray-500`} fill="currentColor" viewBox="0 0 24 24">
        <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z" />
      </svg>;
    }
  };

  const handleCheckboxChange = (fileId: string, checked: boolean) => {
    const newSelection = checked
      ? [...selectedFiles, fileId]
      : selectedFiles.filter(id => id !== fileId);
    onSelectMultiple(newSelection);
  };

  const handleSelectAll = (checked: boolean) => {
    const allIds = files.map(f => f.id);
    onSelectMultiple(checked ? allIds : []);
  };

  // 切换文件选中状态
  const toggleFileSelection = (fileId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    const file = files.find(f => f.id === fileId);
    if (!file) return;

    const isSelected = selectedFiles.includes(fileId);

    // Ctrl/Cmd 点击切换多选状态
    if (e.ctrlKey || e.metaKey) {
      const newSelection = isSelected
        ? selectedFiles.filter(id => id !== fileId)
        : [...selectedFiles, fileId];
      onSelectMultiple(newSelection);
    } else {
      // 普通点击：切换当前文件的选中状态并打开预览
      if (isSelected) {
        // 已选中则取消选中
        onSelectMultiple([]);
      } else {
        // 未选中则选中
        onSelectMultiple([fileId]);
        onSelectFile(file);
      }
    }
  };

  if (files.length === 0) {
    return (
      <div className="text-center py-12">
        <svg className="w-16 h-16 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <p className="text-gray-500">暂无文件</p>
      </div>
    );
  }

  if (viewMode === 'list') {
    return (
      <div className="space-y-2">
        {/* 表头 */}
        <div className="flex items-center space-x-4 px-4 py-3 bg-gray-50 rounded-lg">
          <input
            type="checkbox"
            checked={selectedFiles.length === files.length}
            onChange={(e) => handleSelectAll(e.target.checked)}
            className="w-4 h-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
          />
          <div className="flex-1 text-sm font-medium text-gray-700">文件名</div>
          <div className="w-24 text-sm font-medium text-gray-700">类型</div>
          <div className="w-24 text-sm font-medium text-gray-700">大小</div>
          <div className="w-32 text-sm font-medium text-gray-700">上传日期</div>
          <div className="w-24 text-sm font-medium text-gray-700">操作</div>
        </div>

        {/* 文件列表 */}
        {files.map((file) => (
          <div
            key={file.id}
            className={`flex items-center space-x-4 px-4 py-3 bg-white border rounded-lg hover:bg-gray-50 transition-colors ${
              selectedFiles.includes(file.id) ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
            }`}
          >
            <input
              type="checkbox"
              checked={selectedFiles.includes(file.id)}
              onChange={(e) => {
                e.stopPropagation();
                handleCheckboxChange(file.id, e.target.checked);
              }}
              className="w-4 h-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
            />
            <div
              className="flex items-center space-x-3 flex-1 cursor-pointer"
              onClick={(e) => toggleFileSelection(file.id, e)}
            >
              {getFileIcon(file.type, file.format)}
              <div className="flex-1">
                <p className="font-medium text-gray-900">{file.name}</p>
              </div>
            </div>
            <div className="w-24">
              <span className="text-sm text-gray-600">{file.format}</span>
            </div>
            <div className="w-24">
              <span className="text-sm text-gray-600">{formatFileSize(file.size)}</span>
            </div>
            <div className="w-32">
              <span className="text-sm text-gray-600">{file.uploadDate}</span>
            </div>
            <div className="w-24 flex items-center space-x-2">
              <button
                type="button"
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  console.log('列表下载按钮点击:', file.id, file.name);
                  if (onDownloadFile) {
                    onDownloadFile(file.id, file.name);
                  }
                }}
                className="p-1.5 hover:bg-blue-100 rounded transition-colors z-10 relative"
                title="下载"
              >
                <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </button>
              <button
                type="button"
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  if (onDeleteFile) {
                    onDeleteFile(file.id);
                  }
                }}
                className="p-1.5 hover:bg-red-100 rounded transition-colors z-10 relative"
                title="删除"
              >
                <svg className="w-4 h-4 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
          </div>
        ))}
      </div>
    );
  }

  // 网格视图
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 auto-rows-max">
      {files.map((file) => (
        <div
          key={file.id}
          className={`bg-white border rounded-lg p-4 hover:shadow-lg transition-all group w-full h-80 flex flex-col ${
            selectedFiles.includes(file.id) ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
          }`}
          style={{ minWidth: '240px', maxWidth: '280px' }}
        >
          {/* 复选框和操作按钮 */}
          <div className="flex items-center justify-between mb-3">
            <input
              type="checkbox"
              checked={selectedFiles.includes(file.id)}
              onChange={(e) => {
                e.stopPropagation();
                handleCheckboxChange(file.id, e.target.checked);
              }}
              className="w-4 h-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
            />
            <div className="flex space-x-1">
              <button
                type="button"
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  console.log('下载按钮点击:', file.id, file.name);
                  if (onDownloadFile) {
                    onDownloadFile(file.id, file.name);
                  } else {
                    console.error('onDownloadFile 未定义');
                  }
                }}
                className="p-1.5 hover:bg-blue-100 rounded transition-colors z-10 relative"
                title="下载"
              >
                <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </button>
              <button
                type="button"
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  if (onDeleteFile) {
                    onDeleteFile(file.id);
                  }
                }}
                className="p-1.5 hover:bg-red-100 rounded transition-colors z-10 relative"
                title="删除"
              >
                <svg className="w-4 h-4 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
          </div>

          {/* 文件图标和文件信息区域 - 可点击选择 */}
          <div
            className="flex-1 flex flex-col cursor-pointer"
            onClick={(e) => toggleFileSelection(file.id, e)}
          >
            {/* 文件图标 */}
            <div className="flex justify-center mb-3">
              {getFileIcon(file.type, file.format)}
            </div>

            {/* 文件信息 */}
            <div className="flex-1 flex flex-col space-y-2">
              <h3 className="font-medium text-gray-900 text-sm truncate">{file.name}</h3>

              <div className="flex items-center justify-between text-xs text-gray-500">
                <span>{formatFileSize(file.size)}</span>
                <span>{file.uploadDate}</span>
              </div>

              {/* 弹性空间 */}
              <div className="flex-grow"></div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default FileList;