"""
重置并重新初始化 LLM 数据的脚本
运行: python reset_llm_data.py
"""

import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.llm_init import init_all_llm_data
from app.infrastructure.database.llm_models import LLM, LLMFactory, TenantLLM, Tenant


async def reset_and_init():
    """重置并重新初始化 LLM 数据"""

    # 数据库连接
    DATABASE_URL = "postgresql+asyncpg://postgres:password@localhost:5432/ai_hr"
    engine = create_async_engine(DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        print("开始重置 LLM 数据...")

        # 1. 删除所有租户 LLM 配置
        await db.execute(delete(TenantLLM))
        print("已删除所有租户 LLM 配置")

        # 2. 删除所有 LLM 模型
        await db.execute(delete(LLM))
        print("已删除所有 LLM 模型")

        # 3. 删除所有 LLM 厂商
        await db.execute(delete(LLMFactory))
        print("已删除所有 LLM 厂商")

        # 4. 删除默认租户
        DEFAULT_TENANT_ID = "00000000-0000-0000-0000-000000000001"
        existing_tenant = await db.get(Tenant, DEFAULT_TENANT_ID)
        if existing_tenant:
            await db.delete(existing_tenant)
            print("已删除默认租户")

        await db.commit()

        # 5. 重新初始化
        print("开始重新初始化 LLM 数据...")
        await init_all_llm_data(db, DEFAULT_TENANT_ID)

        await db.commit()
        print("LLM 数据重置并初始化完成！")

        # 验证结果
        from app.application.services.llm_service import LLMFactoryService, LLMService

        factories = await LLMFactoryService.get_all_factories(db)
        print(f"\n已创建 {len(factories)} 个厂商:")

        for factory in factories:
            models = await LLMService.get_all(db, fid=factory.name)
            print(f"  - {factory.name}: {len(models)} 个模型")
            if factory.name == "ZHIPU-AI":
                for model in models:
                    print(f"    * {model.llm_name} ({model.model_type})")


if __name__ == "__main__":
    asyncio.run(reset_and_init())
