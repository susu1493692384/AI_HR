"""AI模型配置API端点"""

from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.application.schemas.ai_model import (
    AIModel as AIModelSchema,
    AIModelCreate,
    AIModelUpdate,
    ModelTestRequest,
    ModelTestResponse,
)
from app.application.use_cases.model_configuration import ModelConfigurationUseCase
from app.infrastructure.repositories.ai_model_repository import AIModelRepository

router = APIRouter()


@router.get("/", response_model=List[AIModelSchema])
async def list_ai_models(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> Any:
    """获取AI模型列表"""
    model_repo = AIModelRepository(db)
    models = await model_repo.get_multi(skip=skip, limit=limit)
    return models


@router.post("/", response_model=AIModelSchema)
async def create_ai_model(
    model_config: AIModelCreate,
    db: Session = Depends(get_db),
) -> Any:
    """创建AI模型配置"""
    try:
        config_use_case = ModelConfigurationUseCase(db)
        model = await config_use_case.create_model(model_config)

        return AIModelSchema(
            id=model.id,
            name=model.name,
            provider=model.provider,
            model_name=model.model_name,
            api_key_encrypted="***",  # 不返回真实的API Key
            base_url=model.base_url,
            model_type=model.model_type,
            is_active=model.is_active,
            test_results=model.test_results,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"创建AI模型配置失败: {str(e)}"
        )


@router.get("/{model_id}", response_model=AIModelSchema)
async def get_ai_model(
    model_id: str,
    db: Session = Depends(get_db),
) -> Any:
    """获取AI模型详情"""
    model_repo = AIModelRepository(db)
    model = await model_repo.get(model_id)

    if not model:
        raise HTTPException(
            status_code=404,
            detail="AI模型配置不存在"
        )

    return AIModelSchema(
        id=model.id,
        name=model.name,
        provider=model.provider,
        model_name=model.model_name,
        api_key_encrypted="***",  # 不返回真实的API Key
        base_url=model.base_url,
        model_type=model.model_type,
        is_active=model.is_active,
        test_results=model.test_results,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


@router.put("/{model_id}", response_model=AIModelSchema)
async def update_ai_model(
    model_id: str,
    model_config: AIModelUpdate,
    db: Session = Depends(get_db),
) -> Any:
    """更新AI模型配置"""
    try:
        config_use_case = ModelConfigurationUseCase(db)
        model = await config_use_case.update_model(model_id, model_config)

        if not model:
            raise HTTPException(
                status_code=404,
                detail="AI模型配置不存在"
            )

        return AIModelSchema(
            id=model.id,
            name=model.name,
            provider=model.provider,
            model_name=model.model_name,
            api_key_encrypted="***",
            base_url=model.base_url,
            model_type=model.model_type,
            is_active=model.is_active,
            test_results=model.test_results,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"更新AI模型配置失败: {str(e)}"
        )


@router.delete("/{model_id}")
async def delete_ai_model(
    model_id: str,
    db: Session = Depends(get_db),
) -> Any:
    """删除AI模型配置"""
    try:
        model_repo = AIModelRepository(db)
        model = await model_repo.get(model_id)

        if not model:
            raise HTTPException(
                status_code=404,
                detail="AI模型配置不存在"
            )

        await model_repo.delete(model_id)

        return {
            "success": True,
            "message": "AI模型配置删除成功"
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"删除AI模型配置失败: {str(e)}"
        )


@router.post("/{model_id}/test", response_model=ModelTestResponse)
async def test_ai_model(
    model_id: str,
    test_request: ModelTestRequest,
    db: Session = Depends(get_db),
) -> Any:
    """测试AI模型连接"""
    try:
        config_use_case = ModelConfigurationUseCase(db)
        result = await config_use_case.test_model(
            model_id=model_id,
            test_prompt=test_request.test_prompt
        )

        return ModelTestResponse(
            success=result.success,
            response_time=result.response_time,
            error_message=result.error_message,
            test_prompt=test_request.test_prompt,
            test_response=result.test_response,
            tested_at=result.tested_at,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"测试AI模型失败: {str(e)}"
        )


@router.patch("/{model_id}/toggle")
async def toggle_ai_model(
    model_id: str,
    is_active: bool,
    db: Session = Depends(get_db),
) -> Any:
    """切换AI模型激活状态"""
    try:
        config_use_case = ModelConfigurationUseCase(db)
        model = await config_use_case.toggle_model(model_id, is_active)

        if not model:
            raise HTTPException(
                status_code=404,
                detail="AI模型配置不存在"
            )

        return AIModelSchema(
            id=model.id,
            name=model.name,
            provider=model.provider,
            model_name=model.model_name,
            api_key_encrypted="***",
            base_url=model.base_url,
            model_type=model.model_type,
            is_active=model.is_active,
            test_results=model.test_results,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"切换AI模型状态失败: {str(e)}"
        )


@router.get("/providers")
async def get_available_providers() -> Any:
    """获取可用的AI模型提供商"""
    providers = [
        {
            "value": "openai",
            "label": "OpenAI",
            "models": ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]
        },
        {
            "value": "baidu",
            "label": "百度文心一言",
            "models": ["ernie-bot", "ernie-bot-turbo"]
        },
        {
            "value": "alibaba",
            "label": "阿里通义千问",
            "models": ["qwen-turbo", "qwen-plus", "qwen-max"]
        },
        {
            "value": "google",
            "label": "Google Gemini",
            "models": ["gemini-pro", "gemini-pro-vision"]
        },
        {
            "value": "anthropic",
            "label": "Anthropic Claude",
            "models": ["claude-3-sonnet", "claude-3-opus"]
        }
    ]

    return providers