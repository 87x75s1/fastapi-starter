"""
日志配置模块
提供统一的日志格式和配置
"""
import logging
import sys
from app.core.config import get_settings

settings = get_settings()


def setup_logging():
    """
    配置应用日志
    - DEBUG 模式下输出 DEBUG 级别日志
    - 正式环境输出 INFO 级别日志
    - 统一格式：时间 | 级别 | 模块 | 消息
    """
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    # 日志格式
    log_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # 配置根日志记录器
    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )

    # 降低第三方库日志级别，减少噪音
    # uvicorn.access 保留 INFO，显示请求日志（如 "GET /api/user/login 200"）
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.DEBUG else logging.WARNING
    )

    logger = logging.getLogger("app")
    logger.info(f"日志系统初始化完成，级别: {logging.getLevelName(log_level)}")
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    获取指定名称的日志记录器
    :param name: 日志记录器名称（通常为模块名）
    :return: Logger 实例
    """
    return logging.getLogger(f"app.{name}")