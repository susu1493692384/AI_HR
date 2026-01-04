"""
LLM Database Tables Creation Script
创建 LLM 相关的数据库表
"""

import asyncio
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database.database import async_engine
from app.infrastructure.database.llm_models import Base

logger = logging.getLogger(__name__)


async def create_llm_tables():
    """创建所有 LLM 相关的数据库表"""
    try:
        async with async_engine.begin() as conn:
            # 使用 Base.metadata.create_all 创建所有继承自 Base 的模型
            # 注意：我们使用 Alembic 进行迁移，这里只是用于初始化
            await conn.run_sync(Base.metadata.create_all)

        logger.info("LLM database tables created successfully!")
        return True

    except Exception as e:
        logger.error(f"Failed to create LLM tables: {str(e)}")
        return False


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(create_llm_tables())
