"""
Expert Agents
专家智能体模块 (7维度版本)
"""

from app.application.agents.experts.skills_expert import SkillsExpertAgent
from app.application.agents.experts.experience_expert import ExperienceExpertAgent
from app.application.agents.experts.education_expert import EducationExpertAgent
from app.application.agents.experts.soft_skills_expert import SoftSkillsExpertAgent
from app.application.agents.experts.stability_expert import StabilityExpertAgent
from app.application.agents.experts.work_attitude_expert import WorkAttitudeExpertAgent
from app.application.agents.experts.development_potential_expert import DevelopmentPotentialExpertAgent

__all__ = [
    # 原有4维度
    "SkillsExpertAgent",
    "ExperienceExpertAgent",
    "EducationExpertAgent",
    "SoftSkillsExpertAgent",
    # 新增3维度
    "StabilityExpertAgent",
    "WorkAttitudeExpertAgent",
    "DevelopmentPotentialExpertAgent",
]
