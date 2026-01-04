import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { Send, Loader2, Sparkles, MoreVertical, Trash2, Star, AlertCircle } from 'lucide-react';
import ConversationSidebar from '@/components/ConversationSidebar';
import ReportPanel from '@/components/ReportPanel';
import { conversationsService, Conversation } from '@/services/conversations';
import { getResumeDetail } from '@/services/resume';

interface ExtendedConversation extends Conversation {
  messages: Array<{ role: 'user' | 'assistant'; content: string; isStreaming?: boolean; json_data?: string }>;
  resumeData?: {
    name: string;
    position: string;
    experience: string;
    education: string;
    skills: string[];
    score: number;
  };
}

// ============================================================================
// 打字机效果 Hook
// ============================================================================

const useTypewriter = (
  text: string,
  speed: number = 20,
  enabled: boolean = true
): string => {
  const [displayedText, setDisplayedText] = useState('');
  const [index, setIndex] = useState(0);

  useEffect(() => {
    if (!enabled) {
      setDisplayedText(text);
      return;
    }

    if (index < text.length) {
      const timeout = setTimeout(() => {
        setDisplayedText(prev => prev + text[index]);
        setIndex(prev => prev + 1);
      }, speed);

      return () => clearTimeout(timeout);
    }
  }, [index, text, speed, enabled]);

  return displayedText;
};

// ============================================================================
// 主组件
// ============================================================================

const AIAnalysis: React.FC = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const location = useLocation();

  // 状态管理
  const [conversations, setConversations] = useState<ExtendedConversation[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<string | null>(id || null);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [showSidebar, setShowSidebar] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [retryCount, setRetryCount] = useState(0);
  const [useAgentMode, setUseAgentMode] = useState(() => {
    // 从 localStorage 加载模式偏好
    return localStorage.getItem('ai_agent_mode') === 'true';
  });
  const [isGeneratingReport, setIsGeneratingReport] = useState(false);

  const activeConversation = conversations.find(c => c.id === activeConversationId);

  // 调试：打印 activeConversation 状态
  useEffect(() => {
    console.log('activeConversation changed:', activeConversation);
    console.log('activeConversation.messages:', activeConversation?.messages);
    console.log('Message count:', activeConversation?.messages?.length || 0);
    console.log('activeConversation.resumeData:', activeConversation?.resumeData);
    console.log('Has resumeData:', !!activeConversation?.resumeData);
  }, [activeConversation]);

  // ============================================================================
  // 数据加载
  // ============================================================================

  const loadConversations = useCallback(async () => {
    try {
      setError(null);
      const response = await conversationsService.getConversations();

      // 使用函数式更新来检测并添加新对话
      setConversations(prev => {
        const existingIds = new Set(prev.map(c => c.id));
        const newConversations = response.items.filter(conv => !existingIds.has(conv.id));

        if (newConversations.length > 0) {
          console.log(`Found ${newConversations.length} new conversations`);

          const extendedConversations: ExtendedConversation[] = newConversations.map(conv => {
            // 先从 localStorage 加载消息，避免显示空白
            const storageKey = `chat_messages_${conv.id}`;
            const cached = localStorage.getItem(storageKey);
            let cachedMessages: any[] = [];

            if (cached) {
              try {
                cachedMessages = JSON.parse(cached);
                console.log(`✅ Loaded ${cachedMessages.length} cached messages for conversation ${conv.id}`);
              } catch (err) {
                console.error('Failed to parse cached messages:', err);
              }
            }

            return {
              ...conv,
              messages: cachedMessages
            };
          });

          return [...extendedConversations, ...prev];
        }

        return prev;
      });

      // 如果没有活跃对话，设置第一个为活跃
      if (!activeConversationId) {
        const firstConv = response.items[0];
        if (firstConv) {
          setActiveConversationId(firstConv.id);
          navigate(`/ai-analysis/${firstConv.id}`, { replace: true });
        }
      }
    } catch (err) {
      console.error('Failed to load conversations:', err);
      setError('加载对话列表失败');
    }
  }, [navigate, activeConversationId]);

  const loadMessages = useCallback(async (conversationId: string) => {
    console.log('loadMessages called for conversationId:', conversationId);

    // 先从 localStorage 加载缓存的消息
    const storageKey = `chat_messages_${conversationId}`;
    const cached = localStorage.getItem(storageKey);

    console.log('localStorage key:', storageKey);
    console.log('cached data:', cached);

    if (cached) {
      try {
        const cachedMessages = JSON.parse(cached);
        console.log('Parsed cached messages:', cachedMessages);

        setConversations(prev =>
          prev.map(conv => {
            if (conv.id === conversationId) {
              console.log('Updating conversation with cached messages');
              return { ...conv, messages: cachedMessages };
            }
            return conv;
          })
        );
        console.log('✅ Loaded messages from localStorage:', cachedMessages.length);
      } catch (err) {
        console.error('❌ Failed to parse cached messages:', err);
      }
    } else {
      console.log('⚠️ No cached messages found in localStorage');
    }

    // 然后从 API 加载最新消息
    try {
      console.log('Fetching messages from API...');
      const response = await conversationsService.getMessages(conversationId);

      console.log('API response:', response);
      console.log('API response.items:', response.items);
      console.log('API response.items[0]:', response.items[0]);
      console.log('API response.items[1]:', response.items[1]);

      const messages = response.items.map(msg => ({
        role: msg.role as 'user' | 'assistant',
        content: msg.content
      }));

      console.log('Processed messages from API:', messages);
      console.log('Message roles:', messages.map(m => m.role));

      // 检查 API 返回的消息是否比 localStorage 的更完整
      // 如果 API 返回的消息只有 user 消息，而 localStorage 有 assistant 消息，则保留 localStorage 的数据
      const currentLocalStorage = localStorage.getItem(storageKey);
      let finalMessages = messages;

      if (currentLocalStorage) {
        try {
          const localMessages = JSON.parse(currentLocalStorage);
          const hasAssistantInLocal = localMessages.some((m: any) => m.role === 'assistant');
          const hasAssistantInAPI = messages.some(m => m.role === 'assistant');

          if (hasAssistantInLocal && !hasAssistantInAPI) {
            console.log('⚠️ API missing assistant messages, keeping localStorage data');
            finalMessages = localMessages;
          } else if (messages.length > localMessages.length) {
            // API 有更多消息，使用 API 数据并保存
            console.log('✅ API has more messages, using API data');
            localStorage.setItem(storageKey, JSON.stringify(messages));
          } else {
            // 使用最新的数据
            console.log('✅ Using API data');
            localStorage.setItem(storageKey, JSON.stringify(messages));
          }
        } catch (err) {
          console.error('Failed to parse local storage:', err);
          localStorage.setItem(storageKey, JSON.stringify(messages));
        }
      } else {
        // localStorage 为空，保存 API 数据
        localStorage.setItem(storageKey, JSON.stringify(messages));
        console.log('✅ Saved messages to localStorage');
      }

      setConversations(prev =>
        prev.map(conv => {
          if (conv.id === conversationId) {
            return { ...conv, messages: finalMessages };
          }
          return conv;
        })
      );
    } catch (err) {
      console.error('❌ Failed to load messages from API:', err);
      // 如果 API 失败，至少保留 localStorage 的数据
    }
  }, []);

  // 加载简历数据
  const loadResumeData = useCallback(async (conversationId: string) => {
    try {
      console.log('loadResumeData called for conversationId:', conversationId);
      console.log('location.state:', location.state);

      // 从 location.state 获取 resumeId（如果从简历库跳转过来）
      const state = location.state as { resumeId?: string } | null;
      let resumeId = state?.resumeId;

      console.log('resumeId from location.state:', resumeId);

      // 如果 state 中没有，从 conversations 中查找
      if (!resumeId) {
        // 使用函数式更新，避免依赖 conversations
        setConversations(prev => {
          const conv = prev.find(c => c.id === conversationId);
          const foundResumeId = conv?.resume_id;

          console.log('resumeId from conversations:', foundResumeId);

          if (!foundResumeId) {
            console.log('No resume_id found for conversation:', conversationId);
            return prev;  // 没有找到 resume_id，不更新状态
          }

          // 异步加载简历数据
          console.log('Loading resume data for resume_id:', foundResumeId);
          getResumeDetail(foundResumeId)
            .then(response => {
              const resume = response.data;

              if (!resume || !resume.parsed_content) {
                console.warn('Resume or parsed_content not found');
                return;
              }

              // 转换为 ResumeAnalysis 组件需要的格式
              const parsed = resume.parsed_content;
              const resumeData = {
                name: resume.candidate_name || parsed.basic_info?.name || '未知',
                position: parsed.basic_info?.target_position || parsed.work_experience?.[0]?.position || '未指定',
                experience: parsed.work_experience?.map((w: any) => `${w.company} ${w.position}`).join('; ') || '暂无',
                education: parsed.education?.map((e: any) => `${e.school} ${e.major} ${e.degree}`).join('; ') || '暂无',
                skills: parsed.skills?.map((s: any) => typeof s === 'string' ? s : s.name).flat() || [],
                score: parsed.analysis_result?.overall_score || 0,
              };

              console.log('Setting resumeData for conversation:', conversationId, resumeData);

              // 再次使用函数式更新来设置 resumeData
              setConversations(prevConversations =>
                prevConversations.map(conv => {
                  if (conv.id === conversationId) {
                    return { ...conv, resumeData };
                  }
                  return conv;
                })
              );
            })
            .catch(err => {
              console.error('Failed to load resume data:', err);
            });

          return prev;  // 第一次调用不更新状态
        });

        return;
      }

      // 如果从 location.state 获取到了 resumeId，直接加载
      console.log('Loading resume data for resume_id from state:', resumeId);

      const response = await getResumeDetail(resumeId);
      const resume = response.data;

      console.log('Resume detail response:', resume);
      console.log('Has parsed_content:', !!resume.parsed_content);
      console.log('parsed_content keys:', resume.parsed_content ? Object.keys(resume.parsed_content) : 'N/A');

      if (!resume || !resume.parsed_content) {
        console.warn('Resume or parsed_content not found');
        return;
      }

      // 转换为 ResumeAnalysis 组件需要的格式
      const parsed = resume.parsed_content;
      const resumeData = {
        name: resume.candidate_name || parsed.basic_info?.name || '未知',
        position: parsed.basic_info?.target_position || parsed.work_experience?.[0]?.position || '未指定',
        experience: parsed.work_experience?.map((w: any) => `${w.company} ${w.position}`).join('; ') || '暂无',
        education: parsed.education?.map((e: any) => `${e.school} ${e.major} ${e.degree}`).join('; ') || '暂无',
        skills: parsed.skills?.map((s: any) => typeof s === 'string' ? s : s.name).flat() || [],
        score: parsed.analysis_result?.overall_score || 0,
      };

      console.log('Setting resumeData from state for conversation:', conversationId, resumeData);

      // 更新对话的 resumeData
      setConversations(prev =>
        prev.map(conv => {
          if (conv.id === conversationId) {
            return { ...conv, resumeData };
          }
          return conv;
        })
      );
    } catch (err) {
      console.error('Failed to load resume data:', err);
    }
  }, [location.state]);

  // 初始加载
  useEffect(() => {
    loadConversations();
  }, []); // 只在组件挂载时加载一次

  // 当从简历库跳转过来时，重新加载对话列表
  useEffect(() => {
    if (location.state?.resumeId) {
      console.log('Detected navigation from resume library, reloading conversations');
      loadConversations();
    }
  }, [location.state]);

  // 当切换对话时加载消息和简历数据
  useEffect(() => {
    if (activeConversationId) {
      loadMessages(activeConversationId);
      loadResumeData(activeConversationId);
    }
  }, [activeConversationId, loadMessages, loadResumeData]);

  // 检测是否正在生成报告
  useEffect(() => {
    if (activeConversationId && activeConversation?.resume_id) {
      const messages = activeConversation?.messages || [];
      const hasUserMessage = messages.some(m => m.role === 'user');
      const hasAssistantMessage = messages.some(m => m.role === 'assistant');

      // 如果有用户消息但没有助手回复，说明正在生成报告
      if (hasUserMessage && !hasAssistantMessage) {
        setIsGeneratingReport(true);
      } else {
        setIsGeneratingReport(false);
      }
    } else {
      setIsGeneratingReport(false);
    }
  }, [activeConversation?.messages, activeConversationId, activeConversation?.resume_id]);

  // ============================================================================
  // 事件处理
  // ============================================================================

  const handleNewConversation = async () => {
    try {
      setError(null);
      const newConversation = await conversationsService.createConversation({
        title: '新对话'
      });

      const extendedConv: ExtendedConversation = {
        ...newConversation,
        messages: [{ role: 'assistant', content: '您好！我是AI简历分析助手。您可以上传简历或输入问题，我会帮您分析候选人的技能、经验和匹配度。' }]
      };

      setConversations(prev => [extendedConv, ...prev]);
      setActiveConversationId(newConversation.id);
      navigate(`/ai-analysis/${newConversation.id}`);
    } catch (err) {
      console.error('Failed to create conversation:', err);
      setError('创建对话失败');
    }
  };

  const handleSelectConversation = (convId: string) => {
    setActiveConversationId(convId);
    navigate(`/ai-analysis/${convId}`);
  };

  const handleToggleStar = async (convId: string) => {
    // 本地状态更新
    setConversations(prev =>
      prev.map(conv =>
        conv.id === convId ? { ...conv, is_starred: !conv.is_starred } : conv
      )
    );
  };

  const handleDeleteConversation = async (convId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (confirm('确定要删除这个对话吗？')) {
      try {
        await conversationsService.deleteConversation(convId);

        const newConversations = conversations.filter(c => c.id !== convId);
        setConversations(newConversations);

        if (activeConversationId === convId) {
          const nextActive = newConversations[0]?.id || null;
          setActiveConversationId(nextActive);
          if (nextActive) {
            navigate(`/ai-analysis/${nextActive}`);
          } else {
            navigate('/ai-analysis');
          }
        }
      } catch (err) {
        console.error('Failed to delete conversation:', err);
        setError('删除对话失败');
      }
    }
  };

  // ============================================================================
  // 发送消息（带流式响应）
  // ============================================================================

  const handleSendMessage = async () => {
    if (!inputValue.trim() || !activeConversationId || isLoading) return;

    const userMessage = inputValue.trim();
    setInputValue('');
    setError(null);
    setIsLoading(true);
    setRetryCount(0);

    // 立即添加用户消息到UI
    setConversations(prev => {
      const updated = prev.map(conv => {
        if (conv.id === activeConversationId) {
          const newMessages = [...conv.messages, { role: 'user', content: userMessage }];
          // 立即保存到 localStorage
          localStorage.setItem(`chat_messages_${activeConversationId}`, JSON.stringify(newMessages));
          console.log('💾 Saved user message to localStorage. Total messages:', newMessages.length);
          return {
            ...conv,
            messages: newMessages
          };
        }
        return conv;
      });
      return updated;
    });

    try {
      // 使用流式响应
      setIsStreaming(true);

      // 添加一个空的AI消息占位
      const tempMessageId = Date.now().toString();
      setConversations(prev =>
        prev.map(conv => {
          if (conv.id === activeConversationId) {
            return {
              ...conv,
              messages: [...conv.messages, { role: 'assistant', content: '', isStreaming: true }]
            };
          }
          return conv;
        })
      );

      let accumulatedText = '';
      let responseReceived = false;

      // 设置超时机制：如果 30 秒内没有收到任何回复，提供模拟回复
      // 增加超时时间以适应大模型的响应时间
      const timeoutId = setTimeout(() => {
        if (!responseReceived && !accumulatedText) {
          console.log('⏱️ Timeout reached (30s), providing mock response');
          const mockResponse = '抱歉，AI 服务暂时不可用。请先配置 AI 后端服务。\n\n您可以：\n1. 检查后端服务是否运行\n2. 确认 API 密钥是否配置\n3. 查看 QUICK_START.md 了解配置方法';

          setConversations(prev => {
            const updated = prev.map(conv => {
              if (conv.id === activeConversationId) {
                const messages = conv.messages
                  .filter(m => !m.isStreaming) // 移除流式占位
                  .concat({ role: 'assistant' as const, content: mockResponse });

                // 保存到 localStorage
                localStorage.setItem(`chat_messages_${activeConversationId}`, JSON.stringify(messages));
                console.log('💾 Saved mock response to localStorage (timeout)');

                return { ...conv, messages };
              }
              return conv;
            });
            return updated;
          });

          setIsLoading(false);
          setIsStreaming(false);
        }
      }, 30000); // 30秒超时

      await conversationsService.sendMessageStream(
          activeConversationId,
          { content: userMessage, use_agent: useAgentMode },
          {
            onEvent: (event) => {
              console.log('📨 Stream event received:', event.type);

              switch (event.type) {
                case 'user_message':
                  // 用户消息已确认
                  break;

                case 'json_data':
                  // 存储隐藏的JSON数据到当前assistant消息
                  console.log('📊 Received hidden JSON data');
                  setConversations(prev =>
                    prev.map(conv => {
                      if (conv.id === activeConversationId) {
                        const messages = [...conv.messages];
                        const lastMsg = messages[messages.length - 1];
                        if (lastMsg && lastMsg.role === 'assistant' && lastMsg.isStreaming) {
                          messages[messages.length - 1] = {
                            ...lastMsg,
                            json_data: event.data  // 存储JSON数据，不显示在聊天中
                          };
                        }
                        return { ...conv, messages };
                      }
                      return conv;
                    })
                  );
                  break;

                case 'token':
                  // 流式token更新
                  responseReceived = true;
                  clearTimeout(timeoutId);

                  accumulatedText = event.accumulated || '';
                  setConversations(prev =>
                    prev.map(conv => {
                      if (conv.id === activeConversationId) {
                        const messages = [...conv.messages];
                        const lastMsg = messages[messages.length - 1];
                        if (lastMsg && lastMsg.role === 'assistant' && lastMsg.isStreaming) {
                          messages[messages.length - 1] = {
                            ...lastMsg,
                            content: accumulatedText
                          };
                        }
                        return { ...conv, messages };
                      }
                      return conv;
                    })
                  );
                  break;

              case 'done':
                // 流式完成
                clearTimeout(timeoutId);

                // 如果没有实际内容，提供模拟回复
                if (!accumulatedText) {
                  console.log('⚠️ Empty response, providing mock response');
                  const mockResponse = '抱歉，AI 服务暂时不可用。请先配置 AI 后端服务。\n\n您可以：\n1. 检查后端服务是否运行\n2. 确认 API 密钥是否配置\n3. 查看 QUICK_START.md 了解配置方法';

                  setConversations(prev => {
                    const updated = prev.map(conv => {
                      if (conv.id === activeConversationId) {
                        const messages = conv.messages
                          .filter(m => !m.isStreaming)
                          .concat({ role: 'assistant' as const, content: mockResponse });

                        localStorage.setItem(`chat_messages_${activeConversationId}`, JSON.stringify(messages));
                        console.log('💾 Saved mock response to localStorage (empty response)');

                        return { ...conv, messages };
                      }
                      return conv;
                    });
                    return updated;
                  });
                } else {
                  setConversations(prev => {
                    const updated = prev.map(conv => {
                      if (conv.id === activeConversationId) {
                        const messages = [...conv.messages];
                        const lastMsg = messages[messages.length - 1];
                        if (lastMsg && lastMsg.role === 'assistant') {
                          messages[messages.length - 1] = {
                            ...lastMsg,
                            content: event.message?.content || accumulatedText,
                            isStreaming: false
                          };
                        }

                        console.log('💾 Saving all messages to localStorage after AI response. Total:', messages.length);
                        console.log('Message roles:', messages.map(m => m.role));

                        // 保存到 localStorage
                        localStorage.setItem(`chat_messages_${activeConversationId}`, JSON.stringify(messages));

                        return {
                          ...conv,
                          messages,
                          lastMessage: (event.message?.content || accumulatedText).substring(0, 30) + '...',
                          timestamp: new Date().toLocaleString('zh-CN', { hour12: false })
                        };
                      }
                      return conv;
                    });
                    return updated;
                  });
                }
                break;

              case 'error':
                clearTimeout(timeoutId);
                console.error('Error event received:', event.error);
                // 不抛出异常，而是提供模拟回复
                const mockResponse = '抱歉，AI 服务暂时不可用。请先配置 AI 后端服务。\n\n您可以：\n1. 检查后端服务是否运行\n2. 确认 API 密钥是否配置\n3. 查看 QUICK_START.md 了解配置方法';

                setConversations(prev => {
                  const updated = prev.map(conv => {
                    if (conv.id === activeConversationId) {
                      console.log('Adding mock response for error event');
                      const messages = conv.messages
                        .filter(m => !m.isStreaming) // 移除流式占位
                        .concat({ role: 'assistant' as const, content: mockResponse });

                      // 保存到 localStorage
                      localStorage.setItem(`chat_messages_${activeConversationId}`, JSON.stringify(messages));
                      console.log('💾 Saved mock response to localStorage (error event)');

                      return { ...conv, messages };
                    }
                    return conv;
                  });
                  return updated;
                });

                setIsLoading(false);
                setIsStreaming(false);
                break;
            }
          },
          onError: (error) => {
            clearTimeout(timeoutId);
            console.error('Stream error:', error);
            console.log('🔧 onError triggered, preparing mock response...');

            // AI 后端可能未配置，提供模拟回复
            const mockResponse = '抱歉，AI 服务暂时不可用。请先配置 AI 后端服务。\n\n您可以：\n1. 检查后端服务是否运行\n2. 确认 API 密钥是否配置\n3. 查看 QUICK_START.md 了解配置方法';

            setConversations(prev => {
              const updated = prev.map(conv => {
                if (conv.id === activeConversationId) {
                  console.log('Current messages before filtering:', conv.messages);
                  const messages = conv.messages
                    .filter(m => !m.isStreaming) // 移除流式占位
                    .concat({ role: 'assistant' as const, content: mockResponse });

                  console.log('Messages after adding mock response:', messages);

                  // 保存到 localStorage
                  localStorage.setItem(`chat_messages_${activeConversationId}`, JSON.stringify(messages));
                  console.log('💾 Saved mock response to localStorage (error)');
                  console.log('Verification - reading from localStorage:', localStorage.getItem(`chat_messages_${activeConversationId}`));

                  return { ...conv, messages };
                }
                return conv;
              });
              return updated;
            });

            setIsLoading(false);
            setIsStreaming(false);
          },
          onComplete: () => {
            clearTimeout(timeoutId);
            setIsLoading(false);
            setIsStreaming(false);
          }
        }
      );

    } catch (err) {
      console.error('Failed to send message:', err);

      // 重试逻辑
      if (retryCount < 3) {
        setError(`发送失败，正在重试 (${retryCount + 1}/3)...`);
        setRetryCount(prev => prev + 1);

        // 指数退避重试
        setTimeout(() => {
          setInputValue(userMessage);
          handleSendMessage();
        }, 1000 * (retryCount + 1));
      } else {
        setError('发送失败，请检查网络连接后重试');

        // 移除流式消息占位
        setConversations(prev =>
          prev.map(conv => {
            if (conv.id === activeConversationId) {
              const messages = conv.messages.filter(m => !m.isStreaming);
              return { ...conv, messages };
            }
            return conv;
          })
        );
      }
    } finally {
      setIsLoading(false);
      setIsStreaming(false);
    }
  };

  // ============================================================================
  // 快捷问题模板
  // ============================================================================

  const quickQuestions = [
    '分析候选人的技能优势',
    '评估项目经验',
    '给出综合评分和建议',
    '分析教育背景',
    '评估软技能'
  ];

  // ============================================================================
  // 渲染
  // ============================================================================

  return (
    <div className="flex flex-col -m-6" style={{ height: 'calc(100vh - 4rem)' }}>
      <div className="flex flex-1 overflow-hidden">
        {/* 左侧 - 对话历史侧边栏 */}
        {showSidebar && (
          <div className="w-80 flex-shrink-0 border-r border-gray-200 bg-white">
            <ConversationSidebar
              conversations={conversations}
              activeConversationId={activeConversationId}
              onSelectConversation={handleSelectConversation}
              onNewConversation={handleNewConversation}
              onToggleStar={handleToggleStar}
              onDeleteConversation={handleDeleteConversation}
            />
          </div>
        )}

        {/* 中间 - AI 对话区 */}
        <div className="flex-1 flex flex-col bg-white border-r border-gray-200 min-w-0">
          {/* 头部 */}
          <div className="flex-shrink-0 p-4 border-b border-gray-200 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <button
                onClick={() => setShowSidebar(!showSidebar)}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
              <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <h2 className="text-lg font-semibold text-gray-900">AI 分析助手</h2>
                <p className="text-sm text-gray-500">智能简历分析，快速评估候选人</p>
              </div>
            </div>
            {activeConversation && (
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => handleToggleStar(activeConversation.id)}
                  className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                  title={activeConversation.is_starred ? '取消收藏' : '收藏'}
                >
                  <Star className={`w-5 h-5 ${activeConversation.is_starred ? 'text-yellow-500 fill-yellow-500' : 'text-gray-400'}`} />
                </button>
                <button
                  onClick={(e) => handleDeleteConversation(activeConversation.id, e)}
                  className="p-2 hover:bg-red-50 rounded-lg transition-colors group"
                  title="删除对话"
                >
                  <Trash2 className="w-5 h-5 text-gray-400 group-hover:text-red-500" />
                </button>
                <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors" title="更多">
                  <MoreVertical className="w-5 h-5 text-gray-400" />
                </button>
              </div>
            )}
          </div>

          {/* 错误提示 */}
          {error && (
            <div className="flex-shrink-0 mx-4 mt-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center space-x-2">
              <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0" />
              <span className="text-sm text-red-700">{error}</span>
              <button
                onClick={() => setError(null)}
                className="ml-auto text-red-600 hover:text-red-800"
              >
                ×
              </button>
            </div>
          )}

          {/* 报告生成状态 */}
          {isGeneratingReport && (
            <div className="flex-shrink-0 mx-4 mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="flex items-center space-x-3">
                <Loader2 className="w-5 h-5 text-blue-600 animate-spin flex-shrink-0" />
                <div className="flex-1">
                  <p className="text-sm font-medium text-blue-800">正在生成7维度分析报告</p>
                  <p className="text-xs text-blue-600 mt-1">正在协调专家智能体进行分析，请稍候...</p>
                </div>
              </div>
            </div>
          )}

          {/* 消息列表 */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {activeConversation?.messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[70%] rounded-lg p-3 ${
                    message.role === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-900'
                  }`}
                >
                  {message.role === 'assistant' && message.isStreaming ? (
                    <div className="flex items-center space-x-2">
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                      </div>
                    </div>
                  ) : (
                    <p className="text-sm whitespace-pre-wrap break-words">{message.content}</p>
                  )}
                </div>
              </div>
            ))}
            {isLoading && !isStreaming && (
              <div className="flex justify-start">
                <div className="bg-gray-100 rounded-lg p-3">
                  <Loader2 className="w-5 h-5 text-gray-600 animate-spin" />
                </div>
              </div>
            )}
          </div>

          {/* 输入区 */}
          <div className="flex-shrink-0 p-4 border-t border-gray-200 bg-white">
            {/* 模式切换开关 */}
            <div className="flex items-center justify-between mb-3 px-2">
              <span className="text-sm text-gray-600">AI 回复模式</span>
              <div className="flex items-center space-x-3">
                <span className={`text-xs ${!useAgentMode ? 'text-blue-600 font-medium' : 'text-gray-500'}`}>
                  简单模式
                </span>
                <button
                  onClick={() => {
                    const newMode = !useAgentMode;
                    setUseAgentMode(newMode);
                    localStorage.setItem('ai_agent_mode', String(newMode));
                    console.log(`切换到 ${newMode ? '智能体增强' : '简单'} 模式`);
                  }}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                    useAgentMode ? 'bg-blue-600' : 'bg-gray-300'
                  }`}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                      useAgentMode ? 'translate-x-6' : 'translate-x-1'
                    }`}
                  />
                </button>
                <span className={`text-xs ${useAgentMode ? 'text-blue-600 font-medium' : 'text-gray-500'}`}>
                  智能体增强
                </span>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && handleSendMessage()}
                placeholder="输入您的问题，如：分析候选人的技能优势..."
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                disabled={!activeConversation || isLoading}
              />
              <button
                onClick={handleSendMessage}
                disabled={!inputValue.trim() || isLoading || !activeConversation}
                className="p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
              >
                {isLoading ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <Send className="w-5 h-5" />
                )}
              </button>
            </div>
            <div className="mt-2 flex flex-wrap gap-2">
              {quickQuestions.map((question) => (
                <button
                  key={question}
                  onClick={() => setInputValue(question)}
                  className="text-xs px-3 py-1 bg-gray-100 text-gray-700 rounded-full hover:bg-gray-200 transition-colors"
                  disabled={isLoading}
                >
                  {question}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* 右侧 - 综合分析报告面板 */}
        <div className="w-96 flex-shrink-0 bg-white border-l border-gray-200 overflow-y-auto">
          <ReportPanel
            messages={activeConversation?.messages || []}
            resumeData={activeConversation?.resumeData}
          />
        </div>
      </div>
    </div>
  );
};

export default AIAnalysis;
