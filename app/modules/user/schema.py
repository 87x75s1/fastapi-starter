"""
用户模块 Pydantic 模型
定义请求参数校验和响应数据序列化
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional


# ========== 请求模型 ==========

class UserRegisterRequest(BaseModel):
    """用户注册请求"""
    phone: str = Field(..., min_length=11, max_length=11, description="手机号")
    password: str = Field(..., min_length=6, max_length=20, description="密码")

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """手机号格式校验"""
        if not v.isdigit():
            raise ValueError("手机号必须为纯数字")
        if not v.startswith("1"):
            raise ValueError("手机号格式不正确")
        return v


class UserLoginRequest(BaseModel):
    """用户登录请求"""
    phone: str = Field(..., description="手机号")
    password: str = Field(..., description="密码")


class UserUpdateRequest(BaseModel):
    """用户信息更新请求"""
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    avatar: Optional[str] = Field(None, max_length=255, description="头像 URL")
    gender: Optional[int] = Field(None, ge=0, le=2, description="性别：0未知 1男 2女")


# ========== 响应模型 ==========

class UserInfoResponse(BaseModel):
    """用户信息响应"""
    id: int
    phone: str
    nickname: str = ""
    avatar: str = ""
    gender: int = 0
    balance: int = 0
    status: int = 1
    role: int = 0

    model_config = {"from_attributes": True}


class LoginResponse(BaseModel):
    """登录响应（含 Token）"""
    token: str = Field(..., description="JWT Token")
    user: UserInfoResponse