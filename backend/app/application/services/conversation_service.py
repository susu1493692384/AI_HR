"""
Conversation Service
对话管理服务层
"""

import logging
import json
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime

from sqlalchemy import select, delete, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models import Conversation, Message, Resume
from app.infrastructure.database.llm_models import Tenant
from app.application.agents.coordinator import ResumeAnalysisCoordinator
from app.application.agents.base import BaseAgent
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)


class ConversationService:
    """对话管理服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_conversation(
        self,
        tenant_id: str,
        user_id: Optional[str],
        title: str = "新对话",
        resume_id: Optional[str] = None,
        job_position_id: Optional[str] = None
    ) -> Conversation:
        """创建新对话

        Args:
            tenant_id: 租户ID
            user_id: 用户ID
            title: 对话标题
            resume_id: 关联的简历ID
            job_position_id: 关联的职位ID

        Returns:
            创建的对话对象
        """
        try:
            # 转换 tenant_id 为 UUID
            from uuid import UUID
            tenant_uuid = UUID(tenant_id) if isinstance(tenant_id, str) else tenant_id

            # 创建对话
            conversation = Conversation(
                tenant_id=tenant_uuid,
                user_id=UUID(user_id) if user_id else None,
                title=title,
                resume_id=UUID(resume_id) if resume_id else None,
                job_position_id=UUID(job_position_id) if job_position_id else None,
                status="active"
            )

            self.db.add(conversation)
            await self.db.commit()
            await self.db.refresh(conversation)

            logger.info(f"创建对话成功: {conversation.id}")
            return conversation

        except Exception as e:
            logger.error(f"创建对话失败: {e}", exc_info=True)
            await self.db.rollback()
            raise

    async def get_conversation(
        self,
        conversation_id: str,
        tenant_id: str
    ) -> Optional[Conversation]:
        """获取对话详情

        Args:
            conversation_id: 对话ID
            tenant_id: 租户ID

        Returns:
            对话对象或None
        """
        try:
            from uuid import UUID
            from sqlalchemy import select

            query = select(Conversation).where(
                Conversation.id == UUID(conversation_id),
                Conversation.tenant_id == UUID(tenant_id)
            )

            result = await self.db.execute(query)
            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(f"获取对话失败: {e}", exc_info=True)
            return None

    async def list_conversations(
        self,
        tenant_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> tuple[List[Conversation], int]:
        """获取对话列表

        Args:
            tenant_id: 租户ID
            limit: 限制数量
            offset: 偏移量

        Returns:
            (对话列表, 总数)
        """
        try:
            from uuid import UUID
            from sqlalchemy import select, func

            # 获取总数
            count_query = select(func.count()).where(
                Conversation.tenant_id == UUID(tenant_id),
                Conversation.status == "active"
            )
            total_result = await self.db.execute(count_query)
            total = total_result.scalar() or 0

            # 获取列表
            query = select(Conversation).where(
                Conversation.tenant_id == UUID(tenant_id),
                Conversation.status == "active"
            ).order_by(desc(Conversation.created_at)).limit(limit).offset(offset)

            result = await self.db.execute(query)
            conversations = result.scalars().all()

            return list(conversations), total

        except Exception as e:
            logger.error(f"获取对话列表失败: {e}", exc_info=True)
            return [], 0

    async def delete_conversation(
        self,
        conversation_id: str,
        tenant_id: str
    ) -> bool:
        """删除对话（软删除）

        Args:
            conversation_id: 对话ID
            tenant_id: 租户ID

        Returns:
            是否成功
        """
        try:
            from uuid import UUID
            from sqlalchemy import select, update

            conversation = await self.get_conversation(conversation_id, tenant_id)
            if not conversation:
                return False

            # 软删除
            conversation.status = "deleted"
            await self.db.commit()

            logger.info(f"删除对话成功: {conversation_id}")
            return True

        except Exception as e:
            logger.error(f"删除对话失败: {e}", exc_info=True)
            await self.db.rollback()
            return False

    async def create_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        meta_data: Optional[Dict[str, Any]] = None,
        tokens_used: Optional[int] = None
    ) -> Message:
        """创建消息

        Args:
            conversation_id: 对话ID
            role: 角色（user/assistant/system）
            content: 消息内容
            meta_data: 元数据
            tokens_used: 使用的token数量

        Returns:
            创建的消息对象
        """
        try:
            from uuid import UUID

            message = Message(
                conversation_id=UUID(conversation_id),
                role=role,
                content=content,
                meta_data=meta_data or {},
                tokens_used=tokens_used
            )

            self.db.add(message)
            await self.db.commit()
            await self.db.refresh(message)

            return message

        except Exception as e:
            logger.error(f"创建消息失败: {e}", exc_info=True)
            await self.db.rollback()
            raise

    async def get_messages(
        self,
        conversation_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[Message]:
        """获取对话的消息列表

        Args:
            conversation_id: 对话ID
            limit: 限制数量
            offset: 偏移量

        Returns:
            消息列表
        """
        try:
            from uuid import UUID
            from sqlalchemy import select

            query = select(Message).where(
                Message.conversation_id == UUID(conversation_id)
            ).order_by(Message.created_at).limit(limit).offset(offset)

            result = await self.db.execute(query)
            return list(result.scalars().all())

        except Exception as e:
            logger.error(f"获取消息列表失败: {e}", exc_info=True)
            return []

    async def get_conversation_messages(
        self,
        conversation_id: str
    ) -> List[Dict[str, str]]:
        """获取对话的消息历史（用于LLM上下文）

        Args:
            conversation_id: 对话ID

        Returns:
            消息历史列表 [{"role": "user", "content": "..."}, ...]
        """
        try:
            from uuid import UUID
            from sqlalchemy import select

            query = select(Message).where(
                Message.conversation_id == UUID(conversation_id)
            ).order_by(Message.created_at)

            result = await self.db.execute(query)
            messages = result.scalars().all()

            return [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]

        except Exception as e:
            logger.error(f"获取对话消息历史失败: {e}", exc_info=True)
            return []

    async def process_user_message(
        self,
        conversation_id: str,
        user_message: str,
        tenant_id: str,
        resume_id: Optional[str] = None
    ) -> str:
        """处理用户消息并生成AI回复

        Args:
            conversation_id: 对话ID
            user_message: 用户消息
            tenant_id: 租户ID
            resume_id: 关联的简历ID

        Returns:
            AI回复内容
        """
        try:
            # 1. 保存用户消息
            await self.create_message(
                conversation_id=conversation_id,
                role="user",
                content=user_message
            )

            # 2. 获取对话历史
            history = await self.get_conversation_messages(conversation_id)

            # 3. 获取关联的简历信息
            resume_context = ""
            if resume_id:
                from uuid import UUID
                from sqlalchemy import select

                query = select(Resume).where(Resume.id == UUID(resume_id))
                result = await self.db.execute(query)
                resume = result.scalar_one_or_none()

                if resume and resume.parsed_content:
                    resume_context = f"\n\n关联简历信息:\n{json.dumps(resume.parsed_content, ensure_ascii=False, indent=2)}"

            # 4. 构建LLM提示
            system_prompt = """你是一位专业的HR AI助手，帮助用户进行简历分析和招聘相关工作。

你的职责：
1. 回答用户关于简历分析的问题
2. 提供招聘建议和意见
3. 解释分析结果的含义
4. 协助进行候选人评估

请保持专业、友好的语气，提供有价值的见解。"""

            # 构建消息列表
            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(history)
            messages.append({
                "role": "user",
                "content": user_message + resume_context
            })

            # 5. 调用LLM生成回复
            from app.application.services.llm_service import TenantLLMService, TenantService
            from app.core.config import settings
            from app.core.llm_init import DEFAULT_TENANT_ID
            import os

            # 首先获取租户信息，看看租户配置了什么默认模型
            tenant = await TenantService.get_by_id(self.db, tenant_id)

            # 确定要使用的模型
            model_to_use = settings.DEFAULT_AI_MODEL  # 默认值
            if tenant and tenant.llm_id:
                model_to_use = tenant.llm_id
            elif tenant_id == DEFAULT_TENANT_ID:
                # 对于默认租户，尝试从初始化配置获取
                model_to_use = "glm-4@ZHIPU-AI"  # 或从配置读取

            # 获取租户的LLM配置
            llm_config = await TenantLLMService.get_api_key(
                self.db, tenant_id, model_to_use
            )

            # 检查是否有API密钥配置
            api_key = None
            if llm_config and llm_config.api_key:
                api_key = llm_config.api_key
            else:
                # 尝试从环境变量获取
                api_key = os.getenv("OPENAI_API_KEY")

            if not api_key:
                # 没有配置API密钥，返回友好提示
                error_msg = """抱歉，AI助手暂时无法使用。

请先配置AI模型的API密钥：
1. 进入「AI模型管理」页面
2. 添加您的OpenAI API密钥
3. 设置默认模型后即可使用

如果您使用的是第三方API服务（如Azure OpenAI），请确保配置了正确的API Base地址。"""
                await self.create_message(
                    conversation_id=conversation_id,
                    role="assistant",
                    content=error_msg
                )
                return error_msg

            # 使用较低温度使回复更严谨
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

            # 生成回复
            from langchain_core.messages import (
                HumanMessage,
                SystemMessage,
                AIMessage
            )

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

            # 6. 保存AI回复
            await self.create_message(
                conversation_id=conversation_id,
                role="assistant",
                content=ai_reply,
                meta_data={"model": llm_config.llm_name if llm_config else settings.DEFAULT_AI_MODEL}
            )

            return ai_reply

        except Exception as e:
            logger.error(f"处理用户消息失败: {e}", exc_info=True)
            # 返回错误消息
            error_msg = f"抱歉，处理您的消息时出现了错误：{str(e)}"
            await self.create_message(
                conversation_id=conversation_id,
                role="assistant",
                content=error_msg
            )
            return error_msg

    async def update_conversation_title(
        self,
        conversation_id: str,
        tenant_id: str,
        title: str
    ) -> bool:
        """更新对话标题

        Args:
            conversation_id: 对话ID
            tenant_id: 租户ID
            title: 新标题

        Returns:
            是否成功
        """
        try:
            from uuid import UUID

            conversation = await self.get_conversation(conversation_id, tenant_id)
            if not conversation:
                return False

            conversation.title = title
            await self.db.commit()

            return True

        except Exception as e:
            logger.error(f"更新对话标题失败: {e}", exc_info=True)
            await self.db.rollback()
            return False
