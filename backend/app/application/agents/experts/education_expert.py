"""
Education Expert Agent
教育背景分析专家智能体
"""

import logging
from typing import Dict, Any

from app.application.agents.base import BaseAgent
from app.application.agents.prompts.education import get_education_prompt

logger = logging.getLogger(__name__)


class EducationExpertAgent(BaseAgent):
    """教育背景分析专家智能体

    评估候选人的学历和专业背景
    """

    def __init__(self, db, tenant_id: str):
        """初始化教育专家

        Args:
            db: 数据库会话
            tenant_id: 租户ID
        """
        super().__init__(db, tenant_id, temperature=0.5)

    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """分析教育背景

        Args:
            context: 包含 education_background, resume_text, resume_data 等的上下文

        Returns:
            教育背景分析结果
        """
        # 支持 resume_data 格式
        resume_data = context.get("resume_data", {})

        # 获取教育背景信息
        if isinstance(resume_data, dict):
            education_background = (
                resume_data.get("extracted_text") or
                resume_data.get("resume_text") or
                context.get("education_background") or
                context.get("resume_text", "")
            )
        else:
            education_background = context.get("education_background") or context.get("resume_text", "")

        # 构建提示词
        prompt = get_education_prompt(education_background)

        try:
            # 调用 LLM
            response = await self._invoke_llm(prompt)
            logger.info(f"教育分析LLM响应: {response[:500]}...")  # 记录响应前500字符

            # 解析 JSON 响应
            result = self._parse_json_response(response)
            score = result.get('score', 0)
            logger.info(f"教育分析完成，评分: {score}")
            return result

        except Exception as e:
            logger.error(f"教育分析失败: {e}", exc_info=True)
            # 返回默认结构，给出中等评分而不是0分
            return {
                "score": 60,  # 改为60分而不是0分
                "highest_degree": "无法确定",
                "university_tier": "无法评估",
                "major_relevance": "信息不足",
                "gpa": "未提供",
                "honors": [],
                "certifications": [],
                "academic_strengths": ["需要面试进一步评估"],
                "learning_capability": "需要面试进一步评估",
                "recommendations": f"简历中教育信息不足，建议通过面试核实学历背景和专业能力。错误: {str(e)[:100]}"
            }
