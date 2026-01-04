import React from 'react';

interface MessageBubbleProps {
  message: string;
  isUser: boolean;
  timestamp?: string;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message, isUser, timestamp }) => {
  return (
    <div className={`flex mb-4 ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-[70%] ${isUser ? 'order-2' : 'order-1'}`}>
        {/* AI头像（仅非用户消息显示） */}
        {!isUser && (
          <div className="flex items-center mb-2">
            <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center mr-2">
              <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
              </svg>
            </div>
            <span className="text-sm font-medium text-gray-700">AI助手</span>
          </div>
        )}

        {/* 消息气泡 */}
        <div
          className={`
            px-4 py-3 rounded-2xl shadow-sm
            ${isUser
              ? 'bg-blue-600 text-white rounded-br-sm'
              : 'bg-white border border-gray-200 rounded-bl-sm text-gray-900'
            }
          `}
        >
          <p className="text-sm whitespace-pre-wrap">{message}</p>
        </div>

        {/* 时间戳 */}
        {timestamp && (
          <p className={`text-xs text-gray-500 mt-1 ${isUser ? 'text-right' : 'text-left'}`}>
            {timestamp}
          </p>
        )}
      </div>
    </div>
  );
};

export default MessageBubble;