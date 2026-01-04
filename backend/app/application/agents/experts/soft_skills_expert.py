"""
Soft Skills Expert Agent
软技能评估专家智能体
"""

import logging
from typing import Dict, Any

from app.application.agents.base import BaseAgent
from app.application.agents.prompts.soft_skills import get_soft_skills_prompt

logger = logging.getLogger(__name__)


class SoftSkillsExpertAgent(BaseAgent):
    """软技能评估专家智能体

    分析候选人的综合素质和软技能
    """

    def __init__(self, db, tenant_id: str):
        """初始化软技能专家

        Args:
            db: 数据库会话
            tenant_id: 租户ID
        """
        super().__init__(db, tenant_id, temperature=0.5)

    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """分析软技能

        Args:
            context: 包含 resume_summary, resume_text, resume_data 等的上下文

        Returns:
            软技能分析结果
        """
        # 支持 resume_data 格式
        resume_data = context.get("resume_data", {})

        # 获取简历摘要
        if isinstance(resume_data, dict):
            resume_summary = (
                resume_data.get("extracted_text") or
                resume_data.get("resume_text") or
                context.get("resume_summary") or
                context.get("resume_text", "")
            )
        else:
            resume_summary = context.get("resume_summary") or context.get("resume_text", "")

        # 构建提示词
        prompt = get_soft_skills_prompt(resume_summary)

        try:
            # 调用 LLM
            response = await self._invoke_llm(prompt)
            logger.info(f"软技能分析LLM响应: {response[:500]}...")  # 记录响应前500字符

            # 解析 JSON 响应
            result = self._parse_json_response(response)
            score = result.get('score', 0)
            logger.info(f"软技能分析完成，评分: {score}")
            return result

        except Exception as e:
            logger.error(f"软技能分析失败: {e}", exc_info=True)
            # 返回默认结构，给出中等评分而不是0分
            return {
                "score": 60,  # 改为60分而不是0分
                "communication": "需面试评估",
                "teamwork": "需面试评估",
                "leadership": "需面试评估",
                "problem_solving": "需面试评估",
                "innovation": "需面试评估",
                "adaptability": "需面试评估",
                "responsibility": "需面试评估",
                "strengths": ["需要通过面试进一步评估"],
                "areas_for_improvement": ["简历信息不足，无法判断"],
                "recommendations": f"简历中软技能信息不足，建议通过行为面试问题评估沟通能力、团队协作和问题解决能力。错误: {str(e)[:100]}"
            }
