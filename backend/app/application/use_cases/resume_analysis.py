"""Resume analysis use case - 多智能体系统实现"""

import logging
import time
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.application.agents.coordinator import ResumeAnalysisCoordinator
from app.application.schemas.agent_analysis import (
    ResumeAnalysisRequest,
    ResumeAnalysisResponse,
    AnalysisResult
)
from app.infrastructure.database.models import Resume

logger = logging.getLogger(__name__)


class ResumeAnalysisUseCase:
    """简历分析用例 - 使用多智能体系统"""

    def __init__(self, db: AsyncSession):
        """初始化用例

        Args:
            db: 数据库会话
        """
        self.db = db

    async def analyze_with_agents(
        self,
        request: ResumeAnalysisRequest,
        tenant_id: str
    ) -> ResumeAnalysisResponse:
        """使用多智能体系统分析简历

        Args:
            request: 分析请求
            tenant_id: 租户ID

        Returns:
            分析响应
        """
        start_time = time.time()

        try:
            # 1. 获取简历数据
            resume_data = await self._get_resume_data(request.resume_id)
            if not resume_data:
                raise ValueError(f"简历不存在: {request.resume_id}")

            logger.info(f"开始分析简历: {request.resume_id}")

            # 2. 准备职位要求
            job_requirements = request.job_requirements or self._get_default_job_requirements()

            # 3. 创建协调智能体
            coordinator = ResumeAnalysisCoordinator(self.db, tenant_id)

            # 4. 执行分析
            analysis_result = await coordinator.analyze(resume_data, job_requirements)

            # 5. 构建响应
            processing_time = time.time() - start_time
            message_id = f"msg_{request.resume_id}_{int(start_time)}"

            # 6. 保存分析结果（可选）
            await self._save_analysis_result(
                resume_id=request.resume_id,
                analysis=analysis_result,
                processing_time=processing_time
            )

            logger.info(f"简历分析完成，评分: {analysis_result.get('overall_score', 0)}, 耗时: {processing_time:.2f}秒")

            return ResumeAnalysisResponse(
                analysis=AnalysisResult(**analysis_result),
                message_id=message_id,
                processing_time=processing_time
            )

        except ValueError as e:
            logger.error(f"简历分析失败（参数错误）: {e}")
            raise
        except Exception as e:
            logger.error(f"简历分析失败（系统错误）: {e}", exc_info=True)
            raise RuntimeError(f"分析失败: {str(e)}")

    async def _get_resume_data(self, resume_id: str) -> Optional[Dict[str, Any]]:
        """获取简历数据

        Args:
            resume_id: 简历ID

        Returns:
            简历数据字典
        """
        try:
            # 尝试将字符串ID转换为UUID
            try:
                from uuid import UUID
                resume_uuid = UUID(resume_id) if isinstance(resume_id, str) else resume_id
            except ValueError:
                # 如果不是UUID格式，可能是其他ID类型
                resume_uuid = resume_id

            # 查询数据库
            query = select(Resume).where(Resume.id == resume_uuid)
            result = await self.db.execute(query)
            resume = result.scalar_one_or_none()

            if not resume:
                logger.warning(f"简历不存在: {resume_id}")
                return None

            # 构建简历数据
            resume_data = {
                "id": str(resume.id),
                "filename": resume.filename,
                "candidate_name": resume.candidate_name,
                "candidate_email": resume.candidate_email,
                "candidate_phone": resume.candidate_phone,
                "candidate_location": resume.candidate_location,
            }

            # 添加解析内容
            if resume.parsed_content:
                resume_data.update(resume.parsed_content)

            # 添加原始文本
            if resume.extracted_text:
                resume_data["extracted_text"] = resume.extracted_text

            return resume_data

        except Exception as e:
            logger.error(f"获取简历数据失败: {e}", exc_info=True)
            return None

    def _get_default_job_requirements(self) -> Dict[str, Any]:
        """获取默认职位要求

        Returns:
            默认职位要求
        """
        return {
            "position": "软件工程师",
            "description": "负责软件开发和维护",
            "requirements": "具备良好的编程能力和团队协作精神",
            "skills": ["Python", "JavaScript", "SQL"]
        }

    async def _save_analysis_result(
        self,
        resume_id: str,
        analysis: Dict[str, Any],
        processing_time: float
    ):
        """保存分析结果

        Args:
            resume_id: 简历ID
            analysis: 分析结果
            processing_time: 处理时间
        """
        try:
            # TODO: 实现保存到数据库的逻辑
            # 可以创建新的表或更新现有的 resume_analyses 表
            logger.info(f"分析结果已准备保存，简历ID: {resume_id}")
        except Exception as e:
            logger.error(f"保存分析结果失败: {e}", exc_info=True)
            # 保存失败不影响分析结果返回

    async def get_resume_by_id(self, resume_id: str) -> Optional[Resume]:
        """根据ID获取简历

        Args:
            resume_id: 简历ID

        Returns:
            简历对象
        """
        try:
            from uuid import UUID
            resume_uuid = UUID(resume_id) if isinstance(resume_id, str) else resume_id

            query = select(Resume).where(Resume.id == resume_uuid)
            result = await self.db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"获取简历失败: {e}")
            return None
