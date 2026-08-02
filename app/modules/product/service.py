"""
商品 Service 层
"""
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.base_service import BaseService
from app.modules.product.model import Product


class ProductService(BaseService):
    """商品服务"""
    model = Product

    @classmethod
    async def get_list_filtered(
        cls, db: AsyncSession, keyword: str = None, category: str = None,
        status: int = None, min_price: int = None, max_price: int = None,
        sort: str = "default", offset: int = 0, limit: int = 20,
    ) -> dict:
        """
        商品列表 - 支持关键词搜索、分类、价格区间筛选和排序
        """
        query = select(Product)
        count_query = select(Product)

        # 关键词搜索（名称或描述）
        if keyword:
            kw = f"%{keyword}%"
            query = query.where(or_(Product.name.ilike(kw), Product.description.ilike(kw)))
            count_query = count_query.where(or_(Product.name.ilike(kw), Product.description.ilike(kw)))

        # 分类筛选
        if category:
            query = query.where(Product.category == category)
            count_query = count_query.where(Product.category == category)

        # 状态筛选
        if status is not None:
            query = query.where(Product.status == status)
            count_query = count_query.where(Product.status == status)

        # 价格区间
        if min_price is not None:
            query = query.where(Product.price >= min_price)
            count_query = count_query.where(Product.price >= min_price)
        if max_price is not None:
            query = query.where(Product.price <= max_price)
            count_query = count_query.where(Product.price <= max_price)

        # 排序
        if sort == "price_asc":
            query = query.order_by(Product.price.asc(), Product.sort_order.desc())
        elif sort == "price_desc":
            query = query.order_by(Product.price.desc(), Product.sort_order.desc())
        elif sort == "newest":
            query = query.order_by(Product.created_at.desc(), Product.sort_order.desc())
        else:
            query = query.order_by(Product.sort_order.desc(), Product.created_at.desc())

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

    @classmethod
    async def get_categories(cls, db: AsyncSession) -> list:
        """获取所有已有商品的去重分类列表"""
        result = await db.execute(
            select(Product.category)
            .where(Product.category != "", Product.status == 1)
            .distinct()
            .order_by(Product.category)
        )
        return [row[0] for row in result.all()]

    @classmethod
    async def get_list_by_category(
        cls, db: AsyncSession, category: str = None, status: int = None,
        offset: int = 0, limit: int = 20,
    ) -> dict:
        """
        按分类/状态筛选商品列表（兼容旧调用）
        """
        return await cls.get_list_filtered(db, category=category, status=status, offset=offset, limit=limit)