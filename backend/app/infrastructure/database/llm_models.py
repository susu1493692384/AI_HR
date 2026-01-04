"""
LLM Database Models
Based on RAGFlow LLM configuration system
"""

import time
from sqlalchemy import Column, String, Integer, Boolean, Text, BigInteger, ForeignKey, Index, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

from app.infrastructure.database.database import Base


class BaseModel(Base):
    """基础模型类"""
    __abstract__ = True

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    created_at = Column(BigInteger, default=lambda: int(time.time() * 1000))
    updated_at = Column(BigInteger, default=lambda: int(time.time() * 1000), onupdate=lambda: int(time.time() * 1000))


class Tenant(BaseModel):
    """租户模型 - 对应 RAGFlow 的 tenant 表"""
    __tablename__ = "tenants"

    name = Column(String(100), nullable=True, index=True)
    public_key = Column(String(255), nullable=True, index=True)

    # 默认模型配置
    llm_id = Column(String(128), nullable=False, default="gpt-3.5-turbo@OpenAI", index=True)
    embd_id = Column(String(128), nullable=False, default="text-embedding-3-small@OpenAI", index=True)
    asr_id = Column(String(128), nullable=False, default="whisper-1@OpenAI", index=True)
    img2txt_id = Column(String(128), nullable=False, default="gpt-4o@OpenAI", index=True)
    rerank_id = Column(String(128), nullable=False, default="BAAI/bge-reranker-v2-m3@BAAI", index=True)
    tts_id = Column(String(256), nullable=True, index=True)

    # 配额
    credit = Column(Integer, default=512, index=True)
    status = Column(String(1), nullable=True, default="1", index=True)

    # 关系
    llm_configs = relationship("TenantLLM", back_populates="tenant", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="tenant", cascade="all, delete-orphan")


class LLMFactory(Base):
    """LLM 厂商模型 - 对应 RAGFlow 的 llm_factories 表"""
    __tablename__ = "llm_factories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(128), unique=True, nullable=False, index=True)
    logo = Column(Text, nullable=True)  # base64 encoded logo
    tags = Column(String(255), nullable=False, index=True)  # LLM,Text Embedding,Image2Text,ASR
    rank = Column(Integer, default=0)
    status = Column(String(1), nullable=True, default="1", index=True)


class LLM(Base):
    """LLM 模型元数据 - 对应 RAGFlow 的 llm 表"""
    __tablename__ = "llm"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fid = Column(String(128), nullable=False, index=True)  # Factory ID
    llm_name = Column(String(128), nullable=False, index=True)  # Model name
    model_type = Column(String(128), nullable=False, index=True)  # chat, embedding, image2text, etc.
    max_tokens = Column(Integer, default=0)
    tags = Column(String(255), nullable=False, index=True)
    is_tools = Column(Boolean, nullable=False, default=False)  # 是否支持工具调用
    status = Column(String(1), nullable=True, default="1", index=True)

    __table_args__ = (
        Index('ix_llm_fid_llm_name', 'fid', 'llm_name', unique=True),
    )


class TenantLLM(BaseModel):
    """租户 LLM 配置 - 对应 RAGFlow 的 tenant_llm 表"""
    __tablename__ = "tenant_llm"

    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    llm_factory = Column(String(128), nullable=False, index=True)
    model_type = Column(String(128), nullable=True, index=True)
    llm_name = Column(String(128), nullable=True, default="", index=True)
    api_key = Column(Text, nullable=True)
    api_base = Column(String(255), nullable=True)
    max_tokens = Column(Integer, default=8192, index=True)
    used_tokens = Column(Integer, default=0, index=True)
    status = Column(String(1), nullable=False, default="1")

    # 关系
    tenant = relationship("Tenant", back_populates="llm_configs")

    __table_args__ = (
        Index('ix_tenant_llm_composite', 'tenant_id', 'llm_factory', 'llm_name', unique=True),
    )
