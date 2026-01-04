# 多智能体系统架构说明文档

## 目录

- [系统概述](#系统概述)
- [架构设计](#架构设计)
- [核心组件](#核心组件)
- [智能体详情](#智能体详情)
- [工作流程](#工作流程)
- [路由与意图识别](#路由与意图识别)
- [权重配置](#权重配置)
- [Prompt工程](#prompt工程)
- [数据流图](#数据流图)
- [扩展指南](#扩展指南)

---

## 系统概述

AI 招聘系统采用基于 **LangGraph** 的多智能体协作架构，通过模拟真实 HR 团队的协作方式，对候选人简历进行全方位、多维度的智能分析。

### 核心特点

| 特性 | 说明 |
|------|------|
| **7维度分析** | 技能、经验、教育、软技能、稳定性、态度、潜力 |
| **并行处理** | 多专家智能体并行分析，提高效率 |
| **可配置权重** | 支持不同岗位类型的权重配置 |
| **批判性思维** | 技能专家具备批判性思维，识别夸大陈述 |
| **动态路由** | 根据用户意图智能调用相应专家 |
| **温度分层** | 不同智能体使用不同温度参数 |

### 技术栈

```
LangChain 1.2+      # AI 框架
LangGraph 1.0+      # 智能体编排
OpenAI/Anthropic    # LLM 提供商
AsyncIO             # 异步并发
Pydantic            # 数据验证
```

---

## 架构设计

### 系统架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                         用户请求层                              │
│  (前端 / API / 对话界面)                                         │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      AgentRouter (智能体路由器)                  │
│  • 意图识别 (关键词匹配 + 置信度计算)                            │
│  • 动态路由决策                                                 │
│  • 上下文准备                                                   │
└─────────────────────────────┬───────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │  对话模式     │  │  专家模式     │  │  完整分析    │
    │  (直接LLM)   │  │  (单专家)     │  │  (协调器)    │
    └──────────────┘  └──────┬───────┘  └──────┬───────┘
                             │                  │
                             ▼                  ▼
                    ┌────────────────────────────────┐
                    │   ResumeAnalysisCoordinator    │
                    │   (主协调智能体 - 温度: 0.3)   │
                    └────────────────────────────────┘
                                       │
          ┌──────────────────────────┼──────────────────────────┐
          │                          │                          │
          ▼                          ▼                          ▼
  ┌───────────────┐          ┌───────────────┐          ┌───────────────┐
  │ 技能专家       │          │ 经验专家       │          │ 教育专家       │
  │ (温度: 0.5)   │          │ (温度: 0.5)   │          │ (温度: 0.5)   │
  │ • 批判性思维  │          │ • 项目深度    │          │ • 学历匹配    │
  │ • 可信度评分  │          │ • 职业轨迹    │          │ • 专业相关    │
  └───────────────┘          └───────────────┘          └───────────────┘
          │                          │                          │
          └──────────────────────────┼──────────────────────────┘
                                     │
          ┌──────────────────────────┼──────────────────────────┐
          ▼                          ▼                          ▼
  ┌───────────────┐          ┌───────────────┐          ┌───────────────┐
  │ 软技能专家     │          │ 稳定性专家     │          │ 态度专家       │
  │ (温度: 0.5)   │          │ (温度: 0.5)   │          │ (温度: 0.5)   │
  │ • 沟通协作    │          │ • 跳槽频率    │          │ • 抗压能力    │
  │ • 领导力      │          │ • 职业连贯性  │          │ • 责任心      │
  └───────────────┘          └───────────────┘          └───────────────┘
                                     │
                                     ▼
                          ┌───────────────┐
                          │ 潜力专家       │
                          │ (温度: 0.5)   │
                          │ • 学习能力    │
                          │ • 创新能力    │
                          └───────────────┘
                                     │
                                     ▼
                          ┌─────────────────────────────┐
                          │    综合评分与报告生成        │
                          │  • 加权平均 (可配置)         │
                          │  • 摘要生成                  │
                          │  • 建议生成                  │
                          └─────────────────────────────┘
```

---

## 核心组件

### 1. BaseAgent (基础智能体)

**文件位置**: `backend/app/application/agents/base.py`

**职责**:
- 提供所有智能体的基础功能
- LLM 初始化与管理
- 租户模型配置管理
- 通用工具方法

**核心方法**:

```python
class BaseAgent(ABC):
    async def _initialize_llm(self) -> ChatOpenAI
        # LLM 初始化优先级：
        # 1. 租户全局模型 (Tenant.llm_id)
        # 2. 传入的 model_name
        # 3. 系统默认模型

    def _parse_json_response(self, response: str) -> Dict
        # 智能解析 LLM 返回的 JSON
        # 支持：直接解析、markdown代码块、花括号提取、清理后解析

    def _format_resume_data(self, resume_data: Dict) -> str
        # 格式化简历数据为可读文本

    @abstractmethod
    async def analyze(self, context: Dict) -> Dict
        # 抽象方法：子类必须实现
```

**LLM 初始化流程**:

```
开始
  │
  ├─→ 是否已初始化？
  │   └─→ 是 → 返回缓存
  │   └─→ 否 ↓
  ├─→ 获取租户全局模型 (Tenant.llm_id)
  │   └─→ 有 → 使用租户模型
  │   └─→ 无 ↓
  ├─→ 使用传入的 model_name
  │   └─→ 有 → 使用指定模型
  │   └─→ 无 ↓
  └─→ 使用系统默认模型
```

---

### 2. ResumeAnalysisCoordinator (主协调智能体)

**文件位置**: `backend/app/application/agents/coordinator.py`

**职责**:
- 协调 7 个专家智能体
- 并行调用专家分析
- 综合评分计算
- 生成摘要和建议

**温度参数**: `0.3` (更低温度 = 更严谨的协调)

**核心流程**:

```python
async def analyze(resume_data, job_requirements):
    # 1. 并行调用 7 个专家
    results = await asyncio.gather(
        skills_expert.analyze(context),
        experience_expert.analyze(context),
        education_expert.analyze(context),
        soft_skills_expert.analyze(context),
        stability_expert.analyze(context),
        work_attitude_expert.analyze(context),
        development_potential_expert.analyze(context),
        return_exceptions=True  # 防止单个失败影响整体
    )

    # 2. 异常处理与默认值填充
    for result in results:
        result = ensure_dimension_complete(result)

    # 3. 计算综合评分 (使用可配置权重)
    overall_score = (
        skills_score * (weights['skills'] / 100) +
        experience_score * (weights['experience'] / 100) +
        education_score * (weights['education'] / 100) +
        soft_skills_score * (weights['soft_skills'] / 100) +
        stability_score * (weights['stability'] / 100) +
        attitude_score * (weights['attitude'] / 100) +
        potential_score * (weights['potential'] / 100)
    )

    # 4. 生成综合摘要
    summary = await _generate_summary(...)

    # 5. 生成建议
    recommendations = await _generate_recommendations(...)

    return {
        "overall_score": overall_score,
        "skills": skills_result,
        # ... 其他维度
        "summary": summary,
        "recommendations": recommendations
    }
```

**关键特性**:

| 特性 | 实现 |
|------|------|
| 并行执行 | `asyncio.gather` 同时调用 7 个专家 |
| 容错处理 | `return_exceptions=True` + 默认值填充 |
| 权重可配 | 支持不同岗位类型的权重配置 |
| 结果补全 | `_ensure_dimension_complete()` 确保字段完整 |

---

### 3. AgentRouter (智能体路由器)

**文件位置**: `backend/app/application/agents/agent_router.py`

**职责**:
- 识别用户意图
- 动态路由到相应专家
- 对话上下文管理

**意图识别**:

```python
INTENT_KEYWORDS = {
    "skills": ["技能", "技术栈", "编程", "语言", "框架", "工具"],
    "experience": ["经验", "工作", "项目", "履历", "职业", "公司"],
    "education": ["学历", "学位", "学校", "专业", "毕业", "教育背景"],
    "soft_skills": ["沟通", "团队", "领导", "协作", "能力", "素质"],
    "stability": ["稳定", "忠诚", "跳槽", "离职", "tenure"],
    "attitude": ["态度", "抗压", "责任心", "敬业", "情绪"],
    "potential": ["潜力", "学习", "创新", "成长", "发展"],
    "full_analysis": ["分析", "评估", "匹配", "推荐", "面试", "综合"]
}
```

**路由决策流程**:

```
用户消息
   │
   ├─→ 意图识别 (关键词匹配)
   │   └─→ 计算每个意图的匹配分数
   │
   ├─→ 获取最高分意图
   │   └─→ 置信度 = 分数 / 词数
   │
   ├─→ 意图优化
   │   └─→ 如果 full_analysis 分数高
   │       └─→ 检查是否有更具体的意图
   │           └─→ 具体意图分数 >= full_analysis * 0.8
   │               └─→ 使用具体意图
   │
   └─→ 路由决策
       ├─→ full_analysis + 高置信度 → 调用协调器
       ├─→ 具体意图 + 高置信度 → 调用单个专家
       └─→ 低置信度 → 通用对话 (直接 LLM)
```

**关键方法**:

```python
async def identify_intent(user_message, history) -> (intent, confidence)
    # 1. 关键词匹配
    # 2. 分数计算
    # 3. 意图优化 (避免误触发 full_analysis)
    # 4. 返回 (意图类型, 置信度)

async def should_call_agents(user_message, history) -> bool
    # 判断是否需要调用智能体

async def route_to_expert(user_message, history, resume_data) -> Dict
    # 路由到具体专家并返回结果
```

---

## 智能体详情

### 7 个专家智能体总览

| 专家 | 文件 | 温度 | 评分维度 | 核心能力 |
|------|------|------|----------|----------|
| **技能匹配度专家** | `skills_expert.py` | 0.5 | 批判性思维 | 识别夸大、可信度评分 |
| **工作经验专家** | `experience_expert.py` | 0.5 | 项目深度 | 履历分析、职业轨迹 |
| **教育背景专家** | `education_expert.py` | 0.5 | 学历匹配 | 学历层次、专业相关 |
| **软技能专家** | `soft_skills_expert.py` | 0.5 | 综合素质 | 沟通、协作、领导力 |
| **稳定性专家** | `stability_expert.py` | 0.5 | 忠诚度 | 跳槽频率、职业连贯性 |
| **工作态度专家** | `work_attitude_expert.py` | 0.5 | 敬业度 | 抗压能力、责任心 |
| **发展潜力专家** | `development_potential_expert.py` | 0.5 | 成长性 | 学习能力、创新能力 |

### 温度参数说明

| 温度 | 适用组件 | 效果 |
|------|----------|------|
| 0.3 | 协调器、对话 | 非常严谨、确定性高 |
| 0.5 | 专家智能体 | 平衡、适度灵活 |
| 0.7 | 创意场景 | 灵活、多样化 |

---

### 1. 技能匹配度专家

**文件**: `experts/skills_expert.py`

**Prompt**: `prompts/skills.py`

**核心输出结构** (批判性思维版本):

```json
{
  "credibility_score": 75,
  "risk_level": "B",
  "verified_claims": [
    {
      "claim": "5年Python开发经验",
      "evidence": "多个Python项目提及，时间跨度匹配"
    }
  ],
  "questionable_claims": [
    {
      "claim": "精通性能优化",
      "concern": "未提供具体性能指标或案例"
    }
  ],
  "logical_inconsistencies": [],
  "exaggeration_indicators": [],
  "interview_questions": [
    "请描述一个你优化过的性能案例，具体提升了多少？"
  ],
  "constructive_feedback": [
    "建议在简历中添加量化的项目成果"
  ],
  "score": 75,
  "score_reason": "技能匹配度良好，但有部分夸大嫌疑",
  "recommendations": "建议通过技能测试验证实际水平"
}
```

**分析要点**:
- 识别技能陈述的真实性
- 检测夸大和模糊表述
- 生成验证性问题
- 提供改进建议

---

### 2. 工作经验专家

**文件**: `experts/experience_expert.py`

**核心输出**:

```json
{
  "score": 82,
  "score_reason": "工作经验丰富，项目相关性强",
  "total_years": 5.5,
  "relevant_years": 4.0,
  "career_progression": "良好",
  "project_highlights": [
    "主导电商平台重构，支撑百万级用户",
    "设计微服务架构，提升系统可扩展性"
  ],
  "strengths": [
    "职业发展轨迹清晰，晋升合理",
    "项目经验丰富，涉及多个技术栈"
  ],
  "concerns": [
    "最近一份工作时长较短（8个月）"
  ]
}
```

---

### 3. 教育背景专家

**文件**: `experts/education_expert.py`

**核心输出**:

```json
{
  "score": 90,
  "score_reason": "学历优秀，专业高度相关",
  "highest_degree": "硕士",
  "major_relevance": "专业对口（计算机科学）",
  "honors": [
    "校级优秀毕业生",
    "国家奖学金获得者"
  ],
  "certifications": [
    "AWS解决方案架构师认证",
    "PMP项目管理认证"
  ]
}
```

---

### 4. 软技能专家

**文件**: `experts/soft_skills_expert.py`

**核心输出**:

```json
{
  "score": 78,
  "score_reason": "软技能表现良好，团队经验丰富",
  "communication": "良好",
  "teamwork": "强",
  "leadership": "具备潜力",
  "strengths": [
    "跨部门协作经验丰富",
    "具备项目管理经验"
  ],
  "areas_for_improvement": [
    "缺乏大规模团队管理经验"
  ]
}
```

---

### 5. 稳定性/忠诚度专家

**文件**: `experts/stability_expert.py`

**核心输出**:

```json
{
  "score": 65,
  "score_reason": "工作稳定性一般，存在频繁跳槽倾向",
  "job_tenure_avg": 1.8,
  "job_changes_count": 6,
  "frequent_hopper_flag": true,
  "career_progression_score": 70,
  "positive_indicators": [
    "职业发展方向持续向好"
  ],
  "risk_factors": [
    "平均工作时长不足2年",
    "最近3年跳槽3次"
  ]
}
```

---

### 6. 工作态度/抗压专家

**文件**: `experts/work_attitude_expert.py`

**核心输出**:

```json
{
  "score": 72,
  "score_reason": "工作态度积极，具备一定抗压能力",
  "stress_resistance": "良好",
  "responsibility_level": "较强",
  "dedication_indicators": [
    "主导紧急项目上线",
    "多次主动承担额外工作"
  ],
  "strengths": [
    "工作投入度高",
    "责任心强"
  ],
  "concerns": [
    "未明确提及处理工作压力的具体方式"
  ]
}
```

---

### 7. 发展潜力专家

**文件**: `experts/development_potential_expert.py`

**核心输出**:

```json
{
  "score": 85,
  "score_reason": "学习能力强，具备良好的发展潜力",
  "learning_ability": "强",
  "innovation_capability": "良好",
  "adaptability_score": 80,
  "high_potential_flags": [
    "持续学习新技术（云原生、AI）",
    "参与开源项目",
    "技术博客作者"
  ],
  "growth_trajectory": "从开发工程师逐步成长到技术负责人，学习意愿强烈"
}
```

---

## 工作流程

### 完整分析流程

```
┌─────────────────────────────────────────────────────────────┐
│                    1. 用户请求                              │
│  分析简历 / 评估技能 / 查看经验 / 综合评估                  │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    2. 意图识别                              │
│  AgentRouter.identify_intent()                             │
│  • 关键词匹配                                               │
│  • 置信度计算                                               │
│  • 意图优化 (避免误触发)                                    │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    3. 路由决策                              │
│  ┌────────────────┬────────────────┬────────────────┐     │
│  │ 通用对话       │  单个专家       │  完整分析       │     │
│  │ (直接 LLM)     │ (特定维度)      │  (协调器)       │     │
│  └────────────────┴────────────────┴────────────────┘     │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              4. 专家智能体分析 (并行执行)                    │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │技能专家  │ │经验专家  │ │教育专家  │ │软技能    │       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                   │
│  │稳定性    │ │态度专家  │ │潜力专家  │                   │
│  └──────────┘ └──────────┘ └──────────┘                   │
│                                                             │
│  asyncio.gather([expert.analyze() for expert in experts])  │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              5. 结果处理与综合                              │
│  • 异常处理 (默认值填充)                                    │
│  • 字段补全 (_ensure_dimension_complete)                   │
│  • 评分计算 (加权平均)                                      │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              6. 报告生成                                    │
│  • 综合摘要 (_generate_summary)                             │
│  • 建议生成 (_generate_recommendations)                     │
│  • 格式化输出 (_format_coordinator_result)                  │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    7. 返回结果                              │
│  {                                                          │
│    "overall_score": 85,                                     │
│    "skills": {...},                                         │
│    "experience": {...},                                     │
│    "education": {...},                                      │
│    "soft_skills": {...},                                    │
│    "stability": {...},                                      │
│    "work_attitude": {...},                                  │
│    "development_potential": {...},                           │
│    "summary": "...",                                        │
│    "recommendations": [...]                                  │
│  }                                                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 路由与意图识别

### 意图识别算法

```python
# 1. 关键词匹配
intent_scores = {}
for intent, keywords in INTENT_KEYWORDS.items():
    score = sum(1 for keyword in keywords if keyword in message_lower)
    if score > 0:
        intent_scores[intent] = score

# 2. 置信度计算
confidence = max_score / len(message.split())

# 3. 意图优化 (关键!)
if top_intent == "full_analysis":
    for specific_intent in ["skills", "experience", ...]:
        if intent_scores[specific_intent] >= intent_scores["full_analysis"] * 0.8:
            top_intent = specific_intent  # 使用更具体的意图
            break

# 4. 路由决策
if confidence < 0.1:
    return "general"  # 通用对话
elif intent == "full_analysis":
    return "coordinator"  # 完整分析
else:
    return intent  # 单个专家
```

### 路由示例

| 用户消息 | 识别意图 | 调用组件 |
|----------|----------|----------|
| "帮我分析一下这份简历" | full_analysis | Coordinator |
| "这个候选人的技能怎么样？" | skills | SkillsExpert |
| "他有多少年工作经验？" | experience | ExperienceExpert |
| "他的学历背景如何？" | education | EducationExpert |
| "你好 / 谢谢 / 再见" | general | 直接 LLM |

---

## 权重配置

### 分析配置类型

**文件**: `backend/app/core/analysis_weights.py`

```python
class AnalysisProfile(str, Enum):
    STANDARD = "standard"           # 标准配置
    TECH_FOCUSED = "tech_focused"   # 技术岗侧重
    LEADERSHIP = "leadership"       # 管理岗侧重
    JUNIOR = "junior"               # 初级岗位
    SENIOR = "senior"               # 高级岗位
```

### 权重配置表

| 维度 | STANDARD | TECH_FOCUSED | LEADERSHIP | JUNIOR | SENIOR |
|------|----------|--------------|------------|--------|--------|
| skills | 20% | **25%** | 15% | 15% | 20% |
| experience | 20% | **25%** | 20% | 10% | **25%** |
| education | 15% | 15% | 15% | **20%** | 10% |
| soft_skills | 15% | 10% | **20%** | 15% | **20%** |
| stability | 15% | 10% | 15% | 10% | 15% |
| attitude | 10% | 10% | 10% | **15%** | 5% |
| potential | 5% | 5% | 5% | **15%** | 5% |

### 使用示例

```python
# 初始化协调器时指定配置
coordinator = ResumeAnalysisCoordinator(
    db,
    tenant_id,
    analysis_profile="tech_focused"  # 技术岗侧重
)

# 权重自动应用
overall_score = (
    skills_score * 0.25 +  # 技能权重更高
    experience_score * 0.25 +
    ...
)
```

---

## Prompt工程

### 协调器 Prompt 结构

**文件**: `prompts/coordinator.py`

```
角色定义: HR分析专家和项目经理
团队介绍: 4个专业专家工具
工作流程: 依次调用 → 收集结果 → 计算评分 → 生成报告
输出要求: 严格的JSON格式
评分标准: 90-100优秀, 80-89良好, 70-79合格, 60-69一般, <60不合格
```

### 专家 Prompt 结构

每个专家的 Prompt 包含:

1. **角色定义**: 清晰的专家身份
2. **分析维度**: 具体的评估方向
3. **输入数据**: 简历文本的格式说明
4. **输出格式**: JSON 结构要求
5. **评分标准**: 详细的评分依据
6. **注意事项**: 常见问题和处理方式

### 技能专家 Prompt 示例

```python
SKILLS_SYSTEM_PROMPT = """你是一位资深的技能评估专家，专门负责评估候选人的技术技能与目标职位的匹配程度。

## 你的专长
1. 批判性思维：识别简历中的夸大、虚假或模糊的技能陈述
2. 可信度评估：基于证据强度给出可信度评分
3. 风险识别：标记需要进一步验证的技能点
4. 面试指导：生成针对性的面试问题

## 输出要求 (必须严格遵守)
请以JSON格式输出分析结果，包含以下字段：
{
  "credibility_score": 0-100的整数,
  "risk_level": "A/B/C/D"风险等级,
  "verified_claims": [{"claim": "陈述", "evidence": "证据"}],
  "questionable_claims": [{"claim": "陈述", "concern": "疑虑"}],
  "interview_questions": ["问题1", "问题2"],
  "constructive_feedback": ["建议1", "建议2"]
}
"""
```

---

## 数据流图

### 完整数据流

```
用户上传简历
    │
    ├─→ 文件解析 (PDF/DOCX/HTML → Text)
    │
    ├─→ 简历数据结构化
    │   {
    │     "candidate_name": "...",
    │     "extracted_text": "...",
    │     "basic_info": {...},
    │     "work_experience": [...],
    │     "education": [...],
    │     "skills": [...]
    │   }
    │
    ├─→ 存储到数据库
    │
    └─→ 触发分析请求
            │
            ├─→ API: POST /api/v1/agent-analysis/analyze/resume
            │   {
            │     "resume_id": "uuid",
            │     "job_description": "...",
            │     "position": "前端工程师",
            │     "dimensions": ["skills", "experience", ...]
            │   }
            │
            ├─→ 意图识别 (AgentRouter)
            │
            ├─→ 调用协调器 (ResumeAnalysisCoordinator)
            │
            ├─→ 并行专家分析
            │   ├─→ SkillsExpert.analyze()
            │   ├─→ ExperienceExpert.analyze()
            │   ├─→ EducationExpert.analyze()
            │   ├─→ SoftSkillsExpert.analyze()
            │   ├─→ StabilityExpert.analyze()
            │   ├─→ WorkAttitudeExpert.analyze()
            │   └─→ DevelopmentPotentialExpert.analyze()
            │
            ├─→ 综合评分计算
            │   overall_score = Σ(score_i × weight_i)
            │
            ├─→ 摘要生成 (LLM)
            │
            ├─→ 建议生成 (规则 + LLM)
            │
            ├─→ 结果格式化
            │
            └─→ 返回完整报告
                    │
                    ├─→ 存储分析结果到数据库
                    │
                    └─→ 返回给前端展示
```

---

## 扩展指南

### 添加新的专家智能体

#### 1. 创建专家文件

```python
# backend/app/application/agents/experts/custom_expert.py

from app.application.agents.base import BaseAgent

class CustomExpertAgent(BaseAgent):
    """自定义专家智能体"""

    def __init__(self, db, tenant_id: str):
        super().__init__(db, tenant_id, temperature=0.5)

    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # 1. 获取输入数据
        resume_data = context.get("resume_data", {})

        # 2. 构建 Prompt
        prompt = self._build_prompt(resume_data)

        # 3. 调用 LLM
        response = await self._invoke_llm(prompt)

        # 4. 解析结果
        result = self._parse_json_response(response)

        return result
```

#### 2. 创建 Prompt 文件

```python
# backend/app/application/agents/prompts/custom.py

CUSTOM_EXPERT_PROMPT = """你是...专家

## 分析维度
...

## 输出格式
{
  "score": 0-100,
  "details": "...",
  ...
}
"""

def get_custom_prompt(resume_text: str) -> str:
    return f"""{CUSTOM_EXPERT_PROMPT}

## 简历内容
{resume_text}

请进行分析并输出JSON格式结果。"""
```

#### 3. 注册到协调器

```python
# coordinator.py

from app.application.agents.experts.custom_expert import CustomExpertAgent

class ResumeAnalysisCoordinator(BaseAgent):
    def __init__(self, db, tenant_id: str):
        super().__init__(db, tenant_id, temperature=0.3)

        # 初始化新专家
        self.custom_expert = CustomExpertAgent(db, tenant_id)

    async def analyze(self, resume_data, job_requirements):
        # 并行调用
        results = await asyncio.gather(
            ...,
            self.custom_expert.analyze(context),
            ...
        )
```

#### 4. 更新权重配置

```python
# analysis_weights.py

WEIGHT_CONFIGS = {
    AnalysisProfile.STANDARD: {
        ...
        'custom': 10.0  # 新维度权重
    }
}
```

### 添加新的分析配置

```python
# analysis_weights.py

class AnalysisProfile(str, Enum):
    ...
    CUSTOM_PROFILE = "custom_profile"  # 新配置

WEIGHT_CONFIGS[AnalysisProfile.CUSTOM_PROFILE] = {
    'skills': 30.0,  # 自定义权重分配
    'experience': 20.0,
    ...
}
```

---

## 附录

### A. 组件文件清单

| 组件 | 文件路径 |
|------|----------|
| 基础智能体 | `agents/base.py` |
| 协调器 | `agents/coordinator.py` |
| 路由器 | `agents/agent_router.py` |
| 技能专家 | `agents/experts/skills_expert.py` |
| 经验专家 | `agents/experts/experience_expert.py` |
| 教育专家 | `agents/experts/education_expert.py` |
| 软技能专家 | `agents/experts/soft_skills_expert.py` |
| 稳定性专家 | `agents/experts/stability_expert.py` |
| 态度专家 | `agents/experts/work_attitude_expert.py` |
| 潜力专家 | `agents/experts/development_potential_expert.py` |
| 权重配置 | `core/analysis_weights.py` |
| Prompt 模板 | `agents/prompts/*.py` |

### B. API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/v1/agent-analysis/analyze/resume` | POST | 完整分析 (协调器) |
| `/api/v1/agent-analysis/analyze/{resume_id}` | GET | 获取分析结果 |
| `/api/v1/agent-analysis/conversations/{id}/stream` | POST | 对话分析 (智能路由) |

### C. 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `DEFAULT_AI_MODEL` | `gpt-4` | 默认 LLM 模型 |
| `DEFAULT_MAX_TOKENS` | `2000` | 最大 token 数 |
| `DEFAULT_ANALYSIS_PROFILE` | `standard` | 默认分析配置 |

### D. 性能指标

| 指标 | 数值 |
|------|------|
| 并行专家数 | 7 |
| 单次分析耗时 | ~30-60 秒 |
| Token 消耗 | ~5000-10000 |
| 温度范围 | 0.3-0.5 |

---

**文档版本**: v1.0
**最后更新**: 2025-01-01
**维护者**: AI HR Team
