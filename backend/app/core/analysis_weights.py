"""
AI分析维度权重配置
定义不同场景下的维度权重分配方案
"""

from enum import Enum
from typing import Dict


class AnalysisProfile(str, Enum):
    """分析预设配置"""
    STANDARD = "standard"           # 标准配置
    TECH_FOCUSED = "tech_focused"   # 技术岗侧重
    LEADERSHIP = "leadership"       # 管理岗侧重
    JUNIOR = "junior"               # 初级岗位
    SENIOR = "senior"               # 高级岗位


# 7维度权重配置模板
WEIGHT_CONFIGS: Dict[AnalysisProfile, Dict[str, float]] = {
    AnalysisProfile.STANDARD: {
        'skills': 20.0,
        'experience': 20.0,
        'education': 15.0,
        'soft_skills': 15.0,
        'stability': 15.0,
        'attitude': 10.0,
        'potential': 5.0
    },
    AnalysisProfile.TECH_FOCUSED: {
        'skills': 25.0,
        'experience': 25.0,
        'education': 15.0,
        'soft_skills': 10.0,
        'stability': 10.0,
        'attitude': 10.0,
        'potential': 5.0
    },
    AnalysisProfile.LEADERSHIP: {
        'skills': 15.0,
        'experience': 20.0,
        'education': 15.0,
        'soft_skills': 20.0,
        'stability': 15.0,
        'attitude': 10.0,
        'potential': 5.0
    },
    AnalysisProfile.JUNIOR: {
        'skills': 15.0,
        'experience': 10.0,
        'education': 20.0,
        'soft_skills': 15.0,
        'stability': 10.0,
        'attitude': 15.0,
        'potential': 15.0
    },
    AnalysisProfile.SENIOR: {
        'skills': 20.0,
        'experience': 25.0,
        'education': 10.0,
        'soft_skills': 20.0,
        'stability': 15.0,
        'attitude': 5.0,
        'potential': 5.0
    }
}


# 维度中文名称映射
DIMENSION_NAMES = {
    'skills': '技能匹配度',
    'experience': '工作经验',
    'education': '教育背景',
    'soft_skills': '软技能',
    'stability': '稳定性/忠诚度',
    'attitude': '工作态度/抗压',
    'potential': '发展潜力'
}


# 技能熟练度等级标准
class ProficiencyLevel(str, Enum):
    """技能熟练度等级"""
    MASTER = "master"       # 大师级 (5级)
    EXPERT = "expert"       # 专家级 (4级)
    ADVANCED = "advanced"   # 高级 (3级)
    INTERMEDIATE = "intermediate"  # 中级 (2级)
    BASIC = "basic"         # 基础 (1级)


PROFICIENCY_LEVELS = {
    5: {
        "name": "大师级",
        "level": ProficiencyLevel.MASTER,
        "description": "行业认可，创新贡献，深度影响",
        "criteria": {
            "years": 7,
            "evidence_required": ["industry_recognition", "innovation", "mentorship"]
        }
    },
    4: {
        "name": "专家级",
        "level": ProficiencyLevel.EXPERT,
        "description": "深度理解，设计能力，导师角色",
        "criteria": {
            "years": 5,
            "evidence_required": ["deep_understanding", "design_experience", "leadership"]
        }
    },
    3: {
        "name": "高级",
        "level": ProficiencyLevel.ADVANCED,
        "description": "独立工作，解决复杂问题",
        "criteria": {
            "years": 3,
            "evidence_required": ["independent_work", "complex_problems"]
        }
    },
    2: {
        "name": "中级",
        "level": ProficiencyLevel.INTERMEDIATE,
        "description": "常规任务，需要一定指导",
        "criteria": {
            "years": 1,
            "evidence_required": ["routine_tasks"]
        }
    },
    1: {
        "name": "基础",
        "level": ProficiencyLevel.BASIC,
        "description": "简单任务，需要大量指导",
        "criteria": {
            "years": 0,
            "evidence_required": ["basic_knowledge"]
        }
    }
}


# 稳定性评估阈值
STABILITY_THRESHOLDS = {
    'frequent_hopper_months': 12,      # <12个月 per job = 频繁跳槽
    'good_tenure_years': 2.5,          # >=2.5年 = 良好
    'excellent_tenure_years': 3.5      # >=3.5年 = 优秀
}


def get_weights(profile: AnalysisProfile = AnalysisProfile.STANDARD) -> Dict[str, float]:
    """获取指定配置的权重分配

    Args:
        profile: 分析配置类型

    Returns:
        维度权重字典
    """
    return WEIGHT_CONFIGS.get(profile, WEIGHT_CONFIGS[AnalysisProfile.STANDARD]).copy()


def validate_weights(weights: Dict[str, float]) -> bool:
    """验证权重总和是否为100

    Args:
        weights: 权重字典

    Returns:
        是否有效
    """
    total = sum(weights.values())
    return abs(total - 100.0) < 0.01


def get_proficiency_info(level: int) -> dict:
    """获取熟练度等级信息

    Args:
        level: 等级 (1-5)

    Returns:
        等级信息字典
    """
    return PROFICIENCY_LEVELS.get(level, PROFICIENCY_LEVELS[1])
