"""
LLM Initialization Script
初始化 LLM 厂商和模型数据
"""

import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.infrastructure.database.llm_models import LLMFactory, LLM, Tenant
from app.application.services.llm_service import LLMFactoryService, LLMService, TenantService

logger = logging.getLogger(__name__)

# 默认租户 ID - 使用固定的 UUID
DEFAULT_TENANT_ID = "00000000-0000-0000-0000-000000000001"


# LLM 厂商和模型配置数据
LLM_FACTORIES_AND_MODELS = [
    {
        "name": "OpenAI",
        "tags": "LLM,Text Embedding,Image2Text,Speech2Text,TTS",
        "rank": 1,
        "models": [
            {"llm_name": "gpt-4o", "model_type": "chat", "max_tokens": 128000, "tags": "LLM,32k", "is_tools": True},
            {"llm_name": "gpt-4o-mini", "model_type": "chat", "max_tokens": 16384, "tags": "LLM", "is_tools": True},
            {"llm_name": "gpt-4-turbo", "model_type": "chat", "max_tokens": 128000, "tags": "LLM,32k", "is_tools": True},
            {"llm_name": "gpt-3.5-turbo", "model_type": "chat", "max_tokens": 16384, "tags": "LLM", "is_tools": True},
            {"llm_name": "text-embedding-3-small", "model_type": "embedding", "max_tokens": 8191, "tags": "Text Embedding"},
            {"llm_name": "text-embedding-3-large", "model_type": "embedding", "max_tokens": 8191, "tags": "Text Embedding"},
            {"llm_name": "gpt-4o", "model_type": "image2text", "max_tokens": 128000, "tags": "Image2Text", "is_tools": False},
            {"llm_name": "whisper-1", "model_type": "speech2text", "max_tokens": 0, "tags": "Speech2Text", "is_tools": False},
            {"llm_name": "tts-1", "model_type": "tts", "max_tokens": 0, "tags": "TTS", "is_tools": False},
            {"llm_name": "tts-1-hd", "model_type": "tts", "max_tokens": 0, "tags": "TTS", "is_tools": False},
        ]
    },
    {
        "name": "Anthropic",
        "tags": "LLM",
        "rank": 2,
        "models": [
            {"llm_name": "claude-3-5-sonnet-20241022", "model_type": "chat", "max_tokens": 200000, "tags": "LLM,200k", "is_tools": True},
            {"llm_name": "claude-3-5-sonnet-20240620", "model_type": "chat", "max_tokens": 200000, "tags": "LLM,200k", "is_tools": True},
            {"llm_name": "claude-3-opus-20240229", "model_type": "chat", "max_tokens": 200000, "tags": "LLM,200k", "is_tools": True},
            {"llm_name": "claude-3-sonnet-20240229", "model_type": "chat", "max_tokens": 200000, "tags": "LLM,200k", "is_tools": True},
            {"llm_name": "claude-3-haiku-20240307", "model_type": "chat", "max_tokens": 200000, "tags": "LLM,200k", "is_tools": True},
        ]
    },
    {
        "name": "Azure-OpenAI",
        "tags": "LLM,Text Embedding,Image2Text,Speech2Text,TTS",
        "rank": 3,
        "models": [
            {"llm_name": "gpt-4o", "model_type": "chat", "max_tokens": 128000, "tags": "LLM,32k", "is_tools": True},
            {"llm_name": "gpt-4o-mini", "model_type": "chat", "max_tokens": 16384, "tags": "LLM", "is_tools": True},
            {"llm_name": "gpt-35-turbo", "model_type": "chat", "max_tokens": 16384, "tags": "LLM", "is_tools": True},
            {"llm_name": "text-embedding-3-small", "model_type": "embedding", "max_tokens": 8191, "tags": "Text Embedding"},
            {"llm_name": "text-embedding-ada-002", "model_type": "embedding", "max_tokens": 8191, "tags": "Text Embedding"},
        ]
    },
    {
        "name": "Google Cloud",
        "tags": "LLM,Text Embedding,Image2Text,Speech2Text,TTS",
        "rank": 4,
        "models": [
            {"llm_name": "gemini-1.5-pro", "model_type": "chat", "max_tokens": 2800000, "tags": "LLM", "is_tools": True},
            {"llm_name": "gemini-1.5-flash", "model_type": "chat", "max_tokens": 2800000, "tags": "LLM", "is_tools": True},
            {"llm_name": "gemini-pro", "model_type": "chat", "max_tokens": 91728, "tags": "LLM", "is_tools": True},
            {"llm_name": "gemini-pro-vision", "model_type": "image2text", "max_tokens": 65536, "tags": "Image2Text", "is_tools": False},
            {"llm_name": "text-embedding-004", "model_type": "embedding", "max_tokens": 0, "tags": "Text Embedding", "is_tools": False},
        ]
    },
    {
        "name": "Bedrock",
        "tags": "LLM,Text Embedding",
        "rank": 5,
        "models": [
            {"llm_name": "anthropic.claude-3-5-sonnet-20241022-v2:0", "model_type": "chat", "max_tokens": 200000, "tags": "LLM", "is_tools": True},
            {"llm_name": "anthropic.claude-3-opus-20240229-v1:0", "model_type": "chat", "max_tokens": 200000, "tags": "LLM", "is_tools": True},
            {"llm_name": "anthropic.claude-3-sonnet-20240229-v1:0", "model_type": "chat", "max_tokens": 200000, "tags": "LLM", "is_tools": True},
            {"llm_name": "us.amazon.nova-pro-v1:0", "model_type": "chat", "max_tokens": 512000, "tags": "LLM", "is_tools": True},
            {"llm_name": "amazon.titan-embed-text-v1", "model_type": "embedding", "max_tokens": 8192, "tags": "Text Embedding", "is_tools": False},
        ]
    },
    {
        "name": "Ollama",
        "tags": "LLM,Text Embedding,Image2Text,Speech2Text,Rerank,TTS,OCR",
        "rank": 6,
        "models": [
            # Ollama 模型由用户自己部署，这里只提供常见示例
            {"llm_name": "llama3.2", "model_type": "chat", "max_tokens": 128000, "tags": "LLM", "is_tools": True},
            {"llm_name": "llama3.1", "model_type": "chat", "max_tokens": 128000, "tags": "LLM", "is_tools": True},
            {"llm_name": "qwen2.5", "model_type": "chat", "max_tokens": 128000, "tags": "LLM", "is_tools": True},
            {"llm_name": "mistral", "model_type": "chat", "max_tokens": 128000, "tags": "LLM", "is_tools": True},
            {"llm_name": "nomic-embed-text", "model_type": "embedding", "max_tokens": 8192, "tags": "Text Embedding", "is_tools": False},
            {"llm_name": "mxbai-embed-large", "model_type": "embedding", "max_tokens": 8192, "tags": "Text Embedding", "is_tools": False},
            {"llm_name": "llava", "model_type": "image2text", "max_tokens": 0, "tags": "Image2Text", "is_tools": False},
        ]
    },
    {
        "name": "Xinference",
        "tags": "LLM,Text Embedding,Image2Text,Speech2Text,Rerank,TTS,OCR",
        "rank": 7,
        "models": [
            {"llm_name": "auto", "model_type": "chat", "max_tokens": 0, "tags": "LLM", "is_tools": True},
            {"llm_name": "auto", "model_type": "embedding", "max_tokens": 0, "tags": "Text Embedding", "is_tools": False},
            {"llm_name": "auto", "model_type": "rerank", "max_tokens": 0, "tags": "Rerank", "is_tools": False},
        ]
    },
    {
        "name": "LocalAI",
        "tags": "LLM,Text Embedding,Image2Text,Speech2Text,TTS",
        "rank": 8,
        "models": [
            {"llm_name": "auto", "model_type": "chat", "max_tokens": 0, "tags": "LLM", "is_tools": True},
            {"llm_name": "auto", "model_type": "embedding", "max_tokens": 0, "tags": "Text Embedding", "is_tools": False},
        ]
    },
    {
        "name": "LM-Studio",
        "tags": "LLM,Image2Text,Speech2Text",
        "rank": 9,
        "models": [
            {"llm_name": "auto", "model_type": "chat", "max_tokens": 0, "tags": "LLM", "is_tools": True},
        ]
    },
    {
        "name": "HuggingFace",
        "tags": "LLM,Text Embedding,Image2Text,Speech2Text,Rerank,TTS",
        "rank": 10,
        "models": [
            {"llm_name": "auto", "model_type": "chat", "max_tokens": 0, "tags": "LLM", "is_tools": True},
            {"llm_name": "auto", "model_type": "embedding", "max_tokens": 0, "tags": "Text Embedding", "is_tools": False},
        ]
    },
    {
        "name": "VolcEngine",
        "tags": "LLM,Text Embedding",
        "rank": 11,
        "models": [
            {"llm_name": "doubao-pro-32k", "model_type": "chat", "max_tokens": 32768, "tags": "LLM", "is_tools": True},
            {"llm_name": "doubao-pro-256k", "model_type": "chat", "max_tokens": 262144, "tags": "LLM", "is_tools": True},
            {"llm_name": "doubao-embedding", "model_type": "embedding", "max_tokens": 0, "tags": "Text Embedding", "is_tools": False},
        ]
    },
    {
        "name": "Tongyi-Qianwen",
        "tags": "LLM,Text Embedding",
        "rank": 12,
        "models": [
            {"llm_name": "qwen-max", "model_type": "chat", "max_tokens": 30720, "tags": "LLM", "is_tools": True},
            {"llm_name": "qwen-plus", "model_type": "chat", "max_tokens": 128000, "tags": "LLM", "is_tools": True},
            {"llm_name": "qwen-turbo", "model_type": "chat", "max_tokens": 8192, "tags": "LLM", "is_tools": True},
            {"llm_name": "text-embedding-v3", "model_type": "embedding", "max_tokens": 0, "tags": "Text Embedding", "is_tools": False},
        ]
    },
    {
        "name": "Moonshot",
        "tags": "LLM",
        "rank": 13,
        "models": [
            {"llm_name": "moonshot-v1-128k", "model_type": "chat", "max_tokens": 131072, "tags": "LLM", "is_tools": True},
            {"llm_name": "moonshot-v1-32k", "model_type": "chat", "max_tokens": 32768, "tags": "LLM", "is_tools": True},
            {"llm_name": "moonshot-v1-8k", "model_type": "chat", "max_tokens": 8192, "tags": "LLM", "is_tools": True},
        ]
    },
    {
        "name": "ZHIPU-AI",
        "tags": "LLM,Text Embedding",
        "rank": 14,
        "models": [
            {"llm_name": "glm-4-plus", "model_type": "chat", "max_tokens": 128000, "tags": "LLM", "is_tools": True},
            {"llm_name": "glm-4-0520", "model_type": "chat", "max_tokens": 128000, "tags": "LLM", "is_tools": True},
            {"llm_name": "glm-4-air", "model_type": "chat", "max_tokens": 128000, "tags": "LLM", "is_tools": True},
            {"llm_name": "glm-4-airx", "model_type": "chat", "max_tokens": 128000, "tags": "LLM", "is_tools": True},
            {"llm_name": "glm-4-flash", "model_type": "chat", "max_tokens": 128000, "tags": "LLM", "is_tools": True},
            {"llm_name": "glm-4", "model_type": "chat", "max_tokens": 128000, "tags": "LLM", "is_tools": True},
            {"llm_name": "glm-4-long", "model_type": "chat", "max_tokens": 128000, "tags": "LLM", "is_tools": True},
            {"llm_name": "glm-3-turbo", "model_type": "chat", "max_tokens": 128000, "tags": "LLM", "is_tools": True},
            {"llm_name": "glm-4.5", "model_type": "chat", "max_tokens": 128000, "tags": "LLM", "is_tools": True},
            {"llm_name": "glm-4.5-plus", "model_type": "chat", "max_tokens": 128000, "tags": "LLM", "is_tools": True},
            {"llm_name": "glm-4.5-air", "model_type": "chat", "max_tokens": 128000, "tags": "LLM", "is_tools": True},
            {"llm_name": "glm-4.5-flash", "model_type": "chat", "max_tokens": 128000, "tags": "LLM", "is_tools": True},
            {"llm_name": "embedding-3", "model_type": "embedding", "max_tokens": 0, "tags": "Text Embedding", "is_tools": False},
            {"llm_name": "embedding-2", "model_type": "embedding", "max_tokens": 0, "tags": "Text Embedding", "is_tools": False},
        ]
    },
    {
        "name": "DeepSeek",
        "tags": "LLM,Text Embedding",
        "rank": 15,
        "models": [
            {"llm_name": "deepseek-chat", "model_type": "chat", "max_tokens": 128000, "tags": "LLM", "is_tools": True},
            {"llm_name": "deepseek-coder", "model_type": "chat", "max_tokens": 128000, "tags": "LLM", "is_tools": True},
            {"llm_name": "deepseek-reasoner", "model_type": "chat", "max_tokens": 65536, "tags": "LLM", "is_tools": True},
        ]
    },
    {
        "name": "Minimax",
        "tags": "LLM",
        "rank": 16,
        "models": [
            {"llm_name": "abab6.5s-chat", "model_type": "chat", "max_tokens": 245760, "tags": "LLM", "is_tools": True},
            {"llm_name": "abab6.5g-chat", "model_type": "chat", "max_tokens": 245760, "tags": "LLM", "is_tools": True},
            {"llm_name": "abab5.5s-chat", "model_type": "chat", "max_tokens": 8192, "tags": "LLM", "is_tools": True},
        ]
    },
    {
        "name": "Tencent Hunyuan",
        "tags": "LLM",
        "rank": 17,
        "models": [
            {"llm_name": "hunyuan-pro", "model_type": "chat", "max_tokens": 128000, "tags": "LLM", "is_tools": True},
            {"llm_name": "hunyuan-standard", "model_type": "chat", "max_tokens": 128000, "tags": "LLM", "is_tools": True},
            {"llm_name": "hunyuan-lite", "model_type": "chat", "max_tokens": 256000, "tags": "LLM", "is_tools": True},
        ]
    },
    {
        "name": "XunFei Spark",
        "tags": "LLM,TTS",
        "rank": 18,
        "models": [
            {"llm_name": "spark-default", "model_type": "chat", "max_tokens": 128000, "tags": "LLM", "is_tools": True},
            {"llm_name": "spark-pro", "model_type": "chat", "max_tokens": 128000, "tags": "LLM", "is_tools": True},
            {"llm_name": "spark-lite", "model_type": "chat", "max_tokens": 128000, "tags": "LLM", "is_tools": True},
            {"llm_name": "tts-default", "model_type": "tts", "max_tokens": 0, "tags": "TTS", "is_tools": False},
        ]
    },
    {
        "name": "BaiduYiyan",
        "tags": "LLM",
        "rank": 19,
        "models": [
            {"llm_name": "ernie-4.0-8k", "model_type": "chat", "max_tokens": 8192, "tags": "LLM", "is_tools": True},
            {"llm_name": "ernie-4.0-8k-preview", "model_type": "chat", "max_tokens": 8192, "tags": "LLM", "is_tools": True},
            {"llm_name": "ernie-speed-128k", "model_type": "chat", "max_tokens": 131072, "tags": "LLM", "is_tools": True},
            {"llm_name": "ernie-tiny-8k", "model_type": "chat", "max_tokens": 8192, "tags": "LLM", "is_tools": True},
        ]
    },
    {
        "name": "Fish Audio",
        "tags": "TTS",
        "rank": 20,
        "models": [
            {"llm_name": "fish-default", "model_type": "tts", "max_tokens": 0, "tags": "TTS", "is_tools": False},
        ]
    },
    {
        "name": "BAAI",
        "tags": "Text Embedding,Rerank",
        "rank": 21,
        "models": [
            {"llm_name": "bge-large-zh-v1.5", "model_type": "embedding", "max_tokens": 512, "tags": "Text Embedding", "is_tools": False},
            {"llm_name": "bge-small-zh-v1.5", "model_type": "embedding", "max_tokens": 512, "tags": "Text Embedding", "is_tools": False},
            {"llm_name": "bge-m3", "model_type": "embedding", "max_tokens": 8192, "tags": "Text Embedding", "is_tools": False},
            {"llm_name": "bge-reranker-v2-m3", "model_type": "rerank", "max_tokens": 0, "tags": "Rerank", "is_tools": False},
        ]
    },
    {
        "name": "OpenRouter",
        "tags": "LLM",
        "rank": 22,
        "models": [
            {"llm_name": "auto", "model_type": "chat", "max_tokens": 0, "tags": "LLM", "is_tools": True},
        ]
    },
    {
        "name": "MinerU",
        "tags": "OCR",
        "rank": 23,
        "models": [
            {"llm_name": "mineru-default", "model_type": "ocr", "max_tokens": 0, "tags": "OCR", "is_tools": False},
        ]
    },
    {
        "name": "Gemini",
        "tags": "LLM",
        "rank": 24,
        "models": [
            {"llm_name": "gemini-2.0-flash-exp", "model_type": "chat", "max_tokens": 1000000, "tags": "LLM", "is_tools": True},
            {"llm_name": "gemini-exp-1206", "model_type": "chat", "max_tokens": 1000000, "tags": "LLM", "is_tools": True},
        ]
    },
    {
        "name": "Mistral",
        "tags": "LLM,Text Embedding",
        "rank": 25,
        "models": [
            {"llm_name": "mistral-large-latest", "model_type": "chat", "max_tokens": 128000, "tags": "LLM", "is_tools": True},
            {"llm_name": "mistral-small-latest", "model_type": "chat", "max_tokens": 32000, "tags": "LLM", "is_tools": True},
            {"llm_name": "codestral-latest", "model_type": "chat", "max_tokens": 32000, "tags": "LLM", "is_tools": True},
            {"llm_name": "mistral-embed", "model_type": "embedding", "max_tokens": 0, "tags": "Text Embedding", "is_tools": False},
        ]
    },
]


async def init_llm_factories_and_models(db: AsyncSession) -> None:
    """
    初始化 LLM 厂商和模型数据
    如果厂商或模型已存在则跳过
    """
    try:
        logger.info("开始初始化 LLM 厂商和模型数据...")

        for factory_data in LLM_FACTORIES_AND_MODELS:
            factory_name = factory_data["name"]

            # 检查厂商是否已存在
            existing_factory = await LLMFactoryService.get_factory_by_name(db, factory_name)

            if not existing_factory:
                # 创建新厂商
                await LLMFactoryService.create_factory(
                    db=db,
                    name=factory_name,
                    tags=factory_data["tags"],
                    rank=factory_data.get("rank", 0),
                    status="1"
                )
                logger.info(f"创建厂商: {factory_name}")
            else:
                logger.info(f"厂商已存在，跳过: {factory_name}")

            # 获取厂商（可能是刚创建的）
            factory = await LLMFactoryService.get_factory_by_name(db, factory_name)

            # 添加模型
            for model_data in factory_data.get("models", []):
                # 检查模型是否已存在
                existing_model = await LLMService.get_by_factory_and_name(
                    db,
                    fid=factory_name,
                    llm_name=model_data["llm_name"]
                )

                if not existing_model:
                    await LLMService.create_llm(
                        db=db,
                        fid=factory_name,
                        llm_name=model_data["llm_name"],
                        model_type=model_data["model_type"],
                        max_tokens=model_data.get("max_tokens", 0),
                        tags=model_data.get("tags", ""),
                        is_tools=model_data.get("is_tools", False),
                        status="1"
                    )
                    logger.info(f"  创建模型: {factory_name}/{model_data['llm_name']}")
                else:
                    logger.info(f"  模型已存在，跳过: {factory_name}/{model_data['llm_name']}")

        logger.info("LLM 厂商和模型数据初始化完成！")

    except Exception as e:
        logger.error(f"初始化 LLM 数据失败: {str(e)}")
        raise


async def init_default_tenant(db: AsyncSession, tenant_id: str = None) -> None:
    """
    初始化默认租户
    如果不存在则创建
    """
    # 使用固定的默认租户 UUID
    DEFAULT_TENANT_ID = "00000000-0000-0000-0000-000000000001"

    try:
        # 检查租户是否已存在
        existing_tenant = await TenantService.get_by_id(db, DEFAULT_TENANT_ID)

        if not existing_tenant:
            # 创建新租户
            tenant = Tenant(
                id=DEFAULT_TENANT_ID,
                name="默认租户",
                llm_id="gpt-3.5-turbo@OpenAI",
                embd_id="text-embedding-3-small@OpenAI",
                asr_id="whisper-1@OpenAI",
                img2txt_id="gpt-4o@OpenAI",
                rerank_id="bge-reranker-v2-m3@BAAI",
                tts_id="tts-1@OpenAI",
                credit=512,
                status="1"
            )
            db.add(tenant)
            await db.commit()
            logger.info(f"创建默认租户: {DEFAULT_TENANT_ID}")
        else:
            logger.info(f"租户已存在: {DEFAULT_TENANT_ID}")

    except Exception as e:
        logger.error(f"初始化默认租户失败: {str(e)}")
        raise


async def init_all_llm_data(db: AsyncSession, default_tenant_id: str = None) -> None:
    """
    初始化所有 LLM 相关数据
    """
    await init_llm_factories_and_models(db)
    await init_default_tenant(db)
