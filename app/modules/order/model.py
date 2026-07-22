"""
订单表模型
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Order(Base):
    """订单表"""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True, comment="订单ID")
    user_id = Column(Integer, nullable=False, index=True, comment="用户ID")
    order_no = Column(String(32), unique=True, nullable=False, index=True, comment="订单编号")
    total_amount = Column(Integer, nullable=False, comment="订单总金额（单位：分）")
    status = Column(Integer, default=0, comment="状态：0待付款 1已付款 2已完成 3已取消")
    remark = Column(String(500), default="", comment="订单备注")
    address_snapshot = Column(Text, default="", comment="收货地址快照（JSON）")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关联订单项
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "order_no": self.order_no,
            "total_amount": self.total_amount,
            "status": self.status,
            "remark": self.remark,
            "address_snapshot": self.address_snapshot,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class OrderItem(Base):
    """订单项表"""
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True, comment="订单项ID")
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True, comment="订单ID")
    product_id = Column(Integer, nullable=False, comment="商品ID")
    product_name = Column(String(100), nullable=False, comment="商品名称（快照）")
    product_image = Column(String(255), default="", comment="商品图片（快照）")
    price = Column(Integer, nullable=False, comment="单价（单位：分，快照）")
    quantity = Column(Integer, nullable=False, comment="数量")

    order = relationship("Order", back_populates="items")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "order_id": self.order_id,
            "product_id": self.product_id,
            "product_name": self.product_name,
            "product_image": self.product_image,
            "price": self.price,
            "quantity": self.quantity,
        }