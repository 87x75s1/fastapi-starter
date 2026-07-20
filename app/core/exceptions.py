"""
自定义业务异常模块
提供统一的业务异常类，配合全局异常处理器使用
"""
from fastapi import HTTPException, status


class BusinessException(Exception):
    """
    自定义业务异常基类
    用于在 Service 层抛出业务逻辑错误，由全局异常处理器统一捕获
    """

    def __init__(self, message: str = "操作失败", code: int = -1):
        self.message = message
        self.code = code
        super().__init__(self.message)


class NotFoundException(BusinessException):
    """资源不存在异常"""

    def __init__(self, message: str = "资源不存在"):
        super().__init__(message=message, code=404)


class UnauthorizedException(BusinessException):
    """未授权异常"""

    def __init__(self, message: str = "未授权，请先登录"):
        super().__init__(message=message, code=401)


class ForbiddenException(BusinessException):
    """禁止访问异常"""

    def __init__(self, message: str = "禁止访问"):
        super().__init__(message=message, code=403)


class DuplicateException(BusinessException):
    """重复资源异常（如手机号已注册）"""

    def __init__(self, message: str = "资源已存在"):
        super().__init__(message=message, code=409)