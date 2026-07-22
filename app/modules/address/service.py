"""
地址 Service 层
"""
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.base_service import BaseService
from app.core.exceptions import NotFoundException
from app.modules.address.model import Address


class AddressService(BaseService):
    """地址服务"""
    model = Address

    @classmethod
    async def get_user_addresses(cls, db: AsyncSession, user_id: int) -> list[Address]:
        """获取用户所有地址（默认地址排前面）"""
        result = await db.execute(
            select(Address)
            .where(Address.user_id == user_id)
            .order_by(Address.is_default.desc(), Address.created_at.desc())
        )
        return result.scalars().all()

    @classmethod
    async def create_address(cls, db: AsyncSession, user_id: int, data: dict) -> Address:
        """创建地址，如果是默认地址则取消其他默认"""
        if data.get("is_default") == 1:
            await cls._clear_default(db, user_id)
        data["user_id"] = user_id
        return await cls.create(db, data)

    @classmethod
    async def update_address(cls, db: AsyncSession, address_id: int, user_id: int,
                              update_data: dict) -> Address:
        """更新地址"""
        address = await cls.get_by_id(db, address_id)
        if address is None or address.user_id != user_id:
            raise NotFoundException("地址不存在")

        # 如果设为默认，先取消其他默认
        if update_data.get("is_default") == 1:
            await cls._clear_default(db, user_id)

        updated = await cls.update(db, address_id, update_data)
        return updated

    @classmethod
    async def set_default(cls, db: AsyncSession, address_id: int, user_id: int) -> Address:
        """设置默认地址"""
        address = await cls.get_by_id(db, address_id)
        if address is None or address.user_id != user_id:
            raise NotFoundException("地址不存在")
        await cls._clear_default(db, user_id)
        address.is_default = 1
        await db.flush()
        await db.refresh(address)
        return address

    @classmethod
    async def _clear_default(cls, db: AsyncSession, user_id: int):
        """取消用户所有默认地址"""
        await db.execute(
            update(Address).where(Address.user_id == user_id, Address.is_default == 1)
            .values(is_default=0)
        )
        await db.flush()