"""
系统配置模块路由
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.response import success
from app.core.exceptions import NotFoundException, BusinessException
from app.modules.sys_config.schema import (
    SysConfigCreateRequest,
    SysConfigUpdateRequest,
    SysConfigResponse,
)
from app.modules.sys_config.service import SysConfigService

router = APIRouter(prefix="/api/config", tags=["系统配置"])


@router.post("/create", summary="创建配置")
async def create_config(req: SysConfigCreateRequest, db: AsyncSession = Depends(get_db)):
    """创建系统配置项"""
    config = await SysConfigService.create_config(db, req.model_dump())
    return success(data=SysConfigResponse.model_validate(config).model_dump(), message="创建成功")


@router.get("/list", summary="配置列表")
async def get_config_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """获取所有配置列表"""
    offset = (page - 1) * page_size
    result = await SysConfigService.get_list(db, offset, page_size)
    items = [SysConfigResponse.model_validate(item).model_dump() for item in result["items"]]
    return success(data={"items": items, "total": result["total"], "page": result["page"],
                         "page_size": result["page_size"], "total_pages": result["total_pages"]})


@router.get("/key/{key}", summary="按key获取配置")
async def get_config_by_key(key: str, db: AsyncSession = Depends(get_db)):
    """根据 key 获取配置值（前端常用）"""
    config = await SysConfigService.get_by_key(db, key)
    if config is None:
        raise NotFoundException(f"配置键「{key}」不存在")
    return success(data=SysConfigResponse.model_validate(config).model_dump())


@router.put("/key/{key}", summary="按key更新配置")
async def update_config_by_key(key: str, req: SysConfigUpdateRequest, db: AsyncSession = Depends(get_db)):
    """根据 key 更新配置值"""
    update_data = req.model_dump(exclude_none=True)
    if not update_data:
        raise BusinessException(message="没有需要更新的字段")
    config = await SysConfigService.update_by_key(db, key, update_data)
    return success(data=SysConfigResponse.model_validate(config).model_dump(), message="更新成功")


@router.delete("/{config_id}", summary="删除配置")
async def delete_config(config_id: int, db: AsyncSession = Depends(get_db)):
    """删除配置项"""
    deleted = await SysConfigService.delete(db, config_id)
    if not deleted:
        raise NotFoundException("配置不存在")
    return success(message="删除成功")