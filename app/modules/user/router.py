"""
用户模块路由
严格遵循 Router -> Service -> Model 三层结构，Router 中不写业务逻辑
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.response import success
from app.core.dependencies import get_current_user
from app.core.exceptions import BusinessException
from app.modules.user.model import User
from app.modules.user.schema import (
    UserRegisterRequest,
    UserLoginRequest,
    UserUpdateRequest,
    UserInfoResponse,
    LoginResponse,
)
from app.modules.user.service import UserService

router = APIRouter(prefix="/api/user", tags=["用户模块"])


@router.post("/register", summary="用户注册")
async def register(req: UserRegisterRequest, db: AsyncSession = Depends(get_db)):
    """手机号 + 密码注册"""
    user = await UserService.register(db, req.phone, req.password)
    return success(data=UserInfoResponse.model_validate(user).model_dump(), message="注册成功")


@router.post("/login", summary="用户登录")
async def login(req: UserLoginRequest, db: AsyncSession = Depends(get_db)):
    """手机号 + 密码登录，返回 JWT Token"""
    result = await UserService.login(db, req.phone, req.password)
    user_info = UserInfoResponse.model_validate(result["user"]).model_dump()
    login_data = LoginResponse(token=result["token"], user=UserInfoResponse(**user_info))
    return success(data=login_data.model_dump(), message="登录成功")


@router.get("/me", summary="获取当前用户信息")
async def get_me(current_user: User = Depends(get_current_user)):
    """获取当前登录用户的个人信息"""
    user_info = UserInfoResponse.model_validate(current_user).model_dump()
    return success(data=user_info)


@router.put("/update", summary="更新用户信息")
async def update_user(
    req: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新当前用户的昵称、头像、性别"""
    # 过滤掉 None 值的字段
    update_data = req.model_dump(exclude_none=True)
    if not update_data:
        raise BusinessException(message="没有需要更新的字段")

    user = await UserService.update(db, current_user.id, update_data)
    if user is None:
        raise BusinessException(message="用户不存在")

    user_info = UserInfoResponse.model_validate(user).model_dump()
    return success(data=user_info, message="更新成功")