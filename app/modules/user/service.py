"""
用户 Service 层
继承 BaseService，实现注册、登录等业务逻辑
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.base_service import BaseService
from app.core.jwt_handler import create_access_token
from app.core.exceptions import DuplicateException, UnauthorizedException
from app.modules.user.model import User
from app.utils.common import hash_password, verify_password


class UserService(BaseService):
    """用户服务，继承 BaseService 获得通用 CRUD"""
    model = User

    @classmethod
    async def get_by_phone(cls, db: AsyncSession, phone: str) -> User | None:
        """
        根据手机号查询用户
        :param db: 异步数据库会话
        :param phone: 手机号
        :return: 用户实例或 None
        """
        result = await db.execute(select(User).where(User.phone == phone))
        return result.scalar_one_or_none()

    @classmethod
    async def register(cls, db: AsyncSession, phone: str, password: str) -> User:
        """
        用户注册
        :param db: 异步数据库会话
        :param phone: 手机号
        :param password: 明文密码
        :return: 新创建的用户实例
        :raises DuplicateException: 手机号已注册
        """
        # 检查手机号是否已注册
        existing = await cls.get_by_phone(db, phone)
        if existing:
            raise DuplicateException("该手机号已注册")

        # 密码哈希后存储
        hashed_pwd = hash_password(password)
        user_data = {
            "phone": phone,
            "password": hashed_pwd,
        }

        # 自动设为管理员
        from app.core.init_data import ADMIN_PHONE
        if phone == ADMIN_PHONE:
            user_data["role"] = 1

        user = await cls.create(db, user_data)
        return user

    @classmethod
    async def login(cls, db: AsyncSession, phone: str, password: str) -> dict:
        """
        用户登录
        :param db: 异步数据库会话
        :param phone: 手机号
        :param password: 明文密码
        :return: {"token": ..., "user": User实例}
        :raises UnauthorizedException: 手机号未注册或密码错误
        """
        # 查询用户
        user = await cls.get_by_phone(db, phone)
        if user is None:
            raise UnauthorizedException("手机号未注册")

        # 校验密码
        if not verify_password(password, user.password):
            raise UnauthorizedException("密码错误")

        # 检查用户状态
        if user.status == 0:
            raise UnauthorizedException("用户已被禁用")

        # 生成 JWT Token
        token = create_access_token(data={"sub": str(user.id)})

        return {
            "token": token,
            "user": user,
        }