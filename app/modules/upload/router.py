"""
文件上传模块路由
"""
from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.response import success
from app.core.dependencies import get_current_user
from app.modules.upload.service import UploadService
from app.modules.user.model import User
from app.modules.upload.schema import UploadResponse

router = APIRouter(prefix="/api/upload", tags=["文件上传"])


@router.post("/image", summary="上传图片")
async def upload_image(
    file: UploadFile = File(..., description="图片文件"),
    current_user: User = Depends(get_current_user),
):
    """
    上传单个图片文件（需登录）
    支持格式：jpg, jpeg, png, gif, webp
    最大尺寸：5MB（可在 .env 中配置）
    返回可访问的 URL
    """
    result = await UploadService.save_image(file)
    upload_data = UploadResponse(**result)
    return success(data=upload_data.model_dump(), message="上传成功")