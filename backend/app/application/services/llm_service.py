"""
LLM Service
Manages LLM model metadata and configuration
Based on RAGFlow llm_service.py
"""

import logging
from typing import List, Optional, Dict, Any
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.llm_models import LLM, LLMFactory, TenantLLM, Tenant

logger = logging.getLogger(__name__)


class LLMFactoryService:
    """LLM 厂商服务"""

    @staticmethod
    async def get_all_factories(
        db: AsyncSession,
        status: Optional[str] = None
    ) -> List[LLMFactory]:
        """获取所有 LLM 厂商"""
        query = select(LLMFactory)
        if status:
            query = query.where(LLMFactory.status == status)
        query = query.order_by(LLMFactory.rank)

        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_factory_by_name(
        db: AsyncSession,
        name: str
    ) -> Optional[LLMFactory]:
        """根据名称获取厂商"""
        query = select(LLMFactory).where(LLMFactory.name == name)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def create_factory(
        db: AsyncSession,
        name: str,
        tags: str,
        logo: Optional[str] = None,
        rank: int = 0,
        status: str = "1"
    ) -> LLMFactory:
        """创建厂商"""
        factory = LLMFactory(
            name=name,
            tags=tags,
            logo=logo,
            rank=rank,
            status=status
        )
        db.add(factory)
        await db.commit()
        await db.refresh(factory)
        return factory

    @staticmethod
    async def get_allowed_factories(
        db: AsyncSession,
        exclude_names: Optional[List[str]] = None
    ) -> List[LLMFactory]:
        """获取允许的厂商列表"""
        query = select(LLMFactory).where(LLMFactory.status == "1")
        if exclude_names:
            query = query.where(LLMFactory.name.notin_(exclude_names))
        query = query.order_by(LLMFactory.rank)

        result = await db.execute(query)
        return result.scalars().all()


class LLMService:
    """LLM 模型服务"""

    @staticmethod
    async def get_all(
        db: AsyncSession,
        fid: Optional[str] = None,
        model_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[LLM]:
        """获取所有 LLM 模型"""
        query = select(LLM)
        conditions = []

        if fid:
            conditions.append(LLM.fid == fid)
        if model_type:
            conditions.append(LLM.model_type == model_type)
        if status:
            conditions.append(LLM.status == status)

        if conditions:
            query = query.where(and_(*conditions))

        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_by_factory_and_name(
        db: AsyncSession,
        fid: str,
        llm_name: str
    ) -> Optional[LLM]:
        """根据厂商和模型名获取 LLM"""
        query = select(LLM).where(
            and_(
                LLM.fid == fid,
                LLM.llm_name == llm_name
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def create_llm(
        db: AsyncSession,
        fid: str,
        llm_name: str,
        model_type: str,
        max_tokens: int = 0,
        tags: str = "",
        is_tools: bool = False,
        status: str = "1"
    ) -> LLM:
        """创建 LLM 模型"""
        llm = LLM(
            fid=fid,
            llm_name=llm_name,
            model_type=model_type,
            max_tokens=max_tokens,
            tags=tags,
            is_tools=is_tools,
            status=status
        )
        db.add(llm)
        await db.commit()
        await db.refresh(llm)
        return llm

    @staticmethod
    async def get_model_types_by_factory(
        db: AsyncSession,
        factory_name: str
    ) -> set:
        """获取厂商支持的模型类型"""
        llms = await LLMService.get_all(db, fid=factory_name, status="1")
        return set(llm.model_type for llm in llms)


class TenantLLMService:
    """租户 LLM 配置服务"""

    @staticmethod
    async def get_api_key(
        db: AsyncSession,
        tenant_id: str,
        model_name: str
    ) -> Optional[TenantLLM]:
        """获取租户的模型 API 配置"""
        # 解析 model_name (可能包含 @Factory)
        parts = model_name.split("@")
        if len(parts) == 2:
            llm_name, factory = parts[0], parts[1]
        else:
            llm_name, factory = model_name, None

        query = select(TenantLLM).where(
            and_(
                TenantLLM.tenant_id == tenant_id,
                TenantLLM.llm_name == llm_name
            )
        )

        if factory:
            query = query.where(TenantLLM.llm_factory == factory)

        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_my_llms(
        db: AsyncSession,
        tenant_id: str
    ) -> List[Dict[str, Any]]:
        """获取租户已配置的所有模型"""
        query = select(
            TenantLLM.llm_factory,
            LLMFactory.logo,
            LLMFactory.tags,
            TenantLLM.model_type,
            TenantLLM.llm_name,
            TenantLLM.used_tokens,
            TenantLLM.status
        ).join(
            LLMFactory,
            TenantLLM.llm_factory == LLMFactory.name
        ).where(
            and_(
                TenantLLM.tenant_id == tenant_id,
                TenantLLM.api_key.isnot(None)
            )
        )

        result = await db.execute(query)
        rows = result.all()

        return [
            {
                "llm_factory": row.llm_factory,
                "logo": row.logo,
                "tags": row.tags,
                "model_type": row.model_type,
                "llm_name": row.llm_name,
                "used_tokens": row.used_tokens or 0,
                "status": row.status
            }
            for row in rows
        ]

    @staticmethod
    async def get_my_llms_detailed(
        db: AsyncSession,
        tenant_id: str
    ) -> Dict[str, Any]:
        """获取租户已配置的模型（详细）"""
        query = select(TenantLLM).where(
            and_(
                TenantLLM.tenant_id == tenant_id,
                TenantLLM.api_key.isnot(None)
            )
        )

        result = await db.execute(query)
        tenant_llms = result.scalars().all()

        # 获取所有厂商信息
        factories = await LLMFactoryService.get_all_factories(db, status="1")
        factory_dict = {f.name: f for f in factories}

        # 按厂商分组
        res = {}
        for llm in tenant_llms:
            factory_name = llm.llm_factory
            if factory_name not in res:
                factory = factory_dict.get(factory_name)
                res[factory_name] = {
                    "tags": factory.tags if factory else "",
                    "llm": []
                }

            res[factory_name]["llm"].append({
                "type": llm.model_type,
                "name": llm.llm_name,
                "used_token": llm.used_tokens or 0,
                "api_base": llm.api_base or "",
                "max_tokens": llm.max_tokens or 8192,
                "status": llm.status or "1"
            })

        return res

    @staticmethod
    async def add_or_update_llm(
        db: AsyncSession,
        tenant_id: str,
        llm_factory: str,
        llm_name: str,
        model_type: str,
        api_key: str,
        api_base: Optional[str] = None,
        max_tokens: Optional[int] = None
    ) -> TenantLLM:
        """添加或更新租户 LLM 配置"""
        # 查找是否已存在
        query = select(TenantLLM).where(
            and_(
                TenantLLM.tenant_id == tenant_id,
                TenantLLM.llm_factory == llm_factory,
                TenantLLM.llm_name == llm_name
            )
        )
        result = await db.execute(query)
        existing = result.scalar_one_or_none()

        if existing:
            # 更新
            existing.api_key = api_key
            if api_base is not None:
                existing.api_base = api_base
            if max_tokens is not None:
                existing.max_tokens = max_tokens
            await db.commit()
            await db.refresh(existing)
            return existing
        else:
            # 新建
            tenant_llm = TenantLLM(
                tenant_id=tenant_id,
                llm_factory=llm_factory,
                llm_name=llm_name,
                model_type=model_type,
                api_key=api_key,
                api_base=api_base or "",
                max_tokens=max_tokens or 8192
            )
            db.add(tenant_llm)
            await db.commit()
            await db.refresh(tenant_llm)
            return tenant_llm

    @staticmethod
    async def delete_llm(
        db: AsyncSession,
        tenant_id: str,
        llm_factory: str,
        llm_name: str
    ) -> bool:
        """删除租户 LLM 配置"""
        query = select(TenantLLM).where(
            and_(
                TenantLLM.tenant_id == tenant_id,
                TenantLLM.llm_factory == llm_factory,
                TenantLLM.llm_name == llm_name
            )
        )
        result = await db.execute(query)
        tenant_llm = result.scalar_one_or_none()

        if tenant_llm:
            await db.delete(tenant_llm)
            await db.commit()
            return True
        return False

    @staticmethod
    async def set_llm_status(
        db: AsyncSession,
        tenant_id: str,
        llm_factory: str,
        llm_name: str,
        status: str
    ) -> bool:
        """设置 LLM 状态"""
        query = select(TenantLLM).where(
            and_(
                TenantLLM.tenant_id == tenant_id,
                TenantLLM.llm_factory == llm_factory,
                TenantLLM.llm_name == llm_name
            )
        )
        result = await db.execute(query)
        tenant_llm = result.scalar_one_or_none()

        if tenant_llm:
            tenant_llm.status = status
            await db.commit()
            return True
        return False

    @staticmethod
    async def delete_factory(
        db: AsyncSession,
        tenant_id: str,
        llm_factory: str
    ) -> int:
        """删除租户的整个厂商配置"""
        query = select(TenantLLM).where(
            and_(
                TenantLLM.tenant_id == tenant_id,
                TenantLLM.llm_factory == llm_factory
            )
        )
        result = await db.execute(query)
        tenant_llms = result.scalars().all()

        count = 0
        for tenant_llm in tenant_llms:
            await db.delete(tenant_llm)
            count += 1

        await db.commit()
        return count

    @staticmethod
    async def increase_usage(
        db: AsyncSession,
        tenant_id: str,
        llm_type: str,
        used_tokens: int,
        llm_name: Optional[str] = None
    ) -> int:
        """增加 token 使用量"""
        # 根据 llm_type 获取默认模型名称
        tenant = await db.get(Tenant, tenant_id)
        if not tenant:
            return 0

        llm_map = {
            "embedding": tenant.embd_id,
            "speech2text": tenant.asr_id,
            "image2text": tenant.img2txt_id,
            "chat": tenant.llm_id,
            "rerank": tenant.rerank_id,
            "tts": tenant.tts_id,
        }

        mdlnm = llm_map.get(llm_type)
        if not mdlnm:
            return 0

        # 解析模型名和厂商
        parts = mdlnm.split("@")
        if len(parts) == 2:
            actual_llm_name, llm_factory = parts[0], parts[1]
        else:
            actual_llm_name, llm_factory = mdlnm, None

        # 更新使用量
        query = select(TenantLLM).where(
            and_(
                TenantLLM.tenant_id == tenant_id,
                TenantLLM.llm_name == actual_llm_name
            )
        )

        if llm_factory:
            query = query.where(TenantLLM.llm_factory == llm_factory)

        result = await db.execute(query)
        tenant_llm = result.scalar_one_or_none()

        if tenant_llm:
            tenant_llm.used_tokens = (tenant_llm.used_tokens or 0) + used_tokens
            await db.commit()
            return 1

        return 0


class TenantService:
    """租户服务"""

    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        tenant_id: str
    ) -> Optional[Tenant]:
        """根据 ID 获取租户"""
        return await db.get(Tenant, tenant_id)

    @staticmethod
    async def update_default_models(
        db: AsyncSession,
        tenant_id: str,
        llm_id: Optional[str] = None,
        embd_id: Optional[str] = None,
        asr_id: Optional[str] = None,
        img2txt_id: Optional[str] = None,
        rerank_id: Optional[str] = None,
        tts_id: Optional[str] = None
    ) -> Optional[Tenant]:
        """更新租户默认模型"""
        tenant = await db.get(Tenant, tenant_id)
        if not tenant:
            return None

        if llm_id is not None:
            tenant.llm_id = llm_id
        if embd_id is not None:
            tenant.embd_id = embd_id
        if asr_id is not None:
            tenant.asr_id = asr_id
        if img2txt_id is not None:
            tenant.img2txt_id = img2txt_id
        if rerank_id is not None:
            tenant.rerank_id = rerank_id
        if tts_id is not None:
            tenant.tts_id = tts_id

        await db.commit()
        await db.refresh(tenant)
        return tenant
