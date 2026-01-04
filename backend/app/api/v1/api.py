"""API v1路由汇总"""

from fastapi import APIRouter

from app.api.v1.endpoints import resumes, ai_models, ragflow, auth, llm_config, llm_init, agent_analysis, stats

api_router = APIRouter()

# 公开路由（不需要认证）
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

# LLM 初始化路由（不需要认证，用于初始化数据）
api_router.include_router(llm_init.router, prefix="/llm-init", tags=["llm-init"])

# 需要认证的路由
api_router.include_router(resumes.router, prefix="/resumes", tags=["resumes"])
api_router.include_router(stats.router, prefix="/stats", tags=["stats"])
api_router.include_router(ai_models.router, prefix="/ai-models", tags=["ai-models"])
api_router.include_router(ragflow.router, prefix="/ragflow", tags=["ragflow"])

# LLM 模型配置路由
api_router.include_router(llm_config.router, prefix="/llm", tags=["llm"])

# 智能体分析路由
api_router.include_router(agent_analysis.router, prefix="/agent-analysis", tags=["agent-analysis"])