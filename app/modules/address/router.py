"""
地址模块路由
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.response import success
from app.core.dependencies import get_current_user
from app.core.exceptions import NotFoundException, BusinessException
from app.modules.user.model import User
from app.modules.address.schema import (
    AddressCreateRequest,
    AddressUpdateRequest,
    AddressResponse,
)
from app.modules.address.service import AddressService

router = APIRouter(prefix="/api/address", tags=["地址管理"])


@router.post("/create", summary="创建地址")
async def create_address(
    req: AddressCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """创建收货地址"""
    address = await AddressService.create_address(db, current_user.id, req.model_dump())
    return success(data=AddressResponse.model_validate(address).model_dump(), message="创建成功")


@router.get("/list", summary="我的地址列表")
async def get_my_addresses(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取当前用户所有地址"""
    addresses = await AddressService.get_user_addresses(db, current_user.id)
    items = [AddressResponse.model_validate(addr).model_dump() for addr in addresses]
    return success(data=items)


@router.get("/{address_id}", summary="地址详情")
async def get_address(
    address_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取单个地址详情"""
    address = await AddressService.get_by_id(db, address_id)
    if address is None or address.user_id != current_user.id:
        raise NotFoundException("地址不存在")
    return success(data=AddressResponse.model_validate(address).model_dump())


@router.put("/{address_id}", summary="更新地址")
async def update_address(
    address_id: int,
    req: AddressUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新地址信息"""
    update_data = req.model_dump(exclude_none=True)
    if not update_data:
        raise BusinessException(message="没有需要更新的字段")
    address = await AddressService.update_address(db, address_id, current_user.id, update_data)
    return success(data=AddressResponse.model_validate(address).model_dump(), message="更新成功")


@router.put("/{address_id}/default", summary="设为默认地址")
async def set_default_address(
    address_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """设置默认地址"""
    address = await AddressService.set_default(db, address_id, current_user.id)
    return success(data=AddressResponse.model_validate(address).model_dump(), message="设置成功")


@router.delete("/{address_id}", summary="删除地址")
async def delete_address(
    address_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除地址"""
    address = await AddressService.get_by_id(db, address_id)
    if address is None or address.user_id != current_user.id:
        raise NotFoundException("地址不存在")
    await AddressService.delete(db, address_id)
    return success(message="删除成功")