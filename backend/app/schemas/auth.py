"""认证相关的数据模式"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator, ConfigDict


class UserBase(BaseModel):
    """用户基础信息"""
    username: str
    email: str
    role: Optional[str] = "user"

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        """验证邮箱格式 - 使用更宽松的规则"""
        if not v or '@' not in v:
            raise ValueError('邮箱格式不正确：必须包含 @ 符号')
        # 基本检查：确保@前后都有内容
        parts = v.split('@')
        if len(parts) != 2 or not parts[0] or not parts[1]:
            raise ValueError('邮箱格式不正确')
        return v


class UserCreate(UserBase):
    """创建用户"""
    password: str


class UserUpdate(BaseModel):
    """更新用户"""
    email: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """用户响应"""
    model_config = ConfigDict(from_attributes=True)

    id: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None


class UserLogin(BaseModel):
    """用户登录"""
    username: str
    password: str


class Token(BaseModel):
    """令牌响应"""
    access_token: str
    token_type: str
    expires_in: int


class TokenData(BaseModel):
    """令牌数据"""
    username: Optional[str] = None
    role: Optional[str] = None