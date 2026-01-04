"""
LLM Configuration API Endpoints
Based on RAGFlow llm_app.py
Provides model configuration endpoints for the AI HR system
"""

import json
import logging
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, get_current_tenant_id_optional
from app.application.schemas.llm import (
    SetApiKeyRequest,
    AddLlmRequest,
    DeleteLlmRequest,
    EnableLlmRequest,
    UpdateTenantRequest,
    ApiResponse,
    LLMFactoryResponse,
    LlmListResponse,
    MyLlmResponse,
    LLMModelResponse,
    MyLlmValue,
    TenantLLMDetail,
    TenantInfoResponse,
)
from app.application.services.llm_service import (
    LLMFactoryService,
    LLMService,
    TenantLLMService,
    TenantService,
)

router = APIRouter()
logger = logging.getLogger(__name__)


# Helper function to create API response
def create_response(data: Any = None, code: int = 0, message: str = None) -> Dict:
    """创建统一格式的 API 响应"""
    response = {"code": code}
    if data is not None:
        response["data"] = data
    if message:
        response["message"] = message
    return response


@router.get("/factories", response_model=ApiResponse)
async def get_factories(
    db: AsyncSession = Depends(get_db),
):
    """
    获取支持的 LLM 厂商列表
    GET /api/v1/llm/factories
    """
    try:
        # 获取允许的厂商列表（排除内部厂商）
        fac = await LLMFactoryService.get_allowed_factories(
            db,
            exclude_names=["Youdao", "FastEmbed", "BAAI", "Builtin"]
        )

        # 获取所有 LLM 模型以确定每个厂商支持的模型类型
        llms = await LLMService.get_all(db, status="1")

        # 按厂商分组模型类型
        mdl_types: Dict[str, set] = {}
        for m in llms:
            if m.fid not in mdl_types:
                mdl_types[m.fid] = set()
            mdl_types[m.fid].add(m.model_type)

        # 构建响应
        factories = []
        for f in fac:
            factory_dict = {
                "name": f.name,
                "logo": f.logo or "",
                "tags": f.tags,
                "rank": f.rank,
                "status": f.status,
                "model_types": list(mdl_types.get(f.name, {
                    "chat", "embedding", "rerank",
                    "image2text", "speech2text", "tts", "ocr"
                }))
            }
            factories.append(factory_dict)

        return create_response(data=factories)

    except Exception as e:
        logger.error(f"获取厂商列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/set_api_key", response_model=ApiResponse)
async def set_api_key(
    request: SetApiKeyRequest,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id_optional),
):
    """
    设置 API Key（批量配置厂商模型）
    POST /api/v1/llm/set_api_key
    """
    try:
        factory = request.llm_factory

        # 获取该厂商的所有模型
        llms = await LLMService.get_all(db, fid=factory)

        if not llms:
            raise HTTPException(
                status_code=400,
                detail=f"未找到厂商 {factory} 的模型配置"
            )

        # TODO: 添加实际的 API Key 验证逻辑
        # 这里需要调用对应厂商的 API 进行验证
        # 暂时跳过验证，直接保存

        llm_config = {
            "api_key": request.api_key,
            "api_base": request.base_url or ""
        }

        if request.model_type:
            llm_config["model_type"] = request.model_type
        if request.llm_name:
            llm_config["llm_name"] = request.llm_name

        # 为该厂商的所有模型添加配置
        for llm in llms:
            # 如果指定了 model_type 或 llm_name，只配置匹配的模型
            if request.model_type and llm.model_type != request.model_type:
                continue
            if request.llm_name and llm.llm_name != request.llm_name:
                continue

            llm_config["max_tokens"] = llm.max_tokens or 8192

            # 为智谱AI设置默认的API Base URL
            api_base = request.base_url
            if factory == "ZHIPU-AI" and not api_base:
                api_base = "https://open.bigmodel.cn/api/paas/v4"

            await TenantLLMService.add_or_update_llm(
                db,
                tenant_id=tenant_id,
                llm_factory=factory,
                llm_name=llm.llm_name,
                model_type=llm.model_type,
                api_key=request.api_key,
                api_base=api_base,
                max_tokens=llm.max_tokens or 8192
            )

        return create_response(data=True)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"设置 API Key 失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/add_llm", response_model=ApiResponse)
async def add_llm(
    request: AddLlmRequest,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id_optional),
):
    """
    添加单个 LLM 配置
    POST /api/v1/llm/add_llm
    """
    try:
        factory = request.llm_factory
        api_key = request.api_key if isinstance(request.api_key, str) else "x"
        llm_name = request.llm_name

        # 检查厂商是否允许
        allowed_factories = await LLMFactoryService.get_allowed_factories(db)
        factory_names = [f.name for f in allowed_factories]

        if factory not in factory_names:
            raise HTTPException(
                status_code=400,
                detail=f"LLM 厂商 {factory} 不被允许"
            )

        # 根据厂商类型处理特殊的 API Key 格式
        if factory == "VolcEngine":
            api_key = json.dumps({
                "ark_api_key": request.ark_api_key or "",
                "endpoint_id": request.endpoint_id or ""
            })
        elif factory == "Tencent Hunyuan":
            api_key = json.dumps({
                "hunyuan_sid": request.hunyuan_sid or "",
                "hunyuan_sk": request.hunyuan_sk or ""
            })
        elif factory == "Tencent Cloud":
            api_key = json.dumps({
                "tencent_cloud_sid": request.tencent_cloud_sid or "",
                "tencent_cloud_sk": request.tencent_cloud_sk or ""
            })
        elif factory == "Bedrock":
            api_key = json.dumps({
                "auth_mode": request.auth_mode or "api_key",
                "bedrock_ak": request.bedrock_ak or "",
                "bedrock_sk": request.bedrock_sk or "",
                "bedrock_region": request.bedrock_region or "",
                "aws_role_arn": request.aws_role_arn or ""
            })
        elif factory == "LocalAI":
            llm_name += "___LocalAI"
        elif factory == "HuggingFace":
            llm_name += "___HuggingFace"
        elif factory == "OpenAI-API-Compatible":
            llm_name += "___OpenAI-API"
        elif factory == "VLLM":
            llm_name += "___VLLM"
        elif factory == "XunFei Spark":
            if request.model_type == "chat":
                api_key = request.spark_api_password or ""
            elif request.model_type == "tts":
                api_key = json.dumps({
                    "spark_app_id": request.spark_app_id or "",
                    "spark_api_secret": request.spark_api_secret or "",
                    "spark_api_key": request.spark_api_key or ""
                })
        elif factory == "BaiduYiyan":
            api_key = json.dumps({
                "yiyan_ak": request.yiyan_ak or "",
                "yiyan_sk": request.yiyan_sk or ""
            })
        elif factory == "Fish Audio":
            api_key = json.dumps({
                "fish_audio_ak": request.fish_audio_ak or "",
                "fish_audio_refid": request.fish_audio_refid or ""
            })
        elif factory == "Google Cloud":
            api_key = json.dumps({
                "google_project_id": request.google_project_id or "",
                "google_region": request.google_region or "",
                "google_service_account_key": request.google_service_account_key or ""
            })
        elif factory == "Azure-OpenAI":
            api_key = json.dumps({
                "api_key": api_key,
                "api_version": request.api_version or ""
            })
        elif factory == "OpenRouter":
            api_key = json.dumps({
                "api_key": api_key,
                "provider_order": request.provider_order or ""
            })
        elif factory == "MinerU":
            api_key = json.dumps({
                "mineru_backend": request.mineru_backend or "magic-pdf",
                "mineru_server_url": request.mineru_server_url or "",
                "mineru_delete_output": request.mineru_delete_output or True
            })

        # TODO: 添加实际的模型验证逻辑
        # 根据不同的 model_type 调用相应的验证 API

        # 为智谱AI设置默认的API Base URL
        api_base = request.api_base or ""
        if factory == "ZHIPU-AI" and not api_base:
            api_base = "https://open.bigmodel.cn/api/paas/v4"

        # 保存配置
        await TenantLLMService.add_or_update_llm(
            db,
            tenant_id=tenant_id,
            llm_factory=factory,
            llm_name=llm_name,
            model_type=request.model_type,
            api_key=api_key,
            api_base=api_base,
            max_tokens=request.max_tokens or 8192
        )

        return create_response(data=True)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"添加 LLM 失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/delete_llm", response_model=ApiResponse)
async def delete_llm(
    request: DeleteLlmRequest,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id_optional),
):
    """
    删除模型配置
    POST /api/v1/llm/delete_llm
    """
    try:
        success = await TenantLLMService.delete_llm(
            db,
            tenant_id=tenant_id,
            llm_factory=request.llm_factory,
            llm_name=request.llm_name or ""
        )

        if not success:
            raise HTTPException(
                status_code=404,
                detail="未找到指定的模型配置"
            )

        return create_response(data=True)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除 LLM 失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/enable_llm", response_model=ApiResponse)
async def enable_llm(
    request: EnableLlmRequest,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id_optional),
):
    """
    启用/禁用模型
    POST /api/v1/llm/enable_llm
    """
    try:
        success = await TenantLLMService.set_llm_status(
            db,
            tenant_id=tenant_id,
            llm_factory=request.llm_factory,
            llm_name=request.llm_name,
            status=request.status
        )

        if not success:
            raise HTTPException(
                status_code=404,
                detail="未找到指定的模型配置"
            )

        return create_response(data=True)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"设置 LLM 状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/delete_factory", response_model=ApiResponse)
async def delete_factory(
    request: DeleteLlmRequest,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id_optional),
):
    """
    删除整个厂商配置
    POST /api/v1/llm/delete_factory
    """
    try:
        count = await TenantLLMService.delete_factory(
            db,
            tenant_id=tenant_id,
            llm_factory=request.llm_factory
        )

        return create_response(data=True)

    except Exception as e:
        logger.error(f"删除厂商配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/my_llms", response_model=ApiResponse)
async def get_my_llms(
    include_details: bool = Query(False, description="是否返回详细信息"),
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id_optional),
):
    """
    获取我的模型列表
    GET /api/v1/llm/my_llms?include_details=true
    """
    try:
        if include_details:
            # 返回详细信息
            res = await TenantLLMService.get_my_llms_detailed(db, tenant_id)
        else:
            # 返回简化信息
            llms = await TenantLLMService.get_my_llms(db, tenant_id)

            # 按厂商分组
            res = {}
            for llm in llms:
                factory_name = llm["llm_factory"]
                if factory_name not in res:
                    res[factory_name] = {
                        "tags": llm["tags"],
                        "llm": []
                    }

                res[factory_name]["llm"].append({
                    "type": llm["model_type"],
                    "name": llm["llm_name"],
                    "used_token": llm["used_tokens"],
                    "status": llm["status"]
                })

        return create_response(data=res)

    except Exception as e:
        logger.error(f"获取我的模型列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list", response_model=ApiResponse)
async def list_llms(
    model_type: Optional[str] = Query(None, description="过滤模型类型"),
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id_optional),
):
    """
    获取可用模型列表
    GET /api/v1/llm/list?model_type=chat
    """
    try:
        # 自部署厂商列表（始终可用）
        self_deployed = ["FastEmbed", "Ollama", "Xinference", "LocalAI", "LM-Studio", "GPUStack"]

        # 获取租户已配置的模型
        tenant_llms = await TenantLLMService.get_my_llms(db, tenant_id)

        # 获取已配置的厂商集合
        facts = set(
            llm["llm_factory"]
            for llm in tenant_llms
            if llm["llm_factory"] and llm.get("status") == "1"
        )

        # 获取已配置的模型状态
        status = set(
            f"{llm['llm_name']}@{llm['llm_factory']}"
            for llm in tenant_llms
            if llm.get("status") == "1"
        )

        # 获取所有可用的模型元数据
        all_llms = await LLMService.get_all(db, status="1")

        # 过滤并标记可用性
        llms = []
        for m in all_llms:
            model_key = f"{m.llm_name}@{m.fid}"

            # 检查是否可用（已配置或自部署）
            is_available = (
                m.fid in facts or
                m.fid in self_deployed or
                model_key in status
            )

            llms.append({
                "llm_name": m.llm_name,
                "model_type": m.model_type,
                "fid": m.fid,
                "max_tokens": m.max_tokens,
                "available": is_available,
                "status": m.status,
                "tags": m.tags,
                "is_tools": m.is_tools
            })

        # 按模型类型过滤
        if model_type:
            llms = [m for m in llms if model_type in m["model_type"]]

        # 按厂商分组
        res = {}
        for m in llms:
            if m["fid"] not in res:
                res[m["fid"]] = []
            res[m["fid"]].append(m)

        return create_response(data=res)

    except Exception as e:
        logger.error(f"获取模型列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tenant_info", response_model=ApiResponse)
async def get_tenant_info(
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id_optional),
):
    """
    获取租户信息（系统模型设置）
    GET /api/v1/llm/tenant_info
    """
    try:
        from app.infrastructure.database.llm_models import Tenant

        tenant = await TenantService.get_by_id(db, tenant_id)

        if not tenant:
            # 租户不存在，自动创建（使用传入的 tenant_id）
            tenant = Tenant(
                id=tenant_id,
                name="租户",
                llm_id="gpt-3.5-turbo@OpenAI",
                embd_id="text-embedding-3-small@OpenAI",
                asr_id="whisper-1@OpenAI",
                img2txt_id="gpt-4o@OpenAI",
                rerank_id="bge-reranker-v2-m3@BAAI",
                tts_id="tts-1@OpenAI",
                credit=512,
                status="1"
            )
            db.add(tenant)
            await db.commit()
            await db.refresh(tenant)

        data = {
            "tenant_id": str(tenant.id),
            "name": tenant.name,
            "llm_id": tenant.llm_id,
            "embd_id": tenant.embd_id,
            "asr_id": tenant.asr_id,
            "img2txt_id": tenant.img2txt_id,
            "rerank_id": tenant.rerank_id,
            "tts_id": tenant.tts_id
        }

        return create_response(data=data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取租户信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/set_tenant_info", response_model=ApiResponse)
async def set_tenant_info(
    request: UpdateTenantRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    设置租户信息（系统模型设置）
    POST /api/v1/llm/set_tenant_info
    """
    try:
        tenant = await TenantService.update_default_models(
            db,
            tenant_id=request.tenant_id,
            llm_id=request.llm_id,
            embd_id=request.embd_id,
            asr_id=request.asr_id,
            img2txt_id=request.img2txt_id,
            rerank_id=request.rerank_id,
            tts_id=request.tts_id
        )

        if not tenant:
            raise HTTPException(
                status_code=404,
                detail="租户不存在"
            )

        return create_response(data=True)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"设置租户信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
