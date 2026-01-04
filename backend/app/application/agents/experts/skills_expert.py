"""
Skills Expert Agent
技能匹配度专家智能体
"""

import logging
from typing import Dict, Any

from app.application.agents.base import BaseAgent
from app.application.agents.prompts.skills import get_skills_prompt

logger = logging.getLogger(__name__)


class SkillsExpertAgent(BaseAgent):
    """技能匹配度专家智能体

    评估候选人的技术技能与目标职位的匹配程度
    """

    def __init__(self, db, tenant_id: str):
        """初始化技能专家

        Args:
            db: 数据库会话
            tenant_id: 租户ID
        """
        super().__init__(db, tenant_id, temperature=0.5)

    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """分析技能匹配度

        Args:
            context: 包含 resume_skills, job_skills（可选）, resume_text, resume_data 等的上下文

        Returns:
            技能分析结果
        """
        # 支持 resume_data 格式
        resume_data = context.get("resume_data", {})

        # 获取简历技能信息
        if isinstance(resume_data, dict):
            resume_text = (
                resume_data.get("extracted_text") or
                resume_data.get("resume_text") or
                context.get("resume_text") or
                context.get("resume_skills", "")
            )
        else:
            resume_text = context.get("resume_text") or context.get("resume_skills", "")

        job_skills = context.get("job_skills", "")

        # 构建提示词
        prompt = get_skills_prompt(resume_text, job_skills)

        try:
            # 调用 LLM
            response = await self._invoke_llm(prompt)
            logger.info(f"技能分析LLM响应: {response[:500]}...")  # 记录响应前500字符

            # 解析 JSON 响应
            result = self._parse_json_response(response)
            score = result.get('score', 0)
            logger.info(f"技能分析完成，评分: {score}")
            return result

        except Exception as e:
            logger.error(f"技能分析失败: {e}", exc_info=True)
            # 返回默认结构，给出中等评分
            return {
                "score": 50,  # 给出50分而不是0分
                "credibility_score": 50,
                "risk_level": "C",
                "verified_claims": [],
                "questionable_claims": [],
                "logical_inconsistencies": [],
                "exaggeration_indicators": [],
                "interview_questions": ["请提供详细的技能信息"],
                "constructive_feedback": ["简历中技能信息不足"],
                "recommendations": f"简历中技能信息不足，无法进行准确评估。建议通过面试或技能测试核实技术能力。错误: {str(e)[:100]}"
            }
