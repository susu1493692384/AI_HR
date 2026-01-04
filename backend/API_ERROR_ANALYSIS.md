# API调用错误分析报告

## 📋 问题描述

**症状**: 在AI分析过程中，先出现API调用错误输出，然后被正确输出覆盖

**错误日志**:
```
技能分析失败: Expecting property name enclosed in double quotes: line 13 column 22 (char 442)
协调分析失败: 'str' object has no attribute 'get'
```

## 🔍 根本原因分析

### 问题流程

1. **用户发送消息**: "分析候选人的技能优势"

2. **系统调用专家智能体**:
   - 进入智能体模式 (`use_agent=True`)
   - 调用 `SkillsExpertAgent.analyze()`

3. **LLM返回JSON格式错误**:
   - 技能专家调用LLM（模型: glm-4-flash）
   - LLM返回的内容不是有效的JSON格式
   - 在第13行第22个字符处有格式错误

4. **JSON解析失败**:
   ```python
   # base.py:148-175
   def _parse_json_response(self, response: str) -> Dict[str, Any]:
       try:
           return json.loads(response)  # ❌ 失败
       except json.JSONDecodeError:
           # 尝试提取JSON部分
           json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
           if json_match:
               return json.loads(json_match.group(1))  # ❌ 仍然失败
           # ...
           raise ValueError(f"无法解析JSON响应...")
   ```

5. **异常被捕获，返回默认结构**:
   ```python
   # skills_expert.py:55-65
   except Exception as e:
       logger.error(f"技能分析失败: {e}")
       return {
           "score": 0,
           "matched_skills": [],
           "missing_skills": [],
           "strengths": [],
           "gaps": ["分析失败，请重试"],
           "recommendations": f"技能分析过程出错: {str(e)}"
       }
   ```

6. **协调器处理失败**:
   ```python
   # coordinator.py:95
   summary = await self._generate_summary(
       resume_data,     # Dict
       job_requirements,
       skills_result,   # Dict (默认错误结构)
       experience_result,
       education_result,
       soft_skills_result,
       overall_score
   )
   ```

   错误发生在这里:
   ```python
   # coordinator.py:138-150
   async def _generate_summary(
       self,
       resume_data: Dict[str, Any],
       job_requirements: Dict[str, Any],  # ❌ 但实际传入了字符串或其他类型
       skills_result: Dict[str, Any],
       # ...
   ) -> str:
       # 代码期望 job_requirements 是字典，但可能不是
       summary_text = job_requirements.get(...)  # ❌ 'str' object has no attribute 'get'
   ```

7. **Fallback到主AI模型**:
   - 专家智能体调用链失败
   - 系统fallback到直接LLM对话
   - 主AI模型成功回复，生成正确输出
   - **用户看到正确输出覆盖了之前的错误**

## 🐛 核心问题

### 问题1: JSON解析不够健壮

**位置**: [base.py:148-175](backend/app/application/agents/base.py#L148-L175)

**问题**:
- LLM返回的JSON可能包含:
  - 单引号而非双引号
  - 尾随逗号
  - 注释
  - 非标准的转义字符
- 当前的正则表达式无法处理所有情况

### 问题2: 调用参数类型错误

**位置**: [coordinator.py:95-102](backend/app/application/agents/coordinator.py#L95-L102)

**问题**:
```python
# 调用时传入了job_requirements (但实际可能是None或字符串)
summary = await self._generate_summary(
    resume_data,
    job_requirements,  # ❌ 这里的类型可能不正确
    skills_result,
    # ...
)
```

### 问题3: 提示词不够严格

**位置**: [skills.py:69-106](backend/app/application/agents/prompts/skills.py#L69-L106)

**问题**:
- 提示词要求返回JSON，但LLM可能不严格遵守
- 需要更强的约束和示例

## 🔧 解决方案

### 方案1: 改进JSON解析 (推荐)

**修改文件**: [base.py](backend/app/application/agents/base.py)

```python
def _parse_json_response(self, response: str) -> Dict[str, Any]:
    """解析LLM返回的JSON格式响应 - 增强版"""
    import re

    # 清理响应
    response = response.strip()

    # 1. 尝试直接解析
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        pass

    # 2. 尝试提取markdown代码块
    patterns = [
        r'```json\s*(.*?)\s*```',  # ```json ... ```
        r'```\s*(.*?)\s*```',       # ``` ... ```
        r'\{.*\}',                  # 第一个{到最后一个}
    ]

    for pattern in patterns:
        match = re.search(pattern, response, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except (json.JSONDecodeError, IndexError):
                continue

    # 3. 尝试清理常见问题并解析
    try:
        # 移除注释
        cleaned = re.sub(r'//.*?\n', '', response)
        cleaned = re.sub(r'/\*.*?\*/', '', cleaned, flags=re.DOTALL)

        # 替换单引号为双引号 (简单情况)
        cleaned = re.sub(r"'([^']*)'", r'"\1"', cleaned)

        # 移除尾随逗号
        cleaned = re.sub(r',\s*([}\]])', r'\1', cleaned)

        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # 4. 最后尝试: 使用更宽松的JSON解析器
    try:
        import json5  # pip install json5
        return json5.loads(response)
    except ImportError:
        logger.warning("json5未安装，无法使用宽松JSON解析")
    except Exception:
        pass

    # 如果所有方法都失败，抛出异常
    raise ValueError(f"无法解析JSON响应，原始内容:\n{response[:500]}")
```

### 方案2: 添加类型检查和错误处理

**修改文件**: [coordinator.py](backend/app/application/agents/coordinator.py)

```python
async def _generate_summary(
    self,
    resume_data: Dict[str, Any],
    job_requirements: Dict[str, Any],
    skills_result: Dict[str, Any],
    experience_result: Dict[str, Any],
    education_result: Dict[str, Any],
    soft_skills_result: Dict[str, Any],
    overall_score: int
) -> str:
    """使用LLM生成综合分析摘要"""

    # 添加类型检查
    if not isinstance(job_requirements, dict):
        logger.warning(f"job_requirements类型错误: {type(job_requirements)}，使用空字典")
        job_requirements = {}

    # 添加None检查
    if skills_result is None:
        skills_result = {"score": 0, "error": "分析结果为空"}
    if experience_result is None:
        experience_result = {"score": 0, "error": "分析结果为空"}
    if education_result is None:
        education_result = {"score": 0, "error": "分析结果为空"}
    if soft_skills_result is None:
        soft_skills_result = {"score": 0, "error": "分析结果为空"}

    # 原有逻辑...
```

### 方案3: 改进提示词

**修改文件**: [skills.py](backend/app/application/agents/prompts/skills.py)

```python
def get_skills_prompt(resume_skills: str, job_skills: str = "") -> str:
    """生成技能专家的完整提示词 - 增强版"""
    instruction = """你是一位技术技能评估专家。

## 重要提示
1. 你必须且只能返回纯JSON格式的响应
2. 不要包含任何markdown代码块标记（如```json）
3. 不要包含任何解释性文字
4. JSON必须是有效的，使用双引号，不要使用尾随逗号
5. 直接输出JSON对象，从{开始，以}结束

输出示例（严格按此格式）:
{{"score": 85, "matched_skills": [], "missing_skills": [], "strengths": [], "gaps": [], "recommendations": "..."}}

---

"""

    if job_skills:
        return f"""{instruction}
## 候选人简历
{resume_skills}

## 职位要求技能
{job_skills}

请分析并返回纯JSON格式结果（不要任何额外文字）:
"""
    else:
        return f"""{instruction}
## 候选人简历
{resume_skills}

请分析并返回纯JSON格式结果（不要任何额外文字）:
"""
```

### 方案4: 添加重试机制

**修改文件**: [base.py](backend/app/application/agents/base.py)

```python
async def _invoke_llm_with_retry(self, prompt: str, max_retries: int = 2) -> Dict[str, Any]:
    """调用LLM并解析JSON，带重试机制"""

    for attempt in range(max_retries):
        try:
            response = await self._invoke_llm(prompt)
            return self._parse_json_response(response)
        except Exception as e:
            if attempt < max_retries - 1:
                logger.warning(f"LLM调用失败，第{attempt + 1}次重试: {e}")
                # 添加更强的格式要求
                prompt += "\n\n重要：请只返回纯JSON，不要包含任何其他文字或代码块标记。"
                continue
            else:
                logger.error(f"LLM调用失败，已重试{max_retries}次: {e}")
                raise

    # 理论上不会到达这里
    raise RuntimeError("LLM调用失败")
```

## 📊 影响范围

**受影响的专家智能体**:
- ✅ SkillsExpertAgent (技能专家) - 已确认有问题
- ⚠️ ExperienceExpertAgent (经验专家) - 可能有问题
- ⚠️ EducationExpertAgent (教育专家) - 可能有问题
- ⚠️ SoftSkillsExpertAgent (软技能专家) - 可能有问题

**受影响的调用链**:
```
用户消息
  ↓
agent_analysis.py (流式端点)
  ↓
AgentRouter.route_to_expert()
  ↓
ResumeAnalysisCoordinator.analyze()
  ↓
4个专家并行调用 (其中一个失败)
  ↓
coordinator._generate_summary() ← 这里出错
  ↓
Fallback到主LLM (成功，用户看到正确输出)
```

## 🎯 修复优先级

1. **高优先级**: 方案1 (改进JSON解析) - 立即修复
2. **中优先级**: 方案2 (类型检查) - 防止崩溃
3. **中优先级**: 方案3 (改进提示词) - 减少错误率
4. **低优先级**: 方案4 (重试机制) - 提升稳定性

## ✅ 验证方法

修复后，执行以下测试:

1. **功能测试**:
   ```bash
   # 发送测试消息
   curl -X POST http://localhost:8000/api/v1/agent-analysis/conversations/{id}/stream \
     -H "Content-Type: application/json" \
     -d '{"content": "分析候选人的技能优势", "use_agent": true}'
   ```

2. **日志检查**:
   ```bash
   # 不应该再看到这些错误
   docker-compose logs backend | grep "技能分析失败"
   docker-compose logs backend | grep "协调分析失败"
   ```

3. **输出验证**:
   - 专家分析应该成功
   - 不应该fallback到主LLM
   - 返回的结构化数据应该完整

## 📝 额外建议

1. **添加单元测试**: 为JSON解析函数添加测试用例
2. **添加集成测试**: 测试完整的专家调用流程
3. **监控和告警**: 添加JSON解析失败率的监控
4. **考虑使用JSON Schema**: 使用pydantic等库验证返回结构

---

**创建时间**: 2025-12-26
**分析人**: Claude Code
**状态**: 待修复
