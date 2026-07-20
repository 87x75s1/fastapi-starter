"""
通用 Service 基类 - 泛型 BaseService
封装通用的 CRUD 方法，所有业务 Service 继承此类即可复用
"""
from typing import TypeVar, Type, Optional, Any, Sequence, Dict
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base

# 泛型类型变量，约束为 Base 子类（即 ORM 模型）
ModelType = TypeVar("ModelType", bound=Base)


class BaseService:
    """
    泛型 Service 基类，提供通用 CRUD 操作
    子类需设置 model 属性为对应的 ORM 模型类

    用法示例：
        class UserService(BaseService):
            model = User
    """

    model: Type[Base] = None  # 子类必须覆盖此属性

    @classmethod
    async def get_by_id(cls, db: AsyncSession, id: int) -> Optional[ModelType]:
        """
        根据 ID 获取单条记录
        :param db: 异步数据库会话
        :param id: 主键 ID
        :return: 模型实例或 None
        """
        result = await db.execute(select(cls.model).where(cls.model.id == id))
        return result.scalar_one_or_none()

    @classmethod
    async def get_count(cls, db: AsyncSession) -> int:
        """
        获取记录总数
        :param db: 异步数据库会话
        :return: 记录总数
        """
        result = await db.execute(select(func.count()).select_from(cls.model))
        return result.scalar_one()

    @classmethod
    async def get_list(
        cls,
        db: AsyncSession,
        offset: int = 0,
        limit: int = 20,
    ) -> Dict[str, Any]:
        """
        获取分页列表（含分页元数据）
        :param db: 异步数据库会话
        :param offset: 偏移量
        :param limit: 每页数量
        :return: {"items": 列表, "total": 总数, "page": 当前页, "page_size": 每页数量, "total_pages": 总页数}
        """
        # 查询总数
        total = await cls.get_count(db)

        # 查询数据
        result = await db.execute(
            select(cls.model).offset(offset).limit(limit)
        )
        items = result.scalars().all()

        # 计算分页信息
        page = (offset // limit) + 1 if limit > 0 else 1
        total_pages = (total + limit - 1) // limit if limit > 0 else 0

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": limit,
            "total_pages": total_pages,
        }

    @classmethod
    async def create(cls, db: AsyncSession, obj_data: dict) -> ModelType:
        """
        创建新记录
        :param db: 异步数据库会话
        :param obj_data: 字典形式的数据
        :return: 新建的模型实例
        """
        obj = cls.model(**obj_data)
        db.add(obj)
        await db.flush()
        await db.refresh(obj)
        return obj

    @classmethod
    async def update(cls, db: AsyncSession, id: int, update_data: dict, exclude_unset: bool = True) -> Optional[ModelType]:
        """
        根据 ID 更新记录
        :param db: 异步数据库会话
        :param id: 主键 ID
        :param update_data: 需要更新的字段字典
        :param exclude_unset: 是否排除值为 None 的字段（默认 True，兼容旧行为）；
                              设为 False 时允许将字段更新为 None
        :return: 更新后的模型实例或 None
        """
        obj = await cls.get_by_id(db, id)
        if obj is None:
            return None
        for key, value in update_data.items():
            if exclude_unset and value is None:
                continue
            setattr(obj, key, value)
        await db.flush()
        await db.refresh(obj)
        return obj

    @classmethod
    async def delete(cls, db: AsyncSession, id: int) -> bool:
        """
        根据 ID 删除记录
        :param db: 异步数据库会话
        :param id: 主键 ID
        :return: 是否删除成功
        """
        obj = await cls.get_by_id(db, id)
        if obj is None:
            return False
        await db.delete(obj)
        await db.flush()
        return True