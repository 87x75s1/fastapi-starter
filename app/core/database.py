"""
数据库模块 - SQLAlchemy 2.0 异步引擎
提供 Base 模型基类、异步 Session 工厂、get_db 依赖注入
"""
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator

from app.core.config import get_settings

settings = get_settings()

# 创建异步引擎（SQLite 需要 check_same_thread=False）
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
)

# 异步 Session 工厂
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """ORM 模型基类，所有表模型继承此类"""
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI 依赖注入：获取异步数据库会话
    用法：在路由函数参数中声明 db: AsyncSession = Depends(get_db)
    """
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_tables():
    """启动时自动创建所有表（根据 Base 元数据）"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)