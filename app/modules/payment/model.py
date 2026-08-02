"""
支付记录表模型
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, func
from app.core.database import Base


class Payment(Base):
    """支付记录表"""
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True, comment="支付ID")
    order_id = Column(Integer, nullable=False, index=True, comment="订单ID")
    user_id = Column(Integer, nullable=False, index=True, comment="用户ID")
    order_no = Column(String(32), nullable=False, comment="订单编号")
    amount = Column(Integer, nullable=False, comment="支付金额（单位：分）")
    pay_method = Column(String(20), default="wechat", comment="支付方式：wechat微信 / mock模拟")
    transaction_id = Column(String(64), default="", comment="第三方交易号")
    status = Column(Integer, default=0, comment="状态：0待支付 1已支付 2失败")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "order_id": self.order_id,
            "user_id": self.user_id,
            "order_no": self.order_no,
            "amount": self.amount,
            "pay_method": self.pay_method,
            "transaction_id": self.transaction_id,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }