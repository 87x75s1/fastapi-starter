"""
启动初始化 - 自动创建管理员账号
"""
from sqlalchemy import select
from app.core.database import async_session
from app.modules.user.model import User
from app.utils.common import hash_password

# 管理员账号，写死
ADMIN_PHONE = "18435709771"
ADMIN_PASSWORD = "000000"


async def init_admin_user():
    """启动时确保管理员账号存在且role=1，不存在则自动创建"""
    async with async_session() as db:
        result = await db.execute(select(User).where(User.phone == ADMIN_PHONE))
        user = result.scalar_one_or_none()

        if user is None:
            # 不存在，直接创建
            user = User(
                phone=ADMIN_PHONE,
                password=hash_password(ADMIN_PASSWORD),
                role=1,
                nickname="管理员",
            )
            db.add(user)
            await db.commit()
            print(f"✅ 已创建管理员账号 {ADMIN_PHONE}，密码 {ADMIN_PASSWORD}")
        elif user.role != 1:
            # 存在但不是管理员，修正
            user.role = 1
            await db.commit()
            print(f"✅ {ADMIN_PHONE} 已设为管理员")
        else:
            print(f"✅ {ADMIN_PHONE} 已是管理员")