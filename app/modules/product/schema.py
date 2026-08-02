"""
商品模块 Pydantic 模型
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ========== 请求模型 ==========

class ProductCreateRequest(BaseModel):
    """创建商品请求"""
    name: str = Field(..., min_length=1, max_length=100, description="商品名称")
    description: str = Field("", max_length=2000, description="商品描述")
    price: int = Field(..., ge=0, description="价格（单位：分）")
    image: str = Field("", max_length=255, description="商品图片URL")
    category: str = Field("", max_length=50, description="分类")
    stock: int = Field(0, ge=0, description="库存数量，0表示不限")
    sort_order: int = Field(0, ge=0, description="排序值")


class ProductUpdateRequest(BaseModel):
    """更新商品请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="商品名称")
    description: Optional[str] = Field(None, max_length=2000, description="商品描述")
    price: Optional[int] = Field(None, ge=0, description="价格（单位：分）")
    image: Optional[str] = Field(None, max_length=255, description="商品图片URL")
    category: Optional[str] = Field(None, max_length=50, description="分类")
    stock: Optional[int] = Field(None, ge=0, description="库存数量")
    status: Optional[int] = Field(None, ge=0, le=1, description="状态：0下架 1上架")
    sort_order: Optional[int] = Field(None, ge=0, description="排序值")


# ========== 响应模型 ==========

class ProductResponse(BaseModel):
    """商品信息响应"""
    id: int
    name: str
    description: str = ""
    price: int = 0
    image: str = ""
    category: str = ""
    stock: int = 0
    status: int = 1
    sort_order: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}