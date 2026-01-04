"""简历领域实体"""

from enum import Enum
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass
import uuid


class ResumeStatus(str, Enum):
    """简历状态枚举"""
    UPLOADED = "uploaded"        # 已上传
    PARSING = "parsing"          # 解析中
    ANALYZING = "analyzing"      # 分析中
    COMPLETED = "completed"      # 已完成
    FAILED = "failed"           # 失败


@dataclass
class PersonalInfo:
    """个人信息值对象"""
    name: str
    email: str
    phone: str
    location: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None


@dataclass
class WorkExperience:
    """工作经历值对象"""
    company: str
    position: str
    start_date: datetime
    end_date: Optional[datetime] = None
    description: str = ""
    responsibilities: List[str] = None
    achievements: List[str] = None

    def __post_init__(self):
        if self.responsibilities is None:
            self.responsibilities = []
        if self.achievements is None:
            self.achievements = []


@dataclass
class Education:
    """教育背景值对象"""
    school: str
    degree: str
    major: str
    start_date: datetime
    end_date: Optional[datetime] = None
    gpa: Optional[float] = None
    honors: List[str] = None

    def __post_init__(self):
        if self.honors is None:
            self.honors = []


@dataclass
class Skill:
    """技能值对象"""
    name: str
    level: str  # basic, intermediate, advanced, expert
    category: str  # programming, framework, tool, soft_skill
    years_of_experience: Optional[float] = None
    last_used: Optional[datetime] = None


@dataclass
class Project:
    """项目经验值对象"""
    name: str
    description: str
    technologies: List[str]
    start_date: datetime
    end_date: Optional[datetime] = None
    role: str = ""
    achievements: List[str] = None

    def __post_init__(self):
        if self.achievements is None:
            self.achievements = []


@dataclass
class Certification:
    """证书认证值对象"""
    name: str
    issuer: str
    date: datetime
    expiry_date: Optional[datetime] = None
    credential_id: Optional[str] = None


@dataclass
class ResumeParsedContent:
    """简历解析内容值对象"""
    personal_info: PersonalInfo
    work_experience: List[WorkExperience]
    education: List[Education]
    skills: List[Skill]
    projects: List[Project]
    certifications: List[Certification]
    languages: List[Dict[str, str]] = None  # [{"language": "英语", "level": "熟练"}]
    summary: Optional[str] = None  # 个人简介

    def __post_init__(self):
        if self.languages is None:
            self.languages = []


class Resume:
    """简历聚合根"""

    def __init__(
        self,
        filename: str,
        file_path: str,
        file_type: str,
        file_size: int,
        original_content: Optional[str] = None,
        id: Optional[str] = None
    ):
        self.id = id or str(uuid.uuid4())
        self.filename = filename
        self.file_path = file_path
        self.file_type = file_type
        self.file_size = file_size
        self.original_content = original_content
        self.parsed_content: Optional[ResumeParsedContent] = None
        self.status = ResumeStatus.UPLOADED
        self.upload_time = datetime.utcnow()
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def parse_content(self, parsed_content: ResumeParsedContent):
        """解析简历内容"""
        self.parsed_content = parsed_content
        self.status = ResumeStatus.PARSING
        self.updated_at = datetime.utcnow()

    def complete_parsing(self):
        """完成解析"""
        self.status = ResumeStatus.ANALYZING
        self.updated_at = datetime.utcnow()

    def start_analysis(self):
        """开始分析"""
        self.status = ResumeStatus.ANALYZING
        self.updated_at = datetime.utcnow()

    def complete_analysis(self):
        """完成分析"""
        self.status = ResumeStatus.COMPLETED
        self.updated_at = datetime.utcnow()

    def fail(self, error_message: Optional[str] = None):
        """处理失败"""
        self.status = ResumeStatus.FAILED
        self.updated_at = datetime.utcnow()
        # 可以记录错误信息到审计日志

    def can_be_analyzed(self) -> bool:
        """是否可以进行分析"""
        return self.status == ResumeStatus.COMPLETED and self.parsed_content is not None

    def get_years_of_experience(self) -> float:
        """计算工作经验年限"""
        if not self.parsed_content or not self.parsed_content.work_experience:
            return 0.0

        total_months = 0
        current_date = datetime.utcnow()

        for exp in self.parsed_content.work_experience:
            end_date = exp.end_date or current_date
            months = (end_date.year - exp.start_date.year) * 12 + (end_date.month - exp.start_date.month)
            total_months += months

        return round(total_months / 12, 1)

    def get_skill_names(self) -> List[str]:
        """获取技能名称列表"""
        if not self.parsed_content:
            return []
        return [skill.name for skill in self.parsed_content.skills]

    def get_recent_work_experience(self, years: int = 5) -> List[WorkExperience]:
        """获取最近N年的工作经验"""
        if not self.parsed_content or not self.parsed_content.work_experience:
            return []

        cutoff_date = datetime.utcnow().replace(year=datetime.utcnow().year - years)
        recent_exp = []

        for exp in self.parsed_content.work_experience:
            if exp.start_date >= cutoff_date or exp.end_date >= cutoff_date:
                recent_exp.append(exp)

        return recent_exp

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "id": self.id,
            "filename": self.filename,
            "file_path": self.file_path,
            "file_type": self.file_type,
            "file_size": self.file_size,
            "original_content": self.original_content,
            "parsed_content": self.parsed_content.__dict__ if self.parsed_content else None,
            "status": self.status.value,
            "upload_time": self.upload_time.isoformat(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }