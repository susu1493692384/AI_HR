"""
Work Attitude Expert Agent
工作态度/抗压性专家智能体
"""

import logging
from typing import Dict, Any

from app.application.agents.base import BaseAgent
from app.application.agents.prompts.work_attitude import get_work_attitude_prompt

logger = logging.getLogger(__name__)


class WorkAttitudeExpertAgent(BaseAgent):
    """工作态度/抗压性专家智能体

    评估候选人的工作态度、责任心和抗压能力
    """

    def __init__(self, db, tenant_id: str):
        """初始化工作态度专家

        Args:
            db: 数据库会话
            tenant_id: 租户ID
        """
        super().__init__(db, tenant_id, temperature=0.5)

    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """分析工作态度/抗压性

        Args:
            context: 包含简历数据的上下文

        Returns:
            工作态度分析结果
        """
        # 获取简历数据
        resume_data = context.get("resume_data", {})

        # 构建提示词
        prompt = get_work_attitude_prompt(resume_data)

        try:
            # 调用 LLM
            response = await self._invoke_llm(prompt)

            # 解析 JSON 响应
            result = self._parse_json_response(response)
            logger.info(f"工作态度分析完成，评分: {result.get('score', 0)}")
            return result

        except Exception as e:
            logger.error(f"工作态度分析失败: {e}")
            # 返回默认结构
            return {
                "score": 50,
                "stress_resistance": "信息不足",
                "stress_handling_examples": [],
                "responsibility_level": "信息不足",
                "ownership_examples": [],
                "dedication_indicators": [],
                "overtime_willingness": "信息不足",
                "emotional_intelligence": "信息不足",
                "conflict_handling": "信息不足",
                "stress_score": 50,
                "responsibility_score": 50,
                "dedication_score": 50,
                "emotional_score": 50,
                "strengths": [],
                "concerns": ["分析失败，数据不足"],
                "recommendations": f"工作态度分析失败: {str(e)}"
            }
