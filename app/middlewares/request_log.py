"""
请求日志中间件
打印每个 API 请求的方法、路径、状态码和耗时，方便开发调试
"""
import time
import logging

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("app.request")


class RequestLogMiddleware(BaseHTTPMiddleware):
    """请求日志中间件：记录每个请求的方法、路径、状态码、耗时"""

    async def dispatch(self, request: Request, call_next) -> Response:
        # 跳过静态文件和 docs 等非 API 路径
        path = request.url.path
        if path.startswith("/static") or path in ("/docs", "/redoc", "/openapi.json"):
            return await call_next(request)

        start = time.time()
        method = request.method

        try:
            response = await call_next(request)
            elapsed = (time.time() - start) * 1000
            status = response.status_code

            # 根据状态码选择日志级别
            if status < 400:
                log_func = logger.info
            elif status < 500:
                log_func = logger.warning
            else:
                log_func = logger.error

            log_func(f"{method} {path} -> {status} ({elapsed:.0f}ms)")
            return response

        except Exception as exc:
            elapsed = (time.time() - start) * 1000
            logger.error(f"{method} {path} -> 500 ({elapsed:.0f}ms) 异常: {exc}")
            raise