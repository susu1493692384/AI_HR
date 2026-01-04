"""应用配置管理"""

from functools import lru_cache
from typing import List, Optional
from pydantic import AnyHttpUrl, EmailStr, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用设置"""

    # 项目信息
    PROJECT_NAME: str = "AI招聘系统"
    PROJECT_DESCRIPTION: str = "基于LangChain/LangGraph的智能简历分析与人才管理系统"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True

    # 安全配置
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30  # 30 days

    # CORS配置
    ALLOWED_HOSTS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # 数据库配置
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/ai_hr"
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "ai_hr"

    # Redis配置
    REDIS_URL: str = "redis://localhost:6379"

    # RAGFlow配置
    RAGFLOW_BASE_URL: str = "https://api.ragflow.ai"
    RAGFLOW_API_KEY: str = ""
    RAGFLOW_KNOWLEDGE_BASE_ID: str = ""

    # 文件上传配置
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "uploads"
    ALLOWED_FILE_TYPES: List[str] = ["application/pdf", "application/msword",
                                     "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]

    # AI模型配置
    DEFAULT_AI_MODEL: str = "gpt-3.5-turbo"
    DEFAULT_TEMPERATURE: float = 0.7
    DEFAULT_MAX_TOKENS: int = 2000

    # 智能体配置
    # 注意：模型配置优先使用租户全局配置 (Tenant.llm_id)
    MAX_PARALLEL_AGENTS: int = 4  # 最大并行智能体数量
    ANALYSIS_TIMEOUT: int = 300  # 分析超时时间（秒）

    # Celery配置
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = None

    @field_validator("ALLOWED_HOSTS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """获取配置实例（单例模式）"""
    return Settings()


settings = get_settings()