"""
反馈模块 Pydantic 模型
"""
from pydantic import BaseModel, Field
from typing import Optional


# ========== 请求模型 ==========

class FeedbackCreateRequest(BaseModel):
    """提交反馈请求"""
    content: str = Field(..., min_length=1, max_length=2000, description="反馈内容")
    contact: str = Field("", max_length=100, description="联系方式")


class FeedbackReplyRequest(BaseModel):
    """管理员回复请求"""
    reply: str = Field(..., min_length=1, max_length=2000, description="回复内容")


# ========== 响应模型 ==========

class FeedbackResponse(BaseModel):
    """反馈信息响应"""
    id: int
    user_id: int
    content: str
    contact: str = ""
    status: int = 0
    reply: str = ""
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    model_config = {"from_attributes": True}