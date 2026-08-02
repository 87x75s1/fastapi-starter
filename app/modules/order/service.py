"""
订单 Service 层
"""
import time
import json
from datetime import datetime, timedelta
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.base_service import BaseService
from app.core.exceptions import NotFoundException, BusinessException
from app.modules.order.model import Order, OrderItem
from app.modules.product.model import Product


class OrderService(BaseService):
    """订单服务"""
    model = Order

    # 订单号计数器（进程内，重启从数据库恢复）
    _order_seq = 0
    _last_seq_date = ""

    @classmethod
    def _generate_order_no(cls) -> str:
        """生成可读订单号：SO + 日期 + 6位序号，如 SO20260723-000001"""
        today = datetime.now().strftime("%Y%m%d")
        if cls._last_seq_date != today:
            cls._last_seq_date = today
            cls._order_seq = 0
        cls._order_seq += 1
        return f"SO{today}-{cls._order_seq:06d}"

    @classmethod
    async def create_order(cls, db: AsyncSession, user_id: int, items_data: list[dict],
                           remark: str = "", address_snapshot: str = "") -> Order:
        """
        创建订单（含库存扣减）
        :param items_data: [{"product_id": 1, "quantity": 2}, ...]
        """
        total_amount = 0
        order_items = []

        for item in items_data:
            product_id = item["product_id"]
            quantity = item["quantity"]

            # 查询商品
            result = await db.execute(select(Product).where(Product.id == product_id))
            product = result.scalar_one_or_none()
            if product is None:
                raise NotFoundException(f"商品ID {product_id} 不存在")
            if product.status != 1:
                raise BusinessException(message=f"商品「{product.name}」已下架")

            # 库存检查（stock=0表示不限库存）
            if product.stock > 0 and product.stock < quantity:
                raise BusinessException(message=f"商品「{product.name}」库存不足，当前库存{product.stock}")

            # 计算金额
            item_amount = product.price * quantity
            total_amount += item_amount

            order_items.append({
                "product_id": product.id,
                "product_name": product.name,
                "product_image": product.image,
                "price": product.price,
                "quantity": quantity,
            })

        # 创建订单
        order_no = cls._generate_order_no()
        order = Order(
            user_id=user_id,
            order_no=order_no,
            total_amount=total_amount,
            remark=remark,
            address_snapshot=address_snapshot,
        )
        db.add(order)
        await db.flush()
        await db.refresh(order)

        # 创建订单项 + 扣减库存
        for item_data in order_items:
            item_data["order_id"] = order.id
            order_item = OrderItem(**item_data)
            db.add(order_item)

            # 扣减库存（stock=0不限库存不扣）
            if item_data["quantity"] > 0:
                product_id = item_data["product_id"]
                qty = item_data["quantity"]
                result = await db.execute(
                    update(Product)
                    .where(Product.id == product_id, Product.stock > 0)
                    .values(stock=Product.stock - qty)
                )
                # 如果没有行被更新，说明stock=0（不限库存），不需要扣

        await db.flush()
        await db.refresh(order)
        return order

    @classmethod
    async def get_user_orders(cls, db: AsyncSession, user_id: int,
                               status: int = None, offset: int = 0, limit: int = 20) -> dict:
        """获取用户订单列表"""
        query = select(Order).where(Order.user_id == user_id)
        count_query = select(func.count()).select_from(Order).where(Order.user_id == user_id)

        if status is not None:
            query = query.where(Order.status == status)
            count_query = count_query.where(Order.status == status)

        query = query.order_by(Order.created_at.desc())

        total_result = await db.execute(count_query)
        total = total_result.scalar_one()

        result = await db.execute(query.offset(offset).limit(limit))
        orders = result.scalars().all()

        page = (offset // limit) + 1 if limit > 0 else 1
        total_pages = (total + limit - 1) // limit if limit > 0 else 0

        return {"items": orders, "total": total, "page": page,
                "page_size": limit, "total_pages": total_pages}

    @classmethod
    async def get_order_detail(cls, db: AsyncSession, order_id: int, user_id: int = None) -> Order:
        """获取订单详情（含订单项）"""
        query = select(Order).where(Order.id == order_id)
        if user_id:
            query = query.where(Order.user_id == user_id)

        result = await db.execute(query)
        order = result.scalar_one_or_none()
        if order is None:
            raise NotFoundException("订单不存在")
        return order

    @classmethod
    async def update_status(cls, db: AsyncSession, order_id: int, status: int,
                            cancel_reason: str = "") -> Order:
        """
        更新订单状态（含状态流转校验）
        流转规则：0待付款→1已付款→2已完成 / 0待付款→3已取消
        """
        order = await cls.get_by_id(db, order_id)
        if order is None:
            raise NotFoundException("订单不存在")

        # 状态流转校验
        valid_transitions = {
            0: [1, 3],  # 待付款→已付款/已取消
            1: [2, 3],  # 已付款→已完成/已取消
            2: [],       # 已完成不可变更
            3: [],       # 已取消不可变更
        }
        if status not in valid_transitions.get(order.status, []):
            raise BusinessException(message=f"订单状态不允许从{order.status}变更为{status}")

        order.status = status

        # 支付时间
        if status == 1:
            order.paid_at = datetime.now()

        # 完成时间
        if status == 2:
            order.completed_at = datetime.now()

        # 取消原因 + 恢复库存
        if status == 3:
            order.cancel_reason = cancel_reason or "用户取消"
            await cls._restore_stock(db, order)

        await db.flush()
        await db.refresh(order)
        return order

    @classmethod
    async def _restore_stock(cls, db: AsyncSession, order: Order):
        """取消订单时恢复库存"""
        result = await db.execute(
            select(OrderItem).where(OrderItem.order_id == order.id)
        )
        items = result.scalars().all()
        for item in items:
            if item.quantity > 0:
                await db.execute(
                    update(Product)
                    .where(Product.id == item.product_id, Product.stock > 0)
                    .values(stock=Product.stock + item.quantity)
                )

    @classmethod
    async def cancel_expired_orders(cls, db: AsyncSession) -> int:
        """取消超时未付款订单（30分钟），返回取消数量"""
        expire_time = datetime.now() - timedelta(minutes=30)
        result = await db.execute(
            select(Order).where(
                Order.status == 0,
                Order.created_at < expire_time
            )
        )
        expired_orders = result.scalars().all()
        count = 0
        for order in expired_orders:
            order.status = 3
            order.cancel_reason = "超时未付款，系统自动取消"
            await cls._restore_stock(db, order)
            count += 1
        if count > 0:
            await db.flush()
        return count