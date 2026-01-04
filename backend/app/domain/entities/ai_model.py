"""AI模型领域实体"""

from enum import Enum
from typing import Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass
import uuid


class AIModelProvider(str, Enum):
    """AI模型提供商枚举"""
    OPENAI = "openai"
    BAIDU = "baidu"
    ALIBABA = "alibaba"
    GOOGLE = "google"
    ANTHROPIC = "anthropic"
    CUSTOM = "custom"


class AIModelType(str, Enum):
    """AI模型类型枚举"""
    CHAT = "chat"
    COMPLETION = "completion"
    EMBEDDING = "embedding"


class ModelTestStatus(str, Enum):
    """模型测试状态枚举"""
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"


@dataclass
class ModelTestResult:
    """模型测试结果值对象"""
    status: ModelTestStatus
    response_time: Optional[float] = None  # 响应时间（毫秒）
    error_message: Optional[str] = None
    test_prompt: str = ""
    test_response: Optional[str] = None
    tested_at: datetime = None

    def __post_init__(self):
        if self.tested_at is None:
            self.tested_at = datetime.utcnow()


@dataclass
class ModelConfig:
    """模型配置值对象"""
    temperature: float = 0.7
    max_tokens: int = 2000
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0

    def validate(self) -> bool:
        """验证配置参数"""
        return (
            0.0 <= self.temperature <= 2.0 and
            self.max_tokens > 0 and
            0.0 <= self.top_p <= 1.0 and
            -2.0 <= self.frequency_penalty <= 2.0 and
            -2.0 <= self.presence_penalty <= 2.0
        )


@dataclass
class ModelCapabilities:
    """模型能力值对象"""
    supports_chat: bool = False
    supports_completion: bool = False
    supports_embedding: bool = False
    supports_vision: bool = False
    supports_function_calling: bool = False
    max_input_tokens: Optional[int] = None
    max_output_tokens: Optional[int] = None
    cost_per_input_token: Optional[float] = None
    cost_per_output_token: Optional[float] = None


class AIModel:
    """AI模型聚合根"""

    def __init__(
        self,
        name: str,
        provider: AIModelProvider,
        model_name: str,
        api_key: str,
        model_type: AIModelType,
        base_url: Optional[str] = None,
        config: Optional[ModelConfig] = None,
        id: Optional[str] = None
    ):
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.provider = provider
        self.model_name = model_name
        self.api_key_encrypted = self._encrypt_api_key(api_key)
        self.base_url = base_url
        self.model_type = model_type
        self.config = config or ModelConfig()
        self.is_active = False
        self.test_results: Optional[ModelTestResult] = None
        self.capabilities = self._get_default_capabilities()
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def _encrypt_api_key(self, api_key: str) -> str:
        """加密API密钥（简化实现，生产环境需要使用更安全的加密方式）"""
        # TODO: 实现真实的加密逻辑
        return f"encrypted_{api_key}"

    def _decrypt_api_key(self) -> str:
        """解密API密钥"""
        # TODO: 实现真实的解密逻辑
        if self.api_key_encrypted.startswith("encrypted_"):
            return self.api_key_encrypted[10:]
        return self.api_key_encrypted

    def _get_default_capabilities(self) -> ModelCapabilities:
        """获取默认模型能力"""
        capabilities = ModelCapabilities()

        if self.provider == AIModelProvider.OPENAI:
            if "gpt-4" in self.model_name.lower():
                capabilities.supports_chat = True
                capabilities.supports_completion = True
                capabilities.supports_vision = "vision" in self.model_name.lower()
                capabilities.supports_function_calling = True
                capabilities.max_input_tokens = 128000
                capabilities.max_output_tokens = 4096
            elif "gpt-3.5" in self.model_name.lower():
                capabilities.supports_chat = True
                capabilities.supports_completion = True
                capabilities.supports_function_calling = True
                capabilities.max_input_tokens = 16385
                capabilities.max_output_tokens = 4096

        elif self.provider == AIModelProvider.BAIDU:
            capabilities.supports_chat = True
            capabilities.max_input_tokens = 128000

        elif self.provider == AIModelProvider.ALIBABA:
            capabilities.supports_chat = True
            capabilities.supports_completion = True
            capabilities.max_input_tokens = 30000

        elif self.provider == AIModelProvider.GOOGLE:
            capabilities.supports_chat = True
            capabilities.supports_vision = "vision" in self.model_name.lower()
            capabilities.max_input_tokens = 32768

        elif self.provider == AIModelProvider.ANTHROPIC:
            capabilities.supports_chat = True
            capabilities.max_input_tokens = 200000

        return capabilities

    def activate(self):
        """激活模型"""
        if self.test_results and self.test_results.status == ModelTestStatus.SUCCESS:
            self.is_active = True
            self.updated_at = datetime.utcnow()
        else:
            raise ValueError("只有测试成功的模型才能激活")

    def deactivate(self):
        """停用模型"""
        self.is_active = False
        self.updated_at = datetime.utcnow()

    def update_test_result(self, result: ModelTestResult):
        """更新测试结果"""
        self.test_results = result
        self.updated_at = datetime.utcnow()

    def update_config(self, config: ModelConfig):
        """更新模型配置"""
        if not config.validate():
            raise ValueError("无效的模型配置参数")

        self.config = config
        self.updated_at = datetime.utcnow()

    def update_api_key(self, api_key: str):
        """更新API密钥"""
        self.api_key_encrypted = self._encrypt_api_key(api_key)
        self.is_active = False  # 更新密钥后需要重新测试
        self.test_results = None
        self.updated_at = datetime.utcnow()

    def can_be_used_for_chat(self) -> bool:
        """是否可以用于对话"""
        return (
            self.is_active and
            self.capabilities.supports_chat and
            self.model_type == AIModelType.CHAT
        )

    def can_be_used_for_completion(self) -> bool:
        """是否可以用于文本补全"""
        return (
            self.is_active and
            self.capabilities.supports_completion and
            self.model_type == AIModelType.COMPLETION
        )

    def can_be_used_for_embedding(self) -> bool:
        """是否可以用于文本嵌入"""
        return (
            self.is_active and
            self.capabilities.supports_embedding and
            self.model_type == AIModelType.EMBEDDING
        )

    def get_api_key(self) -> str:
        """获取解密后的API密钥"""
        return self._decrypt_api_key()

    def is_healthy(self) -> bool:
        """检查模型是否健康"""
        if not self.test_results:
            return False

        # 检查测试结果是否过期（24小时）
        time_diff = datetime.utcnow() - self.test_results.tested_at
        if time_diff.total_seconds() > 24 * 3600:
            return False

        return (
            self.test_results.status == ModelTestStatus.SUCCESS and
            self.is_active
        )

    def get_cost_estimate(self, input_tokens: int, output_tokens: int) -> Optional[float]:
        """估算使用成本"""
        if not self.capabilities.cost_per_input_token or not self.capabilities.cost_per_output_token:
            return None

        return (
            input_tokens * self.capabilities.cost_per_input_token +
            output_tokens * self.capabilities.cost_per_output_token
        )

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "id": self.id,
            "name": self.name,
            "provider": self.provider.value,
            "model_name": self.model_name,
            "api_key_encrypted": self.api_key_encrypted,
            "base_url": self.base_url,
            "model_type": self.model_type.value,
            "config": self.config.__dict__,
            "is_active": self.is_active,
            "test_results": self.test_results.__dict__ if self.test_results else None,
            "capabilities": self.capabilities.__dict__,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }