"""
AI Agents Module
多智能体简历分析系统
"""

from app.application.agents.base import BaseAgent
from app.application.agents.coordinator import ResumeAnalysisCoordinator

__all__ = ["BaseAgent", "ResumeAnalysisCoordinator"]
