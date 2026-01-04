"""
LLM Initialization API Endpoint
初始化 LLM 厂商和模型数据的 API
"""

import logging
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func
from sqlalchemy.orm import selectinload

from app.core.dependencies import get_db
from app.core.llm_init import init_all_llm_data
from app.infrastructure.database.llm_models import LLM, LLMFactory, TenantLLM, Tenant

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/init-llm-data")
async def init_llm_data(
    tenant_id: str = None,
    db: AsyncSession = Depends(get_db),
):
    """
    初始化 LLM 厂商和模型数据
    POST /api/v1/llm/init-llm-data?tenant_id=default-tenant

    这个端点会：
    1. 先检查是否已初始化（如果已初始化则快速返回）
    2. 创建所有 LLM 厂商（OpenAI, Anthropic, 等）
    3. 创建所有支持的模型
    4. 创建默认租户配置
    """
    try:
        # 快速检查：如果已有厂商数据，说明已经初始化过了
        from sqlalchemy import func as sql_func

        existing = await db.execute(
            select(sql_func.count(LLMFactory.id))
        )
        factory_count = existing.scalar() or 0

        if factory_count > 0:
            logger.info(f"LLM 数据已初始化 ({factory_count} 个厂商)，跳过")
            return {
                "code": 0,
                "message": "LLM data already initialized",
                "data": {
                    "tenant_id": tenant_id,
                    "factories_count": factory_count,
                    "skipped": True
                }
            }

        # 首次初始化，可能需要较长时间
        logger.info("首次初始化 LLM 数据，这可能需要 30-60 秒...")
        await init_all_llm_data(db, tenant_id)

        return {
            "code": 0,
            "message": "LLM data initialized successfully",
            "data": {
                "tenant_id": tenant_id,
                "factories_initialized": 25,
                "models_initialized": "hundreds"
            }
        }
    except Exception as e:
        logger.error(f"初始化 LLM 数据失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"初始化失败: {str(e)}"
        )


@router.post("/reset-and-init")
async def reset_and_init_llm_data(
    tenant_id: str = None,
    db: AsyncSession = Depends(get_db),
):
    """
    重置并重新初始化 LLM 厂商和模型数据
    POST /api/v1/llm-init/reset-and-init

    这个端点会：
    1. 删除所有租户 LLM 配置
    2. 删除所有 LLM 模型
    3. 删除所有 LLM 厂商
    4. 重新创建所有厂商和模型
    5. 重新创建默认租户配置
    """
    try:
        logger.info("开始重置 LLM 数据...")

        # 1. 删除所有租户 LLM 配置
        await db.execute(delete(TenantLLM))
        logger.info("已删除所有租户 LLM 配置")

        # 2. 删除所有 LLM 模型
        await db.execute(delete(LLM))
        logger.info("已删除所有 LLM 模型")

        # 3. 删除所有 LLM 厂商
        await db.execute(delete(LLMFactory))
        logger.info("已删除所有 LLM 厂商")

        # 4. 删除默认租户（如果存在）
        DEFAULT_TENANT_ID = "00000000-0000-0000-0000-000000000001"
        existing_tenant = await db.get(Tenant, DEFAULT_TENANT_ID)
        if existing_tenant:
            await db.delete(existing_tenant)
            logger.info("已删除默认租户")

        await db.commit()

        # 5. 重新初始化所有数据
        await init_all_llm_data(db, tenant_id or DEFAULT_TENANT_ID)

        logger.info("LLM 数据重置并初始化完成")

        return {
            "code": 0,
            "message": "LLM data reset and initialized successfully",
            "data": {
                "tenant_id": tenant_id or DEFAULT_TENANT_ID,
                "factories_initialized": 25,
                "models_initialized": "hundreds"
            }
        }
    except Exception as e:
        logger.error(f"重置并初始化 LLM 数据失败: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"重置失败: {str(e)}"
        )


@router.get("/check-init-status")
async def check_init_status(
    db: AsyncSession = Depends(get_db),
):
    """
    检查 LLM 数据是否已初始化
    GET /api/v1/llm/check-init-status
    """
    from app.application.services.llm_service import LLMFactoryService

    try:
        factories = await LLMFactoryService.get_all_factories(db)

        return {
            "code": 0,
            "data": {
                "initialized": len(factories) > 0,
                "factory_count": len(factories)
            }
        }
    except Exception as e:
        logger.error(f"检查初始化状态失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"检查失败: {str(e)}"
        )
