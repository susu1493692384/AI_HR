import React, { useState } from 'react';
import { MessageSquare, Plus, Clock, Star, Trash2, MoreVertical } from 'lucide-react';

interface Conversation {
  id: string;
  title: string;
  lastMessage: string;
  timestamp: string;
  isStarred?: boolean;
  message_count?: number;
}

interface ConversationSidebarProps {
  conversations: Conversation[];
  activeConversationId: string | null;
  onSelectConversation: (id: string) => void;
  onNewConversation: () => void;
  onToggleStar?: (id: string) => void;
  onDeleteConversation?: (id: string, e: React.MouseEvent) => void;
}

const ConversationSidebar: React.FC<ConversationSidebarProps> = ({
  conversations,
  activeConversationId,
  onSelectConversation,
  onNewConversation,
  onToggleStar,
  onDeleteConversation
}) => {
  const [showMenu, setShowMenu] = useState<string | null>(null);

  const handleDelete = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (confirm('确定要删除这个对话吗？')) {
      onDeleteConversation?.(id, e);
    }
    setShowMenu(null);
  };

  return (
    <div className="w-80 bg-white border-r border-gray-200 flex flex-col">
      {/* 头部 */}
      <div className="p-4 border-b border-gray-200">
        <button
          onClick={onNewConversation}
          className="w-full flex items-center justify-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus className="w-4 h-4" />
          <span>新建对话</span>
        </button>
      </div>

      {/* 收藏的对话 */}
      {conversations.some(c => c.isStarred) && (
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center space-x-2 text-sm font-medium text-gray-700 mb-3">
            <Star className="w-4 h-4 text-yellow-500 fill-yellow-500" />
            <span>收藏的对话</span>
          </div>
          <div className="space-y-2">
            {conversations
              .filter(c => c.isStarred)
              .map(conv => (
                <div
                  key={conv.id}
                  onClick={() => onSelectConversation(conv.id)}
                  className={`w-full text-left p-3 rounded-lg transition-colors cursor-pointer relative ${
                    activeConversationId === conv.id
                      ? 'bg-blue-50 border border-blue-200'
                      : 'bg-gray-50 hover:bg-gray-100'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-gray-900 truncate text-sm">{conv.title}</p>
                      <p className="text-xs text-gray-500 truncate mt-1">{conv.lastMessage}</p>
                    </div>
                    <div className="flex items-center space-x-1 ml-2">
                      {onToggleStar && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            onToggleStar(conv.id);
                          }}
                          className="flex-shrink-0"
                        >
                          <Star className="w-4 h-4 text-yellow-500 fill-yellow-500" />
                        </button>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center justify-between mt-2">
                    <div className="flex items-center text-xs text-gray-400">
                      <Clock className="w-3 h-3 mr-1" />
                      <span>{conv.timestamp}</span>
                    </div>
                    {conv.message_count !== undefined && (
                      <span className="text-xs text-gray-400">{conv.message_count} 条消息</span>
                    )}
                  </div>
                </div>
              ))}
          </div>
        </div>
      )}

      {/* 历史对话列表 */}
      <div className="flex-1 overflow-y-auto p-4">
        <div className="flex items-center space-x-2 text-sm font-medium text-gray-700 mb-3">
          <MessageSquare className="w-4 h-4" />
          <span>历史对话</span>
          <span className="text-xs text-gray-400">({conversations.filter(c => !c.isStarred).length})</span>
        </div>
        <div className="space-y-2">
          {conversations
            .filter(c => !c.isStarred)
            .map(conv => (
              <div
                key={conv.id}
                onClick={() => onSelectConversation(conv.id)}
                className={`w-full text-left p-3 rounded-lg transition-colors cursor-pointer relative ${
                  activeConversationId === conv.id
                    ? 'bg-blue-50 border border-blue-200'
                    : 'bg-gray-50 hover:bg-gray-100'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-gray-900 truncate text-sm">{conv.title}</p>
                    <p className="text-xs text-gray-500 truncate mt-1">{conv.lastMessage}</p>
                  </div>
                  <div className="flex items-center space-x-1 ml-2">
                    {onToggleStar && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onToggleStar(conv.id);
                        }}
                        className="flex-shrink-0"
                      >
                        <Star className={`w-4 h-4 ${conv.isStarred ? 'text-yellow-500 fill-yellow-500' : 'text-gray-300 hover:text-yellow-500'}`} />
                      </button>
                    )}
                  </div>
                </div>
                <div className="flex items-center justify-between mt-2">
                  <div className="flex items-center text-xs text-gray-400">
                    <Clock className="w-3 h-3 mr-1" />
                    <span>{conv.timestamp}</span>
                  </div>
                  {conv.message_count !== undefined && (
                    <span className="text-xs text-gray-400">{conv.message_count} 条消息</span>
                  )}
                </div>
              </div>
            ))}
        </div>

        {conversations.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            <MessageSquare className="w-12 h-12 mx-auto mb-3 text-gray-300" />
            <p className="text-sm">还没有对话记录</p>
            <p className="text-xs mt-1">点击上方按钮开始新对话</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ConversationSidebar;
