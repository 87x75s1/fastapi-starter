"""
用户表模型
定义用户表的字段结构
"""
from sqlalchemy import Column, Integer, String, DateTime, func
from app.core.database import Base


class User(Base):
    """用户表"""
    __tablename__ = "users"

    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True, index=True, comment="用户ID")

    # 基础信息
    phone = Column(String(20), unique=True, nullable=False, index=True, comment="手机号")
    password = Column(String(128), nullable=False, comment="密码（bcrypt 哈希）")
    nickname = Column(String(50), default="", comment="昵称")
    avatar = Column(String(255), default="", comment="头像 URL")
    gender = Column(Integer, default=0, comment="性别：0未知 1男 2女")

    # 业务字段
    balance = Column(Integer, default=0, comment="余额（单位：分）")
    status = Column(Integer, default=1, comment="状态：0禁用 1启用")

    # 时间字段
    created_at = Column(
        DateTime, server_default=func.now(), comment="创建时间"
    )
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间"
    )

    def to_dict(self) -> dict:
        """转换为字典（排除敏感字段）"""
        return {
            "id": self.id,
            "phone": self.phone,
            "nickname": self.nickname,
            "avatar": self.avatar,
            "gender": self.gender,
            "balance": self.balance,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }