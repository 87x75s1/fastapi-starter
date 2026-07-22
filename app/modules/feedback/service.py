"""
反馈 Service 层
"""
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.base_service import BaseService
from app.modules.feedback.model import Feedback


class FeedbackService(BaseService):
    """反馈服务"""
    model = Feedback

    @classmethod
    async def get_user_feedbacks(cls, db: AsyncSession, user_id: int,
                                  offset: int = 0, limit: int = 20) -> dict:
        """获取用户的反馈列表"""
        query = select(Feedback).where(Feedback.user_id == user_id).order_by(Feedback.created_at.desc())
        total_result = await db.execute(
            select(func.count()).select_from(Feedback).where(Feedback.user_id == user_id)
        )
        total = total_result.scalar_one()

        result = await db.execute(query.offset(offset).limit(limit))
        items = result.scalars().all()

        page = (offset // limit) + 1 if limit > 0 else 1
        total_pages = (total + limit - 1) // limit if limit > 0 else 0

        return {"items": items, "total": total, "page": page,
                "page_size": limit, "total_pages": total_pages}

    @classmethod
    async def reply_feedback(cls, db: AsyncSession, feedback_id: int, reply: str) -> Feedback:
        """管理员回复反馈"""
        feedback = await cls.get_by_id(db, feedback_id)
        if feedback is None:
            from app.core.exceptions import NotFoundException
            raise NotFoundException("反馈不存在")
        feedback.reply = reply
        feedback.status = 1
        await db.flush()
        await db.refresh(feedback)
        return feedback