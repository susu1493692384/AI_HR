"""统计API端点"""

import logging
from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.core.dependencies import get_db, get_current_user
from app.infrastructure.database.models import Resume, User, ResumeAnalysis

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/dashboard")
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    获取仪表板统计数据

    返回：
    - total_resumes: 总简历数（当前用户上传的）
    - talent_pool: 人才库（已解析完成的简历数）
    - pending: 待处理（待解析的简历数）
    - ai_analyzed: AI分析数（已分析的简历数）
    """
    try:
        # 1. 总简历数 - 当前用户上传的所有简历
        total_resumes_result = await db.execute(
            select(func.count(Resume.id))
            .where(Resume.uploaded_by == current_user.id)
        )
        total_resumes = total_resumes_result.scalar() or 0

        # 2. 人才库 - 已解析完成的简历数（status = "completed"）
        talent_pool_result = await db.execute(
            select(func.count(Resume.id))
            .where(
                and_(
                    Resume.uploaded_by == current_user.id,
                    Resume.status == "completed"
                )
            )
        )
        talent_pool = talent_pool_result.scalar() or 0

        # 3. 待处理 - 待解析的简历数（status = "uploaded"）
        pending_result = await db.execute(
            select(func.count(Resume.id))
            .where(
                and_(
                    Resume.uploaded_by == current_user.id,
                    Resume.status == "uploaded"
                )
            )
        )
        pending = pending_result.scalar() or 0

        # 4. AI分析数 - 当前用户的简历被分析的次数
        ai_analyzed_result = await db.execute(
            select(func.count(ResumeAnalysis.id))
            .select_from(ResumeAnalysis)
            .join(Resume, ResumeAnalysis.resume_id == Resume.id)
            .where(Resume.uploaded_by == current_user.id)
        )
        ai_analyzed = ai_analyzed_result.scalar() or 0

        return {
            "code": 0,
            "data": {
                "total_resumes": total_resumes,
                "talent_pool": talent_pool,
                "pending": pending,
                "ai_analyzed": ai_analyzed,
            }
        }

    except Exception as e:
        logger.error(f"获取统计数据失败: {str(e)}")
        raise Exception(f"获取统计数据失败: {str(e)}")
