"""
Agent Router
智能体路由器 - 动态调用专家智能体到对话中
"""

import logging
import json
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.agents.coordinator import ResumeAnalysisCoordinator
from app.application.agents.experts import (
    SkillsExpertAgent,
    ExperienceExpertAgent,
    EducationExpertAgent,
    SoftSkillsExpertAgent,
    StabilityExpertAgent,
    WorkAttitudeExpertAgent,
    DevelopmentPotentialExpertAgent
)

logger = logging.getLogger(__name__)


class AgentRouter:
    """智能体路由器

    负责识别用户意图并动态调用相应的专家智能体
    """

    # 意图关键词映射
    INTENT_KEYWORDS = {
        "skills": [
            "技能", "技术栈", "编程", "语言", "框架", "工具", "技术能力",
            "programming", "skill", "tech stack", "framework", "技术"
        ],
        "experience": [
            "经验", "工作", "项目", "履历", "职业", "公司", "年限", "晋升",
            "work experience", "project", "job", "career", "公司"
        ],
        "education": [
            "学历", "学位", "学校", "专业", "毕业", "教育背景", "证书", "认证",
            "education", "degree", "university", "major", "证书"
        ],
        "soft_skills": [
            "沟通", "团队", "领导", "协作", "能力", "素质", "软技能", "性格",
            "communication", "teamwork", "leadership", "软技能"
        ],
        "stability": [
            "稳定", "忠诚", "跳槽", "离职", " tenure", "稳定性",
            "stability", "loyal", "job hopping", "工作稳定"
        ],
        "attitude": [
            "态度", "抗压", "责任心", "敬业", "情绪", "压力",
            "attitude", "stress", "responsibility", "dedication", "抗压"
        ],
        "potential": [
            "潜力", "学习", "创新", "成长", "发展", "适应",
            "potential", "learning", "innovation", "growth", "发展潜力"
        ],
        "full_analysis": [
            "分析", "评估", "匹配", "推荐", "面试", "候选人", "简历",
            "综合", "评分", "建议", "总", "全面", "评价", "总结", "报告",
            "analyze", "evaluation", "match", "recommend", "分析", "score", "suggestion", "report"
        ]
    }

    def __init__(self, db: AsyncSession, tenant_id: str):
        """初始化路由器

        Args:
            db: 数据库会话
            tenant_id: 租户ID
        """
        self.db = db
        self.tenant_id = tenant_id

        # 初始化专家智能体
        self.coordinator = ResumeAnalysisCoordinator(db, tenant_id)

    async def identify_intent(self, user_message: str, conversation_history: List[Dict]) -> Tuple[str, float]:
        """识别用户意图

        Args:
            user_message: 用户消息
            conversation_history: 对话历史

        Returns:
            (意图类型, 置信度)
            意图类型: skills, experience, education, soft_skills, full_analysis, general
        """
        message_lower = user_message.lower()

        # 计算每个意图的匹配分数
        intent_scores = {}

        for intent, keywords in self.INTENT_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in message_lower)
            if score > 0:
                intent_scores[intent] = score

        logger.info(f"[意图识别] 用户消息: {user_message[:50]}...")
        logger.info(f"[意图识别] 意图分数: {intent_scores}")

        if not intent_scores:
            return "general", 0.0

        # 获取最高分的意图
        top_intent = max(intent_scores, key=intent_scores.get)
        confidence = intent_scores[top_intent] / len(user_message.split())

        # 如果分数太低，认为是通用对话
        if confidence < 0.1:
            return "general", confidence

        # 🔥 关键修复：如果同时匹配到具体意图和full_analysis，优先使用具体意图
        # 因为"分析"这个词很通用，容易误触发full_analysis
        specific_intents = ["skills", "experience", "education", "soft_skills", "stability", "attitude", "potential"]
        if top_intent == "full_analysis":
            # 检查是否有其他具体意图也匹配了
            for specific_intent in specific_intents:
                if specific_intent in intent_scores:
                    # 如果具体意图的分数不低于full_analysis太多（允许20%的差异），使用具体意图
                    if intent_scores[specific_intent] >= intent_scores["full_analysis"] * 0.8:
                        logger.info(f"[意图识别] 从full_analysis切换到{specific_intent}（更具体）")
                        top_intent = specific_intent
                        confidence = intent_scores[specific_intent] / len(user_message.split())
                        break

        return top_intent, confidence

    async def should_call_agents(self, user_message: str, conversation_history: List[Dict]) -> bool:
        """判断是否需要调用智能体

        Args:
            user_message: 用户消息
            conversation_history: 对话历史

        Returns:
            是否需要调用智能体
        """
        intent, confidence = await self.identify_intent(user_message, conversation_history)

        # 如果是明确的分析意图，调用智能体
        if intent in ["full_analysis"]:
            return True

        # 如果有较高置信度的特定意图，调用智能体
        if intent != "general" and confidence > 0.15:
            return True

        return False

    async def route_to_expert(
        self,
        user_message: str,
        conversation_history: List[Dict],
        resume_data: Optional[Dict] = None
    ) -> Optional[Dict[str, Any]]:
        """路由到相应的专家智能体

        Args:
            user_message: 用户消息
            conversation_history: 对话历史
            resume_data: 简历数据（如果有的话）

        Returns:
            专家分析结果，如果不需要调用专家则返回 None
        """
        intent, confidence = await self.identify_intent(user_message, conversation_history)

        logger.info(f"[路由] 意图={intent}, 置信度={confidence:.2f}")

        # 如果没有简历数据，无法调用专家
        if not resume_data:
            logger.info("[路由] 没有简历数据，跳过专家调用")
            return None

        # 根据意图调用专家
        if intent == "skills":
            return await self._call_skills_expert(resume_data)
        elif intent == "experience":
            return await self._call_experience_expert(resume_data)
        elif intent == "education":
            return await self._call_education_expert(resume_data)
        elif intent == "soft_skills":
            return await self._call_soft_skills_expert(resume_data)
        elif intent == "stability":
            return await self._call_stability_expert(resume_data)
        elif intent == "attitude":
            return await self._call_attitude_expert(resume_data)
        elif intent == "potential":
            return await self._call_potential_expert(resume_data)
        elif intent == "full_analysis":
            return await self._call_coordinator(resume_data)

        return None

    def _prepare_resume_context(self, resume_data: Dict) -> Dict[str, Any]:
        """准备简历上下文数据

        将原始简历数据转换为专家智能体期望的格式

        Args:
            resume_data: 原始简历数据

        Returns:
            转换后的上下文数据
        """
        logger.info(f"[AgentRouter] 准备简历上下文, keys={list(resume_data.keys()) if isinstance(resume_data, dict) else type(resume_data)}")

        # 获取简历文本
        resume_text = ""
        if "extracted_text" in resume_data:
            resume_text = resume_data["extracted_text"]
            logger.info(f"[AgentRouter] 使用 extracted_text, 长度={len(resume_text)}")
        elif isinstance(resume_data, str):
            resume_text = resume_data
            logger.info(f"[AgentRouter] resume_data 是字符串, 长度={len(resume_text)}")
        else:
            # 尝试从其他字段构建文本
            parts = []
            if resume_data.get("candidate_name"):
                parts.append(f"姓名: {resume_data['candidate_name']}")
            if resume_data.get("candidate_email"):
                parts.append(f"邮箱: {resume_data['candidate_email']}")
            if resume_data.get("candidate_phone"):
                parts.append(f"电话: {resume_data['candidate_phone']}")
            resume_text = "\n".join(parts)
            logger.info(f"[AgentRouter] 从基本信息构建文本, 长度={len(resume_text)}")

        logger.info(f"[AgentRouter] 最终 resume_text 长度={len(resume_text)}")

        return {
            "resume_text": resume_text,  # 通用简历文本
            "resume_skills": resume_text,  # 技能专家使用完整文本
            "work_experience": resume_text,  # 经验专家使用完整文本
            "project_experience": "",  # 项目经验（从完整文本中提取）
            "education": resume_text,  # 教育背景
            "education_background": resume_text,  # 教育专家
            "resume_summary": resume_text,  # 软技能专家
            "resume_data": resume_data  # 原始数据
        }

    async def _call_skills_expert(self, resume_data: Dict) -> Dict[str, Any]:
        """调用技能专家"""
        logger.info("[专家] 调用技能匹配度专家")
        context = self._prepare_resume_context(resume_data)
        result = await self.coordinator.skills_expert.analyze(context)
        return {"expert": "技能匹配度专家", "result": result}

    async def _call_experience_expert(self, resume_data: Dict) -> Dict[str, Any]:
        """调用经验专家"""
        logger.info("[专家] 调用工作经验评估专家")
        context = self._prepare_resume_context(resume_data)
        result = await self.coordinator.experience_expert.analyze(context)
        return {"expert": "工作经验评估专家", "result": result}

    async def _call_education_expert(self, resume_data: Dict) -> Dict[str, Any]:
        """调用教育专家"""
        logger.info("[专家] 调用教育背景分析专家")
        context = self._prepare_resume_context(resume_data)
        result = await self.coordinator.education_expert.analyze(context)
        return {"expert": "教育背景分析专家", "result": result}

    async def _call_soft_skills_expert(self, resume_data: Dict) -> Dict[str, Any]:
        """调用软技能专家"""
        logger.info("[专家] 调用软技能评估专家")
        context = self._prepare_resume_context(resume_data)
        result = await self.coordinator.soft_skills_expert.analyze(context)
        return {"expert": "软技能评估专家", "result": result}

    async def _call_stability_expert(self, resume_data: Dict) -> Dict[str, Any]:
        """调用稳定性/忠诚度专家"""
        logger.info("[专家] 调用稳定性/忠诚度专家")
        context = self._prepare_resume_context(resume_data)
        result = await self.coordinator.stability_expert.analyze(context)
        return {"expert": "稳定性/忠诚度专家", "result": result}

    async def _call_attitude_expert(self, resume_data: Dict) -> Dict[str, Any]:
        """调用工作态度/抗压专家"""
        logger.info("[专家] 调用工作态度/抗压专家")
        context = self._prepare_resume_context(resume_data)
        result = await self.coordinator.work_attitude_expert.analyze(context)
        return {"expert": "工作态度/抗压专家", "result": result}

    async def _call_potential_expert(self, resume_data: Dict) -> Dict[str, Any]:
        """调用发展潜力专家"""
        logger.info("[专家] 调用发展潜力专家")
        context = self._prepare_resume_context(resume_data)
        result = await self.coordinator.development_potential_expert.analyze(context)
        return {"expert": "发展潜力专家", "result": result}

    async def _call_coordinator(self, resume_data: Dict) -> Dict[str, Any]:
        """调用协调器（完整分析）"""
        logger.info("[专家] 调用完整多智能体分析系统")
        context = self._prepare_resume_context(resume_data)
        result = await self.coordinator.analyze(
            resume_data=context,
            job_requirements={}  # 可以从上下文中获取职位要求
        )
        return {"expert": "多智能体协调系统", "result": result}

    def format_expert_result(self, expert_result: Dict[str, Any]) -> str:
        """将专家结果格式化为对话文本

        Args:
            expert_result: 专家分析结果

        Returns:
            格式化的文本（包含原始JSON）
        """
        expert_name = expert_result["expert"]
        result = expert_result["result"]

        if "error" in result:
            return f"⚠️ {expert_name}分析时遇到问题: {result['error']}"

        # 🔥 关键修改：保留原始JSON数据，让前端可以解析
        # 先将原始JSON转换为字符串
        original_json = json.dumps(result, ensure_ascii=False, indent=2)

        # 根据不同专家类型生成格式化文本 + JSON
        formatted_text = ""
        if "技能" in expert_name:
            formatted_text = self._format_skills_result(result)
        elif "经验" in expert_name:
            formatted_text = self._format_experience_result(result)
        elif "教育" in expert_name:
            formatted_text = self._format_education_result(result)
        elif "软技能" in expert_name:
            formatted_text = self._format_soft_skills_result(result)
        elif "稳定性" in expert_name:
            formatted_text = self._format_stability_result(result)
        elif "态度" in expert_name or "抗压" in expert_name:
            formatted_text = self._format_attitude_result(result)
        elif "潜力" in expert_name:
            formatted_text = self._format_potential_result(result)
        elif "协调" in expert_name:
            formatted_text = self._format_coordinator_result(result)
        else:
            formatted_text = f"✨ {expert_name}完成分析"

        # 返回格式化文本 + 原始JSON代码块
        return f"{formatted_text}\n\n```json\n{original_json}\n```"

    def _format_skills_result(self, result: Dict) -> str:
        """格式化技能分析结果 - 批判性思维版本"""
        score = result.get("score", 0)
        credibility_score = result.get("credibility_score", score)
        risk_level = result.get("risk_level", "")
        verified = result.get("verified_claims", [])
        questionable = result.get("questionable_claims", [])
        interview_questions = result.get("interview_questions", [])
        feedback = result.get("constructive_feedback", [])
        recommendations = result.get("recommendations", "")

        # 兼容旧格式的字段
        matched = result.get("matched_skills", [])
        missing = result.get("missing_skills", [])
        strengths = result.get("strengths", [])
        gaps = result.get("gaps", [])

        # 等级评定
        if score >= 90:
            grade = "A"
            grade_desc = "优秀"
        elif score >= 70:
            grade = "B"
            grade_desc = "良好"
        elif score >= 50:
            grade = "C"
            grade_desc = "一般"
        else:
            grade = "D"
            grade_desc = "较差"

        output = f"## 🎯 技能分析 (评分: {score}/100 | {grade}级 - {grade_desc})\n\n"

        # 风险等级
        if risk_level:
            output += f"**风险等级**: {risk_level}级\n\n"

        # 优先使用批判性思维数据
        if verified:
            output += "### ✅ 可信的技能陈述\n"
            for item in verified[:5]:
                claim = item.get("claim", "")[:80]
                evidence = item.get("evidence", "")[:50]
                output += f"- **{claim}** ({evidence})\n"
            output += "\n"

        if questionable:
            output += "### ⚠️ 需要验证的技能陈述\n"
            for item in questionable[:3]:
                claim = item.get("claim", "")[:80]
                concern = item.get("concern", "")[:60]
                output += f"- **{claim}** - {concern}\n"
            output += "\n"

        if interview_questions:
            output += "### 🔍 建议面试问题\n"
            for q in interview_questions[:3]:
                output += f"- {q}\n"
            output += "\n"

        if feedback:
            output += "### 💡 改进建议\n"
            for f in feedback[:2]:
                output += f"- {f}\n"
            output += "\n"

        # 如果有推荐建议，添加到最后
        if recommendations:
            output += f"### 📋 综合建议\n{recommendations}\n"

        return output

    def _format_experience_result(self, result: Dict) -> str:
        """格式化经验分析结果"""
        score = result.get("score", 0)
        total_years = result.get("total_years", 0)
        relevant_years = result.get("relevant_years", 0)
        highlights = result.get("project_highlights", [])
        strengths = result.get("strengths", [])
        concerns = result.get("concerns", [])

        # 等级评定
        if score >= 90:
            grade = "A"
        elif score >= 70:
            grade = "B"
        elif score >= 50:
            grade = "C"
        else:
            grade = "D"

        output = f"## 💼 工作经验分析 (评分: {score}/100 | 等级: {grade}级)\n\n"

        # 评分依据
        output += f"**评分依据**: 工作年限、相关经验深度、项目复杂度、行业匹配度等维度综合评估\n\n"
        output += f"- **总工作年限**: {total_years} 年\n"
        output += f"- **相关工作经验**: {relevant_years} 年\n\n"

        if highlights:
            output += "### 🌟 项目亮点\n"
            for highlight in highlights[:3]:
                output += f"- {highlight}\n"
            output += "\n"

        if strengths:
            output += "### 💪 优势\n"
            for strength in strengths[:3]:
                output += f"- {strength}\n"
            output += "\n"

        if concerns:
            output += "### ⚠️ 关注点\n"
            for concern in concerns[:3]:
                output += f"- {concern}\n"

        return output

    def _format_education_result(self, result: Dict) -> str:
        """格式化教育分析结果"""
        score = result.get("score", 0)
        degree = result.get("highest_degree", "N/A")
        relevance = result.get("major_relevance", "N/A")
        honors = result.get("honors", [])
        certifications = result.get("certifications", [])

        # 等级评定
        if score >= 90:
            grade = "A"
        elif score >= 70:
            grade = "B"
        elif score >= 50:
            grade = "C"
        else:
            grade = "D"

        output = f"## 🎓 教育背景分析 (评分: {score}/100 | 等级: {grade}级)\n\n"

        # 评分依据
        output += f"**评分依据**: 学历层次、学校声誉、专业相关性、学术表现、持续学习能力等维度综合评估\n\n"
        output += f"- **最高学位**: {degree}\n"
        output += f"- **专业相关性**: {relevance}\n\n"

        if honors:
            output += "### 🏆 荣誉奖项\n"
            for honor in honors[:3]:
                output += f"- {honor}\n"
            output += "\n"

        if certifications:
            output += "### 📜 证书认证\n"
            for cert in certifications[:3]:
                output += f"- {cert}\n"

        return output

    def _format_soft_skills_result(self, result: Dict) -> str:
        """格式化软技能分析结果"""
        score = result.get("score", 0)
        communication = result.get("communication", "N/A")
        teamwork = result.get("teamwork", "N/A")
        leadership = result.get("leadership", "N/A")
        strengths = result.get("strengths", [])
        areas_for_improvement = result.get("areas_for_improvement", [])

        # 等级评定
        if score >= 90:
            grade = "A"
        elif score >= 70:
            grade = "B"
        elif score >= 50:
            grade = "C"
        else:
            grade = "D"

        output = f"## 👥 软技能评估 (评分: {score}/100 | 等级: {grade}级)\n\n"

        # 评分依据
        output += f"**评分依据**: 沟通能力、团队协作、领导力、问题解决能力、创新能力等维度综合评估\n\n"
        output += f"- **沟通能力**: {communication}\n"
        output += f"- **团队协作**: {teamwork}\n"
        output += f"- **领导力**: {leadership}\n\n"

        if strengths:
            output += "### 💪 优势\n"
            for strength in strengths[:3]:
                output += f"- {strength}\n"
            output += "\n"

        if areas_for_improvement:
            output += "### 📈 提升空间\n"
            for area in areas_for_improvement[:3]:
                output += f"- {area}\n"

        return output

    def _format_stability_result(self, result: Dict) -> str:
        """格式化稳定性分析结果"""
        score = result.get("score", 0)
        tenure_avg = result.get("job_tenure_avg", 0)
        job_changes = result.get("job_changes_count", 0)
        frequent_hopper = result.get("frequent_hopper_flag", False)
        progression_score = result.get("career_progression_score", 0)
        positive_indicators = result.get("positive_indicators", [])
        risk_factors = result.get("risk_factors", [])

        # 等级评定
        if score >= 90:
            grade = "A"
        elif score >= 70:
            grade = "B"
        elif score >= 50:
            grade = "C"
        else:
            grade = "D"

        output = f"## 🔒 稳定性/忠诚度分析 (评分: {score}/100 | 等级: {grade}级)\n\n"

        # 评分依据
        output += f"**评分依据**: 工作稳定性(平均工作时长、跳槽频率)、职业发展轨迹(晋升合理性)、离职原因合理性等维度综合评估\n\n"
        output += f"- **平均工作时长**: {tenure_avg} 年\n"
        output += f"- **跳槽次数**: {job_changes} 次\n"
        output += f"- **职业发展评分**: {progression_score}/100\n"
        output += f"- **频繁跳槽标记**: {'是 ⚠️' if frequent_hopper else '否 ✅'}\n\n"

        if positive_indicators:
            output += "### ✅ 积极指标\n"
            for indicator in positive_indicators[:3]:
                output += f"- {indicator}\n"
            output += "\n"

        if risk_factors:
            output += "### ⚠️ 风险因素\n"
            for factor in risk_factors[:3]:
                output += f"- {factor}\n"

        return output

    def _format_attitude_result(self, result: Dict) -> str:
        """格式化工作态度分析结果"""
        score = result.get("score", 0)
        stress_resistance = result.get("stress_resistance", "")
        responsibility = result.get("responsibility_level", "")
        dedication_indicators = result.get("dedication_indicators", [])
        strengths = result.get("strengths", [])
        concerns = result.get("concerns", [])

        # 等级评定
        if score >= 90:
            grade = "A"
        elif score >= 70:
            grade = "B"
        elif score >= 50:
            grade = "C"
        else:
            grade = "D"

        output = f"## 💪 工作态度/抗压分析 (评分: {score}/100 | 等级: {grade}级)\n\n"

        # 评分依据
        output += f"**评分依据**: 抗压能力、责任心、工作敬业度、情绪管理等维度综合评估\n\n"
        output += f"- **抗压能力**: {stress_resistance}\n"
        output += f"- **责任心水平**: {responsibility}\n\n"

        if dedication_indicators:
            output += "### 💼 敬业度指标\n"
            for indicator in dedication_indicators[:3]:
                output += f"- {indicator}\n"
            output += "\n"

        if strengths:
            output += "### 💪 优势\n"
            for strength in strengths[:3]:
                output += f"- {strength}\n"
            output += "\n"

        if concerns:
            output += "### ⚠️ 关注点\n"
            for concern in concerns[:3]:
                output += f"- {concern}\n"

        return output

    def _format_potential_result(self, result: Dict) -> str:
        """格式化发展潜力分析结果"""
        score = result.get("score", 0)
        learning_ability = result.get("learning_ability", "")
        innovation_capability = result.get("innovation_capability", "")
        adaptability_score = result.get("adaptability_score", 0)
        high_potential_flags = result.get("high_potential_flags", [])
        growth_trajectory = result.get("growth_trajectory", "")

        # 等级评定
        if score >= 90:
            grade = "A"
        elif score >= 70:
            grade = "B"
        elif score >= 50:
            grade = "C"
        else:
            grade = "D"

        output = f"## 🚀 发展潜力分析 (评分: {score}/100 | 等级: {grade}级)\n\n"

        # 评分依据
        output += f"**评分依据**: 学习能力、创新能力、成长意愿、适应变化能力等维度综合评估\n\n"
        output += f"- **学习能力**: {learning_ability}\n"
        output += f"- **创新能力**: {innovation_capability}\n"
        output += f"- **适应能力评分**: {adaptability_score}/100\n\n"

        if high_potential_flags:
            output += "### ⭐ 高潜力标记\n"
            for flag in high_potential_flags[:3]:
                output += f"- {flag}\n"
            output += "\n"

        if growth_trajectory:
            output += f"### 📈 成长轨迹\n{growth_trajectory}\n"

        return output

    def _format_coordinator_result(self, result: Dict) -> str:
        """格式化协调器结果 - 7维度完整报告

        直接使用 coordinator 的格式化方法，确保显示所有详细信息
        """
        # 直接使用 coordinator 已经完善的格式化方法
        return self.coordinator._format_coordinator_result(result)
