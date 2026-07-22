"""
FastAPI 应用入口
- 注册路由
- 全局异常捕获
- 启动时自动建表和创建 uploads 目录
- 挂载静态文件路由
"""
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.database import create_tables
from app.core.exceptions import BusinessException
from app.core.response import success, error
from app.core.logging import setup_logging

# 导入模块路由
from app.modules.user.router import router as user_router
from app.modules.upload.router import router as upload_router
from app.modules.product.router import router as product_router
from app.modules.order.router import router as order_router
from app.modules.address.router import router as address_router
from app.modules.feedback.router import router as feedback_router
from app.modules.sys_config.router import router as sys_config_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动时执行"""
    # 初始化日志
    setup_logging()

    # 创建上传目录（必须在 mount 静态文件之前）
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)

    # 挂载静态文件（放在 lifespan 中确保目录已创建）
    app.mount(
        settings.UPLOAD_URL_PREFIX,
        StaticFiles(directory=settings.UPLOAD_DIR),
        name="static",
    )

    # 自动创建所有数据库表
    await create_tables()

    print(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} 启动成功！")
    print(f"📖 接口文档：http://127.0.0.1:8000/docs")

    yield


# 创建 FastAPI 应用实例
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="面向个人开发者的万能小程序后台模板",
    lifespan=lifespan,
)


# ========== CORS 中间件（小程序前端跨域支持）==========

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应替换为具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========== 全局异常处理 ==========

@app.exception_handler(BusinessException)
async def business_exception_handler(request: Request, exc: BusinessException):
    """自定义业务异常全局捕获"""
    return JSONResponse(
        status_code=200,
        content={
            "code": exc.code,
            "message": exc.message,
            "data": None,
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """未知异常全局捕获，防止 500 错误暴露内部信息"""
    return JSONResponse(
        status_code=500,
        content={
            "code": -1,
            "message": "服务器内部错误" if not settings.DEBUG else str(exc),
            "data": None,
        },
    )


# ========== 注册路由 ==========

app.include_router(user_router)
app.include_router(upload_router)
app.include_router(product_router)
app.include_router(order_router)
app.include_router(address_router)
app.include_router(feedback_router)
app.include_router(sys_config_router)


# ========== 健康检查 ==========

@app.get("/", tags=["系统"], summary="健康检查")
@app.get("/health", tags=["系统"], summary="健康检查")
async def health_check():
    """服务健康检查接口"""
    return success(data={"status": "ok", "version": settings.APP_VERSION}, message="服务运行正常")