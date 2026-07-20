"""
统一响应格式模块
所有接口返回格式：{code, message, data}
"""
from typing import Any, Optional
from fastapi.responses import JSONResponse


class ResponseModel:
    """统一响应构造器"""

    @staticmethod
    def success(data: Any = None, message: str = "操作成功", code: int = 0) -> dict:
        """
        成功响应
        :param data: 业务数据
        :param message: 提示信息
        :param code: 业务状态码，0 表示成功
        """
        return {
            "code": code,
            "message": message,
            "data": data,
        }

    @staticmethod
    def error(
        message: str = "操作失败",
        code: int = -1,
        data: Any = None,
        status_code: int = 200,
    ) -> JSONResponse:
        """
        错误响应（返回 JSONResponse 以支持自定义 HTTP 状态码）
        :param message: 错误信息
        :param code: 业务错误码，-1 表示通用错误
        :param data: 附加数据
        :param status_code: HTTP 状态码
        """
        return JSONResponse(
            status_code=status_code,
            content={
                "code": code,
                "message": message,
                "data": data,
            },
        )


# 便捷函数，供路由直接调用
def success(data: Any = None, message: str = "操作成功") -> dict:
    """快捷成功响应"""
    return ResponseModel.success(data=data, message=message)


def error(message: str = "操作失败", code: int = -1, status_code: int = 200) -> JSONResponse:
    """快捷错误响应"""
    return ResponseModel.error(message=message, code=code, status_code=status_code)