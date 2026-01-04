# AI对话功能对接文档

## 功能概述

AI分析对话模块提供：
- AI简历分析对话
- 对话历史管理
- 实时简历评分报告
- 多轮对话交互

## 前端实现状态

### 已实现功能

| 功能 | 状态 | 说明 |
|------|------|------|
| 三栏布局 | ✅ | 侧边栏 + 对话区 + 简历报告 |
| 对话历史侧边栏 | ✅ | 显示、新建、切换、收藏对话 |
| 消息展示 | ✅ | 用户/AI消息气泡 |
| 快捷问题 | ✅ | 预设问题按钮 |
| 简历评分报告 | ✅ | 右侧实时显示 |
| 路由支持 | ✅ | `/ai-analysis/:id` |

### 页面文件

```
frontend/src/pages/AIAnalysis/index.tsx
```

### 组件文件

```
frontend/src/components/
├── ConversationSidebar/index.tsx  # 对话历史侧边栏
├── ResumeAnalysis/index.tsx       # 简历评分报告
└── MessageBubble/index.tsx        # 消息气泡
```

## 后端接口对接

### 需要的后端接口

| 方法 | 路径 | 描述 | 认证 |
|------|------|------|------|
| GET | `/conversations/` | 获取对话列表 | 是 |
| POST | `/conversations/` | 创建新对话 | 是 |
| GET | `/conversations/{id}` | 获取对话详情 | 是 |
| DELETE | `/conversations/{id}` | 删除对话 | 是 |
| POST | `/conversations/{id}/messages` | 发送消息 | 是 |
| GET | `/conversations/{id}/messages` | 获取消息历史 | 是 |
| POST | `/conversations/{id}/star` | 收藏/取消收藏 | 是 |
| POST | `/analyze/resume` | AI简历分析 | 是 |

### 请求/响应格式

**1. 对话列表**

```typescript
// 请求
GET /api/v1/conversations/

// 响应
interface Conversation {
  id: string;
  title: string;
  last_message: string;
  timestamp: string;
  is_starred: boolean;
  message_count: number;
}

interface ConversationListResponse {
  items: Conversation[];
  total: number;
}
```

**2. 创建对话**

```typescript
// 请求
POST /api/v1/conversations/
{
  title?: string;  // 可选，默认"新对话"
  resume_id?: string;  // 关联的简历ID
}

// 响应
{
  id: string;
  title: string;
  created_at: string;
}
```

**3. 发送消息**

```typescript
// 请求
POST /api/v1/conversations/{id}/messages
{
  content: string;
  resume_id?: string;
}

// 响应（流式返回）
interface MessageResponse {
  id: string;
  conversation_id: string;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
}

// 建议使用SSE或WebSocket实现流式响应
```

**4. AI简历分析**

```typescript
// 请求
POST /api/v1/analyze/resume
{
  resume_id: string;
  conversation_id?: string;
  question?: string;  // 用户问题，可选
}

// 响应
interface AnalysisResponse {
  analysis: {
    score: number;
    skills: string[];
    experience: string;
    education: string;
    summary: string;
    recommendations: string[];
  };
  message_id: string;
}
```

**5. 简历评分数据**

```typescript
interface ResumeScore {
  name: string;
  position: string;
  experience: string;
  education: string;
  skills: string[];
  score: number;           // 0-100
  skill_analysis: string;
  experience_analysis: string;
  recommendations: string[];
}
```

## 前端服务层对接

### 创建对话服务

创建 `frontend/src/services/conversations.ts`：

```typescript
import { api } from './api';

export interface Conversation {
  id: string;
  title: string;
  last_message: string;
  timestamp: string;
  is_starred: boolean;
  message_count: number;
}

export interface Message {
  id: string;
  conversation_id: string;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
}

export interface ResumeScore {
  name: string;
  position: string;
  experience: string;
  education: string;
  skills: string[];
  score: number;
  skill_analysis: string;
  experience_analysis: string;
  recommendations: string[];
}

// 获取对话列表
export const getConversations = async (): Promise<Conversation[]> => {
  const response = await api.get('/conversations/');
  return response.data;
};

// 创建新对话
export const createConversation = async (data?: {
  title?: string;
  resume_id?: string;
}): Promise<Conversation> => {
  const response = await api.post('/conversations/', data);
  return response.data;
};

// 获取对话详情
export const getConversation = async (id: string): Promise<Conversation> => {
  const response = await api.get(`/conversations/${id}`);
  return response.data;
};

// 删除对话
export const deleteConversation = async (id: string) => {
  await api.delete(`/conversations/${id}`);
};

// 收藏/取消收藏
export const toggleStar = async (id: string) => {
  await api.post(`/conversations/${id}/star`);
};

// 获取消息历史
export const getMessages = async (conversationId: string): Promise<Message[]> => {
  const response = await api.get(`/conversations/${conversationId}/messages`);
  return response.data;
};

// 发送消息（流式）
export const sendMessage = async (
  conversationId: string,
  content: string,
  onResume: (chunk: string) => void,
  onComplete: (message: Message) => void
) => {
  const response = await api.post(
    `/conversations/${conversationId}/messages`,
    { content },
    {
      responseType: 'text',
      onDownloadProgress: (progressEvent) => {
        const chunk = progressEvent.currentTarget.responseText;
        onResume(chunk);
      }
    }
  );
  onComplete(response.data);
};

// AI简历分析
export const analyzeResume = async (data: {
  resume_id: string;
  conversation_id?: string;
  question?: string;
}): Promise<{ analysis: ResumeScore; message_id: string }> => {
  const response = await api.post('/analyze/resume', data);
  return response.data;
};
```

### 更新AIAnalysis页面

```typescript
// frontend/src/pages/AIAnalysis/index.tsx

import {
  getConversations,
  createConversation,
  deleteConversation,
  toggleStar,
  getMessages,
  sendMessage,
  analyzeResume
} from '@/services/conversations';

const AIAnalysis: React.FC = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<string | null>(id || null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);

  // 获取对话列表
  useEffect(() => {
    const fetchConversations = async () => {
      try {
        const data = await getConversations();
        setConversations(data);
      } catch (error) {
        console.error('获取对话列表失败:', error);
      }
    };
    fetchConversations();
  }, []);

  // 获取消息历史
  useEffect(() => {
    if (activeConversationId) {
      const fetchMessages = async () => {
        try {
          const data = await getMessages(activeConversationId);
          setMessages(data);
        } catch (error) {
          console.error('获取消息失败:', error);
        }
      };
      fetchMessages();
    }
  }, [activeConversationId]);

  // 创建新对话
  const handleNewConversation = async () => {
    try {
      const newConv = await createConversation({
        title: '新对话'
      });
      setConversations(prev => [newConv, ...prev]);
      setActiveConversationId(newConv.id);
      navigate(`/ai-analysis/${newConv.id}`);
    } catch (error) {
      console.error('创建对话失败:', error);
    }
  };

  // 发送消息
  const handleSendMessage = async () => {
    if (!inputValue.trim() || !activeConversationId) return;

    const userMessage = inputValue.trim();
    setMessages(prev => [...prev, {
      id: Date.now().toString(),
      conversation_id: activeConversationId,
      role: 'user',
      content: userMessage,
      created_at: new Date().toISOString()
    }]);

    setInputValue('');
    setLoading(true);

    try {
      await sendMessage(
        activeConversationId,
        userMessage,
        (chunk) => {
          // 处理流式响应
          setMessages(prev => {
            const newMessages = [...prev];
            const lastMessage = newMessages[newMessages.length - 1];
            if (lastMessage?.role === 'assistant') {
              lastMessage.content += chunk;
            } else {
              newMessages.push({
                id: Date.now().toString(),
                conversation_id: activeConversationId,
                role: 'assistant',
                content: chunk,
                created_at: new Date().toISOString()
              });
            }
            return newMessages;
          });
        },
        (message) => {
          setLoading(false);
        }
      );
    } catch (error) {
      console.error('发送消息失败:', error);
      setLoading(false);
    }
  };

  return (
    // JSX...
  );
};
```

## 流式响应实现

### 使用EventSource (SSE)

```typescript
export const sendMessageStream = (
  conversationId: string,
  content: string
): EventSource => {
  const url = `${API_BASE_URL}/api/v1/conversations/${conversationId}/messages`;
  const token = localStorage.getItem('token');

  const eventSource = new EventSource(
    `${url}?token=${token}&content=${encodeURIComponent(content)}`
  );

  return eventSource;
};

// 使用示例
const eventSource = sendMessageStream(conversationId, inputValue);

eventSource.onmessage = (event) => {
  const chunk = event.data;
  // 更新UI
  setMessages(prev => {
    // ...
  });
};

eventSource.onerror = (error) => {
  console.error('SSE error:', error);
  eventSource.close();
};

eventSource.addEventListener('done', () => {
  eventSource.close();
  setLoading(false);
});
```

### 使用WebSocket

```typescript
let ws: WebSocket | null = null;

export const connectWebSocket = (conversationId: string) => {
  const token = localStorage.getItem('token');
  ws = new WebSocket(`ws://localhost:8000/api/v1/conversations/${conversationId}/ws?token=${token}`);

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    // 处理消息
  };

  ws.onerror = (error) => {
    console.error('WebSocket error:', error);
  };

  ws.onclose = () => {
    console.log('WebSocket closed');
  };

  return ws;
};

export const sendMessageWS = (content: string) => {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ content }));
  }
};
```

## 数据流图

```
┌─────────────────┐
│   AIAnalysis    │
│    Component    │
└────────┬────────┘
         │
         ├─ getConversations() ────────► GET /conversations/
         │                                │
         │                                ◄── Conversation[]
         │
         ├─ createConversation() ────────► POST /conversations/
         │                                │
         │                                ◄── Conversation
         │
         ├─ getMessages() ───────────────► GET /conversations/{id}/messages
         │                                │
         │                                ◄── Message[]
         │
         ├─ sendMessage() ───────────────► POST /conversations/{id}/messages
         │                                │
         │                                ◄── SSE/WebSocket Stream
         │
         └─ analyzeResume() ─────────────► POST /analyze/resume
                                          │
                                          ◄── AnalysisResponse
```

## 待办事项

- [ ] 后端实现对话管理接口
- [ ] 后端实现消息接口（支持流式响应）
- [ ] 后端实现AI简历分析接口
- [ ] 创建 `frontend/src/services/conversations.ts`
- [ ] 更新 AIAnalysis 页面对接真实API
- [ ] 实现流式响应（SSE或WebSocket）
- [ ] 添加错误处理和重试机制
- [ ] 添加打字机效果显示AI回复
