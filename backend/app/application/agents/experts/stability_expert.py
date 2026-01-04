"""
Stability Expert Agent
稳定性/忠诚度专家智能体
"""

import logging
from typing import Dict, Any

from app.application.agents.base import BaseAgent
from app.application.agents.prompts.stability import get_stability_prompt

logger = logging.getLogger(__name__)


class StabilityExpertAgent(BaseAgent):
    """稳定性/忠诚度专家智能体

    评估候选人的工作稳定性和忠诚度
    """

    def __init__(self, db, tenant_id: str):
        """初始化稳定性专家

        Args:
            db: 数据库会话
            tenant_id: 租户ID
        """
        super().__init__(db, tenant_id, temperature=0.5)

    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """分析稳定性/忠诚度

        Args:
            context: 包含简历数据的上下文

        Returns:
            稳定性分析结果
        """
        # 获取简历数据
        resume_data = context.get("resume_data", {})

        # 构建提示词
        prompt = get_stability_prompt(resume_data)

        try:
            # 调用 LLM
            response = await self._invoke_llm(prompt)

            # 解析 JSON 响应
            result = self._parse_json_response(response)
            logger.info(f"稳定性分析完成，评分: {result.get('score', 0)}")
            return result

        except Exception as e:
            logger.error(f"稳定性分析失败: {e}")
            # 返回默认结构
            return {
                "score": 50,
                "job_tenure_avg": 0,
                "job_changes_count": 0,
                "frequent_hopper_flag": False,
                "career_progression_score": 50,
                "promotion_history": [],
                "role_evolution": "数据不足",
                "leaving_reasons_quality": "无法评估",
                "reason_flags": ["分析失败，数据不足"],
                "stability_indicators": [],
                "risk_factors": ["分析过程出错"],
                "positive_indicators": [],
                "recommendations": f"稳定性分析失败: {str(e)}"
            }
