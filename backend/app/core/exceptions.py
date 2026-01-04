"""自定义异常处理"""

from typing import Any, Dict, Optional, Union
from fastapi import HTTPException, status


class CustomException(HTTPException):
    """自定义异常基类"""

    def __init__(
        self,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        detail: Any = None,
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class NotFoundException(CustomException):
    """资源未找到异常"""

    def __init__(self, detail: str = "资源不存在"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class BadRequestException(CustomException):
    """请求参数错误异常"""

    def __init__(self, detail: str = "请求参数错误"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class UnauthorizedException(CustomException):
    """未授权访问异常"""

    def __init__(self, detail: str = "未授权访问"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class ForbiddenException(CustomException):
    """权限不足异常"""

    def __init__(self, detail: str = "权限不足"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class ConflictException(CustomException):
    """资源冲突异常"""

    def __init__(self, detail: str = "资源冲突"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class UnprocessableEntityException(CustomException):
    """无法处理的实体异常"""

    def __init__(self, detail: str = "无法处理的实体"):
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)


class InternalServerException(CustomException):
    """服务器内部错误异常"""

    def __init__(self, detail: str = "服务器内部错误"):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)


class FileUploadException(CustomException):
    """文件上传异常"""

    def __init__(self, detail: str = "文件上传失败"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class AIServiceException(CustomException):
    """AI服务异常"""

    def __init__(self, detail: str = "AI服务调用失败"):
        super().__init__(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=detail)


class RAGFlowException(CustomException):
    """RAGFlow服务异常"""

    def __init__(self, detail: str = "RAGFlow服务调用失败"):
        super().__init__(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=detail)