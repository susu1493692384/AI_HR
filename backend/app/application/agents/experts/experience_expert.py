"""
Experience Expert Agent
工作经验评估专家智能体
"""

import logging
from typing import Dict, Any

from app.application.agents.base import BaseAgent
from app.application.agents.prompts.experience import get_experience_prompt

logger = logging.getLogger(__name__)


class ExperienceExpertAgent(BaseAgent):
    """工作经验评估专家智能体

    分析候选人的工作履历和项目经验
    """

    def __init__(self, db, tenant_id: str):
        """初始化经验专家

        Args:
            db: 数据库会话
            tenant_id: 租户ID
        """
        super().__init__(db, tenant_id, temperature=0.5)

    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """分析工作经验

        Args:
            context: 包含 work_experience, project_experience, resume_text, resume_data 等的上下文

        Returns:
            工作经验分析结果
        """
        # 支持 resume_data 格式
        resume_data = context.get("resume_data", {})

        # 获取工作经验信息
        if isinstance(resume_data, dict):
            # 优先使用 extracted_text，其次 resume_text
            work_experience = (
                resume_data.get("extracted_text") or
                resume_data.get("resume_text") or
                context.get("resume_text") or
                context.get("work_experience", "")
            )
            project_experience = (
                context.get("project_experience") or
                resume_data.get("project_experience", "")
            )
        else:
            work_experience = context.get("resume_text") or context.get("work_experience", "")
            project_experience = context.get("project_experience", "")

        # 构建提示词
        prompt = get_experience_prompt(work_experience, project_experience)

        try:
            # 调用 LLM
            response = await self._invoke_llm(prompt)
            logger.info(f"经验分析LLM响应: {response[:500]}...")  # 记录响应前500字符

            # 解析 JSON 响应
            result = self._parse_json_response(response)
            score = result.get('score', 0)
            logger.info(f"经验分析完成，评分: {score}")
            return result

        except Exception as e:
            logger.error(f"经验分析失败: {e}", exc_info=True)
            # 返回默认结构，给出中等评分
            return {
                "score": 50,  # 给出50分而不是0分
                "credibility_score": 50,
                "risk_level": "C",
                "verified_claims": [],
                "questionable_claims": [],
                "timeline_issues": [],
                "exaggeration_indicators": [],
                "interview_questions": ["请提供详细的工作经验信息"],
                "constructive_feedback": ["简历中工作经验信息不足"],
                "recommendations": f"简历中工作经验信息不足，无法进行准确评估。建议通过面试详细了解工作经历和项目经验。错误: {str(e)[:100]}"
            }
