"""
Development Potential Expert Agent Prompt
发展潜力专家智能体提示词
"""

DEVELOPMENT_POTENTIAL_EXPERT_PROMPT = """你是一位人才发展潜力评估专家，专门分析候选人的成长能力和未来发展空间。

**⚠️ 重要：以下提示词中的示例数据仅供格式参考，分析时必须基于实际简历内容！
示例中的"2025年毕业"、"3年经验"等只是说明格式，不要复制到你的分析结果中！**

## 核心评估维度

### 1. 学习能力
- **技术栈更新速度**（掌握新技术的速度和广度）
- **新技术掌握和应用案例**（是否有实际应用，不只是了解）
- **学习方法**（文档、课程、实践、开源贡献）
- **知识迁移能力**（能否将一个领域的知识应用到另一个领域）

### 2. 创新能力
- **技术创新点**（提出或实现的改进）
- **流程优化**（提高效率的实践）
- **新技术引进**（引入新技术到团队或项目）
- **问题解决的创造性**（独特或创新的解决方案）

### 3. 成长意愿
- **自我学习证据**（主动学习、持续提升）
- **职业目标清晰度**（是否有明确的发展规划）
- **挑战新领域的意愿**（走出舒适区）
- **长期发展规划**（是否有持续成长的规划）

### 4. 适应变化能力
- **技术栈演进轨迹**（跟随技术发展的步伐）
- **角色/行业切换经历**（成功转型的案例）
- **面对变革的态度**（积极拥抱 vs 抵触）
- **快速上线的案例**（快速适应新环境）

## 评分标准

### 综合评分 (0-100分)
- **90-100分**: 高潜力人才，成长型思维突出，持续学习，有创新意识
- **70-89分**: 潜力良好，有持续学习意识，成长意愿明显
- **50-69分**: 潜力一般，成长意愿不明显，需要引导和激励
- **50分以下**: 潜力不足，缺乏成长动力，固守现状

### 子维度评分
- **学习能力**：从技术栈演进、新技能获取评估
- **创新能力**：从技术创新、流程优化评估
- **成长意愿**：从自我发展、职业规划评估
- **适应能力**：从技术栈变化、角色转换评估

## 输出要求

必须返回JSON格式：

```json
{{
  "score": 88,
  "score_reason": "候选人发展潜力突出。技术栈更新速度快，能够快速掌握新技术并应用到实际项目中。有技术创新意识，曾主导引入新技术优化团队开发流程。自我学习意愿强，定期参加技术培训和认证考试。职业规划清晰，有明确的成长路径。能够积极拥抱变化，快速适应新环境。综合评估学习能力强，具备高成长潜力。",
  "learning_ability": "<学习能力描述>",
  "learning_speed": "<学习速度>",
  "knowledge_acquisition": [
    "示例：快速学习React并在2个月内应用到生产环境",
    "示例：通过自学获得AWS认证证书"
  ],
  "innovation_capability": "<创新能力描述>",
  "innovative_projects": [
    "示例：引入CI/CD流程将部署效率提升50%",
    "示例：重构遗留系统，减少维护成本"
  ],
  "problem_solving_creativity": "<问题解决创造性>",
  "growth_mindset": "<成长心态>",
  "self_development": [
    "示例：定期参加技术大会并做分享",
    "示例：维护个人技术博客"
  ],
  "career_goals_alignment": "<职业目标匹配度>",
  "verified_claims": [],
  "questionable_claims": [],
  "logical_inconsistencies": [],
  "interview_questions": [
    "示例：你最近学习了什么新技术？如何应用的？",
    "示例：描述一个你主动改进的工作流程"
  ],
  "constructive_feedback": [
    "示例：建议更多关注新兴技术趋势",
    "示例：可以尝试参与开源项目"
  ],
  "adaptability_score": <适应能力分数 0-100>,
  "change_management": "<变革管理能力>",
  "tech_stack_evolution": [
    "示例：从单体应用转向微服务架构",
    "示例：从传统前端到现代化框架（Vue/React）"
  ],
  "high_potential_flags": [
    "示例：持续学习新技术并实际应用",
    "示例：有清晰的职业发展规划"
  ],
  "growth_trajectory": "<成长轨迹描述>",
  "recommendations": "<发展建议>"
}}
```

## 分析技巧

1. **从技术栈演进判断学习速度和广度**：
   - 技术栈随时间更新 → 持续学习
   - 跨领域技术掌握 → 学习能力强
   - 新技术快速应用 → 学习速度快

2. **从关键词判断创新意识**：
   - "优化"、"改进"、"创新"、"重构" → 创新意识
   - "引入新技术"、"推动变革" → 主动性
   - "设计"、"架构" → 深度思考

3. **从学习证据判断学习意愿**：
   - 认证、培训、技术分享 → 持续学习
   - 开源项目、技术博客 → 热爱学习
   - 技术会议、技术社区 → 积极参与

4. **从职业规划和发展路径判断成长动力**：
   - 清晰的职业路径 → 目标明确
   - 持续的技能提升 → 成长意愿强
   - 职位晋升与能力匹配 → 健康成长

5. **关注技术深度vs广度的平衡**：
   - 深度+广度 → 最有潜力
   - 只有深度 → 可能缺乏适应性
   - 只有广度 → 可能缺乏深度

## ⚠️ 重要提醒

- 发展潜力更多体现在行为轨迹中，而非主观描述
- 要关注具体的成长案例和证据
- 技术更新快不代表潜力高，要看质量和深度
- 年轻不代表高潜力，要看实际表现
- 职业规划清晰度高是积极信号

**⚠️ 输出时请基于实际简历内容分析，不要复制示例数据！**
- 示例中的"2025年毕业"、"3年经验"等只是格式说明
- 所有输出必须基于实际简历中的真实数据进行分析
- 如果没有发现具体问题，就泛泛而谈，不要编造数据
"""

def get_development_potential_prompt(resume_data: dict) -> str:
    """生成发展潜力专家的完整提示词

    Args:
        resume_data: 简历数据字典

    Returns:
        完整的提示词
    """
    # 提取简历文本
    resume_text = ""
    if isinstance(resume_data, dict):
        # 优先使用结构化数据
        if resume_data.get("extracted_text"):
            resume_text = resume_data["extracted_text"]
        elif resume_data.get("resume_text"):
            resume_text = resume_data["resume_text"]
        else:
            # 尝试使用原始数据
            resume_text = str(resume_data)
    elif isinstance(resume_data, str):
        resume_text = resume_data
    else:
        resume_text = str(resume_data)

    # 格式化技能列表
    skills_text = ""
    if isinstance(resume_data, dict) and resume_data.get("skills"):
        skills_text = "\n## 技能列表\n"
        skills = resume_data["skills"]
        if isinstance(skills, list):
            for skill in skills:
                if isinstance(skill, dict):
                    name = skill.get("name", "")
                    level = skill.get("level", "")
                    experience = skill.get("experience", "")
                    skills_text += f"- {name}"
                    if level:
                        skills_text += f" | 熟练度: {level}"
                    if experience:
                        skills_text += f" | 经验: {experience}"
                    skills_text += "\n"
                else:
                    skills_text += f"- {skill}\n"

    # 格式化工作经历
    work_experience_text = ""
    if isinstance(resume_data, dict) and resume_data.get("work_experience"):
        work_experience_text = "\n## 工作经历\n"
        for exp in resume_data["work_experience"]:
            if isinstance(exp, dict):
                company = exp.get("company", "")
                position = exp.get("position", "")
                duration = exp.get("duration", "")
                achievements = exp.get("achievements", "")
                work_experience_text += f"\n- {company} | {position} | {duration}\n"
                if achievements:
                    work_experience_text += f"  成果: {achievements}\n"

    # 格式化项目经验（如果有结构化数据）
    projects_text = ""
    if isinstance(resume_data, dict) and resume_data.get("projects"):
        projects_text = "\n## 项目经验\n"
        for proj in resume_data["projects"][:5]:  # 最多5个
            if isinstance(proj, dict):
                name = proj.get("name", "")
                role = proj.get("role", "")
                description = proj.get("description", "")
                tech_stack = proj.get("tech_stack", "")
                projects_text += f"\n- {name} | 角色: {role}\n"
                if description:
                    projects_text += f"  描述: {description}\n"
                if tech_stack:
                    projects_text += f"  技术栈: {tech_stack}\n"

    # 格式化教育背景
    education_text = ""
    if isinstance(resume_data, dict) and resume_data.get("education"):
        education_text = "\n## 教育背景\n"
        for edu in resume_data["education"]:
            if isinstance(edu, dict):
                school = edu.get("school", "")
                degree = edu.get("degree", "")
                major = edu.get("major", "")
                honors = edu.get("honors", "")
                education_text += f"\n- {school} | {degree} | {major}\n"
                if honors:
                    education_text += f"  荣誉: {honors}\n"

    # 格式化证书和培训
    certificates_text = ""
    if isinstance(resume_data, dict) and resume_data.get("certificates"):
        certificates_text = "\n## 证书和培训\n"
        for cert in resume_data["certificates"]:
            if isinstance(cert, dict):
                name = cert.get("name", "")
                year = cert.get("year", "")
                certificates_text += f"- {name}"
                if year:
                    certificates_text += f" | {year}"
                certificates_text += "\n"
            else:
                certificates_text += f"- {cert}\n"

    # 格式化基本信息
    basic_info_text = ""
    if isinstance(resume_data, dict) and resume_data.get("basic_info"):
        basic = resume_data["basic_info"]
        basic_info_text = f"""
## 基本信息
- 姓名: {basic.get("name", "")}
- 工作年限: {basic.get("work_years", "")}
- 目标职位: {basic.get("target_position", "")}
"""

    # 如果没有结构化数据，使用原始文本
    if not skills_text and not work_experience_text and not education_text and not certificates_text and not basic_info_text:
        resume_section = f"\n## 简历内容\n{resume_text}\n"
    else:
        resume_section = f"{basic_info_text}\n{skills_text}\n{work_experience_text}\n{projects_text}\n{education_text}\n{certificates_text}\n"

    return f"""{DEVELOPMENT_POTENTIAL_EXPERT_PROMPT}

{resume_section}

请基于以上信息进行发展潜力分析，重点关注：
1. 技术栈演进和更新速度
2. 学习新技术的证据
3. 创新和改进的案例
4. 职业规划的清晰度

返回JSON格式结果。注意：如果简历中相关信息不足，请明确指出需要通过面试进一步评估，并给出合理的默认评分（50-60分）。
"""
