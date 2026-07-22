"""
系统配置 Service 层
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.base_service import BaseService
from app.core.exceptions import NotFoundException, DuplicateException
from app.modules.sys_config.model import SysConfig


class SysConfigService(BaseService):
    """系统配置服务"""
    model = SysConfig

    @classmethod
    async def get_by_key(cls, db: AsyncSession, key: str) -> SysConfig | None:
        """根据 key 获取配置"""
        result = await db.execute(select(SysConfig).where(SysConfig.key == key))
        return result.scalar_one_or_none()

    @classmethod
    async def get_value(cls, db: AsyncSession, key: str, default: str = "") -> str:
        """根据 key 获取配置值，不存在则返回默认值"""
        config = await cls.get_by_key(db, key)
        return config.value if config else default

    @classmethod
    async def create_config(cls, db: AsyncSession, data: dict) -> SysConfig:
        """创建配置，检查 key 是否重复"""
        existing = await cls.get_by_key(db, data["key"])
        if existing:
            raise DuplicateException(f"配置键「{data['key']}」已存在")
        return await cls.create(db, data)

    @classmethod
    async def update_by_key(cls, db: AsyncSession, key: str, update_data: dict) -> SysConfig:
        """根据 key 更新配置"""
        config = await cls.get_by_key(db, key)
        if config is None:
            raise NotFoundException(f"配置键「{key}」不存在")
        for k, v in update_data.items():
            if v is not None:
                setattr(config, k, v)
        await db.flush()
        await db.refresh(config)
        return config