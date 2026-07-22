"""
意见反馈表模型
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, func
from app.core.database import Base


class Feedback(Base):
    """意见反馈表"""
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True, comment="反馈ID")
    user_id = Column(Integer, nullable=False, index=True, comment="用户ID")
    content = Column(Text, nullable=False, comment="反馈内容")
    contact = Column(String(100), default="", comment="联系方式（手机/邮箱）")
    status = Column(Integer, default=0, comment="状态：0待处理 1已回复")
    reply = Column(Text, default="", comment="管理员回复")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "content": self.content,
            "contact": self.contact,
            "status": self.status,
            "reply": self.reply,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }