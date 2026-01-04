"""
LLM Configuration Schemas
Request and response schemas for LLM model configuration
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime


# ============ Response Schemas ============

class LLMFactoryResponse(BaseModel):
    """LLM 厂商响应"""
    name: str
    logo: str = ""
    tags: str
    rank: int = 0
    status: str = "1"
    model_types: List[str] = []

    class Config:
        from_attributes = True


class LLMModelResponse(BaseModel):
    """LLM 模型响应"""
    fid: str
    llm_name: str
    model_type: str
    max_tokens: int = 0
    available: bool = False
    status: str = "1"
    tags: str = ""
    is_tools: bool = False

    class Config:
        from_attributes = True


class TenantLLMDetail(BaseModel):
    """租户 LLM 详情"""
    type: str
    name: str
    used_token: int = 0
    api_base: str = ""
    max_tokens: int = 8192
    status: str = "1"


class MyLlmValue(BaseModel):
    """我的 LLM 值"""
    tags: str
    llm: List[TenantLLMDetail]


class TenantInfoResponse(BaseModel):
    """租户信息响应"""
    tenant_id: str
    name: Optional[str] = None
    llm_id: Optional[str] = None
    embd_id: Optional[str] = None
    asr_id: Optional[str] = None
    img2txt_id: Optional[str] = None
    rerank_id: Optional[str] = None
    tts_id: Optional[str] = None

    class Config:
        from_attributes = True


# ============ Request Schemas ============

class SetApiKeyRequest(BaseModel):
    """设置 API Key 请求"""
    llm_factory: str = Field(..., description="厂商名称")
    api_key: str = Field(..., description="API Key")
    base_url: Optional[str] = Field(None, description="API Base URL")
    model_type: Optional[str] = Field(None, description="模型类型")
    llm_name: Optional[str] = Field(None, description="模型名称")


class AddLlmRequest(BaseModel):
    """添加 LLM 请求"""
    llm_factory: str = Field(..., description="厂商名称")
    llm_name: str = Field(..., description="模型名称")
    model_type: str = Field(..., description="模型类型: chat, embedding, image2text, speech2text, rerank, tts, ocr")
    api_base: Optional[str] = Field(None, description="API Base URL")
    api_key: Union[str, Dict[str, Any]] = Field(..., description="API Key 或配置对象")
    max_tokens: Optional[int] = Field(None, description="最大 Token 数")

    # 特殊厂商字段
    # Azure OpenAI
    api_version: Optional[str] = None
    # VolcEngine
    ark_api_key: Optional[str] = None
    endpoint_id: Optional[str] = None
    # Bedrock
    auth_mode: Optional[str] = None
    bedrock_ak: Optional[str] = None
    bedrock_sk: Optional[str] = None
    bedrock_region: Optional[str] = None
    aws_role_arn: Optional[str] = None
    # Google Cloud
    google_project_id: Optional[str] = None
    google_region: Optional[str] = None
    google_service_account_key: Optional[str] = None
    # OpenRouter
    provider_order: Optional[str] = None
    # XunFei Spark
    spark_api_password: Optional[str] = None
    spark_app_id: Optional[str] = None
    spark_api_secret: Optional[str] = None
    spark_api_key: Optional[str] = None
    # Baidu Yiyan
    yiyan_ak: Optional[str] = None
    yiyan_sk: Optional[str] = None
    # Fish Audio
    fish_audio_ak: Optional[str] = None
    fish_audio_refid: Optional[str] = None
    # Tencent Hunyuan
    hunyuan_sid: Optional[str] = None
    hunyuan_sk: Optional[str] = None
    # Tencent Cloud
    tencent_cloud_sid: Optional[str] = None
    tencent_cloud_sk: Optional[str] = None
    # MinerU
    mineru_backend: Optional[str] = None
    mineru_server_url: Optional[str] = None
    mineru_delete_output: Optional[bool] = None


class DeleteLlmRequest(BaseModel):
    """删除 LLM 请求"""
    llm_factory: str = Field(..., description="厂商名称")
    llm_name: Optional[str] = Field(None, description="模型名称")


class EnableLlmRequest(BaseModel):
    """启用/禁用 LLM 请求"""
    llm_factory: str = Field(..., description="厂商名称")
    llm_name: str = Field(..., description="模型名称")
    status: str = Field(..., description="状态: 1=启用, 0=禁用")


class UpdateTenantRequest(BaseModel):
    """更新租户请求"""
    tenant_id: str = Field(..., description="租户 ID")
    name: Optional[str] = None
    llm_id: Optional[str] = None
    embd_id: Optional[str] = None
    asr_id: Optional[str] = None
    img2txt_id: Optional[str] = None
    rerank_id: Optional[str] = None
    tts_id: Optional[str] = None


# ============ Common Response Schemas ============

class ApiResponse(BaseModel):
    """API 响应基类"""
    code: int = 0
    data: Any = None
    message: Optional[str] = None


class LlmListResponse(BaseModel):
    """LLM 列表响应"""
    OpenAI: Optional[List[LLMModelResponse]] = None
    Anthropic: Optional[List[LLMModelResponse]] = None
    Azure_OpenAI: Optional[List[LLMModelResponse]] = None
    Google_Cloud: Optional[List[LLMModelResponse]] = None
    Ollama: Optional[List[LLMModelResponse]] = None
    Xinference: Optional[List[LLMModelResponse]] = None
    LocalAI: Optional[List[LLMModelResponse]] = None
    LM_Studio: Optional[List[LLMModelResponse]] = None
    HuggingFace: Optional[List[LLMModelResponse]] = None
    VolcEngine: Optional[List[LLMModelResponse]] = None
    Tongyi_Qianwen: Optional[List[LLMModelResponse]] = None
    Moonshot: Optional[List[LLMModelResponse]] = None
    ZHIPU_AI: Optional[List[LLMModelResponse]] = None
    DeepSeek: Optional[List[LLMModelResponse]] = None
    Minimax: Optional[List[LLMModelResponse]] = None
    Tencent_Hunyuan: Optional[List[LLMModelResponse]] = None
    Tencent_Cloud: Optional[List[LLMModelResponse]] = None
    XunFei_Spark: Optional[List[LLMModelResponse]] = None
    BaiduYiyan: Optional[List[LLMModelResponse]] = None
    Fish_Audio: Optional[List[LLMModelResponse]] = None
    Youdao: Optional[List[LLMModelResponse]] = None
    BAAI: Optional[List[LLMModelResponse]] = None
    OpenRouter: Optional[List[LLMModelResponse]] = None
    MinerU: Optional[List[LLMModelResponse]] = None
    Bedrock: Optional[List[LLMModelResponse]] = None
    Gemini: Optional[List[LLMModelResponse]] = None
    Mistral: Optional[List[LLMModelResponse]] = None


class MyLlmResponse(BaseModel):
    """我的 LLM 响应"""
    OpenAI: Optional[MyLlmValue] = None
    Anthropic: Optional[MyLlmValue] = None
    Azure_OpenAI: Optional[MyLlmValue] = None
    Google_Cloud: Optional[MyLlmValue] = None
    Ollama: Optional[MyLlmValue] = None
    Xinference: Optional[MyLlmValue] = None
    LocalAI: Optional[MyLlmValue] = None
    LM_Studio: Optional[MyLlmValue] = None
    HuggingFace: Optional[MyLlmValue] = None
    VolcEngine: Optional[MyLlmValue] = None
    Tongyi_Qianwen: Optional[MyLlmValue] = None
    Moonshot: Optional[MyLlmValue] = None
    ZHIPU_AI: Optional[MyLlmValue] = None
    DeepSeek: Optional[MyLlmValue] = None
    Minimax: Optional[MyLlmValue] = None
    Tencent_Hunyuan: Optional[MyLlmValue] = None
    Tencent_Cloud: Optional[MyLlmValue] = None
    XunFei_Spark: Optional[MyLlmValue] = None
    BaiduYiyan: Optional[MyLlmValue] = None
    Fish_Audio: Optional[MyLlmValue] = None
    Youdao: Optional[MyLlmValue] = None
    BAAI: Optional[MyLlmValue] = None
    OpenRouter: Optional[MyLlmValue] = None
    MinerU: Optional[MyLlmValue] = None
    Bedrock: Optional[MyLlmValue] = None
    Gemini: Optional[MyLlmValue] = None
    Mistral: Optional[MyLlmValue] = None
