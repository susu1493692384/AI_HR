"""
Base Agent Module
智能体基类，所有智能体的基础实现
"""

import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from langchain_openai import ChatOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.llm_service import TenantLLMService
from app.core.config import settings

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """智能体基类

    提供LLM初始化、租户管理等通用功能
    """

    def __init__(
        self,
        db: AsyncSession,
        tenant_id: str,
        model_name: Optional[str] = None,
        temperature: float = 0.7
    ):
        """初始化智能体

        Args:
            db: 数据库会话
            tenant_id: 租户ID
            model_name: 模型名称（可选，默认使用配置）
            temperature: 温度参数
        """
        self.db = db
        self.tenant_id = tenant_id
        self.model_name = model_name
        self.temperature = temperature
        self.llm: Optional[ChatOpenAI] = None

    async def _initialize_llm(self) -> ChatOpenAI:
        """初始化LLM实例

        优先使用租户全局配置的模型 (Tenant.llm_id)，其次使用传入的 model_name，
        最后使用系统默认配置

        Returns:
            ChatOpenAI实例
        """
        # 如果已经初始化，直接返回
        if self.llm:
            return self.llm

        # 1. 优先从租户全局配置获取模型
        model_to_use = await self._get_tenant_model()

        # 2. 如果租户没有配置，使用传入的模型名
        if not model_to_use:
            model_to_use = self.model_name

        # 3. 如果都没有，使用系统默认模型
        if not model_to_use:
            model_to_use = settings.DEFAULT_AI_MODEL

        # 尝试获取租户的 API 配置
        try:
            tenant_llm = await TenantLLMService.get_api_key(
                self.db, self.tenant_id, model_to_use
            )

            if tenant_llm:
                logger.info(
                    f"使用租户 {self.tenant_id} 配置的模型: {tenant_llm.llm_name} "
                    f"({tenant_llm.llm_factory}), 温度: {self.temperature}"
                )
                self.llm = ChatOpenAI(
                    model=tenant_llm.llm_name,
                    openai_api_key=tenant_llm.api_key,
                    base_url=tenant_llm.api_base or None,
                    temperature=self.temperature,
                    max_tokens=tenant_llm.max_tokens or settings.DEFAULT_MAX_TOKENS,
                )
                return self.llm
        except Exception as e:
            logger.warning(f"获取租户LLM配置失败: {e}, 使用默认配置")

        # 使用默认配置（无 API Key 的情况）
        logger.info(f"使用系统默认模型: {model_to_use}, 温度: {self.temperature}")
        self.llm = ChatOpenAI(
            model=model_to_use,
            temperature=self.temperature,
            max_tokens=settings.DEFAULT_MAX_TOKENS,
        )
        return self.llm

    async def _get_tenant_model(self) -> Optional[str]:
        """获取租户的全局模型配置 (Tenant.llm_id)

        Returns:
            模型ID字符串 (格式: "模型名@厂商") 或 None
        """
        try:
            from sqlalchemy import select
            from app.infrastructure.database.llm_models import Tenant

            # 转换 tenant_id 为 UUID
            from uuid import UUID
            try:
                tenant_uuid = UUID(self.tenant_id) if isinstance(self.tenant_id, str) else self.tenant_id
            except ValueError:
                logger.warning(f"无效的租户ID格式: {self.tenant_id}")
                return None

            # 查询租户配置
            query = select(Tenant.llm_id).where(Tenant.id == tenant_uuid)
            result = await self.db.execute(query)
            llm_id = result.scalar_one_or_none()

            if llm_id:
                logger.info(f"从租户 {self.tenant_id} 获取到全局模型配置: {llm_id}")
                return llm_id

            logger.warning(f"租户 {self.tenant_id} 未配置全局模型")
            return None

        except Exception as e:
            logger.warning(f"获取租户模型配置失败: {e}")
            return None

    @abstractmethod
    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行分析

        Args:
            context: 分析上下文数据

        Returns:
            分析结果字典
        """
        pass

    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """解析LLM返回的JSON格式响应 - 增强版

        Args:
            response: LLM返回的文本

        Returns:
            解析后的字典

        Raises:
            ValueError: 如果JSON解析失败
        """
        import re

        # 清理响应
        response = response.strip()

        # 1. 尝试直接解析
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass

        # 2. 尝试提取markdown代码块
        patterns = [
            r'```json\s*(.*?)\s*```',  # ```json ... ```
            r'```\s*(.*?)\s*```',       # ``` ... ```
        ]

        for pattern in patterns:
            match = re.search(pattern, response, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1))
                except (json.JSONDecodeError, IndexError):
                    continue

        # 3. 尝试提取花括号内容 (从第一个{到最后一个})
        brace_match = re.search(r'\{.*\}', response, re.DOTALL)
        if brace_match:
            try:
                return json.loads(brace_match.group(0))
            except json.JSONDecodeError:
                pass

        # 4. 尝试清理常见问题并解析
        try:
            cleaned = response

            # 移除注释 (// 和 /* */)
            cleaned = re.sub(r'//.*?\n', '\n', cleaned)
            cleaned = re.sub(r'/\*.*?\*/', '', cleaned, flags=re.DOTALL)

            # 替换单引号为双引号 (简单情况，注意不要替换字符串内的单引号)
            # 这是一个简化版本，主要处理键名和简单字符串值
            cleaned = re.sub(r"'([^']*)'", r'"\1"', cleaned)

            # 移除尾随逗号
            cleaned = re.sub(r',\s*([}\]])', r'\1', cleaned)

            # 再次尝试解析
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.debug(f"清理后的JSON仍然无法解析: {e}")

        # 5. 最后尝试: 记录完整错误并抛出
        error_msg = f"无法解析JSON响应\n前500字符: {response[:500]}\n错误信息: {str(e)}"
        logger.error(error_msg)
        raise ValueError(error_msg)

    async def _invoke_llm(self, prompt: str, **kwargs) -> str:
        """调用LLM

        Args:
            prompt: 提示词
            **kwargs: 额外参数

        Returns:
            LLM响应文本
        """
        llm = await self._initialize_llm()
        response = await llm.ainvoke(prompt, **kwargs)
        return response.content

    def _format_resume_data(self, resume_data: Dict[str, Any]) -> str:
        """格式化简历数据为可读文本

        Args:
            resume_data: 简历数据字典

        Returns:
            格式化的文本
        """
        lines = []

        # 检查是否有结构化数据
        has_structured = any(key in resume_data for key in ['basic_info', 'work_experience', 'education', 'skills', 'projects'])

        if has_structured:
            # 使用结构化数据
            if resume_data.get("basic_info"):
                basic = resume_data['basic_info']
                if basic.get("name"):
                    lines.append(f"姓名: {basic['name']}")
                if basic.get("target_position"):
                    lines.append(f"目标职位: {basic['target_position']}")

            if resume_data.get("skills"):
                lines.append(f"\n技能:")
                skills = resume_data["skills"]
                if isinstance(skills, list):
                    for skill in skills:
                        if isinstance(skill, dict):
                            lines.append(f"  - {skill.get('name', skill)}")
                        else:
                            lines.append(f"  - {skill}")
                else:
                    lines.append(f"  - {skills}")

            if resume_data.get("work_experience"):
                lines.append(f"\n工作经验:")
                for exp in resume_data["work_experience"]:
                    if isinstance(exp, dict):
                        lines.append(f"  - {exp.get('company', '')}: {exp.get('position', '')} ({exp.get('duration', '')})")

            if resume_data.get("education"):
                lines.append(f"\n教育背景:")
                for edu in resume_data["education"]:
                    if isinstance(edu, dict):
                        lines.append(f"  - {edu.get('school', '')}: {edu.get('degree', '')} ({edu.get('major', '')})")

            if resume_data.get("projects"):
                lines.append(f"\n项目经验:")
                for proj in resume_data["projects"][:5]:  # 最多显示5个
                    if isinstance(proj, dict):
                        lines.append(f"  - {proj.get('name', '')}: {proj.get('description', '')}")
        else:
            # 使用 extracted_text
            extracted_text = resume_data.get("extracted_text", "")
            if extracted_text:
                lines.append("简历内容:")
                # 限制长度，避免token过多
                if len(extracted_text) > 2000:
                    extracted_text = extracted_text[:2000] + "..."
                lines.append(extracted_text)
            else:
                lines.append("简历数据格式未知")

        return "\n".join(lines)
