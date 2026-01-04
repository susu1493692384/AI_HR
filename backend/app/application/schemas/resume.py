"""简历相关的Pydantic模式"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict

from app.domain.entities.resume import ResumeStatus


class ResumeBase(BaseModel):
    """简历基础模式"""
    filename: str = Field(..., description="文件名")
    file_type: str = Field(..., description="文件类型")
    file_size: int = Field(..., description="文件大小（字节）")
    status: ResumeStatus = Field(default=ResumeStatus.UPLOADED, description="处理状态")


class ResumeCreate(ResumeBase):
    """创建简历模式"""
    file_path: str = Field(..., description="文件路径")
    job_position_id: Optional[str] = Field(None, description="关联的职位ID")


class ResumeUpdate(BaseModel):
    """更新简历模式"""
    status: Optional[ResumeStatus] = None
    parsed_content: Optional[Dict[str, Any]] = None


class ResumeParsedContent(BaseModel):
    """简历解析内容模式"""
    personal_info: Dict[str, Any]
    work_experience: List[Dict[str, Any]]
    education: List[Dict[str, Any]]
    skills: List[Dict[str, Any]]
    projects: List[Dict[str, Any]]
    certifications: List[Dict[str, Any]]


class Resume(ResumeBase):
    """简历完整模式"""
    model_config = ConfigDict(from_attributes=True)

    id: str
    file_path: str
    original_content: Optional[str] = None
    parsed_content: Optional[ResumeParsedContent] = None
    upload_time: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None


class ResumeUploadResponse(BaseModel):
    """简历上传响应模式"""
    success: bool
    resume_id: str
    message: str


class AnalysisRequest(BaseModel):
    """简历分析请求模式"""
    job_position_id: str = Field(..., description="目标职位ID")
    ai_model_id: Optional[str] = Field(None, description="AI模型ID，不指定则使用默认模型")


class AnalysisResponse(BaseModel):
    """简历分析响应模式"""
    success: bool
    task_id: str
    message: str


class ResumeFilter(BaseModel):
    """简历筛选模式"""
    keyword: Optional[str] = Field(None, description="关键字搜索")
    status: Optional[ResumeStatus] = Field(None, description="状态筛选")
    skills: Optional[List[str]] = Field(None, description="技能筛选")
    experience_level: Optional[str] = Field(None, description="经验级别")
    date_range: Optional[Dict[str, str]] = Field(None, description="日期范围")


class JobPositionBase(BaseModel):
    """职位基础模式"""
    title: str = Field(..., description="职位名称")
    description: Optional[str] = Field(None, description="职位描述")
    requirements: Optional[Dict[str, Any]] = Field(None, description="职位要求")
    skills_required: Optional[List[Dict[str, Any]]] = Field(None, description="技能要求")
    experience_level: str = Field(..., description="经验级别")
    is_active: bool = Field(default=True, description="是否激活")


class JobPositionCreate(JobPositionBase):
    """创建职位模式"""
    pass


class JobPositionUpdate(BaseModel):
    """更新职位模式"""
    title: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[Dict[str, Any]] = None
    skills_required: Optional[List[Dict[str, Any]]] = None
    experience_level: Optional[str] = None
    is_active: Optional[bool] = None


class JobPosition(JobPositionBase):
    """职位完整模式"""
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None