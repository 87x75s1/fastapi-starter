"""
反馈模块路由
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.response import success
from app.core.dependencies import get_current_user
from app.core.exceptions import NotFoundException
from app.modules.user.model import User
from app.modules.feedback.schema import (
    FeedbackCreateRequest,
    FeedbackReplyRequest,
    FeedbackResponse,
)
from app.modules.feedback.service import FeedbackService

router = APIRouter(prefix="/api/feedback", tags=["反馈/客服"])


@router.post("/create", summary="提交反馈")
async def create_feedback(
    req: FeedbackCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """提交意见反馈（需登录）"""
    data = {"user_id": current_user.id, "content": req.content, "contact": req.contact}
    feedback = await FeedbackService.create(db, data)
    return success(data=FeedbackResponse.model_validate(feedback).model_dump(), message="提交成功")


@router.get("/list", summary="我的反馈列表")
async def get_my_feedbacks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取当前用户的反馈列表"""
    offset = (page - 1) * page_size
    result = await FeedbackService.get_user_feedbacks(db, current_user.id, offset, page_size)
    items = [FeedbackResponse.model_validate(item).model_dump() for item in result["items"]]
    return success(data={"items": items, "total": result["total"], "page": result["page"],
                         "page_size": result["page_size"], "total_pages": result["total_pages"]})


@router.get("/{feedback_id}", summary="反馈详情")
async def get_feedback(
    feedback_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取反馈详情"""
    feedback = await FeedbackService.get_by_id(db, feedback_id)
    if feedback is None or feedback.user_id != current_user.id:
        raise NotFoundException("反馈不存在")
    return success(data=FeedbackResponse.model_validate(feedback).model_dump())


@router.put("/{feedback_id}/reply", summary="回复反馈（管理员）")
async def reply_feedback(
    feedback_id: int,
    req: FeedbackReplyRequest,
    db: AsyncSession = Depends(get_db),
):
    """管理员回复反馈"""
    feedback = await FeedbackService.reply_feedback(db, feedback_id, req.reply)
    return success(data=FeedbackResponse.model_validate(feedback).model_dump(), message="回复成功")


@router.get("/admin/all", summary="所有反馈列表（管理员）")
async def get_all_feedbacks(
    status: int = Query(None, description="状态筛选：0待处理 1已回复"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """管理员查看所有反馈"""
    from sqlalchemy import select, func
    from app.modules.feedback.model import Feedback
    query = select(Feedback)
    count_query = select(func.count()).select_from(Feedback)
    if status is not None:
        query = query.where(Feedback.status == status)
        count_query = count_query.where(Feedback.status == status)
    query = query.order_by(Feedback.created_at.desc())
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()
    offset = (page - 1) * page_size
    result = await db.execute(query.offset(offset).limit(page_size))
    items = [FeedbackResponse.model_validate(item).model_dump() for item in result.scalars().all()]
    return success(data={"items": items, "total": total, "page": page, "page_size": page_size})