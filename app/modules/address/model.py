"""
收货地址表模型
"""
from sqlalchemy import Column, Integer, String, DateTime, func
from app.core.database import Base


class Address(Base):
    """收货地址表"""
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True, comment="地址ID")
    user_id = Column(Integer, nullable=False, index=True, comment="用户ID")
    name = Column(String(50), nullable=False, comment="收货人姓名")
    phone = Column(String(20), nullable=False, comment="收货人手机号")
    province = Column(String(50), default="", comment="省")
    city = Column(String(50), default="", comment="市")
    district = Column(String(50), default="", comment="区/县")
    detail = Column(String(200), nullable=False, comment="详细地址")
    is_default = Column(Integer, default=0, comment="是否默认：0否 1是")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "phone": self.phone,
            "province": self.province,
            "city": self.city,
            "district": self.district,
            "detail": self.detail,
            "is_default": self.is_default,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }