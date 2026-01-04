"""
Agent Analysis API Endpoints
智能体分析相关的 API 端点
"""

import logging
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.dependencies import get_db, get_current_tenant_id, get_current_tenant_id_optional, get_current_user
from app.application.use_cases.resume_analysis import ResumeAnalysisUseCase
from app.application.schemas.agent_analysis import (
    ResumeAnalysisRequest,
    ResumeAnalysisResponse,
    ConversationCreateRequest,
    SendMessageRequest,
    ConversationDetailResponse,
    Message,
    Conversation,
)
from app.application.services.conversation_service import ConversationService

logger = logging.getLogger(__name__)

router = APIRouter()

# MODULE LOAD TEST LOG - This should appear when the module is first imported
print("=== agent_analysis.py MODULE LOADED === If you see this, the code is active")


# ============================================================================
# 简历分析端点
# ============================================================================

@router.post("/analyze/resume", response_model=ResumeAnalysisResponse)
async def analyze_resume_with_agents(
    request: ResumeAnalysisRequest,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id)
):
    """
    使用多智能体系统分析简历

    并行调用四个专家智能体进行多维度分析：
    - 技能匹配度专家
    - 工作经验评估专家
    - 教育背景分析专家
    - 软技能评估专家

    Args:
        request: 分析请求，包含简历ID和职位要求
        db: 数据库会话
        tenant_id: 租户ID

    Returns:
        ResumeAnalysisResponse: 分析结果，包含综合评分和各维度详细分析

    Raises:
        HTTPException 400: 请求参数错误
        HTTPException 404: 简历不存在
        HTTPException 500: 分析过程出错
    """
    try:
        logger.info(f"收到简历分析请求，简历ID: {request.resume_id}, 租户: {tenant_id}")

        # 创建用例实例
        use_case = ResumeAnalysisUseCase(db)

        # 执行分析
        result = await use_case.analyze_with_agents(
            request=request,
            tenant_id=tenant_id
        )

        logger.info(f"简历分析成功，评分: {result.analysis.score}")
        return result

    except ValueError as e:
        logger.error(f"简历分析失败（参数错误）: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"简历分析失败（系统错误）: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"分析失败: {str(e)}"
        )


@router.get("/analyze/{resume_id}", response_model=ResumeAnalysisResponse)
async def get_resume_analysis(
    resume_id: str,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id)
):
    """
    获取简历的分析结果（如果已存在）

    Args:
        resume_id: 简历ID
        db: 数据库会话
        tenant_id: 租户ID

    Returns:
        ResumeAnalysisResponse: 分析结果
    """
    try:
        use_case = ResumeAnalysisUseCase(db)
        resume = await use_case.get_resume_by_id(resume_id)

        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"简历不存在: {resume_id}"
            )

        # TODO: 从数据库获取已保存的分析结果
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分析结果不存在，请先执行分析"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取分析结果失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取失败: {str(e)}"
        )


# ============================================================================
# 对话管理端点
# ============================================================================

class ConversationListResponse(BaseModel):
    """对话列表响应"""
    items: List[Conversation]
    total: int


class MessageListResponse(BaseModel):
    """消息列表响应"""
    items: List[Message]
    total: int


class SendMessageResponse(BaseModel):
    """发送消息响应"""
    message: Message
    conversation_id: str


@router.post("/conversations")
async def create_conversation(
    request: ConversationCreateRequest,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id_optional)
):
    """
    创建新的对话

    Args:
        request: 对话创建请求
        db: 数据库会话
        tenant_id: 租户ID

    Returns:
        创建的对话信息
    """
    try:
        service = ConversationService(db)

        conversation = await service.create_conversation(
            tenant_id=tenant_id,
            user_id=None,  # 从JWT获取
            title=request.title or "新对话",
            resume_id=request.resume_id
        )

        return {
            "id": str(conversation.id),
            "title": conversation.title,
            "resume_id": str(conversation.resume_id) if conversation.resume_id else None,
            "created_at": conversation.created_at.isoformat(),
            "status": conversation.status
        }

    except Exception as e:
        logger.error(f"创建对话失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建失败: {str(e)}"
        )


async def _extract_report_from_conversation(
    conversation_id: str,
    service: ConversationService
) -> Optional[dict]:
    """从对话历史中提取报告数据

    Args:
        conversation_id: 对话ID
        service: 对话服务

    Returns:
        报告数据字典，如果找不到则返回None
    """
    import json
    import re

    # 获取对话历史消息
    messages = await service.get_conversation_messages(conversation_id)

    # 从最新的消息开始查找
    for msg in reversed(messages):
        if msg["role"] == "assistant":
            content = msg["content"]

            # 查找JSON格式的报告数据
            # 尝试1: 查找 ```json 代码块
            json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                try:
                    report_data = json.loads(json_str)
                    # 验证是否是报告格式（包含 overall_score 或 dimensions）
                    if ("overall_score" in report_data or "dimensions" in report_data or
                        any(key in report_data for key in ["skills", "experience", "education",
                                                            "soft_skills", "stability",
                                                            "work_attitude", "development_potential"])):
                        return report_data
                except json.JSONDecodeError:
                    pass

            # 尝试2: 查找直接的JSON对象（不含代码块）
            # 查找包含 score 和维度名的模式
            if any(keyword in content for keyword in ["综合评分", "各维度评分", "技能匹配度",
                                                      "工作经验", "教育背景", "软技能"]):
                # 这看起来像是一个报告，但可能不是纯JSON
                # 返回一个简化的报告表示
                return {
                    "is_text_report": True,
                    "content": content,
                    "summary": content[:500] + "..." if len(content) > 500 else content
                }

    return None


@router.get("/conversations")
async def list_conversations(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id_optional)
):
    """
    获取对话列表

    Args:
        limit: 限制数量
        offset: 偏移量
        db: 数据库会话
        tenant_id: 租户ID

    Returns:
        对话列表
    """
    try:
        service = ConversationService(db)

        conversations, total = await service.list_conversations(
            tenant_id=tenant_id,
            limit=limit,
            offset=offset
        )

        # 转换为响应格式
        items = []
        for conv in conversations:
            # 获取最后一条消息
            messages = await service.get_messages(str(conv.id), limit=1)
            last_message = messages[0].content if messages else "暂无消息"

            # 获取消息数量
            all_messages = await service.get_messages(str(conv.id))
            message_count = len(all_messages)

            items.append({
                "id": str(conv.id),
                "title": conv.title,
                "last_message": last_message[:100],
                "timestamp": conv.created_at.isoformat(),
                "is_starred": False,
                "message_count": message_count,
                "resume_id": str(conv.resume_id) if conv.resume_id else None  # 添加 resume_id 字段
            })

        return {
            "items": items,
            "total": total
        }

    except Exception as e:
        logger.error(f"获取对话列表失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取失败: {str(e)}"
        )


@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id_optional)
):
    """
    获取对话详情

    Args:
        conversation_id: 对话ID
        db: 数据库会话
        tenant_id: 租户ID

    Returns:
        对话详情
    """
    try:
        service = ConversationService(db)

        conversation = await service.get_conversation(conversation_id, tenant_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"对话不存在: {conversation_id}"
            )

        # 获取消息列表
        messages = await service.get_messages(conversation_id)

        # 转换为响应格式
        message_items = []
        for msg in messages:
            message_items.append({
                "id": str(msg.id),
                "conversation_id": str(msg.conversation_id),
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at.isoformat()
            })

        return {
            "conversation": {
                "id": str(conversation.id),
                "title": conversation.title,
                "last_message": message_items[-1]["content"][:100] if message_items else "暂无消息",
                "timestamp": conversation.created_at.isoformat(),
                "is_starred": False,
                "message_count": len(message_items)
            },
            "messages": message_items
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取对话失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取失败: {str(e)}"
        )


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id_optional)
):
    """
    删除对话

    Args:
        conversation_id: 对话ID
        db: 数据库会话
        tenant_id: 租户ID

    Returns:
        删除结果
    """
    try:
        service = ConversationService(db)

        success = await service.delete_conversation(conversation_id, tenant_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"对话不存在: {conversation_id}"
            )

        return {"success": True, "message": "删除成功"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除对话失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除失败: {str(e)}"
        )


# ============================================================================
# 消息端点
# ============================================================================

@router.post("/conversations/{conversation_id}/messages")
async def send_message(
    conversation_id: str,
    request: SendMessageRequest,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id_optional)
):
    """
    发送消息并获取AI回复

    Args:
        conversation_id: 对话ID
        request: 消息请求
        db: 数据库会话
        tenant_id: 租户ID

    Returns:
        AI回复
    """
    try:
        service = ConversationService(db)

        # 验证对话是否存在
        conversation = await service.get_conversation(conversation_id, tenant_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"对话不存在: {conversation_id}"
            )

        # 处理消息并生成AI回复
        ai_reply = await service.process_user_message(
            conversation_id=conversation_id,
            user_message=request.content,
            tenant_id=tenant_id,
            resume_id=request.resume_id or str(conversation.resume_id) if conversation.resume_id else None
        )

        # 获取最后一条AI消息
        messages = await service.get_messages(conversation_id, limit=1)
        last_message = messages[-1] if messages else None

        return {
            "message": {
                "id": str(last_message.id) if last_message else "",
                "conversation_id": conversation_id,
                "role": "assistant",
                "content": ai_reply,
                "created_at": last_message.created_at.isoformat() if last_message else ""
            },
            "conversation_id": conversation_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"发送消息失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"发送失败: {str(e)}"
        )


@router.get("/conversations/{conversation_id}/messages")
async def get_messages(
    conversation_id: str,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id_optional)
):
    """
    获取对话的消息历史

    Args:
        conversation_id: 对话ID
        limit: 限制数量
        offset: 偏移量
        db: 数据库会话
        tenant_id: 租户ID

    Returns:
        消息列表
    """
    try:
        service = ConversationService(db)

        # 验证对话是否存在
        conversation = await service.get_conversation(conversation_id, tenant_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"对话不存在: {conversation_id}"
            )

        messages = await service.get_messages(conversation_id, limit, offset)

        # 转换为响应格式
        items = []
        for msg in messages:
            items.append({
                "id": str(msg.id),
                "conversation_id": str(msg.conversation_id),
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at.isoformat()
            })

        # 获取总数
        all_messages = await service.get_messages(conversation_id)
        total = len(all_messages)

        return {
            "items": items,
            "total": total
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取消息历史失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取失败: {str(e)}"
        )


# ============================================================================
# 流式响应端点
# ============================================================================

async def generate_streaming_response(
    conversation_id: str,
    user_message: str,
    tenant_id: str,
    service: ConversationService,
    use_agent: bool = False
):
    """生成流式响应

    Args:
        conversation_id: 对话ID
        user_message: 用户消息
        tenant_id: 租户ID
        service: 对话服务
        use_agent: 是否使用智能体模式
    """
    import json
    from datetime import datetime

    # TEST LOG at the very beginning of the streaming response generator
    print(f"=== generate_streaming_response START === conv_id={conversation_id}, use_agent={use_agent}, message={user_message[:50]}")

    try:
        # 1. 保存用户消息
        user_msg = await service.create_message(
            conversation_id=conversation_id,
            role="user",
            content=user_message
        )

        # 发送用户消息事件
        yield f"data: {json.dumps({'type': 'user_message', 'message': {'id': str(user_msg.id), 'role': 'user', 'content': user_message}}, ensure_ascii=False)}\n\n"

        # 2. 获取对话历史
        history = await service.get_conversation_messages(conversation_id)

        # 3. 根据模式选择响应方式
        print(f"=== MODE SELECTION === use_agent={use_agent}, type={type(use_agent)}")
        if use_agent:
            # 智能体模式
            print(f"=== ENTERING AGENT MODE === conversation_id={conversation_id}")
            logger.info(f"使用智能体模式处理消息: conversation_id={conversation_id}")
            async for chunk in _generate_agent_mode_response(history, conversation_id, tenant_id, service):
                yield chunk
        else:
            # 简单对话模式
            print(f"=== ENTERING SIMPLE MODE === conversation_id={conversation_id}")
            async for chunk in _generate_simple_mode_response(history, conversation_id, tenant_id, service):
                yield chunk

    except Exception as e:
        logger.error(f"流式响应生成失败: {e}", exc_info=True)
        yield f"data: {json.dumps({'type': 'error', 'error': str(e)}, ensure_ascii=False)}\n\n"


async def _generate_simple_mode_response(history, conversation_id: str, tenant_id: str, service):
    """生成简单对话响应（直接调用LLM）"""
    import json

    print(f"=== _generate_simple_mode_response START === conversation_id={conversation_id}")

    system_prompt = """你是一位专业的HR AI助手，帮助用户进行简历分析和招聘相关工作。

你的职责：
1. 回答用户关于简历分析的问题
2. 提供招聘建议和意见
3. 解释分析结果的含义
4. 协助进行候选人评估

请保持专业、友好的语气，提供有价值的见解。"""

    # 获取关联的简历信息
    resume_context = ""
    try:
        from uuid import UUID
        from sqlalchemy import select
        from app.infrastructure.database.models import Conversation, Resume

        print(f"[简单模式] 开始获取简历信息，conversation_id={conversation_id}")

        conv_query = select(Conversation).where(Conversation.id == UUID(conversation_id))
        conv_result = await service.db.execute(conv_query)
        conversation = conv_result.scalar_one_or_none()

        print(f"[简单模式] conversation={conversation is not None}, resume_id={conversation.resume_id if conversation else None}")

        if conversation and conversation.resume_id:
            resume_query = select(Resume).where(Resume.id == conversation.resume_id)
            resume_result = await service.db.execute(resume_query)
            resume = resume_result.scalar_one_or_none()

            print(f"[简单模式] resume={resume is not None}, has_parsed={resume.parsed_content is not None if resume else False}")

            if resume:
                # 优先使用 extracted_text (总是有数据)
                if resume.extracted_text:
                    resume_context = f"\n\n【关联简历信息】\n候选人姓名：{resume.candidate_name or '未知'}\n"
                    resume_context += f"\n简历内容：\n{resume.extracted_text}\n"
                    print(f"[简单模式] 使用extracted_text作为简历上下文，长度: {len(resume.extracted_text)}")
                else:
                    # fallback to parsed_content
                    if resume.parsed_content and len(resume.parsed_content) > 0:
                        resume_context = f"\n\n【关联简历信息】\n候选人姓名：{resume.candidate_name or '未知'}\n"
                        parsed = resume.parsed_content

                        # 检查是否有结构化数据（basic_info, work_experience等）
                        has_structured_data = any(key in parsed for key in ['basic_info', 'work_experience', 'education', 'skills', 'projects'])

                        if has_structured_data:
                            # 使用结构化数据
                            # 基本信息
                            if parsed.get('basic_info'):
                                basic = parsed['basic_info']
                                resume_context += f"目标职位：{basic.get('target_position', '未指定')}\n"
                                resume_context += f"工作年限：{basic.get('total_experience', '未指定')}\n"
                                resume_context += f"联系电话：{basic.get('phone', '未提供')}\n"
                                resume_context += f"邮箱：{basic.get('email', '未提供')}\n"

                            # 工作经历
                            if parsed.get('work_experience'):
                                resume_context += "\n工作经历：\n"
                                for idx, work in enumerate(parsed['work_experience'], 1):
                                    resume_context += f"{idx}. {work.get('company', '未知公司')} - {work.get('position', '未知职位')}\n"
                                    resume_context += f"   时间：{work.get('start_date', '')} 至 {work.get('end_date', '至今')}\n"
                                    resume_context += f"   描述：{work.get('description', '暂无描述')}\n"

                            # 教育背景
                            if parsed.get('education'):
                                resume_context += "\n教育背景：\n"
                                for idx, edu in enumerate(parsed['education'], 1):
                                    resume_context += f"{idx}. {edu.get('school', '未知学校')} - {edu.get('major', '未知专业')}\n"
                                    resume_context += f"   学历：{edu.get('degree', '未知')}\n"
                                    resume_context += f"   时间：{edu.get('start_date', '')} 至 {edu.get('end_date', '')}\n"

                            # 技能
                            if parsed.get('skills'):
                                resume_context += "\n技能列表：\n"
                                skills = parsed['skills']
                                skill_list = [s['name'] if isinstance(s, dict) else s for s in skills]
                                resume_context += f"{', '.join(skill_list)}\n"

                            # 项目经验
                            if parsed.get('projects'):
                                resume_context += "\n项目经验：\n"
                                for idx, proj in enumerate(parsed['projects'], 1):
                                    resume_context += f"{idx}. {proj.get('name', '未知项目')}\n"
                                    resume_context += f"   描述：{proj.get('description', '暂无描述')}\n"
                                    resume_context += f"   技术栈：{proj.get('tech_stack', '未指定')}\n"

                            # 完整简历数据（供详细分析）
                            resume_context += f"\n完整简历数据（JSON格式）：\n{json.dumps(parsed, ensure_ascii=False, indent=2)}\n"

                        print(f"[简单模式] 已加载简历上下文，简历ID: {resume.id}, 上下文长度: {len(resume_context)}")
                    else:
                        print(f"[简单模式] 简历数据为空,既没有extracted_text也没有parsed_content")
                        resume_context = ""
            else:
                print(f"[简单模式] 简历对象不存在，resume_id={conversation.resume_id if conversation else None}")
        else:
            print(f"[简单模式] 对话未关联简历或conversation为空")
    except Exception as e:
        logger.error(f"[简单模式] 获取简历数据失败: {e}", exc_info=True)

    messages = [{"role": "system", "content": system_prompt}]

    # 将历史记录中的最后一条用户消息替换为带有简历上下文的版本
    if history:
        # 添加除最后一条用户消息外的所有历史消息
        messages.extend(history[:-1] if len(history) > 1 else [])

        # 处理最后一条消息（用户消息）
        last_message = history[-1]
        if last_message.get('role') == 'user':
            # 将简历上下文添加到用户消息中
            enhanced_content = last_message.get('content', '') + resume_context
            messages.append({"role": "user", "content": enhanced_content})
            logger.info(f"[简单模式] 已添加简历上下文到用户消息: "
                       f"原始长度={len(last_message.get('content', ''))}, "
                       f"简历上下文长度={len(resume_context)}, "
                       f"增强后长度={len(enhanced_content)}")
        else:
            messages.extend(history[-1:])  # 如果不是用户消息，直接添加
    else:
        messages.extend(history)

    # 调用LLM
    from app.application.services.llm_service import TenantLLMService, TenantService
    from app.core.config import settings
    from app.core.llm_init import DEFAULT_TENANT_ID
    import os

    # 获取租户信息
    tenant = await TenantService.get_by_id(service.db, tenant_id)
    model_to_use = settings.DEFAULT_AI_MODEL
    if tenant and tenant.llm_id:
        model_to_use = tenant.llm_id
    elif tenant_id == DEFAULT_TENANT_ID:
        model_to_use = "glm-4@ZHIPU-AI"

    llm_config = await TenantLLMService.get_api_key(
        service.db, tenant_id, model_to_use
    )

    # 检查API密钥
    api_key = None
    if llm_config and llm_config.api_key:
        api_key = llm_config.api_key
    else:
        api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        error_msg = """抱歉，AI助手暂时无法使用。

请先配置AI模型的API密钥：
1. 进入「AI模型管理」页面
2. 添加您的OpenAI API密钥
3. 设置默认模型后即可使用"""

        # 发送错误消息作为token流
        words = error_msg.split()
        accumulated = ""
        for word in words:
            accumulated += word + " "
            yield f"data: {json.dumps({'type': 'token', 'token': word + ' ', 'accumulated': accumulated.strip()}, ensure_ascii=False)}\n\n"

        await service.create_message(
            conversation_id=conversation_id,
            role="assistant",
            content=error_msg
        )
        yield f"data: {json.dumps({'type': 'done', 'message': {'role': 'assistant', 'content': error_msg}}, ensure_ascii=False)}\n\n"
        return

    # 调用LLM - 使用较低温度使回复更严谨
    if llm_config:
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(
            model=llm_config.llm_name,
            openai_api_key=api_key,
            base_url=llm_config.api_base or None,
            temperature=0.3,
            max_tokens=llm_config.max_tokens or settings.DEFAULT_MAX_TOKENS,
        )
    else:
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(
            model=settings.DEFAULT_AI_MODEL,
            openai_api_key=api_key,
            temperature=0.3,
            max_tokens=settings.DEFAULT_MAX_TOKENS,
        )

    # 生成回复
    from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

    langchain_messages = []
    for msg in messages:
        if msg["role"] == "system":
            langchain_messages.append(SystemMessage(content=msg["content"]))
        elif msg["role"] == "user":
            langchain_messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            langchain_messages.append(AIMessage(content=msg["content"]))

    response = await llm.ainvoke(langchain_messages)
    ai_reply = response.content

    # 模拟流式输出
    words = ai_reply.split()
    accumulated = ""
    for word in words:
        accumulated += word + " "
        yield f"data: {json.dumps({'type': 'token', 'token': word + ' ', 'accumulated': accumulated.strip()}, ensure_ascii=False)}\n\n"

    # 保存AI回复
    await service.create_message(
        conversation_id=conversation_id,
        role="assistant",
        content=ai_reply
    )

    # 发送完成事件
    yield f"data: {json.dumps({'type': 'done', 'message': {'role': 'assistant', 'content': ai_reply}}, ensure_ascii=False)}\n\n"


async def _generate_report_based_response(
    user_message: str,
    report_context: dict,
    conversation_id: str,
    tenant_id: str,
    service: ConversationService
):
    """生成基于报告的对话响应（限制在报告相关范围内）

    Args:
        user_message: 用户消息
        report_context: 报告上下文数据
        conversation_id: 对话ID
        tenant_id: 租户ID
        service: 对话服务
    """
    import json
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import HumanMessage, SystemMessage
    from app.core.config import settings

    logger = logging.getLogger(__name__)

    # 构建报告摘要
    if report_context.get("is_text_report"):
        # 文本格式的报告
        report_summary = report_context.get("summary", report_context.get("content", ""))
        dimensions_info = "报告已生成，包含技能匹配度、工作经验、教育背景、软技能、稳定性、工作态度、发展潜力等7个维度的详细分析。"
    else:
        # JSON格式的报告
        overall_score = report_context.get("overall_score", "N/A")
        dimensions = report_context.get("dimensions", {})

        dimensions_info = "\n".join([
            f"- **{dim_name}**: {dim_data.get('score', 'N/A')}/100 - {dim_data.get('score_reason', '')[:100]}"
            for dim_name, dim_data in list(dimensions.items())[:7]
        ])

        report_summary = f"""**综合评分**: {overall_score}/100

**各维度评分**:
{dimensions_info}"""

    # 构建限制范围的系统提示词
    system_prompt = f"""你是一位专业的HR AI助手，刚刚完成了候选人的7维度分析报告。

**分析报告摘要**：
{report_summary}

**重要：你现在的角色是报告解读助手**

你的职责范围：
1. ✅ 解释报告中的评分依据和具体含义
2. ✅ 说明可信陈述和需要验证的陈述
3. ✅ 解读建议的面试问题
4. ✅ 提供改进建议和发展方向
5. ✅ 帮助用户理解报告中的任何术语和概念

**超出范围的话题（需礼貌拒绝）**：
- ❌ 询问无关的HR知识（如"什么是KPI"）
- ❌ 询问其他候选人或职位信息
- ❌ 请求重新生成报告（报告已固定）
- ❌ 询问与当前报告无关的内容

**拒绝话术模板**：
"抱歉，我当前的角色是帮助您理解这份候选人分析报告。关于报告中的评分、建议或面试问题，我很乐意为您解答。"
"这个问题超出了报告解读的范围。我可以帮您分析候选人的[维度]评分，或者解释报告中的任何内容。"

请基于对话历史和报告内容，给用户一个专业、友好、聚焦的回复。
"""

    # 获取LLM配置
    from app.application.services.llm_service import TenantLLMService, TenantService
    from app.core.config import settings
    from app.core.llm_init import DEFAULT_TENANT_ID
    import os

    # 首先获取租户信息，看看租户配置了什么默认模型
    tenant = await TenantService.get_by_id(service.db, tenant_id)

    # 确定要使用的模型
    model_to_use = settings.DEFAULT_AI_MODEL  # 默认值
    if tenant and tenant.llm_id:
        model_to_use = tenant.llm_id
    elif tenant_id == DEFAULT_TENANT_ID:
        # 对于默认租户，尝试从初始化配置获取
        model_to_use = "glm-4@ZHIPU-AI"  # 或从配置读取

    # 获取租户的LLM配置
    llm_config = await TenantLLMService.get_api_key(
        service.db, tenant_id, model_to_use
    )

    # 检查是否有API密钥配置
    api_key = None
    if llm_config and llm_config.api_key:
        api_key = llm_config.api_key
    else:
        # 尝试从环境变量获取
        api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        # 没有配置API密钥
        error_msg = "抱歉，AI服务未配置。请联系管理员配置API密钥。"
        yield f"data: {json.dumps({'type': 'error', 'error': error_msg}, ensure_ascii=False)}\n\n"
        return

    # 创建LLM - 使用较低温度使回复更严谨
    if llm_config:
        llm = ChatOpenAI(
            model=llm_config.llm_name,
            openai_api_key=api_key,
            base_url=llm_config.api_base or None,
            temperature=0.3,
            max_tokens=llm_config.max_tokens or settings.DEFAULT_MAX_TOKENS,
        )
    else:
        llm = ChatOpenAI(
            model=settings.DEFAULT_AI_MODEL,
            openai_api_key=api_key,
            temperature=0.3,
            max_tokens=settings.DEFAULT_MAX_TOKENS,
        )

    # 构建消息历史（只包含最近的几条消息）
    messages = await service.get_conversation_messages(conversation_id)
    langchain_messages = [SystemMessage(content=system_prompt)]

    # 只添加最近的5条消息以保持上下文
    for msg in messages[-5:]:
        if msg["role"] == "user":
            langchain_messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            from langchain_core.messages import AIMessage
            langchain_messages.append(AIMessage(content=msg["content"]))

    # 生成回复
    response = await llm.ainvoke(langchain_messages)
    ai_reply = response.content

    # 模拟流式输出
    words = ai_reply.split()
    accumulated = ""
    for word in words:
        accumulated += word + " "
        yield f"data: {json.dumps({'type': 'token', 'token': word + ' ', 'accumulated': accumulated.strip()}, ensure_ascii=False)}\n\n"

    # 保存AI回复
    await service.create_message(
        conversation_id=conversation_id,
        role="assistant",
        content=ai_reply
    )

    # 发送完成事件
    yield f"data: {json.dumps({'type': 'done', 'message': {'role': 'assistant', 'content': ai_reply}}, ensure_ascii=False)}\n\n"


async def _generate_agent_mode_response(history, conversation_id: str, tenant_id: str, service):
    """生成智能体响应（支持多轮对话记忆 + 动态调用专家智能体）"""
    import json
    import logging

    print(f"=== _generate_agent_mode_response CALLED === conversation_id={conversation_id}")

    logger = logging.getLogger(__name__)

    # 调试日志：打印历史记录
    logger.info(f"[智能体模式] conversation_id={conversation_id}, 历史消息数量={len(history)}")
    print(f"=== [智能体模式] conversation_id={conversation_id}, 历史消息数量={len(history)} ===")

    # 获取最后的用户消息
    last_user_message = ""
    print(f"=== 开始查找最后一条用户消息，历史消息数量={len(history)} ===")
    for msg in reversed(history):
        if msg["role"] == "user":
            last_user_message = msg["content"]
            print(f"=== 找到用户消息: {last_user_message[:50]}... ===")
            break

    logger.info(f"[智能体模式] 用户问题: {last_user_message[:100]}")
    print(f"=== [智能体模式] 用户问题: {last_user_message[:100]} ===")

    # 检查对话中是否已有报告
    report_context = await _extract_report_from_conversation(conversation_id, service)
    print(f"=== [智能体模式] 报告上下文: {report_context is not None} ===")

    # 如果有报告，使用报告解读模式
    if report_context:
        logger.info(f"[智能体模式] 使用报告解读模式")
        async for chunk in _generate_report_based_response(
            last_user_message,
            report_context,
            conversation_id,
            tenant_id,
            service
        ):
            yield chunk
        return

    # 获取对话关联的简历数据
    resume_data = None
    resume_obj = None  # 保存简历对象，用于后续获取 extracted_text
    try:
        print("=== 开始获取简历信息 ===")
        from uuid import UUID
        from sqlalchemy import select
        from app.infrastructure.database.models import Conversation, Resume

        logger.info(f"[智能体模式] 开始获取简历信息，conversation_id={conversation_id}")

        conv_query = select(Conversation).where(Conversation.id == UUID(conversation_id))
        conv_result = await service.db.execute(conv_query)
        conversation = conv_result.scalar_one_or_none()

        print(f"=== 对话信息查询完成: conversation_found={conversation is not None} ===")
        logger.info(f"[智能体模式] 对话信息: conversation_found={conversation is not None}, resume_id={conversation.resume_id if conversation else None}")

        if conversation and conversation.resume_id:
            resume_query = select(Resume).where(Resume.id == conversation.resume_id)
            resume_result = await service.db.execute(resume_query)
            resume_obj = resume_result.scalar_one_or_none()

            logger.info(f"[智能体模式] 简历信息: resume_found={resume_obj is not None}, "
                       f"has_parsed={resume_obj.parsed_content is not None if resume_obj else False}")

            if resume_obj:
                # 优先使用 extracted_text (总是有数据)
                if resume_obj.extracted_text:
                    resume_data = {"extracted_text": resume_obj.extracted_text}
                    logger.info(f"[智能体模式] 使用extracted_text作为简历数据，长度: {len(resume_obj.extracted_text)}")

                    # 如果 parsed_content 有结构化数据,也包含进来
                    if resume_obj.parsed_content and len(resume_obj.parsed_content) > 0:
                        has_structured_data = any(key in resume_obj.parsed_content for key in ['basic_info', 'work_experience', 'education', 'skills', 'projects'])
                        if has_structured_data:
                            # 合并结构化数据
                            resume_data.update(resume_obj.parsed_content)
                            logger.info(f"[智能体模式] 已合并结构化数据")
                else:
                    # fallback to parsed_content
                    if resume_obj.parsed_content and len(resume_obj.parsed_content) > 0:
                        resume_data = resume_obj.parsed_content
                        logger.info(f"[智能体模式] 使用parsed_content作为简历数据")
                    else:
                        logger.warning(f"[智能体模式] 简历数据为空,既没有extracted_text也没有parsed_content")
            else:
                logger.warning(f"[智能体模式] 简历对象不存在，resume_id={conversation.resume_id}")
        else:
            logger.warning(f"[智能体模式] 对话未关联简历或conversation为空")
    except Exception as e:
        print(f"=== 获取简历数据异常: {e} ===")
        logger.error(f"[智能体模式] 获取简历数据失败: {e}", exc_info=True)

    # 初始化路由器
    print("=== 开始初始化AgentRouter ===")
    from app.application.agents.agent_router import AgentRouter

    router = AgentRouter(service.db, tenant_id)
    print("=== AgentRouter初始化完成 ===")

    # 🔍 调试日志
    print(f"=== [智能体模式] resume_data存在: {resume_data is not None} ===")
    logger.info(f"[智能体模式] resume_data存在: {resume_data is not None}")
    if resume_data:
        print(f"=== [智能体模式] resume_data keys: {list(resume_data.keys()) if isinstance(resume_data, dict) else type(resume_data)} ===")
        logger.info(f"[智能体模式] resume_data keys: {list(resume_data.keys()) if isinstance(resume_data, dict) else type(resume_data)}")

    # 判断是否需要调用专家智能体
    print("=== 开始调用should_call_agents ===")
    should_call = await router.should_call_agents(last_user_message, history)
    print(f"=== should_call_agents结果: {should_call} ===")
    logger.info(f"[智能体模式] should_call_agents结果: {should_call}")

    expert_analysis = None

    if should_call and resume_data:
        print("=== [智能体模式] 需要调用专家智能体 ===")
        logger.info(f"[智能体模式] 需要调用专家智能体")
        try:
            print("=== 开始调用 route_to_expert ===")
            expert_result = await router.route_to_expert(last_user_message, history, resume_data)
            print(f"=== route_to_expert 返回: {expert_result is not None} ===")
            if expert_result:
                print("=== 开始格式化专家结果 ===")
                expert_analysis = router.format_expert_result(expert_result)
                print(f"=== 专家分析完成，长度: {len(expert_analysis)}, 包含JSON: {'```json' in expert_analysis} ===")
                logger.info(f"[智能体模式] 专家分析完成，长度: {len(expert_analysis)}")
            else:
                print("=== expert_result 为 None ===")
        except Exception as e:
            print(f"=== 专家调用异常: {e} ===")
            logger.error(f"[智能体模式] 专家调用失败: {e}", exc_info=True)
            expert_analysis = f"\n\n⚠️ 专家分析时遇到问题: {str(e)}"

    # 构建系统提示词
    print(f"=== 构建系统提示词，expert_analysis存在: {expert_analysis is not None} ===")
    if expert_analysis:
        # 如果有专家分析，融入到提示词中
        print(f"=== 使用带专家分析的提示词，expert_analysis前100字符: {expert_analysis[:100]}... ===")
        system_prompt = f"""你是一位专业的HR AI助手，正在使用**多智能体增强模式**。

你的智能体团队包括：
1. **技能匹配度专家** - 评估技术技能和工具
2. **工作经验评估专家** - 分析工作履历和项目经验
3. **教育背景分析专家** - 评估学历和专业背景
4. **软技能评估专家** - 分析综合素质和软技能
5. **协调智能体** - 整合四个专家的分析结果

刚刚我已经调用了相关专家进行分析，分析结果如下：

{expert_analysis}

请基于以上专家分析，结合对话历史，给用户一个专业、友好、有见解的回复：
1. 直接回答用户的问题
2. 引用专家分析的要点（用简洁的语言）
3. 给出具体可操作的建议
4. 使用markdown格式，用专业的HR术语和表达方式

记住：你是多智能体系统，可以调用多个专家来帮助用户！"""
    else:
        # 没有专家分析时的通用提示词
        system_prompt = """你是一位专业的HR AI助手，正在使用**多智能体增强模式**。

你的智能体团队包括：
1. **技能匹配度专家** - 评估技术技能和工具
2. **工作经验评估专家** - 分析工作履历和项目经验
3. **教育背景分析专家** - 评估学历和专业背景
4. **软技能评估专家** - 分析综合素质和软技能
5. **协调智能体** - 整合四个专家的分析结果

**重要：你是一个多智能体系统！** 当用户问你是否是多智能体时，请明确告诉用户：
"是的，我是一个多智能体系统，包含技能、经验、教育、软技能四个专家智能体，以及一个协调智能体。"

请基于对话历史，提供专业、详细的分析和建议：
1. 理解对话上下文，记住之前的对话内容
2. 直接回答用户问题
3. 从专业HR角度提供见解
4. 如果涉及简历评估且有简历数据，告诉用户可以调用专家进行分析
5. 给出具体可操作的建议
6. 使用markdown格式，用专业的HR术语和表达方式"""

    # 构建简历上下文
    resume_context = ""
    if resume_data:
        import json
        # 将简历内容转换为可读格式
        resume_context = f"\n\n【关联简历信息】\n"

        # 检查是否有结构化数据
        has_structured_data = any(key in resume_data for key in ['basic_info', 'work_experience', 'education', 'skills', 'projects'])

        if has_structured_data:
            # 使用结构化数据
            # 基本信息
            if resume_data.get('basic_info'):
                basic = resume_data['basic_info']
                resume_context += f"候选人姓名：{basic.get('name', '未知')}\n"
                resume_context += f"目标职位：{basic.get('target_position', '未指定')}\n"
                resume_context += f"工作年限：{basic.get('total_experience', '未指定')}\n"

            # 工作经历
            if resume_data.get('work_experience'):
                resume_context += "\n工作经历：\n"
                for idx, work in enumerate(resume_data['work_experience'], 1):
                    resume_context += f"{idx}. {work.get('company', '未知公司')} - {work.get('position', '未知职位')}\n"

            # 教育背景
            if resume_data.get('education'):
                resume_context += "\n教育背景：\n"
                for idx, edu in enumerate(resume_data['education'], 1):
                    resume_context += f"{idx}. {edu.get('school', '未知学校')} - {edu.get('major', '未知专业')}\n"

            # 技能
            if resume_data.get('skills'):
                resume_context += "\n技能列表：\n"
                skills = resume_data['skills']
                skill_list = [s['name'] if isinstance(s, dict) else s for s in skills]
                resume_context += f"{', '.join(skill_list)}\n"

            # 完整简历数据
            resume_context += f"\n完整简历数据（JSON格式）：\n{json.dumps(resume_data, ensure_ascii=False, indent=2)}\n"
        elif resume_data.get('extracted_text'):
            # 使用提取的原始文本
            resume_context += f"\n简历内容：\n{resume_data['extracted_text']}\n"
            logger.info(f"[智能体模式] 使用extracted_text构建简历上下文")
        else:
            resume_context = ""  # 没有任何简历数据

        logger.info(f"[智能体模式] 已构建简历上下文，长度: {len(resume_context)}")
    else:
        logger.warning(f"[智能体模式] resume_data为空，无法构建简历上下文")

    # 构建包含历史对话的消息列表
    messages = [{"role": "system", "content": system_prompt}]

    # 将历史记录中的最后一条用户消息替换为带有简历上下文的版本
    if history:
        # 添加除最后一条用户消息外的所有历史消息
        messages.extend(history[:-1] if len(history) > 1 else [])

        # 处理最后一条消息（用户消息）
        last_message = history[-1]
        if last_message.get('role') == 'user':
            # 将简历上下文添加到用户消息中
            enhanced_content = last_message.get('content', '') + resume_context
            messages.append({"role": "user", "content": enhanced_content})
            logger.info(f"[智能体模式] 已添加简历上下文到用户消息: "
                       f"原始长度={len(last_message.get('content', ''))}, "
                       f"简历上下文长度={len(resume_context)}, "
                       f"增强后长度={len(enhanced_content)}")
        else:
            messages.extend(history[-1:])  # 如果不是用户消息，直接添加
    else:
        messages.extend(history)

    logger.info(f"[智能体模式] 构建后的消息总数={len(messages)}")

    # 🔥 关键修改：如果有专家分析，直接输出专家分析，不再调用LLM重新生成
    if expert_analysis:
        print(f"=== 直接输出专家分析，不调用LLM，长度: {len(expert_analysis)} ===")
        logger.info(f"[智能体模式] 直接输出专家分析，不调用LLM，长度: {len(expert_analysis)}")

        # 🔧 修复：检查是否包含JSON代码块
        has_json = "```json" in expert_analysis and "```" in expert_analysis
        json_data = None
        display_text = expert_analysis  # 默认显示全部文本

        if has_json:
            # 提取JSON代码块之前和之后的部分
            json_start = expert_analysis.find("```json")
            json_end = expert_analysis.find("\n```", json_start + 8) + 4

            before_json = expert_analysis[:json_start]
            json_block = expert_analysis[json_start:json_end]
            after_json = expert_analysis[json_end:]

            # 提取纯JSON数据（去掉```json和```标记）
            json_content = json_block.replace("```json", "").replace("```", "").strip()

            try:
                # 验证是否是有效JSON
                json.loads(json_content)
                json_data = json_content
                # 只显示非JSON部分的文本
                display_text = before_json + after_json
                logger.info(f"[智能体模式] 提取到有效JSON数据，长度: {len(json_data)}")
            except:
                logger.warning(f"[智能体模式] JSON解析失败，显示全部文本")
                display_text = expert_analysis

        # 🎯 关键修改：如果有JSON数据，通过隐藏事件发送
        if json_data:
            # 发送隐藏的JSON数据事件（不显示在聊天界面）
            yield f"data: {json.dumps({'type': 'json_data', 'data': json_data}, ensure_ascii=False)}\n\n"
            logger.info(f"[智能体模式] 已发送隐藏的JSON数据事件")

        # 流式输出显示文本（不包含JSON代码块）
        if display_text.strip():
            words = display_text.split()
            accumulated = ""
            for word in words:
                accumulated += word + " "
                yield f"data: {json.dumps({'type': 'token', 'token': word + ' ', 'accumulated': accumulated.strip()}, ensure_ascii=False)}\n\n"

        # 保存到数据库（保存完整内容，包括JSON）
        await service.create_message(
            conversation_id=conversation_id,
            role="assistant",
            content=expert_analysis
        )

        yield f"data: {json.dumps({'type': 'done', 'message': {'role': 'assistant', 'content': display_text}}, ensure_ascii=False)}\n\n"
        return

    # 没有专家分析时，调用LLM生成响应
    from app.application.services.llm_service import TenantLLMService, TenantService
    from app.core.config import settings
    import os

    tenant = await TenantService.get_by_id(service.db, tenant_id)
    model_to_use = tenant.llm_id if tenant else settings.DEFAULT_AI_MODEL

    llm_config = await TenantLLMService.get_api_key(service.db, tenant_id, model_to_use)
    api_key = llm_config.api_key if llm_config else os.getenv("OPENAI_API_KEY")

    if not api_key:
        simple_reply = "抱歉，智能体模式需要配置API密钥。请先在「AI模型管理」中配置。"
        words = simple_reply.split()
        accumulated = ""
        for word in words:
            accumulated += word + " "
            yield f"data: {json.dumps({'type': 'token', 'token': word + ' ', 'accumulated': accumulated.strip()}, ensure_ascii=False)}\n\n"

        await service.create_message(
            conversation_id=conversation_id,
            role="assistant",
            content=simple_reply
        )
        yield f"data: {json.dumps({'type': 'done', 'message': {'role': 'assistant', 'content': simple_reply}}, ensure_ascii=False)}\n\n"
        return

    from langchain_openai import ChatOpenAI
    from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

    llm = ChatOpenAI(
        model=llm_config.llm_name,
        openai_api_key=api_key,
        base_url=llm_config.api_base or None,
        temperature=0.3,
        max_tokens=llm_config.max_tokens or settings.DEFAULT_MAX_TOKENS,
    )

    # 转换为 LangChain 消息格式
    langchain_messages = []
    for msg in messages:
        if msg["role"] == "system":
            langchain_messages.append(SystemMessage(content=msg["content"]))
        elif msg["role"] == "user":
            langchain_messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            langchain_messages.append(AIMessage(content=msg["content"]))

    response = await llm.ainvoke(langchain_messages)
    ai_reply = response.content

    # 流式输出
    words = ai_reply.split()
    accumulated = ""
    for word in words:
        accumulated += word + " "
        yield f"data: {json.dumps({'type': 'token', 'token': word + ' ', 'accumulated': accumulated.strip()}, ensure_ascii=False)}\n\n"

    await service.create_message(
        conversation_id=conversation_id,
        role="assistant",
        content=ai_reply
    )

    yield f"data: {json.dumps({'type': 'done', 'message': {'role': 'assistant', 'content': ai_reply}}, ensure_ascii=False)}\n\n"


@router.post("/conversations/{conversation_id}/stream")
async def send_message_stream(
    conversation_id: str,
    request: SendMessageRequest,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id_optional)
):
    """
    发送消息并获取流式AI回复

    Args:
        conversation_id: 对话ID
        request: 消息请求
        db: 数据库会话
        tenant_id: 租户ID

    Returns:
        流式响应 (Server-Sent Events)
    """
    # TEST LOG - This should appear whenever the endpoint is called
    print(f"=== STREAM ENDPOINT CALLED === conversation_id={conversation_id}, content={request.content[:50]}, use_agent={request.use_agent}")

    try:
        service = ConversationService(db)

        # 验证对话是否存在
        conversation = await service.get_conversation(conversation_id, tenant_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"对话不存在: {conversation_id}"
            )

        return StreamingResponse(
            generate_streaming_response(
                conversation_id=conversation_id,
                user_message=request.content,
                tenant_id=tenant_id,
                service=service,
                use_agent=request.use_agent
            ),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"流式发送消息失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"发送失败: {str(e)}"
        )
