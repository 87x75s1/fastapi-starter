import asyncio
from app.core.database import async_session
from sqlalchemy import select
from app.modules.user.model import User
from app.modules.user.schema import UserInfoResponse

async def test():
    async with async_session() as db:
        result = await db.execute(select(User).where(User.phone == '18435709771'))
        user = result.scalar_one_or_none()
        if user:
            info = UserInfoResponse.model_validate(user).model_dump()
            print('role type:', type(info['role']), 'role value:', info['role'])
            print('full info:', info)
        else:
            print('User not found')

asyncio.run(test())