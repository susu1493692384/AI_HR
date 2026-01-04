"""AI模型相关的Pydantic模式"""

from datetime import datetime
from typing import Any, Dict, Optional, List
from pydantic import BaseModel, Field, ConfigDict, EmailStr

from app.domain.entities.ai_model import AIModelProvider, AIModelType


class AIModelBase(BaseModel):
    """AI模型基础模式"""
    name: str = Field(..., min_length=1, max_length=255, description="配置名称")
    provider: AIModelProvider = Field(..., description="模型提供商")
    model_name: str = Field(..., min_length=1, max_length=255, description="模型名称")
    base_url: Optional[str] = Field(None, description="API基础URL")
    model_type: AIModelType = Field(..., description="模型类型")
    is_active: bool = Field(default=False, description="是否激活")


class AIModelCreate(AIModelBase):
    """创建AI模型模式"""
    api_key: str = Field(..., min_length=10, description="API密钥")
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0, description="Temperature参数")
    max_tokens: Optional[int] = Field(2000, ge=1, le=8000, description="最大Token数")


class AIModelUpdate(BaseModel):
    """更新AI模型模式"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    api_key: Optional[str] = Field(None, min_length=10)
    base_url: Optional[str] = None
    model_name: Optional[str] = Field(None, min_length=1, max_length=255)
    model_type: Optional[AIModelType] = None
    is_active: Optional[bool] = None
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None, ge=1, le=8000)


class AIModel(AIModelBase):
    """AI模型完整模式"""
    model_config = ConfigDict(from_attributes=True)

    id: str
    api_key_encrypted: str
    test_results: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class ModelTestRequest(BaseModel):
    """模型测试请求模式"""
    test_prompt: str = Field(
        default="你好，请回复一个简单的问候。",
        description="测试提示词"
    )


class ModelTestResponse(BaseModel):
    """模型测试响应模式"""
    success: bool
    response_time: Optional[float] = Field(None, description="响应时间（毫秒）")
    error_message: Optional[str] = Field(None, description="错误信息")
    test_prompt: str
    test_response: Optional[str] = Field(None, description="模型响应")
    tested_at: datetime = Field(default_factory=datetime.utcnow)


class AIModelProvider(BaseModel):
    """AI模型提供商模式"""
    value: str
    label: str
    models: List[str]


class ModelConfig(BaseModel):
    """模型配置模式"""
    provider: AIModelProvider
    model: str
    temperature: float = 0.7
    max_tokens: int = 2000
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0


class ModelCapabilities(BaseModel):
    """模型能力模式"""
    supports_chat: bool = True
    supports_completion: bool = False
    supports_embedding: bool = False
    supports_vision: bool = False
    max_input_tokens: Optional[int] = None
    max_output_tokens: Optional[int] = None


class ModelUsageStats(BaseModel):
    """模型使用统计模式"""
    total_requests: int = 0
    total_tokens: int = 0
    success_rate: float = 0.0
    avg_response_time: float = 0.0
    last_used: Optional[datetime] = None