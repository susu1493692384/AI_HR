"""
Agent Prompt Templates
智能体提示词模板
"""

from app.application.agents.prompts.coordinator import COORDINATOR_SYSTEM_PROMPT
from app.application.agents.prompts.skills import SKILLS_EXPERT_PROMPT
from app.application.agents.prompts.experience import EXPERIENCE_EXPERT_PROMPT
from app.application.agents.prompts.education import EDUCATION_EXPERT_PROMPT
from app.application.agents.prompts.soft_skills import SOFT_SKILLS_EXPERT_PROMPT

__all__ = [
    "COORDINATOR_SYSTEM_PROMPT",
    "SKILLS_EXPERT_PROMPT",
    "EXPERIENCE_EXPERT_PROMPT",
    "EDUCATION_EXPERT_PROMPT",
    "SOFT_SKILLS_EXPERT_PROMPT",
]
