"""
订单 Service 层
"""
import time
import json
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.base_service import BaseService
from app.core.exceptions import NotFoundException, BusinessException
from app.modules.order.model import Order, OrderItem
from app.modules.product.model import Product


class OrderService(BaseService):
    """订单服务"""
    model = Order

    @classmethod
    def _generate_order_no(cls) -> str:
        """生成订单编号：时间戳 + 4位随机数"""
        import random
        return f"{int(time.time() * 1000)}{random.randint(1000, 9999)}"

    @classmethod
    async def create_order(cls, db: AsyncSession, user_id: int, items_data: list[dict],
                           remark: str = "", address_snapshot: str = "") -> Order:
        """
        创建订单
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

        # 创建订单项
        for item_data in order_items:
            item_data["order_id"] = order.id
            order_item = OrderItem(**item_data)
            db.add(order_item)

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
    async def update_status(cls, db: AsyncSession, order_id: int, status: int) -> Order:
        """更新订单状态"""
        order = await cls.get_by_id(db, order_id)
        if order is None:
            raise NotFoundException("订单不存在")
        order.status = status
        await db.flush()
        await db.refresh(order)
        return order