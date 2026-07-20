"""
通用依赖模块
提供 get_current_user 等常用 FastAPI 依赖
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.jwt_handler import decode_token

# HTTP Bearer Token 提取器
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    """
    获取当前登录用户（依赖注入）
    从 Authorization: Bearer <token> 中解析用户
    :raises HTTPException: Token 无效或用户不存在/已禁用

    注意：此依赖通过延迟导入 User 模型来避免 core 层对 modules 层的硬依赖。
    在应用启动后（路由注册完成），模块已加载，延迟导入不会失败。
    """
    token = credentials.credentials
    payload = decode_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token 无效或已过期",
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token 中缺少用户信息",
        )

    # 延迟导入，避免 core 层对 modules 层的硬依赖
    from app.modules.user.model import User

    # 查询用户
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
        )

    if user.status == 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用",
        )

    return user