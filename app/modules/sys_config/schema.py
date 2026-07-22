"""
系统配置模块 Pydantic 模型
"""
from pydantic import BaseModel, Field
from typing import Optional


# ========== 请求模型 ==========

class SysConfigCreateRequest(BaseModel):
    """创建配置请求"""
    key: str = Field(..., min_length=1, max_length=100, description="配置键")
    value: str = Field("", max_length=5000, description="配置值")
    description: str = Field("", max_length=255, description="配置说明")


class SysConfigUpdateRequest(BaseModel):
    """更新配置请求"""
    value: Optional[str] = Field(None, max_length=5000, description="配置值")
    description: Optional[str] = Field(None, max_length=255, description="配置说明")


# ========== 响应模型 ==========

class SysConfigResponse(BaseModel):
    """配置信息响应"""
    id: int
    key: str
    value: str = ""
    description: str = ""
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    model_config = {"from_attributes": True}