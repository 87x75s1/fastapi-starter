"""
商品 Service 层
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.base_service import BaseService
from app.modules.product.model import Product


class ProductService(BaseService):
    """商品服务"""
    model = Product

    @classmethod
    async def get_list_by_category(
        cls, db: AsyncSession, category: str = None, status: int = None,
        offset: int = 0, limit: int = 20,
    ) -> dict:
        """
        按分类/状态筛选商品列表
        """
        query = select(Product)
        count_query = select(Product)

        if category:
            query = query.where(Product.category == category)
            count_query = count_query.where(Product.category == category)
        if status is not None:
            query = query.where(Product.status == status)
            count_query = count_query.where(Product.status == status)

        # 按排序值降序、创建时间降序
        query = query.order_by(Product.sort_order.desc(), Product.created_at.desc())

        from sqlalchemy import func
        total_result = await db.execute(select(func.count()).select_from(count_query.subquery()))
        total = total_result.scalar_one()

        result = await db.execute(query.offset(offset).limit(limit))
        items = result.scalars().all()

        page = (offset // limit) + 1 if limit > 0 else 1
        total_pages = (total + limit - 1) // limit if limit > 0 else 0

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": limit,
            "total_pages": total_pages,
        }