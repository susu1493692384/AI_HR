"""
简历上传服务
处理文件上传、解析、向量化等完整流程
"""

import os
import uuid
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.infrastructure.database.models import Resume
from app.application.services.resume_parser import get_resume_parser
from app.application.services.embedding_service import EmbeddingService
from app.core.config import settings

logger = logging.getLogger(__name__)


class ResumeUploadService:
    """简历上传服务"""

    def __init__(self, db: AsyncSession, upload_dir: Optional[str] = None):
        """初始化服务"""
        self.db = db
        self.upload_dir = upload_dir or settings.UPLOAD_DIR
        self.parser = get_resume_parser()
        self.embedding_service = EmbeddingService(db)

        # 确保上传目录存在
        os.makedirs(self.upload_dir, exist_ok=True)

    async def upload_file_only(
        self,
        file_content: bytes,
        filename: str,
        content_type: str,
        user_id: Optional[str] = None
    ) -> Resume:
        """
        仅上传文件，不进行解析

        Args:
            file_content: 文件内容
            filename: 文件名
            content_type: 文件类型
            user_id: 上传用户的ID

        Returns:
            创建的简历记录
        """
        # 1. 保存文件
        file_id = str(uuid.uuid4())
        file_ext = Path(filename).suffix
        saved_filename = f"{file_id}{file_ext}"
        file_path = os.path.abspath(os.path.join(self.upload_dir, saved_filename))

        logger.info(f"保存文件到: {file_path}")
        with open(file_path, 'wb') as f:
            f.write(file_content)

        # 2. 创建简历记录（状态为 uploaded）
        resume = Resume(
            filename=filename,
            file_path=file_path,
            file_type=content_type,
            file_size=len(file_content),
            parsed_content={},
            upload_time=datetime.utcnow(),
            status="uploaded",
            uploaded_by=user_id
        )

        self.db.add(resume)
        await self.db.commit()
        await self.db.refresh(resume)

        logger.info(f"文件上传完成，ID: {resume.id}, 用户ID: {user_id}")
        return resume

    async def upload_and_process(
        self,
        file_content: bytes,
        filename: str,
        content_type: str,
        tenant_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Resume:
        """
        上传并处理简历文件

        Args:
            file_content: 文件内容
            filename: 文件名
            content_type: 文件类型
            tenant_id: 租户ID
            user_id: 上传用户的ID

        Returns:
            创建的简历记录
        """
        from datetime import datetime

        # 1. 保存文件
        file_id = str(uuid.uuid4())
        file_ext = Path(filename).suffix
        saved_filename = f"{file_id}{file_ext}"
        file_path = os.path.abspath(os.path.join(self.upload_dir, saved_filename))

        logger.info(f"保存文件到: {file_path}")
        with open(file_path, 'wb') as f:
            f.write(file_content)

        # 2. 创建简历记录
        import json
        resume = Resume(
            filename=filename,
            file_path=file_path,
            file_type=content_type,
            file_size=len(file_content),
            parsed_content={},
            upload_time=datetime.utcnow(),
            status="parsing",
            uploaded_by=user_id
        )

        self.db.add(resume)
        await self.db.commit()
        await self.db.refresh(resume)

        logger.info(f"简历记录已创建，ID: {resume.id}")

        try:
            # 3. 解析文件内容
            logger.info(f"开始解析简历文件: {filename}")
            parsed_data = await self.parser.parse_file(file_path, filename)

            # 更新解析结果到各个字段
            resume.extracted_text = parsed_data.get("extracted_text")
            resume.candidate_name = parsed_data.get("candidate_name")
            resume.candidate_email = parsed_data.get("candidate_email")
            resume.candidate_phone = parsed_data.get("candidate_phone")
            resume.candidate_location = parsed_data.get("candidate_location")

            # 同时保存完整的解析数据到 parsed_content
            resume.parsed_content = parsed_data

            resume.status = "embedding"

            await self.db.commit()
            logger.info(f"简历解析完成: {filename}, parsed_content已更新")

            # 4. 生成向量（如果配置了 embedding 模型）
            try:
                logger.info(f"开始生成向量: {filename}")
                text_to_embed = self._prepare_text_for_embedding(resume)
                embedding = await self.embedding_service.embed_text(text_to_embed, tenant_id or "default")

                # 存储向量（简化版：存储为逗号分隔的字符串）
                # 生产环境应使用专门的向量数据库
                resume.embedding_id = file_id
                resume.embedding_model = await self._get_embedding_model_name(tenant_id)
                # 将向量存储在 parsed_content 中
                if resume.parsed_content is None:
                    resume.parsed_content = {}
                resume.parsed_content["embedding"] = ",".join(str(x) for x in embedding)
                resume.status = "completed"
                logger.info(f"向量生成完成: {filename}")

            except Exception as embedding_error:
                # 如果 embedding 失败，仍然标记为完成，但不存储向量
                logger.warning(f"向量生成失败（已跳过）: {str(embedding_error)}")
                resume.status = "completed"
                if resume.parsed_content is None:
                    resume.parsed_content = {}
                resume.parsed_content["embedding_error"] = str(embedding_error)

            await self.db.commit()
            await self.db.refresh(resume)

            logger.info(f"简历处理完成: {filename}")

            return resume

        except Exception as e:
            logger.error(f"简历处理失败: {filename}, 错误: {str(e)}", exc_info=True)
            resume.status = "failed"
            if resume.parsed_content is None:
                resume.parsed_content = {}
            resume.parsed_content["error"] = str(e)
            await self.db.commit()
            raise

    def _prepare_text_for_embedding(self, resume: Resume) -> str:
        """准备用于 embedding 的文本"""
        parts = []

        # 添加候选人信息
        if resume.candidate_name:
            parts.append(f"姓名: {resume.candidate_name}")
        if resume.candidate_email:
            parts.append(f"邮箱: {resume.candidate_email}")
        if resume.candidate_phone:
            parts.append(f"电话: {resume.candidate_phone}")
        if resume.candidate_location:
            parts.append(f"地点: {resume.candidate_location}")

        # 添加提取的文本内容
        if resume.extracted_text:
            # 限制文本长度，避免超过 token 限制
            text = resume.extracted_text
            if len(text) > 8000:
                text = text[:8000]
            parts.append(text)

        return "\n\n".join(parts)

    async def _get_embedding_model_name(self, tenant_id: Optional[str]) -> str:
        """获取当前使用的 embedding 模型名称"""
        try:
            config = await self.embedding_service._get_embedding_config(tenant_id or "default")
            model_name = config.get("model", "unknown")
            logger.info(f"使用的 embedding 模型: {model_name}")
            return model_name
        except Exception as e:
            logger.warning(f"获取 embedding 模型名称失败: {str(e)}")
            return "unknown"

    async def parse_resume(self, resume_id: str, tenant_id: Optional[str] = None) -> Resume:
        """
        解析已上传的简历

        Args:
            resume_id: 简历ID
            tenant_id: 租户ID

        Returns:
            更新后的简历记录
        """
        from sqlalchemy import select

        # 获取简历记录
        result = await self.db.execute(select(Resume).where(Resume.id == resume_id))
        resume = result.scalar_one_or_none()

        if not resume:
            raise ValueError(f"简历不存在: {resume_id}")

        # 检查文件是否存在
        if not os.path.exists(resume.file_path):
            raise ValueError(f"文件不存在: {resume.file_path}")

        # 更新状态为解析中
        resume.status = "parsing"
        await self.db.commit()

        try:
            # 1. 解析文件内容
            logger.info(f"开始解析简历文件: {resume.filename}")
            parsed_data = await self.parser.parse_file(resume.file_path, resume.filename)

            # 更新解析结果
            resume.extracted_text = parsed_data.get("extracted_text")
            resume.candidate_name = parsed_data.get("candidate_name")
            resume.candidate_email = parsed_data.get("candidate_email")
            resume.candidate_phone = parsed_data.get("candidate_phone")
            resume.candidate_location = parsed_data.get("candidate_location")

            # 保存完整的解析数据到 parsed_content
            if resume.parsed_content is None:
                resume.parsed_content = {}
            resume.parsed_content.update(parsed_data)
            resume.parsed_content["parsed_at"] = datetime.utcnow().isoformat()

            resume.status = "completed"

            await self.db.commit()
            await self.db.refresh(resume)

            logger.info(f"简历解析完成: {resume.filename}, parsed_content keys: {list(resume.parsed_content.keys())}")
            return resume

        except Exception as e:
            logger.error(f"简历解析失败: {resume.filename}, 错误: {str(e)}", exc_info=True)
            resume.status = "failed"
            if resume.parsed_content is None:
                resume.parsed_content = {}
            resume.parsed_content["error"] = str(e)
            await self.db.commit()
            raise


# 全局服务实例
_upload_services: Dict[str, ResumeUploadService] = {}


def get_upload_service(db: AsyncSession) -> ResumeUploadService:
    """获取上传服务实例"""
    return ResumeUploadService(db)
