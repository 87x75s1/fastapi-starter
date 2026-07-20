"""
全局配置模块 - 使用 Pydantic Settings 读取 .env 环境变量
所有敏感信息（数据库、密钥）统一在此管理
"""
from pydantic import computed_field
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置类，字段与 .env 文件中的变量一一对应"""

    # 应用基础配置
    APP_NAME: str = "FastAPI 小程序后台"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # 数据库配置（默认 SQLite，可无缝切换 MySQL）
    DATABASE_URL: str = "sqlite+aiosqlite:///./app.db"

    # JWT 配置
    JWT_SECRET_KEY: str = "change-me-to-a-very-long-random-secret-key"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 默认7天

    # 文件上传配置
    UPLOAD_DIR: str = "./uploads"
    UPLOAD_URL_PREFIX: str = "/static"
    # 允许的图片扩展名（逗号分隔字符串，通过计算属性转为 set）
    ALLOWED_EXTENSIONS_STR: str = ".jpg,.jpeg,.png,.gif,.webp"
    # 单文件最大尺寸（字节），默认 5MB
    MAX_FILE_SIZE: int = 5 * 1024 * 1024

    @computed_field
    @property
    def ALLOWED_EXTENSIONS(self) -> set[str]:
        """将逗号分隔的字符串转为 set"""
        return {ext.strip() for ext in self.ALLOWED_EXTENSIONS_STR.split(",") if ext.strip()}

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


@lru_cache()
def get_settings() -> Settings:
    """获取全局配置单例（带缓存）"""
    return Settings()