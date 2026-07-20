"""
JWT Token 处理模块
提供 Token 创建和解码功能
"""
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt, JWTError

from app.core.config import get_settings

settings = get_settings()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    创建 JWT Access Token
    :param data: 需要编码的数据（通常是 {"sub": user_id}）
    :param expires_delta: 自定义过期时间，为 None 则使用配置中的默认值
    :return: JWT Token 字符串
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """
    解码 JWT Token
    :param token: JWT Token 字符串
    :return: 解码后的 payload 字典，解码失败返回 None
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError:
        return None