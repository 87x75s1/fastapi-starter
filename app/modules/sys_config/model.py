"""
系统配置表模型
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, func
from app.core.database import Base


class SysConfig(Base):
    """系统配置表（键值对）"""
    __tablename__ = "sys_configs"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True, comment="ID")
    key = Column(String(100), unique=True, nullable=False, index=True, comment="配置键")
    value = Column(Text, default="", comment="配置值")
    description = Column(String(255), default="", comment="配置说明")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "key": self.key,
            "value": self.value,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }