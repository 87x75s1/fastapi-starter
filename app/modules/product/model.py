"""
商品/服务表模型
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, func
from app.core.database import Base


class Product(Base):
    """商品/服务表"""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True, comment="商品ID")
    name = Column(String(100), nullable=False, comment="商品名称")
    description = Column(Text, default="", comment="商品描述")
    price = Column(Integer, nullable=False, comment="价格（单位：分）")
    image = Column(String(255), default="", comment="商品图片URL")
    category = Column(String(50), default="", comment="分类")
    stock = Column(Integer, default=0, comment="库存数量，0表示不限")
    status = Column(Integer, default=1, comment="状态：0下架 1上架")
    sort_order = Column(Integer, default=0, comment="排序值，越大越靠前")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "image": self.image,
            "category": self.category,
            "stock": self.stock,
            "status": self.status,
            "sort_order": self.sort_order,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }