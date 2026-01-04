"""
Agent Analysis Schemas
智能体分析相关的数据模型定义 (增强版 - 7维度)
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# ============================================================================
# 请求模型
# ============================================================================

class ResumeAnalysisRequest(BaseModel):
    """简历分析请求"""
    resume_id: str = Field(..., description="简历ID")
    job_position_id: Optional[str] = Field(None, description="职位ID")
    job_requirements: Optional[Dict[str, Any]] = Field(None, description="职位要求（可选）")
    analysis_profile: Optional[str] = Field("standard", description="分析配置类型 (standard/tech_focused/leadership/junior/senior)")


class ConversationCreateRequest(BaseModel):
    """创建对话请求"""
    title: Optional[str] = Field("新对话", description="对话标题")
    resume_id: Optional[str] = Field(None, description="关联的简历ID")


class SendMessageRequest(BaseModel):
    """发送消息请求"""
    content: str = Field(..., description="消息内容", min_length=1)
    resume_id: Optional[str] = Field(None, description="关联的简历ID")
    use_agent: bool = Field(False, description="是否使用智能体模式（默认为简单对话模式）")


# ============================================================================
# 分析结果模型 - 原有4维度 (增强版)
# ============================================================================

class SkillsAnalysis(BaseModel):
    """技能分析结果 (增强版)"""
    score: int = Field(..., ge=0, le=100, description="技能评分")
    matched_skills: List[Dict[str, str]] = Field(default_factory=list, description="匹配的技能列表")
    missing_skills: List[str] = Field(default_factory=list, description="缺失的技能")
    strengths: List[str] = Field(default_factory=list, description="优势")
    gaps: List[str] = Field(default_factory=list, description="差距")
    recommendations: str = Field("", description="建议")

    # 新增: 子维度评分
    technical_skills_score: int = Field(default=0, ge=0, le=100, description="技术技能分数")
    domain_knowledge_score: int = Field(default=0, ge=0, le=100, description="领域知识分数")
    tools_proficiency_score: int = Field(default=0, ge=0, le=100, description="工具熟练度分数")

    # 新增: 技能熟练度等级 (1-5级)
    skill_proficiency_levels: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="技能熟练度等级列表"
    )
    # 格式: [{"skill": "Python", "level": 4, "evidence": "5年经验，多个项目"}]

    # 新增: 项目量化统计
    project_stats: Dict[str, Any] = Field(
        default_factory=dict,
        description="项目量化统计"
    )
    # 格式: {"total_projects": 15, "lead_projects": 5, "avg_team_size": 8, ...}


class ExperienceAnalysis(BaseModel):
    """工作经验分析结果 (增强版)"""
    score: int = Field(..., ge=0, le=100, description="经验评分")
    total_years: float = Field(..., ge=0, description="总工作年限")
    relevant_years: float = Field(..., ge=0, description="相关工作年限")
    company_analysis: List[Dict[str, str]] = Field(default_factory=list, description="公司分析")
    career_progression: str = Field("", description="职业发展轨迹")
    project_highlights: List[str] = Field(default_factory=list, description="项目亮点")
    management_experience: Optional[str] = Field(None, description="管理经验")
    strengths: List[str] = Field(default_factory=list, description="优势")
    concerns: List[str] = Field(default_factory=list, description="关注点")
    recommendations: str = Field("", description="建议")

    # 新增: 子维度评分
    industry_experience_score: int = Field(default=0, ge=0, le=100, description="行业经验分数")
    role_diversity_score: int = Field(default=0, ge=0, le=100, description="角色多样性分数")
    impact_scale_score: int = Field(default=0, ge=0, le=100, description="影响规模分数")

    # 新增: 量化成就
    quantified_achievements: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="量化成就列表"
    )
    # 格式: [{"metric": "性能提升", "value": "40%", "context": "数据库优化"}]


class EducationAnalysis(BaseModel):
    """教育背景分析结果 (增强版)"""
    score: int = Field(..., ge=0, le=100, description="教育评分")
    highest_degree: str = Field("", description="最高学历")
    university_tier: Optional[str] = Field(None, description="学校层次")
    major_relevance: str = Field("", description="专业相关性")
    gpa: Optional[str] = Field(None, description="GPA")
    honors: List[str] = Field(default_factory=list, description="荣誉奖项")
    certifications: List[str] = Field(default_factory=list, description="证书")
    academic_strengths: List[str] = Field(default_factory=list, description="学术优势")
    learning_capability: str = Field("", description="学习能力")
    recommendations: str = Field("", description="建议")

    # 新增: 子维度评分
    degree_quality_score: int = Field(default=0, ge=0, le=100, description="学历质量分数")
    academic_performance_score: int = Field(default=0, ge=0, le=100, description="学术表现分数")
    continuous_learning_score: int = Field(default=0, ge=0, le=100, description="持续学习分数")


class SoftSkillsAnalysis(BaseModel):
    """软技能分析结果 (增强版)"""
    score: int = Field(..., ge=0, le=100, description="软技能评分")
    communication: str = Field("", description="沟通能力")
    teamwork: str = Field("", description="团队协作")
    leadership: str = Field("", description="领导力")
    problem_solving: str = Field("", description="问题解决能力")
    innovation: str = Field("", description="创新能力")
    adaptability: str = Field("", description="适应能力")
    responsibility: str = Field("", description="责任心")
    strengths: List[str] = Field(default_factory=list, description="优势")
    areas_for_improvement: List[str] = Field(default_factory=list, description="待提升领域")
    recommendations: str = Field("", description="建议")

    # 新增: 子维度评分
    communication_score: int = Field(default=0, ge=0, le=100, description="沟通能力分数")
    collaboration_score: int = Field(default=0, ge=0, le=100, description="协作能力分数")
    leadership_score: int = Field(default=0, ge=0, le=100, description="领导力分数")

    # 新增: 详细指标
    emotional_intelligence: str = Field("", description="情商水平")
    cultural_fit: str = Field("", description="文化匹配度")


# ============================================================================
# 分析结果模型 - 新增3维度
# ============================================================================

class StabilityAnalysis(BaseModel):
    """稳定性/忠诚度分析结果"""
    score: int = Field(..., ge=0, le=100, description="稳定性评分")

    # 工作稳定性指标
    job_tenure_avg: float = Field(..., description="平均每份工作时长（年）")
    job_changes_count: int = Field(..., description="跳槽次数")
    frequent_hopper_flag: bool = Field(default=False, description="频繁跳槽标记")

    # 职业发展轨迹
    career_progression_score: int = Field(..., ge=0, le=100, description="职业发展评分")
    promotion_history: List[str] = Field(default_factory=list, description="晋升历史")
    role_evolution: str = Field("", description="角色演变描述")

    # 离职原因分析
    leaving_reasons_quality: str = Field("", description="离职原因合理性")
    reason_flags: List[str] = Field(default_factory=list, description="离职原因风险标记")

    # 稳定性指标
    stability_indicators: List[Dict[str, str]] = Field(
        default_factory=list,
        description="稳定性指标列表"
    )
    risk_factors: List[str] = Field(default_factory=list, description="风险因素")
    positive_indicators: List[str] = Field(default_factory=list, description="积极指标")

    recommendations: str = Field("", description="建议")


class WorkAttitudeAnalysis(BaseModel):
    """工作态度/抗压性分析结果"""
    score: int = Field(..., ge=0, le=100, description="工作态度评分")

    # 抗压能力
    stress_resistance: str = Field("", description="抗压能力描述")
    stress_handling_examples: List[str] = Field(default_factory=list, description="抗压案例")

    # 责任心
    responsibility_level: str = Field("", description="责任心水平")
    ownership_examples: List[str] = Field(default_factory=list, description="责任心案例")

    # 工作敬业度
    dedication_indicators: List[str] = Field(default_factory=list, description="敬业度指标")
    overtime_willingness: str = Field("", description="加班意愿度")

    # 情绪管理
    emotional_intelligence: str = Field("", description="情绪管理能力")
    conflict_handling: str = Field("", description="冲突处理能力")

    # 子维度评分
    stress_score: int = Field(default=0, ge=0, le=100, description="抗压能力分数")
    responsibility_score: int = Field(default=0, ge=0, le=100, description="责任心分数")
    dedication_score: int = Field(default=0, ge=0, le=100, description="敬业度分数")
    emotional_score: int = Field(default=0, ge=0, le=100, description="情绪管理分数")

    strengths: List[str] = Field(default_factory=list, description="优势")
    concerns: List[str] = Field(default_factory=list, description="关注点")
    recommendations: str = Field("", description="建议")


class DevelopmentPotentialAnalysis(BaseModel):
    """发展潜力分析结果"""
    score: int = Field(..., ge=0, le=100, description="发展潜力评分")

    # 学习能力
    learning_ability: str = Field("", description="学习能力描述")
    learning_speed: str = Field("", description="学习速度")
    knowledge_acquisition: List[str] = Field(default_factory=list, description="知识获取案例")

    # 创新能力
    innovation_capability: str = Field("", description="创新能力描述")
    innovative_projects: List[str] = Field(default_factory=list, description="创新项目")
    problem_solving_creativity: str = Field("", description="问题解决创造性")

    # 成长意愿
    growth_mindset: str = Field("", description="成长心态")
    self_development: List[str] = Field(default_factory=list, description="自我发展证据")
    career_goals_alignment: str = Field("", description="职业目标匹配度")

    # 适应能力
    adaptability_score: int = Field(default=0, ge=0, le=100, description="适应能力分数")
    change_management: str = Field("", description="变革管理能力")
    tech_stack_evolution: List[str] = Field(default_factory=list, description="技术栈演进")

    # 潜力指标
    high_potential_flags: List[str] = Field(default_factory=list, description="高潜力标记")
    growth_trajectory: str = Field("", description="成长轨迹描述")

    recommendations: str = Field("", description="发展建议")


# ============================================================================
# 综合分析结果 (7维度版本)
# ============================================================================

class AnalysisResult(BaseModel):
    """综合分析结果 (7维度版本)"""
    score: int = Field(..., ge=0, le=100, description="综合评分")

    # 原有4维度
    skills: SkillsAnalysis = Field(..., description="技能分析")
    experience: ExperienceAnalysis = Field(..., description="经验分析")
    education: EducationAnalysis = Field(..., description="教育分析")
    soft_skills: SoftSkillsAnalysis = Field(..., description="软技能分析")

    # 新增3维度
    stability: StabilityAnalysis = Field(..., description="稳定性/忠诚度分析")
    work_attitude: WorkAttitudeAnalysis = Field(..., description="工作态度/抗压性分析")
    development_potential: DevelopmentPotentialAnalysis = Field(..., description="发展潜力分析")

    summary: str = Field(..., description="综合评估（3-5句话）")
    recommendations: List[str] = Field(default_factory=list, description="建议列表")

    # 元数据
    analysis_version: str = Field(default="2.0", description="分析版本")
    dimension_count: int = Field(default=7, description="维度数量")


# ============================================================================
# 响应模型
# ============================================================================

class ResumeAnalysisResponse(BaseModel):
    """简历分析响应"""
    analysis: AnalysisResult = Field(..., description="分析结果")
    message_id: str = Field(..., description="消息ID")
    processing_time: float = Field(..., description="处理耗时（秒）")
    conversation_id: Optional[str] = Field(None, description="对话ID")


class Message(BaseModel):
    """消息"""
    id: str = Field(..., description="消息ID")
    conversation_id: str = Field(..., description="对话ID")
    role: str = Field(..., description="角色（user/assistant）")
    content: str = Field(..., description="消息内容")
    created_at: str = Field(..., description="创建时间")


class Conversation(BaseModel):
    """对话"""
    id: str = Field(..., description="对话ID")
    title: str = Field(..., description="对话标题")
    last_message: str = Field(..., description="最后一条消息")
    timestamp: str = Field(..., description="时间戳")
    is_starred: bool = Field(default=False, description="是否收藏")
    message_count: int = Field(..., description="消息数量")


class ConversationListResponse(BaseModel):
    """对话列表响应"""
    items: List[Conversation] = Field(default_factory=list, description="对话列表")
    total: int = Field(..., description="总数")


class ConversationDetailResponse(BaseModel):
    """对话详情响应"""
    conversation: Conversation = Field(..., description="对话信息")
    messages: List[Message] = Field(default_factory=list, description="消息列表")


# ============================================================================
# 流式响应事件模型
# ============================================================================

class AnalysisProgressEvent(BaseModel):
    """分析进度事件"""
    type: str = Field(..., description="事件类型")
    expert: str = Field(..., description="专家名称")
    status: str = Field(..., description="状态")
    message: str = Field(..., description="消息")
    data: Optional[Dict[str, Any]] = Field(None, description="额外数据")
