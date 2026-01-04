/**
 * Conversations Service
 * 对话管理服务 - 与后端 API 交互
 */

import { api } from './api';

// ============================================================================
// 类型定义
// ============================================================================

export interface Message {
  id: string;
  conversation_id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  created_at: string;
  // 存储隐藏的JSON数据（不显示在聊天界面，但供ReportPanel使用）
  json_data?: string;
}

export interface Conversation {
  id: string;
  title: string;
  last_message: string;
  timestamp: string;
  is_starred: boolean;
  message_count: number;
  resume_id?: string;  // 关联的简历ID
}

export interface ConversationDetail {
  conversation: Conversation;
  messages: Message[];
}

export interface ConversationListResponse {
  items: Conversation[];
  total: number;
}

export interface MessageListResponse {
  items: Message[];
  total: number;
}

export interface CreateConversationRequest {
  title?: string;
  resume_id?: string;
}

export interface SendMessageRequest {
  content: string;
  resume_id?: string;
  use_agent?: boolean;  // 是否使用智能体模式
}

export interface SendMessageResponse {
  message: Message;
  conversation_id: string;
}

// ============================================================================
// 流式响应事件类型
// ============================================================================

export interface StreamEvent {
  type: 'user_message' | 'token' | 'done' | 'error' | 'json_data';
  message?: Message;
  token?: string;
  accumulated?: string;
  error?: string;
  data?: string;  // 用于存储JSON字符串
}

export type StreamEventHandler = (event: StreamEvent) => void;
export type StreamErrorHandler = (error: Error) => void;
export type StreamCompleteHandler = () => void;

// ============================================================================
// Conversations Service
// ============================================================================

class ConversationsService {
  private readonly basePath = '/agent-analysis';

  /**
   * 获取对话列表
   */
  async getConversations(params?: { limit?: number; offset?: number }): Promise<ConversationListResponse> {
    const response = await api.get(`${this.basePath}/conversations`, { params });
    return response.data;
  }

  /**
   * 获取单个对话详情
   */
  async getConversation(conversationId: string): Promise<ConversationDetail> {
    const response = await api.get(`${this.basePath}/conversations/${conversationId}`);
    return response.data;
  }

  /**
   * 创建新对话
   */
  async createConversation(data: CreateConversationRequest): Promise<Conversation> {
    const response = await api.post(`${this.basePath}/conversations`, data);
    return response.data;
  }

  /**
   * 删除对话
   */
  async deleteConversation(conversationId: string): Promise<{ success: boolean; message: string }> {
    const response = await api.delete(`${this.basePath}/conversations/${conversationId}`);
    return response.data;
  }

  /**
   * 获取对话的消息列表
   */
  async getMessages(
    conversationId: string,
    params?: { limit?: number; offset?: number }
  ): Promise<MessageListResponse> {
    const response = await api.get(`${this.basePath}/conversations/${conversationId}/messages`, { params });
    return response.data;
  }

  /**
   * 发送消息（非流式）
   */
  async sendMessage(conversationId: string, data: SendMessageRequest): Promise<SendMessageResponse> {
    const response = await api.post(`${this.basePath}/conversations/${conversationId}/messages`, data);
    return response.data;
  }

  /**
   * 发送消息（流式）
   * 使用 Server-Sent Events (SSE) 实现流式响应
   */
  async sendMessageStream(
    conversationId: string,
    data: SendMessageRequest,
    handlers: {
      onEvent: StreamEventHandler;
      onError?: StreamErrorHandler;
      onComplete?: StreamCompleteHandler;
    }
  ): Promise<() => void> {
    const token = localStorage.getItem('token');
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }

    const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    const url = `${baseUrl}/api/v1${this.basePath}/conversations/${conversationId}/stream`;

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers,
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error('Response body is null');
      }

      // 读取流
      const readStream = async (): Promise<void> => {
        try {
          while (true) {
            const { done, value } = await reader.read();

            if (done) {
              handlers.onComplete?.();
              break;
            }

            // 解码数据
            const chunk = decoder.decode(value, { stream: true });
            const lines = chunk.split('\n');

            for (const line of lines) {
              if (line.startsWith('data: ')) {
                const data = line.slice(6);
                try {
                  const event: StreamEvent = JSON.parse(data);
                  handlers.onEvent(event);
                } catch (e) {
                  console.error('Failed to parse SSE data:', data, e);
                }
              }
            }
          }
        } catch (error) {
          handlers.onError?.(error as Error);
        }
      };

      // 开始读取流
      readStream();

      // 返回取消函数
      return () => {
        reader.cancel().catch(console.error);
      };

    } catch (error) {
      handlers.onError?.(error as Error);
      throw error;
    }
  }

  /**
   * 带重试的消息发送
   * @param maxRetries 最大重试次数（默认3）
   * @param retryDelay 重试延迟（毫秒，默认1000）
   */
  async sendMessageWithRetry(
    conversationId: string,
    data: SendMessageRequest,
    options: {
      maxRetries?: number;
      retryDelay?: number;
      useStream?: boolean;
      onEvent?: StreamEventHandler;
    } = {}
  ): Promise<SendMessageResponse | (() => void)> {
    const { maxRetries = 3, retryDelay = 1000, useStream = false, onEvent } = options;

    let lastError: Error | null = null;

    for (let attempt = 0; attempt < maxRetries; attempt++) {
      try {
        if (useStream && onEvent) {
          return await this.sendMessageStream(conversationId, data, {
            onEvent,
            onError: (error) => {
              console.error(`Stream error (attempt ${attempt + 1}/${maxRetries}):`, error);
              lastError = error;
            },
          });
        } else {
          return await this.sendMessage(conversationId, data);
        }
      } catch (error) {
        lastError = error as Error;
        console.error(`Send message failed (attempt ${attempt + 1}/${maxRetries}):`, error);

        // 如果不是最后一次尝试，等待后重试
        if (attempt < maxRetries - 1) {
          await this.delay(retryDelay * (attempt + 1)); // 指数退避
        }
      }
    }

    throw lastError || new Error('Failed to send message after retries');
  }

  /**
   * 辅助方法：延迟执行
   */
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  // ============================================================================
  // 简历分析相关
  // ============================================================================

  /**
   * 分析简历
   */
  async analyzeResume(data: {
    resume_id: string;
    job_position_id?: string;
    job_requirements?: Record<string, unknown>;
  }): Promise<{
    analysis: {
      score: number;
      skills: unknown;
      experience: unknown;
      education: unknown;
      soft_skills: unknown;
      summary: string;
      recommendations: string[];
    };
    message_id: string;
    processing_time: number;
    conversation_id?: string;
  }> {
    const response = await api.post(`${this.basePath}/analyze/resume`, data);
    return response.data;
  }

  /**
   * 获取简历分析结果
   */
  async getResumeAnalysis(resumeId: string): Promise<unknown> {
    const response = await api.get(`${this.basePath}/analyze/${resumeId}`);
    return response.data;
  }
}

// 导出单例
export const conversationsService = new ConversationsService();

// 默认导出
export default conversationsService;
