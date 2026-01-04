import React, { useState } from 'react';

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

const ChatInput: React.FC<ChatInputProps> = ({ onSend, disabled = false }) => {
  const [message, setMessage] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !disabled) {
      onSend(message.trim());
      setMessage('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="bg-white border-t border-gray-200 p-4">
      <form onSubmit={handleSubmit} className="flex items-end space-x-3">
        {/* 输入框 */}
        <div className="flex-1">
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="输入您的问题..."
            disabled={disabled}
            rows={1}
            className="w-full resize-none border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-50 disabled:text-gray-500"
            style={{ minHeight: '2.5rem', maxHeight: '8rem' }}
          />
        </div>

        {/* 发送按钮 */}
        <button
          type="submit"
          disabled={disabled || !message.trim()}
          className="
            p-2 rounded-lg transition-all duration-200
            bg-blue-600 text-white hover:bg-blue-700
            disabled:bg-gray-300 disabled:cursor-not-allowed
            focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
          "
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
          </svg>
        </button>
      </form>

      {/* 快捷操作提示 */}
      <div className="mt-2 flex items-center text-xs text-gray-500">
        <span className="mr-2">快捷操作：</span>
        <button
          className="text-blue-600 hover:text-blue-800 mr-3"
          onClick={() => onSend('分析简历')}
        >
          分析简历
        </button>
        <button
          className="text-blue-600 hover:text-blue-800 mr-3"
          onClick={() => onSend('匹配职位')}
        >
          匹配职位
        </button>
        <button
          className="text-blue-600 hover:text-blue-800"
          onClick={() => onSend('生成报告')}
        >
          生成报告
        </button>
      </div>
    </div>
  );
};

export default ChatInput;