"""
商品模块路由
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.response import success
from app.core.exceptions import BusinessException, NotFoundException
from app.modules.product.model import Product
from app.modules.product.schema import (
    ProductCreateRequest,
    ProductUpdateRequest,
    ProductResponse,
)
from app.modules.product.service import ProductService

router = APIRouter(prefix="/api/product", tags=["商品模块"])


@router.post("/create", summary="创建商品")
async def create_product(req: ProductCreateRequest, db: AsyncSession = Depends(get_db)):
    """创建商品"""
    product = await ProductService.create(db, req.model_dump())
    return success(data=ProductResponse.model_validate(product).model_dump(), message="创建成功")


@router.get("/list", summary="商品列表")
async def get_product_list(
    category: str = Query(None, description="分类筛选"),
    status: int = Query(None, description="状态筛选：0下架 1上架"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
):
    """获取商品列表，支持按分类和状态筛选"""
    offset = (page - 1) * page_size
    result = await ProductService.get_list_by_category(db, category, status, offset, page_size)
    items = [ProductResponse.model_validate(item).model_dump() for item in result["items"]]
    return success(data={"items": items, "total": result["total"], "page": result["page"],
                         "page_size": result["page_size"], "total_pages": result["total_pages"]})


@router.get("/{product_id}", summary="商品详情")
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    """获取单个商品详情"""
    product = await ProductService.get_by_id(db, product_id)
    if product is None:
        raise NotFoundException("商品不存在")
    return success(data=ProductResponse.model_validate(product).model_dump())


@router.put("/{product_id}", summary="更新商品")
async def update_product(product_id: int, req: ProductUpdateRequest, db: AsyncSession = Depends(get_db)):
    """更新商品信息"""
    update_data = req.model_dump(exclude_none=True)
    if not update_data:
        raise BusinessException(message="没有需要更新的字段")
    product = await ProductService.update(db, product_id, update_data)
    if product is None:
        raise NotFoundException("商品不存在")
    return success(data=ProductResponse.model_validate(product).model_dump(), message="更新成功")


@router.delete("/{product_id}", summary="删除商品")
async def delete_product(product_id: int, db: AsyncSession = Depends(get_db)):
    """删除商品"""
    deleted = await ProductService.delete(db, product_id)
    if not deleted:
        raise NotFoundException("商品不存在")
    return success(message="删除成功")