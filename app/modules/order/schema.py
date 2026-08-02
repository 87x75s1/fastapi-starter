"""
订单模块 Pydantic 模型
"""
from pydantic import BaseModel, Field
from typing import Optional


# ========== 请求模型 ==========

class OrderItemInput(BaseModel):
    """订单项输入"""
    product_id: int = Field(..., description="商品ID")
    quantity: int = Field(..., ge=1, description="数量")


class OrderCreateRequest(BaseModel):
    """创建订单请求"""
    items: list[OrderItemInput] = Field(..., min_length=1, description="商品列表")
    remark: str = Field("", max_length=500, description="订单备注")
    address_id: Optional[int] = Field(None, description="收货地址ID（可选）")


class OrderStatusUpdateRequest(BaseModel):
    """更新订单状态请求"""
    status: int = Field(..., ge=0, le=3, description="状态：0待付款 1已付款 2已完成 3已取消")


# ========== 响应模型 ==========

class OrderItemResponse(BaseModel):
    """订单项响应"""
    id: int
    product_id: int
    product_name: str
    product_image: str = ""
    price: int
    quantity: int

    model_config = {"from_attributes": True}


class OrderResponse(BaseModel):
    """订单响应"""
    id: int
    user_id: int
    order_no: str
    total_amount: int
    status: int = 0
    remark: str = ""
    address_snapshot: str = ""
    paid_at: Optional[str] = None
    completed_at: Optional[str] = None
    cancel_reason: str = ""
    items: list[OrderItemResponse] = []
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    model_config = {"from_attributes": True}