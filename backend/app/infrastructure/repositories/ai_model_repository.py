"""AI模型仓库"""

from typing import Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.infrastructure.repositories.base_repository import BaseRepository
from app.infrastructure.database.models import AIModel
from app.application.schemas.ai_model import AIModelCreate, AIModelUpdate


class AIModelRepository(BaseRepository[AIModel, AIModelCreate, AIModelUpdate]):
    """AI模型数据仓库"""

    def __init__(self, db: AsyncSession):
        super().__init__(AIModel, db)

    async def get_active_models(self) -> List[AIModel]:
        """获取所有激活的模型"""
        stmt = select(AIModel).where(AIModel.is_active == True)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_by_provider(self, provider: str) -> List[AIModel]:
        """根据提供商获取模型列表"""
        stmt = select(AIModel).where(AIModel.provider == provider)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_default_model(self) -> Optional[AIModel]:
        """获取默认模型"""
        stmt = select(AIModel).where(
            AIModel.is_active == True
        ).order_by(AIModel.created_at.desc()).limit(1)

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def toggle_active(self, id: Any, is_active: bool) -> bool:
        """切换模型激活状态"""
        stmt = update(AIModel).where(AIModel.id == id).values(
            is_active=is_active
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0

    async def update_test_results(
        self,
        id: Any,
        test_results: dict
    ) -> bool:
        """更新模型测试结果"""
        stmt = update(AIModel).where(AIModel.id == id).values(
            test_results=test_results
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0

    async def get_by_model_type(self, model_type: str) -> List[AIModel]:
        """根据模型类型获取模型列表"""
        stmt = select(AIModel).where(
            AIModel.model_type == model_type,
            AIModel.is_active == True
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_models_for_analysis(self) -> List[AIModel]:
        """获取可用于简历分析的模型"""
        stmt = select(AIModel).where(
            AIModel.model_type == "chat",
            AIModel.is_active == True
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()