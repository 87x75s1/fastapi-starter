"""
支付模块 Pydantic 模型
"""
from pydantic import BaseModel, Field
from typing import Optional


class PayRequest(BaseModel):
    """发起支付请求"""
    order_id: int = Field(..., description="订单ID")


class MockPayRequest(BaseModel):
    """模拟支付请求（测试用）"""
    order_id: int = Field(..., description="订单ID")


class PaymentResponse(BaseModel):
    """支付响应"""
    id: int
    order_id: int
    user_id: int
    order_no: str
    amount: int = 0
    pay_method: str = "wechat"
    transaction_id: str = ""
    status: int = 0
    created_at: Optional[str] = None

    model_config = {"from_attributes": True}


class WechatPayResult(BaseModel):
    """微信支付调起参数"""
    timeStamp: str = ""
    nonceStr: str = ""
    package: str = ""
    signType: str = "MD5"
    paySign: str = ""