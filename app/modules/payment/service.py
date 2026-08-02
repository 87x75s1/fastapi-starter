"""
支付 Service 层
支持微信支付 + 模拟支付（开发测试用）
"""
import time
import uuid
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.base_service import BaseService
from app.core.exceptions import NotFoundException, BusinessException
from app.modules.payment.model import Payment
from app.modules.order.model import Order
from app.modules.order.service import OrderService


class PaymentService(BaseService):
    """支付服务"""
    model = Payment

    @classmethod
    async def create_payment(cls, db: AsyncSession, user_id: int, order_id: int,
                              pay_method: str = "wechat") -> dict:
        """
        创建支付单，返回支付调起参数
        :param pay_method: "wechat" 微信支付 / "mock" 模拟支付
        """
        # 查询订单
        order = await OrderService.get_order_detail(db, order_id, user_id)
        if order.status != 0:
            raise BusinessException(message="订单不是待付款状态，无法支付")

        # 检查是否已有待支付的支付单
        result = await db.execute(
            select(Payment).where(
                Payment.order_id == order_id,
                Payment.status == 0
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            # 复用已有的支付单
            payment = existing
        else:
            # 创建支付记录
            payment = Payment(
                order_id=order_id,
                user_id=user_id,
                order_no=order.order_no,
                amount=order.total_amount,
                pay_method=pay_method,
                status=0,
            )
            db.add(payment)
            await db.flush()
            await db.refresh(payment)

        if pay_method == "mock":
            # 模拟支付：直接返回模拟参数，前端调mock-pay接口完成支付
            return {
                "payment_id": payment.id,
                "order_id": order_id,
                "amount": order.total_amount,
                "pay_method": "mock",
                "order_no": order.order_no,
            }
        else:
            # 微信支付：返回调起参数
            # TODO: 接入真实微信支付后替换
            # 当前返回模拟数据，前端可先对接wx.requestPayment流程
            return {
                "payment_id": payment.id,
                "order_id": order_id,
                "amount": order.total_amount,
                "pay_method": "wechat",
                "order_no": order.order_no,
                # 微信支付调起参数（模拟）
                "pay_params": {
                    "timeStamp": str(int(time.time())),
                    "nonceStr": uuid.uuid4().hex,
                    "package": f"prepay_id=mock_{payment.id}",
                    "signType": "MD5",
                    "paySign": "mock_sign_placeholder",
                }
            }

    @classmethod
    async def mock_pay_complete(cls, db: AsyncSession, user_id: int, order_id: int) -> Payment:
        """模拟支付完成（开发测试用）"""
        # 查询订单
        order = await OrderService.get_order_detail(db, order_id, user_id)
        if order.status != 0:
            raise BusinessException(message="订单不是待付款状态")

        # 查找支付记录
        result = await db.execute(
            select(Payment).where(
                Payment.order_id == order_id,
                Payment.status == 0
            )
        )
        payment = result.scalar_one_or_none()
        if payment is None:
            raise NotFoundException("未找到待支付记录")

        # 更新支付记录
        payment.status = 1
        payment.transaction_id = f"MOCK_{int(time.time() * 1000)}"
        payment.pay_method = "mock"

        # 更新订单状态为已付款
        await OrderService.update_status(db, order_id, 1)

        await db.flush()
        await db.refresh(payment)
        return payment

    @classmethod
    async def wechat_pay_callback(cls, db: AsyncSession, order_id: int,
                                   transaction_id: str) -> Payment:
        """
        微信支付回调处理
        TODO: 接入真实微信支付回调验签后调用此方法
        """
        result = await db.execute(
            select(Payment).where(
                Payment.order_id == order_id,
                Payment.status == 0
            )
        )
        payment = result.scalar_one_or_none()
        if payment is None:
            raise NotFoundException("未找到待支付记录")

        payment.status = 1
        payment.transaction_id = transaction_id
        payment.pay_method = "wechat"

        # 更新订单状态
        await OrderService.update_status(db, order_id, 1)

        await db.flush()
        await db.refresh(payment)
        return payment