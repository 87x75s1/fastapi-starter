"""
订单模块路由
"""
import json
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.response import success
from app.core.dependencies import get_current_user
from app.core.exceptions import NotFoundException, BusinessException
from app.modules.user.model import User
from app.modules.order.schema import (
    OrderCreateRequest,
    OrderStatusUpdateRequest,
    OrderResponse,
    OrderItemResponse,
)
from app.modules.order.service import OrderService

router = APIRouter(prefix="/api/order", tags=["订单模块"])


def _order_to_response(order) -> dict:
    """将订单对象转为响应字典（含订单项）"""
    items = [OrderItemResponse.model_validate(item).model_dump() for item in order.items]
    resp = OrderResponse.model_validate(order).model_dump()
    resp["items"] = items
    return resp


@router.post("/create", summary="创建订单")
async def create_order(
    req: OrderCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """创建订单（需登录）"""
    items_data = [item.model_dump() for item in req.items]
    address_snapshot = ""
    if req.address_id:
        from app.modules.address.model import Address
        from sqlalchemy import select
        result = await db.execute(select(Address).where(Address.id == req.address_id, Address.user_id == current_user.id))
        addr = result.scalar_one_or_none()
        if addr:
            address_snapshot = json.dumps({
                "name": addr.name, "phone": addr.phone,
                "province": addr.province, "city": addr.city,
                "district": addr.district, "detail": addr.detail,
            }, ensure_ascii=False)

    order = await OrderService.create_order(db, current_user.id, items_data, req.remark, address_snapshot)
    return success(data=_order_to_response(order), message="下单成功")


@router.get("/list", summary="我的订单列表")
async def get_my_orders(
    status: int = Query(None, description="状态筛选：0待付款 1已付款 2已完成 3已取消"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取当前用户的订单列表"""
    offset = (page - 1) * page_size
    result = await OrderService.get_user_orders(db, current_user.id, status, offset, page_size)
    items = [_order_to_response(order) for order in result["items"]]
    return success(data={"items": items, "total": result["total"], "page": result["page"],
                         "page_size": result["page_size"], "total_pages": result["total_pages"]})


@router.get("/{order_id}", summary="订单详情")
async def get_order_detail(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取订单详情"""
    order = await OrderService.get_order_detail(db, order_id, current_user.id)
    return success(data=_order_to_response(order))


@router.put("/{order_id}/status", summary="更新订单状态")
async def update_order_status(
    order_id: int,
    req: OrderStatusUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新订单状态（取消/确认等）"""
    order = await OrderService.update_status(db, order_id, req.status)
    return success(data=_order_to_response(order), message="状态更新成功")


@router.delete("/{order_id}", summary="取消订单")
async def cancel_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """取消订单（将状态设为3，恢复库存）"""
    order = await OrderService.update_status(db, order_id, 3, cancel_reason="用户取消")
    return success(data=_order_to_response(order), message="订单已取消")