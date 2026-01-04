"""数据库模型定义"""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.infrastructure.database.database import Base


class BaseModel(Base):
    """基础模型类"""
    __abstract__ = True

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class User(BaseModel):
    """用户模型"""
    __tablename__ = "users"

    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default="user", nullable=False)  # admin, hr, interviewer
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime(timezone=True))

    # 关系
    created_job_positions = relationship("JobPosition", back_populates="creator")

    @property
    def id_str(self) -> str:
        """Return id as string for serialization"""
        return str(self.id)


class Resume(BaseModel):
    """简历模型"""
    __tablename__ = "resumes"

    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size = Column(Integer, nullable=False)
    original_content = Column(Text)
    parsed_content = Column(JSON)
    upload_time = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String(50), default="uploaded", nullable=False)  # uploaded, parsing, completed, failed

    # 提取的文本内容（用于 embedding）
    extracted_text = Column(Text)

    # 向量存储相关
    embedding_id = Column(String(255))  # 向量库中的ID
    embedding_model = Column(String(100))  # 使用的 embedding 模型名称

    # 简历基本信息（从解析结果中提取）
    candidate_name = Column(String(255))
    candidate_email = Column(String(255))
    candidate_phone = Column(String(50))
    candidate_location = Column(String(255))

    # 用户关联 - 用于数据隔离
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)

    # 关系
    analyses = relationship("ResumeAnalysis", back_populates="resume")
    uploader = relationship("User")


class JobPosition(BaseModel):
    """职位模型"""
    __tablename__ = "job_positions"

    title = Column(String(255), nullable=False)
    description = Column(Text)
    requirements = Column(JSON)
    skills_required = Column(JSON)
    experience_level = Column(String(50), nullable=False)  # entry, mid, senior, lead, principal
    salary_range = Column(JSON)  # {min, max, currency}
    is_active = Column(Boolean, default=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # 关系
    creator = relationship("User", back_populates="created_job_positions")
    analyses = relationship("ResumeAnalysis", back_populates="job_position")


class AIModel(BaseModel):
    """AI模型配置模型"""
    __tablename__ = "ai_models"

    name = Column(String(255), nullable=False)
    provider = Column(String(100), nullable=False)  # openai, baidu, alibaba, google, anthropic, custom
    model_name = Column(String(255), nullable=False)
    api_key_encrypted = Column(Text, nullable=False)
    base_url = Column(String(500))
    model_type = Column(String(50), nullable=False)  # chat, completion, embedding
    is_active = Column(Boolean, default=False)
    test_results = Column(JSON)

    # 关系
    analyses = relationship("ResumeAnalysis", back_populates="ai_model")


class ResumeAnalysis(BaseModel):
    """简历分析结果模型"""
    __tablename__ = "resume_analyses"

    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id"), nullable=False)
    job_position_id = Column(UUID(as_uuid=True), ForeignKey("job_positions.id"), nullable=False)
    ai_model_id = Column(UUID(as_uuid=True), ForeignKey("ai_models.id"), nullable=False)
    overall_score = Column(Float)
    skill_score = Column(Float)
    experience_score = Column(Float)
    culture_fit_score = Column(Float)
    detailed_analysis = Column(JSON)
    analysis_duration = Column(Integer)  # 分析耗时（毫秒）

    # 关系
    resume = relationship("Resume", back_populates="analyses")
    job_position = relationship("JobPosition", back_populates="analyses")
    ai_model = relationship("AIModel", back_populates="analyses")
    skill_matches = relationship("SkillMatch", back_populates="resume_analysis")


class SkillMatch(BaseModel):
    """技能匹配模型"""
    __tablename__ = "skill_matches"

    resume_analysis_id = Column(UUID(as_uuid=True), ForeignKey("resume_analyses.id"), nullable=False)
    skill_name = Column(String(255), nullable=False)
    skill_level = Column(String(50))
    relevance_score = Column(Float, nullable=False)
    evidence = Column(Text)

    # 关系
    resume_analysis = relationship("ResumeAnalysis", back_populates="skill_matches")


class RAGFlowKnowledgeBase(BaseModel):
    """RAGFlow知识库配置模型"""
    __tablename__ = "ragflow_knowledge_bases"

    kb_id = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)


class RAGFlowDocument(BaseModel):
    """RAGFlow文档模型"""
    __tablename__ = "ragflow_documents"

    kb_id = Column(String(255), nullable=False)
    ragflow_doc_id = Column(String(255), nullable=False)
    filename = Column(String(255), nullable=False)
    status = Column(String(50), default="processing")  # processing, completed, failed
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True))


class SystemConfig(BaseModel):
    """系统配置模型"""
    __tablename__ = "system_config"

    config_key = Column(String(255), unique=True, nullable=False)
    config_value = Column(JSON, nullable=False)
    description = Column(Text)


class AuditLog(BaseModel):
    """审计日志模型"""
    __tablename__ = "audit_logs"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    action = Column(String(100), nullable=False)  # create, update, delete, login, logout
    resource_type = Column(String(100))  # resume, ai_model, job_position
    resource_id = Column(String(255))
    details = Column(JSON)
    ip_address = Column(String(45))
    user_agent = Column(Text)

    # 关系
    user = relationship("User")


class Conversation(BaseModel):
    """对话模型"""
    __tablename__ = "conversations"

    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    title = Column(String(255), nullable=False, default="新对话")
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id"), nullable=True)
    job_position_id = Column(UUID(as_uuid=True), ForeignKey("job_positions.id"), nullable=True)
    model_name = Column(String(255))  # 使用的AI模型
    status = Column(String(50), default="active")  # active, archived, deleted
    meta_data = Column(JSON)  # 额外的对话元数据

    # 关系
    tenant = relationship("Tenant", back_populates="conversations")
    user = relationship("User")
    resume = relationship("Resume")
    job_position = relationship("JobPosition")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")


class Message(BaseModel):
    """消息模型"""
    __tablename__ = "messages"

    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False)
    role = Column(String(50), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    meta_data = Column(JSON)  # 额外的消息元数据（token使用、模型参数等）
    tokens_used = Column(Integer)  # 使用的token数量

    # 关系
    conversation = relationship("Conversation", back_populates="messages")