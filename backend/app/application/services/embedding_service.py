"""
Embedding 服务
将文本转换为向量，用于语义搜索
"""

import logging
import asyncio
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text

from app.infrastructure.database.llm_models import TenantLLM, Tenant
from app.core.llm_init import DEFAULT_TENANT_ID

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Embedding 服务"""

    def __init__(self, db: AsyncSession):
        """初始化服务"""
        self.db = db
        self._embedding_model: Optional[str] = None
        self._api_key: Optional[str] = None
        self._api_base: Optional[str] = None

    async def _get_embedding_config(self, tenant_id: str = DEFAULT_TENANT_ID) -> Dict[str, str]:
        """获取 embedding 模型配置"""
        # 查询租户配置的 embedding 模型
        result = await self.db.execute(
            select(TenantLLM).where(
                (TenantLLM.tenant_id == tenant_id) &
                (TenantLLM.model_type == 'embedding') &
                (TenantLLM.status == '1')
            )
        )
        config = result.scalar_one_or_none()

        if not config:
            # 使用默认配置
            logger.warning("未找到租户 embedding 配置，使用默认配置")
            return {
                "model": "text-embedding-3-small",
                "api_key": "",
                "api_base": "https://api.openai.com/v1"
            }

        return {
            "model": config.llm_name,
            "api_key": config.api_key or "",
            "api_base": config.api_base or ""
        }

    async def embed_text(self, text: str, tenant_id: str = DEFAULT_TENANT_ID) -> List[float]:
        """
        将文本转换为向量

        Args:
            text: 输入文本
            tenant_id: 租户ID

        Returns:
            向量列表
        """
        config = await self._get_embedding_config(tenant_id)
        model = config["model"]

        try:
            # 根据模型类型选择调用方式
            if "openai" in model.lower() or "embedding-3" in model.lower():
                return await self._embed_openai(text, config)
            elif "zhipu" in model.lower() or "embedding-2" in model.lower():
                return await self._embed_zhipu(text, config)
            elif "ollama" in model.lower():
                return await self._embed_ollama(text, config)
            else:
                # 默认使用 OpenAI 格式
                return await self._embed_openai(text, config)

        except Exception as e:
            logger.error(f"Embedding 生成失败: {str(e)}")
            # 返回零向量作为降级处理
            return [0.0] * 1536  # OpenAI 默认维度

    async def _embed_openai(self, text: str, config: Dict[str, str]) -> List[float]:
        """使用 OpenAI 格式的 API"""
        try:
            import httpx

            headers = {
                "Content-Type": "application/json"
            }
            if config.get("api_key"):
                headers["Authorization"] = f"Bearer {config['api_key']}"

            payload = {
                "input": text,
                "model": config["model"]
            }

            api_base = config.get("api_base", "https://api.openai.com/v1")
            url = f"{api_base.rstrip('/')}/embeddings"

            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                result = response.json()

                return result["data"][0]["embedding"]

        except Exception as e:
            logger.error(f"OpenAI embedding 调用失败: {str(e)}")
            raise

    async def _embed_zhipu(self, text: str, config: Dict[str, str]) -> List[float]:
        """使用智谱 AI 的 embedding API"""
        try:
            import httpx
            import jwt
            import time

            # 生成 JWT token
            api_key = config.get("api_key", "")
            if "." in api_key:
                id, secret = api_key.split(".")
                payload = {
                    "api_key": id,
                    "exp": int(time.time()) + 3600,
                    "timestamp": int(time.time())
                }
                token = jwt.encode(payload, secret, algorithm="HS256")
                authorization = f"Bearer {token}"
            else:
                authorization = f"Bearer {api_key}"

            headers = {
                "Content-Type": "application/json",
                "Authorization": authorization
            }

            payload = {
                "input": text,
                "model": config["model"]
            }

            url = "https://open.bigmodel.cn/api/paas/v4/embeddings"

            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                result = response.json()

                return result["data"][0]["embedding"]

        except Exception as e:
            logger.error(f"智谱 embedding 调用失败: {str(e)}")
            raise

    async def _embed_ollama(self, text: str, config: Dict[str, str]) -> List[float]:
        """使用 Ollama 本地 embedding"""
        try:
            import httpx

            url = f"{config.get('api_base', 'http://localhost:11434')}/api/embeddings"

            payload = {
                "model": config.get("model", "nomic-embed-text"),
                "prompt": text
            }

            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                result = response.json()

                return result.get("embedding", [])

        except Exception as e:
            logger.error(f"Ollama embedding 调用失败: {str(e)}")
            raise

    async def embed_texts_batch(self, texts: List[str], tenant_id: str = DEFAULT_TENANT_ID) -> List[List[float]]:
        """
        批量将文本转换为向量

        Args:
            texts: 输入文本列表
            tenant_id: 租户ID

        Returns:
            向量列表
        """
        # 限制并发数量
        semaphore = asyncio.Semaphore(5)

        async def embed_with_semaphore(text: str):
            async with semaphore:
                return await self.embed_text(text, tenant_id)

        return await asyncio.gather(*[embed_with_semaphore(t) for t in texts])


# 简单的向量存储（基于 PostgreSQL，生产环境建议使用专门的向量数据库）
class VectorStoreService:
    """向量存储服务"""

    @staticmethod
    async def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """计算余弦相似度"""
        if len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = sum(a * a for a in vec1) ** 0.5
        magnitude2 = sum(b * b for b in vec2) ** 0.5

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)

    @staticmethod
    async def search_similar(
        query_vector: List[float],
        candidates: List[Dict[str, Any]],
        top_k: int = 10,
        threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        搜索最相似的向量

        Args:
            query_vector: 查询向量
            candidates: 候选文档列表，每个文档包含 embedding 字段
            top_k: 返回前K个结果
            threshold: 相似度阈值

        Returns:
            排序后的相似文档列表
        """
        results = []

        for candidate in candidates:
            embedding = candidate.get("embedding")
            if not embedding:
                continue

            # 将字符串形式的向量转换为列表
            if isinstance(embedding, str):
                embedding = [float(x) for x in embedding.split(",")]

            similarity = await VectorStoreService.cosine_similarity(query_vector, embedding)

            if similarity >= threshold:
                results.append({
                    **candidate,
                    "similarity": similarity
                })

        # 按相似度排序
        results.sort(key=lambda x: x["similarity"], reverse=True)

        return results[:top_k]
