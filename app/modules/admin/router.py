"""
管理员路由
所有接口需要管理员权限（role=1）
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.response import success
from app.core.dependencies import get_admin_user
from app.core.exceptions import NotFoundException, BusinessException
from app.modules.user.model import User
from app.modules.product.model import Product
from app.modules.product.schema import ProductCreateRequest, ProductUpdateRequest, ProductResponse
from app.modules.product.service import ProductService
from app.modules.order.model import Order
from app.modules.order.schema import OrderResponse, OrderItemResponse
from app.modules.order.service import OrderService
from app.modules.feedback.model import Feedback
from app.modules.feedback.schema import FeedbackReplyRequest, FeedbackResponse
from app.modules.feedback.service import FeedbackService
from app.modules.sys_config.schema import SysConfigCreateRequest, SysConfigUpdateRequest, SysConfigResponse
from app.modules.sys_config.service import SysConfigService

router = APIRouter(prefix="/api/admin", tags=["管理员"])


def _order_to_response(order) -> dict:
    """将订单对象转为响应字典"""
    items = [OrderItemResponse.model_validate(item).model_dump() for item in order.items]
    resp = OrderResponse.model_validate(order).model_dump()
    resp["items"] = items
    return resp


# ========== 商品管理 ==========

@router.post("/product/create", summary="创建商品")
async def admin_create_product(
    req: ProductCreateRequest,
    admin=Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    product = await ProductService.create(db, req.model_dump())
    return success(data=ProductResponse.model_validate(product).model_dump(), message="创建成功")


@router.put("/product/{product_id}", summary="更新商品")
async def admin_update_product(
    product_id: int,
    req: ProductUpdateRequest,
    admin=Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    update_data = req.model_dump(exclude_none=True)
    if not update_data:
        raise BusinessException(message="没有需要更新的字段")
    product = await ProductService.update(db, product_id, update_data)
    if product is None:
        raise NotFoundException("商品不存在")
    return success(data=ProductResponse.model_validate(product).model_dump(), message="更新成功")


@router.delete("/product/{product_id}", summary="删除商品")
async def admin_delete_product(
    product_id: int,
    admin=Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    deleted = await ProductService.delete(db, product_id)
    if not deleted:
        raise NotFoundException("商品不存在")
    return success(message="删除成功")


# ========== 订单管理 ==========

@router.get("/order/list", summary="所有订单列表")
async def admin_get_orders(
    status: int = Query(None, description="状态筛选"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    admin=Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Order)
    count_query = select(func.count()).select_from(Order)
    if status is not None:
        query = query.where(Order.status == status)
        count_query = count_query.where(Order.status == status)
    query = query.order_by(Order.created_at.desc())

    total_result = await db.execute(count_query)
    total = total_result.scalar_one()
    offset = (page - 1) * page_size
    result = await db.execute(query.offset(offset).limit(page_size))
    orders = result.scalars().all()

    items = [_order_to_response(order) for order in orders]
    return success(data={"items": items, "total": total, "page": page, "page_size": page_size})


@router.put("/order/{order_id}/status", summary="更新订单状态")
async def admin_update_order_status(
    order_id: int,
    req: dict,
    admin=Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.order.schema import OrderStatusUpdateRequest
    status_req = OrderStatusUpdateRequest(**req)
    cancel_reason = req.get("cancel_reason", "")
    order = await OrderService.update_status(db, order_id, status_req.status, cancel_reason=cancel_reason)
    return success(data=_order_to_response(order), message="状态更新成功")


# ========== 反馈管理 ==========

@router.get("/feedback/list", summary="所有反馈列表")
async def admin_get_feedbacks(
    status: int = Query(None, description="状态筛选"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    admin=Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
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


@router.put("/feedback/{feedback_id}/reply", summary="回复反馈")
async def admin_reply_feedback(
    feedback_id: int,
    req: FeedbackReplyRequest,
    admin=Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    feedback = await FeedbackService.reply_feedback(db, feedback_id, req.reply)
    return success(data=FeedbackResponse.model_validate(feedback).model_dump(), message="回复成功")


# ========== 系统配置管理 ==========

@router.post("/config/create", summary="创建配置")
async def admin_create_config(
    req: SysConfigCreateRequest,
    admin=Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    config = await SysConfigService.create_config(db, req.model_dump())
    return success(data=SysConfigResponse.model_validate(config).model_dump(), message="创建成功")


@router.put("/config/key/{key}", summary="按key更新配置")
async def admin_update_config(
    key: str,
    req: SysConfigUpdateRequest,
    admin=Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    update_data = req.model_dump(exclude_none=True)
    if not update_data:
        raise BusinessException(message="没有需要更新的字段")
    config = await SysConfigService.update_by_key(db, key, update_data)
    return success(data=SysConfigResponse.model_validate(config).model_dump(), message="更新成功")


@router.delete("/config/{config_id}", summary="删除配置")
async def admin_delete_config(
    config_id: int,
    admin=Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    deleted = await SysConfigService.delete(db, config_id)
    if not deleted:
        raise NotFoundException("配置不存在")
    return success(message="删除成功")


# ========== 数据统计 ==========

@router.get("/stats", summary="数据统计概览")
async def admin_stats(
    admin=Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    user_count = (await db.execute(select(func.count()).select_from(User))).scalar_one()
    product_count = (await db.execute(select(func.count()).select_from(Product))).scalar_one()
    order_count = (await db.execute(select(func.count()).select_from(Order))).scalar_one()
    feedback_count = (await db.execute(select(func.count()).select_from(Feedback))).scalar_one()

    # 今日订单数
    from datetime import datetime, timedelta
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_orders = (await db.execute(
        select(func.count()).select_from(Order).where(Order.created_at >= today)
    )).scalar_one()

    return success(data={
        "user_count": user_count,
        "product_count": product_count,
        "order_count": order_count,
        "feedback_count": feedback_count,
        "today_orders": today_orders,
    })


# ========== 用户管理 ==========

@router.get("/user/list", summary="用户列表")
async def admin_get_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    admin=Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(User).order_by(User.created_at.desc())
    total_result = await db.execute(select(func.count()).select_from(User))
    total = total_result.scalar_one()
    offset = (page - 1) * page_size
    result = await db.execute(query.offset(offset).limit(page_size))
    from app.modules.user.schema import UserInfoResponse
    items = [UserInfoResponse.model_validate(u).model_dump() for u in result.scalars().all()]
    return success(data={"items": items, "total": total, "page": page, "page_size": page_size})


@router.put("/user/{user_id}/role", summary="设置用户角色")
async def admin_set_user_role(
    user_id: int,
    req: dict,
    admin=Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    role = req.get("role")
    if role not in [0, 1]:
        raise BusinessException(message="角色值必须为0或1")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise NotFoundException("用户不存在")
    user.role = role
    await db.flush()
    await db.refresh(user)
    from app.modules.user.schema import UserInfoResponse
    return success(data=UserInfoResponse.model_validate(user).model_dump(), message="角色更新成功")