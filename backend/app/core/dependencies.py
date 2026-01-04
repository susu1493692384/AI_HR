"""FastAPI依赖注入"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.infrastructure.database.database import AsyncSessionLocal
from app.infrastructure.repositories.resume_repository import ResumeRepository
from app.infrastructure.repositories.ai_model_repository import AIModelRepository
from app.infrastructure.database.models import User
from app.core.llm_init import DEFAULT_TENANT_ID

# HTTP认证方案
security = HTTPBearer()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话"""
    async with AsyncSessionLocal() as session:
        yield session


async def get_resume_repository(
    db: AsyncSession = Depends(get_db)
) -> ResumeRepository:
    """获取简历仓库"""
    return ResumeRepository(db)


async def get_ai_model_repository(
    db: AsyncSession = Depends(get_db)
) -> AIModelRepository:
    """获取AI模型仓库"""
    return AIModelRepository(db)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """获取当前用户信息"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        from app.core.security import decode_token
        payload = decode_token(credentials.credentials)
        if payload is None:
            raise credentials_exception

        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception

        # 从数据库获取用户信息 - 使用 ORM 查询
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if user is None:
            raise credentials_exception

        return user

    except Exception:
        raise credentials_exception


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """获取当前活跃用户"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户已被禁用"
        )
    return current_user


async def get_current_tenant_id(
    current_user: User = Depends(get_current_user)
) -> str:
    """
    获取当前租户 ID
    简化版本：使用用户 ID 作为租户 ID
    后续可以扩展为多租户系统
    """
    return str(current_user.id)


async def get_current_tenant_id_optional(
    credentials: HTTPAuthorizationCredentials = Depends(
        HTTPBearer(auto_error=False)
    ),
    db: AsyncSession = Depends(get_db)
) -> str:
    """
    获取当前租户 ID（可选认证）
    如果没有提供 token，使用默认租户 ID
    用于开发环境，允许在没有登录的情况下访问 LLM 配置
    """
    if credentials is None:
        # 没有提供 token，返回默认租户 ID
        return DEFAULT_TENANT_ID

    try:
        from app.core.security import decode_token
        payload = decode_token(credentials.credentials)
        if payload is None:
            return DEFAULT_TENANT_ID

        user_id: str = payload.get("sub")
        return user_id if user_id else DEFAULT_TENANT_ID

    except Exception:
        return DEFAULT_TENANT_ID