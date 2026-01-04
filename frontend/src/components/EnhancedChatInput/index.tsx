import React, { useState, useRef, useEffect } from 'react';

interface EnhancedChatInputProps {
  onSend: (message: string) => void;
  onFileUpload?: () => void;
  onAttachmentUpload?: (file: File) => void;
  disabled?: boolean;
  hasResume?: boolean;
}

const EnhancedChatInput: React.FC<EnhancedChatInputProps> = ({
  onSend,
  onFileUpload,
  onAttachmentUpload,
  disabled = false,
  hasResume = false
}) => {
  const [message, setMessage] = useState('');
  const [isComposing, setIsComposing] = useState(false);
  const [showQuickActions, setShowQuickActions] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // 处理附件上传
  const handleAttachmentSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (disabled || !onAttachmentUpload) return;

    const files = e.target.files;
    if (files && files.length > 0) {
      const file = files[0];
      onAttachmentUpload(file);
      // 清空文件输入
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  // 自动调整文本框高度
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${Math.min(textarea.scrollHeight, 120)}px`;
    }
  }, [message]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !disabled && !isComposing) {
      onSend(message.trim());
      setMessage('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey && !isComposing) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleQuickAction = (action: string) => {
    setMessage(action);
    setShowQuickActions(false);
    textareaRef.current?.focus();
  };

  const handleTemplateSelect = (template: string) => {
    setMessage(template);
    setShowQuickActions(false);
    textareaRef.current?.focus();
  };

  // 快捷操作按钮
  const quickActions = [
    { label: '分析简历', value: '请分析这份简历的综合能力' },
    { label: '匹配职位', value: '根据这份简历，推荐适合的职位' },
    { label: '技能评估', value: '评估候选人的技能水平和发展潜力' },
    { label: '生成报告', value: '生成详细的人才分析报告' },
  ];

  // 模板消息
  const messageTemplates = [
    {
      category: '基础分析',
      templates: [
        '分析这位候选人的工作经验是否符合要求',
        '评估候选人的技能匹配度',
        '分析候选人的教育背景',
      ]
    },
    {
      category: '深度分析',
      templates: [
        '分析候选人的职业发展趋势',
        '评估候选人的管理潜力',
        '分析候选人的薪资期望范围',
      ]
    },
    {
      category: '职位匹配',
      templates: [
        '推荐适合这个背景的技术岗位',
        '分析与高级工程师职位的匹配度',
        '推荐适合的管理岗位',
      ]
    }
  ];

  return (
    <div className="bg-white border-t border-gray-200">
      {/* 快捷操作栏 */}
      <div className="px-4 py-2 border-b border-gray-100">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            {/* 如果没有简历，显示突出的上传按钮 */}
            {!hasResume && onFileUpload ? (
              <button
                type="button"
                onClick={onFileUpload}
                disabled={disabled}
                className="px-3 py-1.5 text-sm bg-green-500 text-white rounded-full hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center space-x-1 animate-pulse"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                <span>上传简历</span>
              </button>
            ) : (
              /* 快捷操作按钮 */
              quickActions.map((action, index) => (
                <button
                  key={index}
                  onClick={() => handleQuickAction(action.value)}
                  disabled={disabled}
                  className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded-full hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {action.label}
                </button>
              ))
            )}
          </div>

          {/* 模板和附件按钮 */}
          <div className="flex items-center space-x-2">
            <button
              type="button"
              onClick={() => setShowQuickActions(!showQuickActions)}
              disabled={disabled}
              className="p-1.5 text-gray-500 hover:text-gray-700 disabled:opacity-50 transition-colors"
              title="模板消息"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            </button>

            {hasResume && onFileUpload && (
              <button
                type="button"
                onClick={onFileUpload}
                disabled={disabled}
                className="p-1.5 text-gray-500 hover:text-green-600 disabled:opacity-50 transition-colors"
                title="重新上传简历"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
                </svg>
              </button>
            )}
          </div>
        </div>

        {/* 模板选择面板 */}
        {showQuickActions && (
          <div className="absolute z-10 mt-2 w-96 bg-white border border-gray-200 rounded-lg shadow-lg">
            <div className="p-4 max-h-64 overflow-y-auto">
              <h3 className="text-sm font-semibold text-gray-900 mb-3">消息模板</h3>
              {messageTemplates.map((group, index) => (
                <div key={index} className="mb-4">
                  <h4 className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-2">
                    {group.category}
                  </h4>
                  <div className="space-y-1">
                    {group.templates.map((template, idx) => (
                      <button
                        key={idx}
                        onClick={() => handleTemplateSelect(template)}
                        className="block w-full text-left px-3 py-2 text-sm text-gray-700 rounded hover:bg-gray-100 transition-colors"
                      >
                        {template}
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* 主输入区域 */}
      <div className="p-4">
        <form onSubmit={handleSubmit} className="flex items-end space-x-3">
          {/* 输入框 */}
          <div className="flex-1 relative">
            <textarea
              ref={textareaRef}
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              onCompositionStart={() => setIsComposing(true)}
              onCompositionEnd={() => setIsComposing(false)}
              placeholder={
                hasResume
                  ? "请描述您想要分析的内容，如：分析简历优势、推荐合适职位等... (Shift+Enter 换行)"
                  : "点击左侧📤上传简历，或在此粘贴简历内容... (Shift+Enter 换行)"
              }
              disabled={disabled}
              rows={1}
              className="w-full resize-none border border-gray-300 rounded-lg px-4 py-3 pr-12 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-50 disabled:text-gray-500"
              style={{ minHeight: '2.5rem', maxHeight: '7rem' }}
            />

            {/* 字符计数 */}
            {message.length > 0 && (
              <div className="absolute bottom-2 right-3 text-xs text-gray-400">
                {message.length}/2000
              </div>
            )}
          </div>

          {/* 上传附件按钮 */}
          {onAttachmentUpload && (
            <>
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.doc,.docx,.txt,.jpg,.jpeg,.png"
                onChange={handleAttachmentSelect}
                disabled={disabled}
                className="hidden"
                id="attachment-input"
              />
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                disabled={disabled}
                className="
                  p-2.5 rounded-lg transition-all duration-200
                  bg-gray-100 text-gray-600 hover:bg-gray-200 hover:text-gray-800
                  disabled:bg-gray-50 disabled:text-gray-400 disabled:cursor-not-allowed
                  focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2
                  flex items-center justify-center
                  group
                "
                title="上传附件"
              >
                <svg className="w-5 h-5 group-hover:scale-110 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                </svg>
              </button>
            </>
          )}

          {/* 发送按钮 */}
          <button
            type="submit"
            disabled={disabled || !message.trim() || isComposing}
            className="
              p-2.5 rounded-lg transition-all duration-200
              bg-blue-600 text-white hover:bg-blue-700
              disabled:bg-gray-300 disabled:cursor-not-allowed
              focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
              group
            "
          >
            <svg className="w-5 h-5 group-hover:scale-110 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          </button>
        </form>

        {/* 底部提示信息 */}
        <div className="mt-3 flex items-center justify-between text-xs text-gray-500">
          <div className="flex items-center space-x-4">
            <span className="flex items-center">
              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              AI 会保护您的隐私
            </span>
            <span>支持中英文对话</span>
          </div>

          {!hasResume && (
            <span className="text-amber-600 flex items-center">
              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
              建议先上传简历以获得更好的分析效果
            </span>
          )}
        </div>
      </div>
    </div>
  );
};

export default EnhancedChatInput;