"""
地址模块 Pydantic 模型
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional


# ========== 请求模型 ==========

class AddressCreateRequest(BaseModel):
    """创建地址请求"""
    name: str = Field(..., min_length=1, max_length=50, description="收货人姓名")
    phone: str = Field(..., min_length=1, max_length=20, description="收货人手机号")
    province: str = Field("", max_length=50, description="省")
    city: str = Field("", max_length=50, description="市")
    district: str = Field("", max_length=50, description="区/县")
    detail: str = Field(..., min_length=1, max_length=200, description="详细地址")
    is_default: int = Field(0, ge=0, le=1, description="是否默认：0否 1是")


class AddressUpdateRequest(BaseModel):
    """更新地址请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="收货人姓名")
    phone: Optional[str] = Field(None, min_length=1, max_length=20, description="收货人手机号")
    province: Optional[str] = Field(None, max_length=50, description="省")
    city: Optional[str] = Field(None, max_length=50, description="市")
    district: Optional[str] = Field(None, max_length=50, description="区/县")
    detail: Optional[str] = Field(None, min_length=1, max_length=200, description="详细地址")
    is_default: Optional[int] = Field(None, ge=0, le=1, description="是否默认：0否 1是")


# ========== 响应模型 ==========

class AddressResponse(BaseModel):
    """地址信息响应"""
    id: int
    user_id: int
    name: str
    phone: str
    province: str = ""
    city: str = ""
    district: str = ""
    detail: str
    is_default: int = 0
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    model_config = {"from_attributes": True}