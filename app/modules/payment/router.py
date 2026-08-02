"""
支付模块路由
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.response import success
from app.core.dependencies import get_current_user
from app.modules.user.model import User
from app.modules.payment.schema import PayRequest, MockPayRequest, PaymentResponse
from app.modules.payment.service import PaymentService

router = APIRouter(prefix="/api/payment", tags=["支付模块"])


@router.post("/create", summary="发起支付")
async def create_payment(
    req: PayRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """创建支付单，返回支付调起参数"""
    # TODO: 上线后改为 wechat，开发阶段用 mock
    result = await PaymentService.create_payment(db, current_user.id, req.order_id, pay_method="mock")
    return success(data=result, message="支付单创建成功")


@router.post("/mock-pay", summary="模拟支付（开发测试用）")
async def mock_pay(
    req: MockPayRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """模拟支付完成，直接将订单标记为已付款"""
    payment = await PaymentService.mock_pay_complete(db, current_user.id, req.order_id)
    return success(data=PaymentResponse.model_validate(payment).model_dump(), message="支付成功")


@router.post("/wechat-callback", summary="微信支付回调")
async def wechat_pay_callback(
    db: AsyncSession = Depends(get_db),
):
    """微信支付回调通知（TODO: 接入真实微信支付后实现验签逻辑）"""
    # TODO: 解析微信回调数据，验签后调用 PaymentService.wechat_pay_callback
    return success(message="回调接收成功")