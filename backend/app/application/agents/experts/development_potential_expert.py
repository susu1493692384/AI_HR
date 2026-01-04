"""
Development Potential Expert Agent
发展潜力专家智能体
"""

import logging
from typing import Dict, Any

from app.application.agents.base import BaseAgent
from app.application.agents.prompts.development_potential import get_development_potential_prompt

logger = logging.getLogger(__name__)


class DevelopmentPotentialExpertAgent(BaseAgent):
    """发展潜力专家智能体

    评估候选人的学习能力、创新能力和未来发展潜力
    """

    def __init__(self, db, tenant_id: str):
        """初始化发展潜力专家

        Args:
            db: 数据库会话
            tenant_id: 租户ID
        """
        super().__init__(db, tenant_id, temperature=0.5)

    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """分析发展潜力

        Args:
            context: 包含简历数据的上下文

        Returns:
            发展潜力分析结果
        """
        # 获取简历数据
        resume_data = context.get("resume_data", {})

        # 构建提示词
        prompt = get_development_potential_prompt(resume_data)

        try:
            # 调用 LLM
            response = await self._invoke_llm(prompt)

            # 解析 JSON 响应
            result = self._parse_json_response(response)
            logger.info(f"发展潜力分析完成，评分: {result.get('score', 0)}")
            return result

        except Exception as e:
            logger.error(f"发展潜力分析失败: {e}")
            # 返回默认结构
            return {
                "score": 50,
                "learning_ability": "信息不足",
                "learning_speed": "信息不足",
                "knowledge_acquisition": [],
                "innovation_capability": "信息不足",
                "innovative_projects": [],
                "problem_solving_creativity": "信息不足",
                "growth_mindset": "信息不足",
                "self_development": [],
                "career_goals_alignment": "信息不足",
                "adaptability_score": 50,
                "change_management": "信息不足",
                "tech_stack_evolution": [],
                "high_potential_flags": [],
                "growth_trajectory": "数据不足",
                "recommendations": f"发展潜力分析失败: {str(e)}"
            }
