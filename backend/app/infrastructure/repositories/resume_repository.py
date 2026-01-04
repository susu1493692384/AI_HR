"""简历仓库"""

from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from app.infrastructure.repositories.base_repository import BaseRepository
from app.infrastructure.database.models import Resume, ResumeAnalysis
from app.application.schemas.resume import ResumeCreate, ResumeUpdate


class ResumeRepository(BaseRepository[Resume, ResumeCreate, ResumeUpdate]):
    """简历数据仓库"""

    def __init__(self, db: AsyncSession):
        super().__init__(Resume, db)

    async def get_with_analyses(self, id: Any) -> Optional[Resume]:
        """获取简历及其分析结果"""
        stmt = select(Resume).options(
            selectinload(Resume.analyses)
        ).where(Resume.id == id)

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_status(self, status: str) -> List[Resume]:
        """根据状态获取简历列表"""
        stmt = select(Resume).where(Resume.status == status)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def update_status(self, id: Any, status: str) -> bool:
        """更新简历状态"""
        stmt = update(Resume).where(Resume.id == id).values(
            status=status
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0

    async def update_parsed_content(
        self,
        id: Any,
        parsed_content: Dict[str, Any]
    ) -> bool:
        """更新简历解析内容"""
        stmt = update(Resume).where(Resume.id == id).values(
            parsed_content=parsed_content,
            status="completed"
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0

    async def search_resumes(
        self,
        keyword: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Resume]:
        """搜索简历"""
        stmt = select(Resume).where(
            Resume.filename.ilike(f"%{keyword}%")
        ).offset(skip).limit(limit)

        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_recent_uploads(self, days: int = 7, limit: int = 10) -> List[Resume]:
        """获取最近上传的简历"""
        from sqlalchemy import and_
        from datetime import datetime, timedelta

        date_threshold = datetime.utcnow() - timedelta(days=days)

        stmt = select(Resume).where(
            and_(
                Resume.upload_time >= date_threshold,
                Resume.status == "completed"
            )
        ).limit(limit).order_by(Resume.upload_time.desc())

        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_analyzed_resumes(self, job_position_id: Optional[str] = None) -> List[Resume]:
        """获取已分析的简历"""
        stmt = select(Resume).where(Resume.status == "completed")

        if job_position_id:
            stmt = stmt.join(ResumeAnalysis).where(
                ResumeAnalysis.job_position_id == job_position_id
            )

        result = await self.db.execute(stmt)
        return result.scalars().all()