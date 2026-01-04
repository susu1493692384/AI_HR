"""
Coordinator Agent
主协调智能体 - 协调7个专家智能体进行简历分析
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import Tool
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from app.application.agents.base import BaseAgent
from app.application.agents.experts import (
    SkillsExpertAgent,
    ExperienceExpertAgent,
    EducationExpertAgent,
    SoftSkillsExpertAgent,
    StabilityExpertAgent,
    WorkAttitudeExpertAgent,
    DevelopmentPotentialExpertAgent
)
from app.application.agents.prompts.coordinator import get_coordinator_prompt
from app.core.analysis_weights import get_weights, AnalysisProfile

logger = logging.getLogger(__name__)


class ResumeAnalysisCoordinator(BaseAgent):
    """简历分析主协调智能体 (7维度版本)

    协调七个专家智能体进行简历分析，使用可配置的权重计算综合评分
    """

    def __init__(self, db, tenant_id: str, analysis_profile: str = "standard"):
        """初始化协调智能体

        Args:
            db: 数据库会话
            tenant_id: 租户ID
            analysis_profile: 分析配置类型 (standard/tech_focused/leadership/junior/senior)
        """
        super().__init__(db, tenant_id, temperature=0.3)

        # 获取权重配置
        try:
            profile = AnalysisProfile(analysis_profile)
            self.weights = get_weights(profile)
        except ValueError:
            logger.warning(f"未知的分析配置: {analysis_profile}, 使用标准配置")
            self.weights = get_weights(AnalysisProfile.STANDARD)

        logger.info(f"初始化协调器，使用权重配置: {analysis_profile}, 权重: {self.weights}")

        # 初始化专家智能体 - 原有4维度
        self.skills_expert = SkillsExpertAgent(db, tenant_id)
        self.experience_expert = ExperienceExpertAgent(db, tenant_id)
        self.education_expert = EducationExpertAgent(db, tenant_id)
        self.soft_skills_expert = SoftSkillsExpertAgent(db, tenant_id)

        # 初始化专家智能体 - 新增3维度
        self.stability_expert = StabilityExpertAgent(db, tenant_id)
        self.work_attitude_expert = WorkAttitudeExpertAgent(db, tenant_id)
        self.development_potential_expert = DevelopmentPotentialExpertAgent(db, tenant_id)

    async def analyze(
        self,
        resume_data: Dict[str, Any],
        job_requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行完整的简历分析 (7维度)

        Args:
            resume_data: 简历数据字典
            job_requirements: 职位要求字典

        Returns:
            完整的分析结果
        """
        logger.info(f"开始简历分析 (7维度)，租户: {self.tenant_id}")

        try:
            # 并行调用七个专家分析
            (
                skills_result,
                experience_result,
                education_result,
                soft_skills_result,
                stability_result,
                work_attitude_result,
                potential_result
            ) = await asyncio.gather(
                self.skills_expert.analyze({"resume_data": resume_data}),
                self.experience_expert.analyze({"resume_data": resume_data}),
                self.education_expert.analyze({"resume_data": resume_data}),
                self.soft_skills_expert.analyze({"resume_data": resume_data}),
                self.stability_expert.analyze({"resume_data": resume_data}),
                self.work_attitude_expert.analyze({"resume_data": resume_data}),
                self.development_potential_expert.analyze({"resume_data": resume_data}),
                return_exceptions=True
            )

            # 处理可能的异常，并确保每个维度包含所有必需字段
            skills_result = self._ensure_dimension_complete(
                skills_result if not isinstance(skills_result, Exception) else {"error": str(skills_result), "credibility_score": 50, "score": 50},
                "技能匹配度"
            )
            experience_result = self._ensure_dimension_complete(
                experience_result if not isinstance(experience_result, Exception) else {"error": str(experience_result), "score": 50},
                "工作经验"
            )
            education_result = self._ensure_dimension_complete(
                education_result if not isinstance(education_result, Exception) else {"error": str(education_result), "score": 60},
                "教育背景"
            )
            soft_skills_result = self._ensure_dimension_complete(
                soft_skills_result if not isinstance(soft_skills_result, Exception) else {"error": str(soft_skills_result), "score": 60},
                "软技能"
            )
            stability_result = self._ensure_dimension_complete(
                stability_result if not isinstance(stability_result, Exception) else {"error": str(stability_result), "score": 50},
                "稳定性/忠诚度"
            )
            work_attitude_result = self._ensure_dimension_complete(
                work_attitude_result if not isinstance(work_attitude_result, Exception) else {"error": str(work_attitude_result), "score": 50},
                "工作态度/抗压"
            )
            potential_result = self._ensure_dimension_complete(
                potential_result if not isinstance(potential_result, Exception) else {"error": str(potential_result), "score": 50},
                "发展潜力"
            )

            # 获取各个评分（兼容批判性思维的credibility_score和传统score）
            skills_score = skills_result.get("credibility_score") or skills_result.get("score", 0)
            experience_score = experience_result.get("score", 0)
            education_score = education_result.get("score", 0)
            soft_skills_score = soft_skills_result.get("score", 0)
            stability_score = stability_result.get("score", 0)
            attitude_score = work_attitude_result.get("score", 0)
            potential_score = potential_result.get("score", 0)

            # 调试日志
            logger.info(f"各维度评分 - 技能: {skills_score}, 经验: {experience_score}, 教育: {education_score}, 软技能: {soft_skills_score}, 稳定: {stability_score}, 态度: {attitude_score}, 潜力: {potential_score}")
            logger.info(f"教育原始结果: {education_result}")
            logger.info(f"软技能原始结果: {soft_skills_result}")

            # 计算综合评分（使用配置的权重）
            overall_score = int(
                skills_score * (self.weights['skills'] / 100) +
                experience_score * (self.weights['experience'] / 100) +
                education_score * (self.weights['education'] / 100) +
                soft_skills_score * (self.weights['soft_skills'] / 100) +
                stability_score * (self.weights['stability'] / 100) +
                attitude_score * (self.weights['attitude'] / 100) +
                potential_score * (self.weights['potential'] / 100)
            )

            # 使用LLM生成综合分析报告
            summary = await self._generate_summary(
                resume_data,
                job_requirements,
                skills_result,
                experience_result,
                education_result,
                soft_skills_result,
                stability_result,
                work_attitude_result,
                potential_result,
                overall_score
            )

            # 生成建议
            recommendations = await self._generate_recommendations(
                skills_result,
                experience_result,
                education_result,
                soft_skills_result,
                stability_result,
                work_attitude_result,
                potential_result,
                overall_score
            )

            logger.info(f"简历分析完成 (7维度)，综合评分: {overall_score}")

            # 构建结果字典
            result = {
                "overall_score": overall_score,
                # 原有4维度
                "skills": skills_result,
                "experience": experience_result,
                "education": education_result,
                "soft_skills": soft_skills_result,
                # 新增3维度
                "stability": stability_result,
                "work_attitude": work_attitude_result,
                "development_potential": potential_result,
                # 综合评估
                "summary": summary,
                "recommendations": recommendations,
                # 元数据
                "analysis_version": "2.0",
                "dimension_count": 7,
                "weights_used": self.weights
            }

            # 提升批判性思维字段到顶层（如果存在）
            credibility_fields = [
                "credibility_score", "risk_level",
                "verified_claims", "questionable_claims",
                "logical_inconsistencies", "exaggeration_indicators",
                "interview_questions", "constructive_feedback"
            ]

            for field in credibility_fields:
                if field in skills_result:
                    result[field] = skills_result[field]

            return result

        except Exception as e:
            logger.error(f"协调分析失败: {e}", exc_info=True)
            return {
                "overall_score": 0,
                "credibility_score": 0,
                "risk_level": "D",
                "error": str(e),
                "skills": {"credibility_score": 0, "score": 0, "error": "分析失败"},
                "experience": {"score": 0, "error": "分析失败"},
                "education": {"score": 0, "error": "分析失败"},
                "soft_skills": {"score": 0, "error": "分析失败"},
                "stability": {"score": 50, "error": "分析失败"},
                "work_attitude": {"score": 50, "error": "分析失败"},
                "development_potential": {"score": 50, "error": "分析失败"},
                "summary": "分析过程出错",
                "recommendations": ["请重试或联系技术支持"],
                "verified_claims": [],
                "questionable_claims": [],
                "logical_inconsistencies": [],
                "exaggeration_indicators": [],
                "interview_questions": [],
                "constructive_feedback": []
            }

    async def _generate_summary(
        self,
        resume_data: Dict[str, Any],
        job_requirements: Dict[str, Any],
        skills_result: Dict[str, Any],
        experience_result: Dict[str, Any],
        education_result: Dict[str, Any],
        soft_skills_result: Dict[str, Any],
        stability_result: Dict[str, Any],
        work_attitude_result: Dict[str, Any],
        potential_result: Dict[str, Any],
        overall_score: int
    ) -> str:
        """使用LLM生成综合分析摘要 (7维度版本)

        Args:
            resume_data: 简历数据
            job_requirements: 职位要求
            skills_result: 技能分析结果
            experience_result: 经验分析结果
            education_result: 教育分析结果
            soft_skills_result: 软技能分析结果
            stability_result: 稳定性分析结果
            work_attitude_result: 工作态度分析结果
            potential_result: 发展潜力分析结果
            overall_score: 综合评分

        Returns:
            综合分析摘要
        """
        resume_text = self._format_resume_data(resume_data)
        job_text = self._format_job_requirements(job_requirements)

        prompt = f"""请基于以下七个专家的分析结果，生成一份3-5句话的综合评估摘要：

## 候选人信息
{resume_text}

## 目标职位要求
{job_text}

## 专家分析结果
### 技能分析（评分：{skills_result.get('score', 0)}）
{json.dumps(skills_result, ensure_ascii=False, indent=2)}

### 经验分析（评分：{experience_result.get('score', 0)}）
{json.dumps(experience_result, ensure_ascii=False, indent=2)}

### 教育分析（评分：{education_result.get('score', 0)}）
{json.dumps(education_result, ensure_ascii=False, indent=2)}

### 软技能分析（评分：{soft_skills_result.get('score', 0)}）
{json.dumps(soft_skills_result, ensure_ascii=False, indent=2)}

### 稳定性分析（评分：{stability_result.get('score', 0)}）
{json.dumps(stability_result, ensure_ascii=False, indent=2)}

### 工作态度分析（评分：{work_attitude_result.get('score', 0)}）
{json.dumps(work_attitude_result, ensure_ascii=False, indent=2)}

### 发展潜力分析（评分：{potential_result.get('score', 0)}）
{json.dumps(potential_result, ensure_ascii=False, indent=2)}

## 综合评分: {overall_score}/100

请生成一份简洁、客观的综合评估摘要（3-5句话），包含：
1. 候选人整体匹配度
2. 主要优势
3. 需要注意的方面

摘要："""

        try:
            return await self._invoke_llm(prompt)
        except Exception as e:
            logger.error(f"生成摘要失败: {e}")
            return f"综合评分为{overall_score}分。技能匹配度{skills_result.get('score', 0)}分，工作经验{experience_result.get('score', 0)}分，教育背景{education_result.get('score', 0)}分，软技能{soft_skills_result.get('score', 0)}分，稳定性{stability_result.get('score', 0)}分，工作态度{work_attitude_result.get('score', 0)}分，发展潜力{potential_result.get('score', 0)}分。"

    async def _generate_recommendations(
        self,
        skills_result: Dict[str, Any],
        experience_result: Dict[str, Any],
        education_result: Dict[str, Any],
        soft_skills_result: Dict[str, Any],
        stability_result: Dict[str, Any],
        work_attitude_result: Dict[str, Any],
        potential_result: Dict[str, Any],
        overall_score: int
    ) -> List[str]:
        """生成面试建议 (7维度版本)

        Args:
            skills_result: 技能分析结果
            experience_result: 经验分析结果
            education_result: 教育分析结果
            soft_skills_result: 软技能分析结果
            stability_result: 稳定性分析结果
            work_attitude_result: 工作态度分析结果
            potential_result: 发展潜力分析结果
            overall_score: 综合评分

        Returns:
            建议列表
        """
        recommendations = []

        # 基于评分给出建议
        if skills_result.get("score", 0) < 60:
            recommendations.append("建议重点考察候选人的技术能力，可通过在线编程测试或技术面试进一步评估")

        if experience_result.get("score", 0) < 60:
            recommendations.append("建议详细了解候选人的项目经历，评估其实际工作能力和项目贡献度")

        if education_result.get("score", 0) < 60:
            recommendations.append("建议核实候选人的学历背景，关注其学习能力和专业发展潜力")

        if soft_skills_result.get("score", 0) < 60:
            recommendations.append("建议通过行为面试问题评估候选人的沟通能力、团队协作和问题解决能力")

        if stability_result.get("score", 0) < 60:
            recommendations.append("建议关注候选人的工作稳定性，了解过往离职原因和职业规划")

        if work_attitude_result.get("score", 0) < 60:
            recommendations.append("建议通过面试评估候选人的工作态度、责任心和抗压能力")

        if potential_result.get("score", 0) < 60:
            recommendations.append("建议评估候选人的学习能力和发展潜力，判断是否符合团队长期发展需求")

        if overall_score >= 80:
            recommendations.append("候选人整体匹配度较高，建议优先安排面试")
        elif overall_score >= 60:
            recommendations.append("候选人基本符合要求，可考虑安排面试进一步了解")
        else:
            recommendations.append("候选人匹配度较低，建议谨慎考虑或重新评估招聘需求")

        # 从专家结果中提取建议
        for result in [skills_result, experience_result, education_result, soft_skills_result,
                       stability_result, work_attitude_result, potential_result]:
            if "recommendations" in result and isinstance(result["recommendations"], str) and result["recommendations"]:
                recommendations.append(result["recommendations"][:100])  # 截取前100字符
            if "suggestions" in result and isinstance(result["suggestions"], list):
                recommendations.extend(result["suggestions"][:1])

        # 去重并限制数量
        seen = set()
        unique_recommendations = []
        for rec in recommendations:
            if rec not in seen:
                seen.add(rec)
                unique_recommendations.append(rec)
                if len(unique_recommendations) >= 7:
                    break

        return unique_recommendations

    def _format_job_requirements(self, job_requirements: Dict[str, Any]) -> str:
        """格式化职位要求

        Args:
            job_requirements: 职位要求字典

        Returns:
            格式化的文本
        """
        if not job_requirements:
            return "未提供具体职位要求"

        lines = []

        if job_requirements.get("position"):
            lines.append(f"职位名称: {job_requirements['position']}")

        if job_requirements.get("description"):
            lines.append(f"\n职位描述:\n{job_requirements['description']}")

        if job_requirements.get("requirements"):
            lines.append(f"\n任职要求:\n{job_requirements['requirements']}")

        if job_requirements.get("skills"):
            lines.append(f"\n技能要求:\n{', '.join(job_requirements['skills'])}")

        return "\n".join(lines)

    def _ensure_dimension_complete(self, result: Dict[str, Any], dimension_name: str) -> Dict[str, Any]:
        """确保维度结果包含所有必需字段

        Args:
            result: 专家返回的原始结果
            dimension_name: 维度名称

        Returns:
            补全字段后的结果
        """
        # 确保 result 是字典
        if not isinstance(result, dict):
            result = {}

        # 必需字段列表
        required_fields = {
            "score": 0,  # 如果没有score，从credibility_score获取或默认为0
            "score_reason": "",  # 评分依据（新增字段）
            "verified_claims": [],
            "questionable_claims": [],
            "logical_inconsistencies": [],
            "interview_questions": [],
            "constructive_feedback": [],
            "recommendations": ""
        }

        # 获取评分（兼容批判性思维格式）
        score = result.get("credibility_score") or result.get("score", 0)
        required_fields["score"] = score

        # 补全缺失的字段
        for field, default_value in required_fields.items():
            if field not in result or result[field] is None:
                # 对于 score_reason，如果缺失则生成
                if field == "score_reason" and score > 0:
                    result[field] = self._generate_score_reason(dimension_name, score, result)
                else:
                    result[field] = default_value

        # 特殊处理：确保credibility_score与score同步（批判性思维格式）
        if "credibility_score" in result and "score" not in result:
            result["score"] = result["credibility_score"]
        elif "score" in result and "credibility_score" not in result:
            result["credibility_score"] = result["score"]

        return result

    def _generate_score_reason(self, dimension_name: str, score: int, result: Dict[str, Any]) -> str:
        """为维度生成评分依据

        Args:
            dimension_name: 维度名称
            score: 评分
            result: 维度分析结果

        Returns:
            评分依据文本
        """
        # 根据分数范围生成基础描述
        if score >= 90:
            level = "优秀"
            reason = f"{dimension_name}表现优秀"
        elif score >= 70:
            level = "良好"
            reason = f"{dimension_name}表现良好"
        elif score >= 50:
            level = "一般"
            reason = f"{dimension_name}表现一般"
        else:
            level = "较差"
            reason = f"{dimension_name}需要提升"

        # 根据不同维度添加具体依据
        dimension_reasons = {
            "技能匹配度": "基于候选人技术栈与职位要求的匹配程度、技术深度和广度综合评估。",
            "工作经验": "基于工作年限、项目经验、职业发展轨迹和成果量化情况综合评估。",
            "教育背景": "基于学历层次、专业匹配度、学校声誉和持续学习能力综合评估。",
            "软技能": "基于沟通能力、团队协作、领导力、问题解决能力等综合素质评估。",
            "稳定性/忠诚度": "基于工作稳定性、跳槽频率、职业发展连贯性综合评估。",
            "工作态度/抗压": "基于责任心、抗压能力、工作投入度和情绪管理能力综合评估。",
            "发展潜力": "基于学习能力、创新能力、成长意愿和适应变化能力综合评估。"
        }

        detail_reason = dimension_reasons.get(dimension_name, "")

        # 结合结果中的具体信息
        if result.get("verified_claims"):
            verified_count = len(result.get("verified_claims", []))
            reason += f"，有{verified_count}项可信技能陈述"

        if result.get("questionable_claims"):
            questionable_count = len(result.get("questionable_claims", []))
            if questionable_count > 0:
                reason += f"，{questionable_count}项需要验证"

        return f"{reason}。{detail_reason}"

    def _format_coordinator_result(self, result: Dict[str, Any]) -> str:
        """格式化协调器结果为markdown报告

        Args:
            result: 协调器分析结果

        Returns:
            格式化的markdown报告
        """
        overall_score = result.get("overall_score", result.get("credibility_score", 0))
        risk_level = result.get("risk_level", "N/A")

        # 确保overall_score是数字类型
        try:
            overall_score = int(overall_score) if not isinstance(overall_score, (int, float)) else overall_score
        except (ValueError, TypeError):
            overall_score = 0

        # 根据评分确定等级
        if overall_score >= 90:
            grade = "A级 - 优秀"
        elif overall_score >= 80:
            grade = "B级 - 良好"
        elif overall_score >= 70:
            grade = "C级 - 中等"
        elif overall_score >= 60:
            grade = "D级 - 合格"
        else:
            grade = "E级 - 需要提升"

        # 维度映射
        dimension_mapping = {
            "skills": ("技能匹配度", "💻"),
            "experience": ("工作经验", "💼"),
            "education": ("教育背景", "🎓"),
            "soft_skills": ("软技能", "🤝"),
            "stability": ("稳定性/忠诚度", "⚖️"),
            "work_attitude": ("工作态度/抗压", "💪"),
            "development_potential": ("发展潜力", "🚀")
        }

        # 构建报告
        report_parts = [
            "# 📊 综合评估报告 (7维度分析)",
            "",
            f"## 综合评分: **{overall_score}/100** ({grade})",
            "",
            "## 🎯 各维度评分",
            ""
        ]

        # 添加各维度详情
        for key, (name, emoji) in dimension_mapping.items():
            dimension_data = result.get(key, {})
            score = dimension_data.get("score", 0)
            score_reason = dimension_data.get("score_reason", dimension_data.get("risk_level", ""))

            # 确保score是数字类型
            try:
                score_num = int(score) if not isinstance(score, (int, float)) else score
            except (ValueError, TypeError):
                score_num = 0

            report_parts.append(f"{emoji} **{name}**: {score_num}/100")
            if score_reason:
                score_reason = str(score_reason) if not isinstance(score_reason, str) else score_reason
                report_parts.append(f"- **评分依据**: {score_reason}")

            # 可信陈述
            verified = dimension_data.get("verified_claims", [])
            if verified:
                report_parts.append("- ✅ **可信陈述**:")
                for claim in verified[:3]:  # 最多显示3个
                    if isinstance(claim, dict):
                        claim_text = claim.get("claim", claim)
                        evidence = claim.get("evidence", "")
                        claim_text = str(claim_text) if not isinstance(claim_text, str) else claim_text
                        evidence = str(evidence) if not isinstance(evidence, str) else evidence
                        if evidence:
                            report_parts.append(f"  - {claim_text} (证据: {evidence})")
                        else:
                            report_parts.append(f"  - {claim_text}")
                    else:
                        claim = str(claim) if not isinstance(claim, str) else claim
                        report_parts.append(f"  - {claim}")

            # 需要验证的陈述
            questionable = dimension_data.get("questionable_claims", [])
            if questionable:
                report_parts.append("- ⚠️ **需要验证**:")
                for claim in questionable[:3]:  # 最多显示3个
                    if isinstance(claim, dict):
                        claim_text = claim.get("claim", claim)
                        concern = claim.get("concern", "")
                        claim_text = str(claim_text) if not isinstance(claim_text, str) else claim_text
                        concern = str(concern) if not isinstance(concern, str) else concern
                        if concern:
                            report_parts.append(f"  - {claim_text} (⚠️ {concern})")
                        else:
                            report_parts.append(f"  - {claim_text}")
                    else:
                        claim = str(claim) if not isinstance(claim, str) else claim
                        report_parts.append(f"  - {claim}")

            # 面试问题
            interview_questions = dimension_data.get("interview_questions", [])
            if interview_questions:
                report_parts.append("- 🔍 **建议面试问题**:")
                for idx, q in enumerate(interview_questions[:3], 1):  # 最多显示3个
                    # 确保q是字符串
                    q_str = str(q) if not isinstance(q, str) else q
                    report_parts.append(f"  {idx}. {q_str}")

            # 改进建议
            feedback = dimension_data.get("constructive_feedback", [])
            if feedback:
                report_parts.append("- 💡 **改进建议**:")
                for item in feedback[:2]:  # 最多显示2个
                    item = str(item) if not isinstance(item, str) else item
                    report_parts.append(f"  - {item}")

            report_parts.append("")

        # 综合建议
        recommendations = result.get("recommendations", [])
        if isinstance(recommendations, list):
            report_parts.extend([
                "## 📝 综合建议",
                ""
            ])
            for rec in recommendations[:5]:  # 最多显示5个
                rec = str(rec) if not isinstance(rec, str) else rec
                report_parts.append(f"- {rec}")
            report_parts.append("")

        # 添加JSON格式的完整数据（供前端解析）
        import json
        report_parts.extend([
            "---",
            "",
            "<!-- 完整数据（JSON格式） -->",
            f"```json",
            json.dumps(result, ensure_ascii=False, indent=2),
            "```"
        ])

        return "\n".join(report_parts)
